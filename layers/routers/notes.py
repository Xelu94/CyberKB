from typing import Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from database import get_db
from models import Note, Command, CVE, MitreTechnique
import json
from pathlib import Path
from datetime import datetime

from layers.routers_functions import _note_dict, NoteIn
# Generador de PDF del Escritor (sus carpetas las pone main.py en sys.path).
from escritor import _a_pdf as _escritor_pdf


router = APIRouter()


@router.get("/api/notes")
def list_notes(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    q = db.query(Note)
    if category and category != "all":
        q = q.filter(Note.category == category)
    if search:
        q = q.filter(
            Note.title.ilike(f"%{search}%") | Note.content.ilike(f"%{search}%")
        )
    notes = q.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    return [_note_dict(n) for n in notes]


@router.get("/api/notes/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)):
    n = db.query(Note).filter(Note.id == note_id).first()
    if not n:
        raise HTTPException(404, "Note not found")
    return _note_dict(n, full=True)


@router.get("/api/notes/{note_id}/pdf")
def download_note_pdf(note_id: int, db: Session = Depends(get_db)):
    """Genera al vuelo un PDF con el resumen de la nota (reutiliza el generador del
    Escritor) y lo devuelve como descarga. La nota no guarda el PDF original, asi que
    se regenera desde su contenido; vale para cualquier nota ya existente."""
    n = db.query(Note).filter(Note.id == note_id).first()
    if not n:
        raise HTTPException(404, "Note not found")
    texto = (n.summary or n.content or "").strip() or "(sin contenido)"
    fecha = (n.updated_at or n.created_at or datetime.utcnow()).isoformat(timespec="seconds")
    import tempfile
    ruta = Path(tempfile.mkdtemp()) / f"nota_{n.id}.pdf"
    _escritor_pdf(ruta, n.title, texto, n.source_file or "app", fecha)
    nombre = "".join(ch if ch not in '\\/:*?"<>|' else " " for ch in n.title).strip()[:80] or f"nota_{n.id}"
    return FileResponse(str(ruta), media_type="application/pdf", filename=f"{nombre}.pdf")


@router.post("/api/notes", status_code=201)
def create_note(data: NoteIn, db: Session = Depends(get_db)):
    n = Note(
        title=data.title,
        content=data.content,
        category=data.category,
        subcategory=data.subcategory,
        summary=data.summary,
        tags=json.dumps(data.tags or []),
        source_file=data.source_file,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return _note_dict(n)


@router.put("/api/notes/{note_id}")
def update_note(note_id: int, data: NoteIn, db: Session = Depends(get_db)):
    n = db.query(Note).filter(Note.id == note_id).first()
    if not n:
        raise HTTPException(404, "Note not found")
    n.title = data.title
    n.content = data.content
    n.category = data.category
    n.subcategory = data.subcategory
    n.summary = data.summary
    n.tags = json.dumps(data.tags or [])
    n.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(n)
    return _note_dict(n)


@router.delete("/api/notes/all", status_code=204)
def delete_all_notes(db: Session = Depends(get_db)):
    """Wipe all notes, commands, CVEs, tool-note associations and graph data."""
    from sqlalchemy import text
    db.execute(text("DELETE FROM tool_notes"))
    db.execute(text("DELETE FROM entity_note_map"))
    db.execute(text("DELETE FROM entity_relations"))
    db.execute(text("DELETE FROM graph_entities"))
    db.query(MitreTechnique).delete()
    db.query(CVE).delete()
    db.query(Command).delete()
    db.query(Note).delete()
    db.commit()


@router.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    n = db.query(Note).filter(Note.id == note_id).first()
    if not n:
        raise HTTPException(404, "Note not found")
    db.delete(n)
    db.commit()