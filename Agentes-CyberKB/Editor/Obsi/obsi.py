"""Agente Obsi de CyberKB.

Ultimo eslabon de la cadena de ingesta: recibe de Agente-BBDD los ids de las
filas que acaba de confirmar en SQLite, las relee directamente de la base de
datos y sincroniza el vault de Obsidian con ellas (crea, actualiza o borra
notas huerfanas), agrupando cada nota en la carpeta que le corresponde segun
el tipo de entidad.

Ruta de la cadena: Agrupador -> Agente-BBDD -> Obsi -> vault de Obsidian.
Ver Editor/Obsi/DECISIONES_OBSI.md para el porque de cada decision de diseno.

Para engancharlo en main.py. El repositorio de agentes es hermano del de la app y su
nombre lleva guion, asi que no se puede importar como paquete:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(
        Path(__file__).resolve().parent.parent / "Agentes-CyberKB" / "Editor" / "Obsi"
    ))
    from obsi import router as obsi_router
    app.include_router(obsi_router)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

# Modulos de la aplicacion. Estan en sys.path porque main.py los carga primero,
# igual que el agente Agente-BBDD importa database/models.
import database
from database import SessionLocal
from models import CVE, Command, MitreTechnique, Note, Tool

# vault_lib.py vive en esta misma carpeta: no hace falta sys.path extra.
import vault_lib as vl

BASE_DIR = Path(__file__).resolve().parent
CFG = json.loads((BASE_DIR / "config.json").read_text(encoding="utf-8"))
ERRORES = CFG["errores"]

# database.py ya resuelve la raiz real de la app (y contempla el caso de un
# build empaquetado con PyInstaller, ver `_runtime_dir()` ahi mismo) -- se
# reutiliza esa misma ancla en vez de recalcularla con Path(__file__), que
# apuntaria al repo de agentes (hermano), no al de la app.
PROJECT_ROOT = database.RUNTIME_DIR
VAULT_DIR = Path(
    os.getenv("OBSIDIAN_VAULT_DIR") or (PROJECT_ROOT / CFG["vault"]["directorio_por_defecto"])
).resolve()

router = APIRouter(prefix="/api/obsi", tags=["obsi"])


class IdsSync(BaseModel):
    """Lo que envia Agente-BBDD (o el frontend, en un reintento aislado).

    Los tipos de id no son homogeneos a proposito: herramientas/comandos usan el
    id numerico de fila; cves/mitre usan cve_id/technique_id (texto), que es como
    el vault ya identifica a esos dos tipos (una nota por identificador unico, no
    por fila — ver vault_lib.py).
    """

    nota_id: int | None = None
    herramientas_ids: list[int] = []
    comandos_ids: list[int] = []
    cves_ids: list[str] = []
    mitre_ids: list[str] = []


# --------------------------------------------------------------- construccion


def _relacionadas_de_nota(nota: Note) -> list[str]:
    rel = [vl.wl(vl.sanitize(t.name, f"Herramienta-{t.id}")) for t in nota.tools]
    rel += [vl.wl(vl.sanitize(c.cve_id, f"CVE-{c.id}")) for c in nota.cves]
    tecnicas_vistas: set[str] = set()
    for m in nota.mitre_techniques:
        tid = (m.technique_id or "").strip()
        if tid and tid not in tecnicas_vistas:
            tecnicas_vistas.add(tid)
            rel.append(vl.wl(f"Tecnica-MITRE-{vl.sanitize(tid, tid)}"))
    rel += [vl.wl(f"Comando-{c.id}") for c in nota.commands]
    return rel


def _sync_nota(db: Session, nota_id: int, resultado: dict) -> None:
    nota = db.get(Note, nota_id)
    if nota is None:
        return

    fields = {
        "id": nota.id,
        "title": nota.title,
        "category": nota.category,
        "subcategory": nota.subcategory,
        "tags": vl.parse_tags(nota.tags),
        "source_file": nota.source_file,
        "summary": nota.summary,
        "content": nota.content,
        "fecha_actualizacion": nota.updated_at or nota.created_at,
    }
    base, body = vl.build_nota(fields, _relacionadas_de_nota(nota))
    _escribir(resultado, "nota", f"nota-{nota.id}", base, body)


def _sync_herramientas(db: Session, ids: list[int], resultado: dict) -> None:
    for tid in ids:
        tool = db.get(Tool, tid)
        if tool is None:
            continue
        related = [vl.wl(vl.sanitize(n.title, f"Nota-{n.id}")) for n in tool.tools]
        fields = {
            "id": tool.id,
            "name": tool.name,
            "url": tool.url,
            "category": tool.category,
            "tool_type": tool.tool_type,
            "description": tool.description,
            "use_cases": tool.use_cases,
            "fecha_actualizacion": tool.updated_at or tool.created_at,
        }
        base, body = vl.build_herramienta(fields, related)
        _escribir(resultado, "herramienta", f"herramienta-{tool.id}", base, body)


def _sync_comandos(db: Session, ids: list[int], resultado: dict) -> None:
    for cid in ids:
        cmd = db.get(Command, cid)
        if cmd is None:
            continue
        related = []
        if cmd.note_id:
            nota = db.get(Note, cmd.note_id)
            if nota is not None:
                related.append(vl.wl(vl.sanitize(nota.title, f"Nota-{nota.id}")))
        if cmd.tool_name:
            tool = db.execute(select(Tool).where(Tool.name.ilike(cmd.tool_name))).scalars().first()
            if tool is not None:
                related.append(vl.wl(vl.sanitize(tool.name, f"Herramienta-{tool.id}")))

        fields = {
            "id": cmd.id,
            "command": cmd.command,
            "os": cmd.os,
            "category": cmd.category,
            "tool_name": cmd.tool_name,
            "description": cmd.description,
            "flags": vl.parse_tags(cmd.flags),
            "fecha_actualizacion": cmd.created_at,
        }
        base, body = vl.build_comando(fields, related)
        _escribir(resultado, "comando", f"comando-{cmd.id}", base, body)


def _sync_cves(db: Session, ids: list[str], resultado: dict) -> None:
    for cve_id in ids:
        cve = db.execute(select(CVE).where(CVE.cve_id == cve_id)).scalars().first()
        if cve is None:
            continue
        related = []
        if cve.note_id:
            nota = db.get(Note, cve.note_id)
            if nota is not None:
                related.append(vl.wl(vl.sanitize(nota.title, f"Nota-{nota.id}")))

        fields = {
            "id": cve.cve_id,
            "title": cve.title,
            "severity": cve.severity,
            "cvss": cve.cvss,
            "affected": cve.affected,
            "description": cve.description,
            "fecha_actualizacion": cve.created_at,
        }
        base, body = vl.build_cve(fields, related)
        _escribir(resultado, "cve", f"cve-{cve.cve_id}", base, body)


def _sync_mitre(db: Session, ids: list[str], resultado: dict) -> None:
    for tecnica_id in ids:
        filas = db.execute(
            select(MitreTechnique).where(MitreTechnique.technique_id == tecnica_id)
        ).scalars().all()
        if not filas:
            continue

        nombre = next((f.technique_name for f in filas if f.technique_name), None)
        tactica = next((f.tactic for f in filas if f.tactic), None)
        snippets = [f.context_snippet for f in filas if f.context_snippet]
        note_ids = {f.note_id for f in filas if f.note_id}

        related = []
        for nid in note_ids:
            nota = db.get(Note, nid)
            if nota is not None:
                related.append(vl.wl(vl.sanitize(nota.title, f"Nota-{nota.id}")))

        fields = {
            "id": tecnica_id,
            "name": nombre,
            "tactic": tactica,
            "snippets": snippets,
            "fecha_actualizacion": None,
        }
        base, body = vl.build_tecnica_mitre(fields, related)
        _escribir(resultado, "tecnica-mitre", f"tecnica-mitre-{tecnica_id}", base, body)


def _escribir(resultado: dict, tipo: str, entity_id: str, base: str, body: str) -> None:
    relativa, accion, borrada = vl.write_synced(VAULT_DIR, tipo, entity_id, base, body)
    if accion == "creada":
        resultado["notas_creadas"].append(relativa)
    else:
        resultado["notas_actualizadas"].append(relativa)
    if borrada:
        resultado["notas_borradas"].append(borrada)


# ----------------------------------------------------------------- orquestacion


def _procesar(datos: IdsSync) -> dict:
    resultado: dict = {"notas_creadas": [], "notas_actualizadas": [], "notas_borradas": []}
    db = SessionLocal()
    try:
        if datos.nota_id is not None:
            _sync_nota(db, datos.nota_id, resultado)
        _sync_herramientas(db, datos.herramientas_ids, resultado)
        _sync_comandos(db, datos.comandos_ids, resultado)
        _sync_cves(db, datos.cves_ids, resultado)
        _sync_mitre(db, datos.mitre_ids, resultado)
    except Exception:
        # No se toca la BBDD en ningun momento (solo lectura): el vault puede
        # haber quedado con una escritura parcial, pero eso no arriesga los
        # datos de la app. El mensaje es el que pidio el usuario para que el
        # frontend pueda ofrecer "Reintentar" sobre el grafo especificamente.
        raise HTTPException(500, ERRORES["generico"])
    finally:
        db.close()

    return {"sincronizado": True, **resultado}


@router.post("/sync")
async def sync(datos: IdsSync):
    """Entrada de Agente-BBDD (o de un reintento aislado desde el frontend):
    ids ya confirmados en SQLite que hay que reflejar en el vault de Obsidian.
    """
    return _procesar(datos)
