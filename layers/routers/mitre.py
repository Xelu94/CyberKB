from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
from models import MitreTechnique
from pydantic import BaseModel
import re

# Catálogo de referencia ATT&CK (helper compartido con _persist_mitre)
from layers.routers_functions import _MITRE_REF, _MITRE_REF_BY_ID


router = APIRouter()


@router.get("/api/mitre")
def list_mitre(db: Session = Depends(get_db)):
    """Return all MITRE techniques grouped by tactic."""
    rows = db.query(MitreTechnique).order_by(MitreTechnique.tactic, MitreTechnique.technique_id).all()
    grouped: dict = {}
    for r in rows:
        tactic = r.tactic or "Uncategorized"
        grouped.setdefault(tactic, []).append({
            "id": r.id,
            "technique_id": r.technique_id,
            "technique_name": r.technique_name,
            "tactic": r.tactic,
            "context_snippet": r.context_snippet,
            "note_id": r.note_id,
        })
    return {"tactics": grouped, "total": len(rows)}


@router.get("/api/mitre/search")
def search_mitre(q: str = "", db: Session = Depends(get_db)):
    """Search MITRE techniques by ID, name or tactic."""
    query = db.query(MitreTechnique)
    if q:
        like = f"%{q}%"
        query = query.filter(
            MitreTechnique.technique_id.ilike(like) |
            MitreTechnique.technique_name.ilike(like) |
            MitreTechnique.tactic.ilike(like) |
            MitreTechnique.context_snippet.ilike(like)
        )
    rows = query.order_by(MitreTechnique.tactic, MitreTechnique.technique_id).limit(200).all()
    return [
        {
            "id": r.id,
            "technique_id": r.technique_id,
            "technique_name": r.technique_name,
            "tactic": r.tactic,
            "context_snippet": r.context_snippet,
            "note_id": r.note_id,
        }
        for r in rows
    ]


@router.get("/api/mitre/reference")
def mitre_reference(q: str = "", limit: int = 40):
    """[Módulo MITRE] Busca en el catálogo de referencia ATT&CK (local) por ID
    (T1055), nombre o táctica. Alimenta el buscador de "añadir técnica". Prioriza
    las coincidencias de ID/nombre sobre las de táctica."""
    query = (q or "").strip().lower()
    if not query:
        return {"count": 0, "results": []}

    def score(t):
        idl, nm = t["id"].lower(), t["name"].lower()
        if idl == query: return 0
        if idl.startswith(query): return 1
        if query in idl: return 2
        if nm.startswith(query): return 3
        if query in nm: return 4
        return 5

    matches = [t for t in _MITRE_REF
               if query in t["id"].lower() or query in t["name"].lower()
               or any(query in tac.lower() for tac in t.get("tactics", []))]
    matches.sort(key=score)
    return {"count": len(matches), "results": matches[:limit]}


class MitreCreate(BaseModel):
    technique_id: str


@router.post("/api/mitre", status_code=201)
def create_mitre(data: MitreCreate, db: Session = Depends(get_db)):
    """[Módulo MITRE] Añade una técnica a la KB desde el buscador de referencia.
    Rellena nombre/táctica/descripción desde el catálogo. Upsert por technique_id
    de las añadidas a mano (note_id NULL): si ya está, no la duplica."""
    tid = (data.technique_id or "").strip().upper()
    if not re.match(r"^T\d{4}(\.\d{3})?$", tid):
        raise HTTPException(400, "ID de técnica inválido (esperado T#### o T####.###)")
    ref = _MITRE_REF_BY_ID.get(tid)
    if not ref:
        raise HTTPException(404, f"{tid} no está en el catálogo de referencia ATT&CK")
    existing = db.query(MitreTechnique).filter(
        MitreTechnique.technique_id == tid, MitreTechnique.note_id.is_(None)).first()
    if existing:
        return {"created": False, "id": existing.id, "technique_id": tid}
    mt = MitreTechnique(
        note_id=None, technique_id=tid, technique_name=ref["name"],
        tactic=(ref.get("tactics") or [None])[0], context_snippet=ref.get("desc"))
    db.add(mt); db.commit(); db.refresh(mt)
    return {"created": True, "id": mt.id, "technique_id": tid}


@router.delete("/api/mitre/technique/{tid}", status_code=204)
def delete_mitre_technique(tid: str, db: Session = Depends(get_db)):
    """[Módulo MITRE] Quita una técnica del módulo POR COMPLETO: borra todas sus
    filas (vengan de notas o añadidas a mano). Es lo que hace el 🗑 de la tarjeta,
    que en la vista está agregada por técnica (2A)."""
    tid = (tid or "").strip().upper()
    rows = db.query(MitreTechnique).filter(MitreTechnique.technique_id == tid).all()
    if not rows:
        raise HTTPException(404, "Técnica no encontrada")
    for r in rows:
        db.delete(r)
    db.commit()
    return


@router.delete("/api/mitre/{mid}", status_code=204)
def delete_mitre(mid: int, db: Session = Depends(get_db)):
    """[Módulo MITRE] Borra una fila concreta de técnica por su id numérico."""
    row = db.query(MitreTechnique).filter(MitreTechnique.id == mid).first()
    if not row:
        raise HTTPException(404, "Técnica no encontrada")
    db.delete(row); db.commit()
    return