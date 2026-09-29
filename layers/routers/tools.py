from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Tool
from models import Command
import json


from layers.routers_functions import _tool_dict, _cmd_dict, ToolUpdate, ToolCreate


router = APIRouter()


@router.get("/api/tools")
def list_tools(db: Session = Depends(get_db)):
    tools = db.query(Tool).order_by(Tool.mention_count.desc()).all()
    return [_tool_dict(t) for t in tools]


@router.get("/api/tools/{tool_id}")
def get_tool(tool_id: int, db: Session = Depends(get_db)):
    t = db.query(Tool).filter(Tool.id == tool_id).first()
    if not t:
        raise HTTPException(404, "Tool not found")
    d = _tool_dict(t)
    d["notes"] = [{"id": note.id, "title": note.title, "category": note.category} for note in t.tools]
    d["commands"] = [_cmd_dict(command) for command in db.query(Command).filter(Command.tool_name.ilike(t.name)).all()]
    return d


@router.put("/api/tools/{tool_id}")
def update_tool(tool_id: int, data: ToolUpdate, db: Session = Depends(get_db)):
    t = db.query(Tool).filter(Tool.id == tool_id).first()
    if not t:
        raise HTTPException(404, "Tool not found")
    if data.url is not None:
        t.url = data.url
    if data.description is not None:
        t.description = data.description
    if data.category is not None:
        t.category = data.category
    if data.use_cases is not None:
        t.use_cases = json.dumps(data.use_cases)
    if data.requires_api is not None:
        t.requires_api = data.requires_api
    if data.api_info is not None:
        t.api_info = data.api_info
    db.commit()
    db.refresh(t)
    return _tool_dict(t)


@router.post("/api/tools", status_code=201)
def create_tool(data: ToolCreate, db: Session = Depends(get_db)):
    """Crea una herramienta a mano. Si ya existe una con ese nombre, sube su
    contador de menciones en vez de duplicarla (upsert por nombre)."""
    name = (data.name or "").strip()
    if not name:
        raise HTTPException(400, "El nombre es obligatorio")
    existing = db.query(Tool).filter(Tool.name.ilike(name)).first()
    if existing:
        existing.mention_count = (existing.mention_count or 0) + 1
        db.commit()
        db.refresh(existing)
        return {"created": False, **_tool_dict(existing)}
    t = Tool(
        name=name,
        url=data.url or None,
        description=data.description or None,
        category=data.category or None,
        tool_type=data.tool_type or "software",
        requires_api=bool(data.requires_api),
        api_info=data.api_info or None,
        mention_count=1,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"created": True, **_tool_dict(t)}


@router.delete("/api/tools/{tool_id}", status_code=204)
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    """Borra una herramienta (p. ej. un falso positivo del análisis por IA)."""
    t = db.query(Tool).filter(Tool.id == tool_id).first()
    if not t:
        raise HTTPException(404, "Tool not found")
    db.delete(t)
    db.commit()
    return


