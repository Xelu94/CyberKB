from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from pathlib import Path
from models import Note
import os
import uuid
import shutil
import document_parser as parser
import progreso  # progreso en vivo del pipeline de agentes (lo lee GET /api/progress)

from layers.routers_functions import AnalyzeIn, _note_dict, _runtime_dir

# Cadena de agentes del Editor (Escritor -> Agrupador -> Agente-BBDD -> Obsi).
# main.py deja las carpetas de los agentes en sys.path al arrancar, antes de
# importar este router, asi que estos imports resuelven.
from escritor import _procesar as _escritor_procesar, MSG_VACIO
from agrupador import _procesar as _agrupador_procesar, ResumenEscritor


router = APIRouter()


RUNTIME_DIR = _runtime_dir()
UPLOAD_DIR = RUNTIME_DIR / os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.get("/api/progress")
def get_progress():
    """Paso actual del pipeline de agentes, para que el frontend lo pinte en vivo.
    Se sirve en paralelo a la peticion larga (los endpoints del pipeline son `def`
    sincronos y corren en el threadpool, asi que el event loop queda libre)."""
    return progreso.get()


@router.post("/api/analyze")
def analyze_text(data: AnalyzeIn, db: Session = Depends(get_db)):
    """Texto pegado directamente en el editor (sin fichero): va derecho a
    Agrupador, sin pasar por Escritor -- pensado para contenido corto y ya
    concreto (un comando, una CVE, una ficha), no para documentos largos que
    necesiten resumen previo."""
    resumen = ResumenEscritor(
        id=uuid.uuid4().hex,
        titulo=(data.title or "").strip() or "Sin titulo",
        resumen=data.text,
        source="app-analyze",
    )
    progreso.iniciar()
    try:
        resultado = _agrupador_procesar(resumen)
    finally:
        progreso.terminar()

    nota = None
    if resultado.get("bbdd_entregado"):
        nota = (
            db.query(Note)
            .filter(Note.title == resultado["titulo"])
            .order_by(Note.id.desc())
            .first()
        )

    return {"agrupador": resultado, "note": _note_dict(nota, full=True) if nota else None}


@router.post("/api/upload")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Documento subido desde el editor: va a Escritor, que encadena a Agrupador
    -> Agente-BBDD -> Obsi. Sin auto_save: la cadena decide por si sola si guarda."""
    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".odt", ".docx", ".html", ".htm", ".txt", ".md", ".log"):
        raise HTTPException(400, f"Unsupported file type: {ext}")

    dest = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = parser.parse_file(str(dest), file.filename)
    if not text.strip():
        raise HTTPException(422, MSG_VACIO)

    progreso.iniciar()
    try:
        resultado = _escritor_procesar(text, "app", file.filename)
    finally:
        progreso.terminar()

    nota = None
    if resultado.get("agrupador_entregado"):
        nota = (
            db.query(Note)
            .filter(Note.title == resultado["titulo"], Note.source_file == file.filename)
            .order_by(Note.id.desc())
            .first()
        )

    return {
        "filename": file.filename,
        "text_length": len(text),
        "escritor": resultado,
        "note": _note_dict(nota, full=True) if nota else None,
    }
