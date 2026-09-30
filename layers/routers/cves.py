from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from database import get_db
from models import CVE
import re


from layers.routers_functions import _cve_dict


router = APIRouter()


@router.get("/api/cves")
def list_cves(db: Session = Depends(get_db)):
    cves = db.query(CVE).order_by(CVE.created_at.desc()).all()
    return [_cve_dict(c) for c in cves]


@router.get("/api/cves/{cve_id}/exploits")
async def cve_exploits(cve_id: str):
    """Query Exploit-DB for public exploits for a given CVE."""
    import httpx
    # Strip 'CVE-' prefix for the search query
    cve_num = re.sub(r"^CVE-", "", cve_id.strip(), flags=re.IGNORECASE)
    try:
        headers = {
            "User-Agent": "CyberKB/3.0",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.exploit-db.com/search",
        }
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            r = await client.get(
                "https://www.exploit-db.com/search",
                params={
                    "action": "search",
                    "cve": cve_num,
                    "draw": "1",
                    "columns[0][data]": "id",
                    "columns[1][data]": "date_published",
                    "columns[2][data]": "title",
                    "columns[3][data]": "type",
                    "columns[4][data]": "platform",
                    "columns[5][data]": "verified",
                    "order[0][column]": "1",
                    "order[0][dir]": "desc",
                    "start": "0",
                    "length": "10",
                },
            )
        if r.status_code != 200:
            return {"cve_id": cve_id, "count": 0, "exploits": [], "error": f"EDB HTTP {r.status_code}"}
        data = r.json()
        rows = data.get("data", [])
        exploits = []
        for row in rows[:10]:
            eid = row.get("id", "")
            exploits.append({
                "id":       eid,
                "title":    row.get("description_cut", row.get("title", "")),
                "date":     row.get("date_published", row.get("date", ""))[:10] if row.get("date_published") or row.get("date") else "",
                "type":     row.get("type", {}).get("name", "") if isinstance(row.get("type"), dict) else str(row.get("type", "")),
                "platform": row.get("platform", {}).get("name", "") if isinstance(row.get("platform"), dict) else str(row.get("platform", "")),
                "url":      f"https://www.exploit-db.com/exploits/{eid}" if eid else "",
                "verified": bool(row.get("verified")),
            })
        return {"cve_id": cve_id, "count": len(exploits), "exploits": exploits}
    except Exception as e:
        return {"cve_id": cve_id, "count": 0, "exploits": [], "error": str(e)}


# ─── Exploit-DB (búsqueda por texto, compartida con el módulo de Enumeración) ──
_EDB_HEADERS = {
    "User-Agent": "CyberKB/3.0",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.exploit-db.com/search",
}


async def _edb_search(extra_params: dict, limit: int = 15):
    """Consulta la búsqueda JSON (formato DataTables) de Exploit-DB y devuelve
    (exploits, error). Lo usa el buscador por versión (módulo Enumeración) vía
    /api/exploit-search; solo cambian los `extra_params` ('q' o 'cve').
    """
    import httpx
    import asyncio
    params = {
        "action": "search", "draw": "1",
        "columns[0][data]": "id", "columns[1][data]": "date_published",
        "columns[2][data]": "title", "columns[3][data]": "type",
        "columns[4][data]": "platform", "columns[5][data]": "verified",
        "order[0][column]": "1", "order[0][dir]": "desc",
        "start": "0", "length": str(limit),
        **extra_params,
    }
    # Exploit-DB va detrás de Cloudflare y responde lento/intermitente (502, 503,
    # 429, timeouts). Reintentamos varias veces con backoff creciente para absorber
    # esos fallos transitorios; los estados NO transitorios (p. ej. 403 = bloqueo)
    # cortan el bucle porque insistir no ayuda y solo alarga la espera.
    TRANSIENT = {429, 500, 502, 503, 504}
    delays = [1.0, 2.0]                 # esperas entre intentos → len(delays)+1 intentos
    last_err = None
    for attempt in range(len(delays) + 1):
        try:
            async with httpx.AsyncClient(timeout=20, headers=_EDB_HEADERS) as client:
                r = await client.get("https://www.exploit-db.com/search", params=params)
            if r.status_code == 200:
                return _edb_map(r.json().get("data", []), limit), None
            last_err = f"Exploit-DB devolvió HTTP {r.status_code}"
            if r.status_code not in TRANSIENT:
                break
        except Exception as e:
            last_err = str(e)
        if attempt < len(delays):
            await asyncio.sleep(delays[attempt])
    return [], last_err


def _edb_map(rows: list, limit: int) -> list:
    """Normaliza las filas crudas de Exploit-DB al objeto que devolvemos.

    El JSON de EDB usa nombres de campo poco intuitivos (viene de un DataTables):
      - el título está en description[1]  (description = ["id", "título"])
      - la plataforma en platform_id      (o platform.platform si es dict)
      - el tipo en type_id                (o type.name)
      - el CVE, dentro de la lista code[]  (y a veces trae códigos que NO son CVE)
    Por eso el mapeo tiene tantos .get() con alternativas.
    """
    exploits = []
    for row in rows[:limit]:
        eid = row.get("id", "")
        desc = row.get("description")
        title = desc[1] if isinstance(desc, list) and len(desc) > 1 else (row.get("title") or "")
        platform = row.get("platform_id") or (
            row.get("platform", {}).get("platform", "") if isinstance(row.get("platform"), dict) else "")
        typ = row.get("type_id") or (
            row.get("type", {}).get("name", "") if isinstance(row.get("type"), dict) else "")
        cve = ""
        code = row.get("code")
        if isinstance(code, list) and code and isinstance(code[0], dict):
            c0 = code[0].get("code", "")
            # Solo lo tratamos como CVE si tiene forma AAAA-NNNN (el campo también
            # trae otros identificadores, p. ej. de Metasploit)
            if re.match(r"^\d{4}-\d{3,}$", c0):
                cve = "CVE-" + c0
        exploits.append({
            "id": eid, "title": title, "date": (row.get("date_published") or "")[:10],
            "type": typ, "platform": platform, "cve": cve,
            "url": f"https://www.exploit-db.com/exploits/{eid}" if eid else "",
            "verified": bool(row.get("verified")),
        })
    return exploits


@router.get("/api/exploit-search")
async def exploit_search(q: str):
    """[Módulo de Enumeración] Busca exploits públicos por producto + versión.

    Da servicio al buscador «Versión → ¿exploit conocido?» de la pestaña ③
    Enumerar servicios: resuelve el paso "tengo una versión detectada en el
    escaneo, ¿existe exploit público?". Consulta en vivo la búsqueda de
    Exploit-DB (exploit-db.com, sin API key) y devuelve, por cada resultado,
    título, tipo, plataforma, fecha, CVE (si lo tiene) y enlace. Es el gemelo
    por texto de GET /api/cves/{cve_id}/exploits, que busca lo mismo por CVE.
    """
    query = (q or "").strip()
    if not query:
        return {"query": q, "count": 0, "exploits": []}
    exploits, error = await _edb_search({"q": query}, limit=15)
    res = {"query": query, "count": len(exploits), "exploits": exploits}
    if error:
        res["error"] = error
    return res


# ─── NVD (National Vulnerability Database, NIST) — ficha oficial de un CVE ─────
async def _nvd_lookup(cve_id: str) -> dict:
    """Consulta la API pública de NVD (NIST) por un CVE y devuelve su ficha
    oficial: descripción, CVSS/severidad, CWE, fechas y referencias.

    NVD es la fuente autoritativa "qué es este CVE y cómo de grave es". No hace
    falta API key (hay límite de tasa, de sobra para uso interactivo).

    Siempre devuelve un dict con la clave 'found' (True/False) para que quien lo
    llame no tenga que capturar excepciones: si algo falla, found=False + 'error'.
    """
    import httpx
    try:
        # La API v2.0 filtra por un CVE concreto con el parámetro cveId
        async with httpx.AsyncClient(timeout=15, headers={"User-Agent": "CyberKB/3.0"}) as client:
            r = await client.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={"cveId": cve_id},
            )
        if r.status_code != 200:
            return {"found": False, "cve_id": cve_id, "error": f"NVD HTTP {r.status_code}"}
        # La respuesta trae una lista 'vulnerabilities'; cada elemento tiene un 'cve'
        vulns = r.json().get("vulnerabilities", [])
        if not vulns:
            return {"found": False, "cve_id": cve_id}
        cve = vulns[0].get("cve", {})

        # Descripción: NVD la da en varios idiomas; cogemos la inglesa
        desc = next((d.get("value", "") for d in cve.get("descriptions", []) if d.get("lang") == "en"), "")

        # CVSS: un CVE puede traer métricas en varias versiones del estándar.
        # Preferimos la más nueva disponible (3.1 > 3.0 > 2.0) y paramos en la 1ª.
        cvss = severity = vector = None
        metrics = cve.get("metrics", {})
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if metrics.get(key):
                m = metrics[key][0]
                cdata = m.get("cvssData", {})
                cvss = cdata.get("baseScore")          # p. ej. 10.0
                severity = cdata.get("baseSeverity") or m.get("baseSeverity")  # p. ej. CRITICAL
                vector = cdata.get("vectorString")     # cadena CVSS (AV:N/AC:L/...)
                break

        # CWE = tipo de fallo (p. ej. CWE-89 = SQLi). Está anidado en 'weaknesses'.
        cwes = []
        for w in cve.get("weaknesses", []):
            for d in w.get("description", []):
                v = d.get("value", "")
                if v.startswith("CWE-") and v not in cwes:
                    cwes.append(v)

        # Referencias (advisories, parches...): nos quedamos con las 6 primeras
        refs = [ref.get("url", "") for ref in cve.get("references", []) if ref.get("url")][:6]

        return {
            "found": True,
            "cve_id": cve.get("id", cve_id),
            "description": desc,
            "cvss": cvss,
            "severity": (severity or "").capitalize() or None,  # CRITICAL -> Critical
            "vector": vector,
            "cwe": cwes,
            "published": (cve.get("published") or "")[:10],       # solo la fecha (YYYY-MM-DD)
            "modified": (cve.get("lastModified") or "")[:10],
            "references": refs,
        }
    except Exception as e:
        return {"found": False, "cve_id": cve_id, "error": str(e)}


@router.get("/api/cve-lookup")
async def cve_lookup(id: str):
    """[Módulo CVEs] Busca cualquier CVE por su ID en NVD (ficha oficial).

    Lo llama el frontend cuando escribes un ID (CVE-AAAA-NNNN) que no tienes en
    la KB y pulsas "Buscar en NVD". Validamos el formato aquí para no gastar una
    petición a NVD con basura.
    """
    cid = (id or "").strip().upper()
    if not re.match(r"^CVE-\d{4}-\d{4,}$", cid):
        raise HTTPException(400, "Formato de CVE inválido (esperado CVE-AAAA-NNNN)")
    return await _nvd_lookup(cid)


# Cuerpo (JSON) que acepta POST /api/cves. Solo cve_id es obligatorio; el resto
# se rellena con lo que traiga la ficha de NVD al guardar.
class CVECreate(BaseModel):
    cve_id: str
    description: Optional[str] = None
    severity: Optional[str] = None
    cvss: Optional[float] = None
    title: Optional[str] = None


@router.post("/api/cves")
def create_cve(data: CVECreate, db: Session = Depends(get_db)):
    """[Módulo CVEs] Guarda un CVE en la KB (botón "Guardar" tras buscar en NVD).

    Va a la misma tabla `cves` que los CVEs que la IA detecta en documentos.
    Es un upsert: si el CVE ya existe, actualiza sus campos en vez de duplicarlo;
    devuelve created=True/False para que el frontend sepa qué pasó.
    """
    cid = data.cve_id.strip().upper()
    if not re.match(r"^CVE-\d{4}-\d{4,}$", cid):
        raise HTTPException(400, "Formato de CVE inválido")
    row = db.query(CVE).filter(CVE.cve_id == cid).first()
    if row:
        # Ya existe → solo sobreescribimos los campos que llegan con valor
        if data.description:
            row.description = data.description
        if data.severity:
            row.severity = data.severity
        if data.cvss is not None:
            row.cvss = data.cvss
        if data.title:
            row.title = data.title
        db.commit()
        db.refresh(row)
        return {"created": False, **_cve_dict(row)}
    # No existe → fila nueva
    row = CVE(cve_id=cid, description=data.description, severity=data.severity,
              cvss=data.cvss, title=data.title)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"created": True, **_cve_dict(row)}


@router.delete("/api/cves/{cid}", status_code=204)
def delete_cve(cid: int, db: Session = Depends(get_db)):
    """[Módulo CVEs] Borra un CVE de la KB (botón 🗑 de la tarjeta).

    Da simetría con Herramientas, que ya tenía borrado. Antes un CVE guardado a
    mano (sin nota asociada) no se podía quitar por ninguna vía. Se borra por id
    numérico (PK), igual que DELETE /api/tools/{id}.
    """
    row = db.query(CVE).filter(CVE.id == cid).first()
    if not row:
        raise HTTPException(404, "CVE no encontrado en la base de datos")
    db.delete(row)
    db.commit()
    return


@router.post("/api/cves/{cve_id}/enrich")
async def enrich_cve(cve_id: str, db: Session = Depends(get_db)):
    """[Módulo CVEs] Rellena CVSS/severidad/descripción oficiales de un CVE que
    YA está en la KB, consultando NVD (botón "↻ Enriquecer").

    Útil porque los CVEs detectados por la IA a veces traen esos campos vacíos o
    imprecisos; aquí los sustituimos por los datos autoritativos de NVD.
    """
    row = db.query(CVE).filter(CVE.cve_id == cve_id).first()
    if not row:
        raise HTTPException(404, "CVE no encontrado en la base de datos")
    nvd = await _nvd_lookup(cve_id)
    if not nvd.get("found"):
        return {"updated": False, "error": nvd.get("error") or "no encontrado en NVD"}
    if nvd.get("cvss") is not None:
        row.cvss = nvd["cvss"]
    if nvd.get("severity"):
        row.severity = nvd["severity"]
    if nvd.get("description"):
        row.description = nvd["description"]
    db.commit()
    db.refresh(row)
    return {"updated": True, **_cve_dict(row)}