from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
import osint_tools as osint
import claude_service as ai
import json
from models import Note, CVE
import re


from layers.routers_functions import _persist_mitre, _reanalizar_con_agrupador


router = APIRouter()


def _family_from_vt_label(label: str) -> str:
    """Extrae la familia de la etiqueta sugerida de VT: 'ransomware.wannacry/x'
    → 'Wannacry'. Se usa solo como respaldo de la firma de MalwareBazaar."""
    if not label:
        return ""
    core = label.split(".", 1)[1] if "." in label else label   # quita la categoría
    fam = core.split("/")[0].strip()                           # familia antes de la variante
    return fam.capitalize()


@router.get("/api/forensic/keys")
def forensic_keys():
    """[Módulo Forense] Presencia de las keys que usa el pipeline. Lo usa el
    frontend para avisar antes de analizar si falta alguna esencial. Solo dice si
    están puestas (no si son válidas — eso se comprueba al analizar de verdad)."""
    return {
        "virustotal":    bool(osint.VT_KEY),
        "malwarebazaar": bool(osint.MALWAREBAZAAR_KEY),
        "anyrun":        bool(osint.ANYRUN_KEY),
    }


@router.post("/api/forensic/analyze")
async def forensic_analyze(hash: str, db: Session = Depends(get_db)):
    """Full forensic pipeline: VT + MalwareBazaar (parallel) → Any.run (conditional) → AI note."""
    import asyncio

    hash_str = hash.strip().lower()
    if not re.match(r"^[0-9a-f]{32}$|^[0-9a-f]{40}$|^[0-9a-f]{64}$", hash_str):
        raise HTTPException(400, "Hash inválido — se admite MD5 (32), SHA1 (40) o SHA256 (64 hex)")

    # ── Step 1+2: VT + MalwareBazaar in parallel ──────────────────────────────
    vt_task  = osint.hash_vt(hash_str)
    mb_task  = osint.hash_malwarebazaar(hash_str)
    vt_data, mb_data = await asyncio.gather(vt_task, mb_task)

    # ── 1C: chequeo de keys ───────────────────────────────────────────────────
    # Si una key esencial no está o no funciona (auth_error), paramos ANTES de
    # gastar la IA y avisamos. MalwareBazaar solo consulta SHA256; con MD5/SHA1
    # su error no es de key, así que solo cuenta como fallo de key si es SHA256.
    bad_keys = []
    if vt_data.get("auth_error"):
        bad_keys.append("VirusTotal")
    if mb_data.get("auth_error") and len(hash_str) == 64:
        bad_keys.append("MalwareBazaar")
    if bad_keys:
        raise HTTPException(400, "API keys no configuradas o inválidas: "
                            + ", ".join(bad_keys) + ". Configúralas en Ajustes (⚙).")

    # ── 2A: sin datos → no alucinar ───────────────────────────────────────────
    # Si ni VT ni MalwareBazaar tienen datos del hash (desconocido/nunca subido),
    # NO llamamos a la IA (inventaría el informe): guardamos una nota honesta.
    if vt_data.get("error") and mb_data.get("error"):
        title = f"Análisis forense — {hash_str[:16]} — sin datos"
        body = (f"**Hash**: `{hash_str}`\n\n## Sin datos de reputación\n"
                "Ni VirusTotal ni MalwareBazaar tienen información de este hash "
                "(muestra desconocida o nunca subida). No se genera análisis para "
                "no especular sin datos.\n\n"
                f"- VirusTotal: {vt_data.get('error', '—')}\n"
                f"- MalwareBazaar: {mb_data.get('error', '—')}\n")
        n = Note(title=title, content=body, category="forense",
                 subcategory="malware-analysis", summary="Hash sin datos de reputación",
                 tags=json.dumps(["forense", "malware", "sin-datos", "veredicto:sin-datos"]),
                 source_file=f"forensic:{hash_str[:16]}")
        db.add(n); db.commit(); db.refresh(n)
        return {"note_id": n.id, "title": title, "vt": vt_data, "mb": mb_data,
                "anyrun": {"note": "no consultado (sin datos)"}, "timeline": {},
                "cves_found": 0, "mitre_found": 0, "tags": ["sin-datos"], "no_data": True}

    # ── Step 3: Any.run if VT detections > 5 ─────────────────────────────────
    anyrun_data: dict = {"note": "No consultado (score VT ≤ 5 o error)"}
    vt_detected = vt_data.get("detected", 0) if not vt_data.get("error") else 0
    if vt_detected > 5:
        anyrun_data = await osint.anyrun_lookup(hash_str)

    # ── Step 4: AI synthesis ──────────────────────────────────────────────────
    note_data = ai.generate_forensic_note(hash_str, vt_data, mb_data, anyrun_data)

    # ── Step 5: Persist note ──────────────────────────────────────────────────
    from datetime import date as _date
    title = note_data.get("title") or f"Análisis forense — {hash_str[:16]}"
    content_body = note_data.get("content", "")
    htype = {32: "MD5", 40: "SHA1", 64: "SHA256"}.get(len(hash_str), "Hash")

    # Prepend timeline block to content
    tl = note_data.get("timeline", {})
    tl_items = [
        ("Creación malware",   tl.get("created", "")),
        ("Primera subida VT",  tl.get("first_submission", "")),
        ("Primera vez in-wild",tl.get("first_seen_itw", "")),
        ("Último análisis",    tl.get("last_analysis", "")),
    ]
    tl_md = "\n".join(f"- **{label}**: {val}" for label, val in tl_items if val)
    if tl_md:
        content_body = f"## Timeline\n{tl_md}\n\n" + content_body

    # Include raw hash at top (con su tipo real: MD5/SHA1/SHA256)
    content_body = f"**{htype}**: `{hash_str}`\n\n" + content_body

    # Veredicto de 2 palabras para el histórico (según detecciones de VirusTotal;
    # si VT no dio score pero MalwareBazaar sí conoce el hash, es malware conocido).
    det = vt_data.get("detected", 0) if not vt_data.get("error") else None
    if det is not None:
        verdict = "limpio" if det == 0 else ("sospechoso" if det <= 4 else "infeccion")
    else:
        verdict = "infeccion" if not mb_data.get("error") else "sin-datos"

    # Nombre de familia SOLO si lo tenemos con confianza: la firma curada de
    # MalwareBazaar, o (con muchas detecciones) la etiqueta sugerida de VT. Si no,
    # el histórico se queda con el veredicto genérico ("Posible infección"…).
    familia = ""
    if not mb_data.get("error") and mb_data.get("signature"):
        familia = str(mb_data["signature"]).strip()
    elif det and det >= 5 and vt_data.get("suggested_label"):
        familia = _family_from_vt_label(vt_data["suggested_label"])

    base_tags = ["forense", "malware", "veredicto:" + verdict]
    if familia:
        base_tags.append("familia:" + familia)
    tags = note_data.get("tags", [])
    tags_json = json.dumps(list(set(base_tags + tags)))

    n = Note(
        title=title,
        content=content_body[:20000],
        category="forense",
        subcategory="malware-analysis",
        summary=note_data.get("summary") or title,
        tags=tags_json,
        source_file=f"forensic:{hash_str[:16]}",
    )
    db.add(n)
    db.commit()
    db.refresh(n)

    # Persist CVEs
    for cve_item in note_data.get("cves", []):
        cve_id = cve_item.get("id", "").strip()
        if not cve_id:
            continue
        if not db.query(CVE).filter(CVE.cve_id == cve_id).first():
            db.add(CVE(cve_id=cve_id, description=cve_item.get("description"), note_id=n.id))
    db.commit()

    # Persist MITRE techniques
    _persist_mitre(note_data.get("mitre_techniques", []), n, db)

    # Reanalisis via Agrupador (tools/commands/cves/mitre/entidades), unificado
    # con /api/notes/{id}/extract y /api/graph/reindex-all -- igual que en main.
    # source="app-reextract" conserva category/subcategory/tags: la clasificacion
    # especializada del forense (veredicto/familia) NO se pisa. Efecto secundario
    # asumido: ruido menor en tools (p.ej. "VirusTotal" puede colarse como tool).
    # Ojo: forensic_analyze es async. La cadena del Agrupador hace HTTP a este
    # mismo servidor (/api/bbdd, /api/obsi), asi que llamarla en linea bloquearia
    # el event loop y el POST anidado se estancaria hasta timeout. La ejecutamos
    # en un hilo (to_thread) para dejar el loop libre y que la cadena funcione.
    # (En main es una llamada directa; aqui la adaptamos por ser endpoint async.)
    try:
        import asyncio
        await asyncio.to_thread(_reanalizar_con_agrupador, n, db)
    except Exception:
        import traceback
        traceback.print_exc()

    return {
        "note_id":    n.id,
        "title":      title,
        "vt":         vt_data,
        "mb":         mb_data,
        "anyrun":     anyrun_data,
        "timeline":   tl,
        "cves_found": len(note_data.get("cves", [])),
        "mitre_found":len(note_data.get("mitre_techniques", [])),
        "tags":       tags,
    }