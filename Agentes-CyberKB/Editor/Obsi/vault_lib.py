"""Utilidades compartidas del vault de Obsidian de CyberKB.

Usado por dos sitios que deben producir un vault indistinguible entre si:

- `obsi.py` (este mismo directorio): sincronizacion dirigida, entidad a entidad,
  disparada por el Agente-BBDD tras cada guardado.
- `scripts/migrate_to_obsidian.py` (repo de la app): volcado completo bajo demanda,
  importa este modulo anadiendo esta carpeta a `sys.path` (son repos hermanos).

Decision de diseno (ver DECISIONES_OBSI.md, Opcion C): en vez de que cada uno
implemente su propio saneado de nombres, frontmatter o deteccion de duplicados,
viven aqui una sola vez. Si un dia divergen, es un bug, no una eleccion.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

SUBFOLDERS = {
    "nota": "Notas",
    "comando": "Comandos",
    "cve": "CVEs",
    "herramienta": "Herramientas",
    "tecnica-mitre": "Tecnicas-MITRE",
}

# Caracteres prohibidos en nombres de fichero (Windows) y conflictivos en Obsidian.
_BAD_CHARS = re.compile(r'[\\/:*?"<>|\[\]#^]+')
_WS = re.compile(r"\s+")
_ID_LINE = re.compile(r"^id:\s*(.+?)\s*$")


# --------------------------------------------------------------- basico (texto)


def sanitize(name: str, fallback: str) -> str:
    """Nombre de fichero/wikilink seguro y legible."""
    if not name:
        return fallback
    name = _BAD_CHARS.sub(" ", str(name))
    name = _WS.sub(" ", name).strip(" .")
    if not name:
        return fallback
    return name[:80].strip()


def to_iso(value) -> str:
    """Convierte una fecha de SQLite a ISO 8601. Si falta, usa 'ahora'."""
    if not value:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    s = str(value).strip().replace(" ", "T", 1)
    return s


def parse_tags(raw) -> list:
    import json

    if not raw:
        return []
    try:
        val = json.loads(raw)
        if isinstance(val, list):
            return [str(t) for t in val if t]
    except (json.JSONDecodeError, TypeError):
        return [t.strip() for t in str(raw).split(",") if t.strip()]
    return []


def wl(name: str) -> str:
    """Formatea un wikilink de Obsidian."""
    return f"[[{name}]]"


def frontmatter(fields: dict) -> str:
    lines = ["---"]
    for k, v in fields.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


# -------------------------------------------------------- localizar por id real


def find_by_id(vault: Path, tipo: str, entity_id: str) -> Path | None:
    """Busca, dentro de la subcarpeta del tipo, el fichero cuyo frontmatter tiene
    `id: <entity_id>`. Es la clave de sincronizacion: el nombre de fichero se
    deriva del titulo y puede cambiar entre pasadas, pero el `id` no.
    """
    folder = vault / SUBFOLDERS[tipo]
    if not folder.is_dir():
        return None
    for ruta in folder.glob("*.md"):
        try:
            with ruta.open("r", encoding="utf-8") as f:
                for i, linea in enumerate(f):
                    if i > 6:  # el frontmatter son 3 campos, no hace falta leer mas
                        break
                    m = _ID_LINE.match(linea)
                    if m and m.group(1) == entity_id:
                        return ruta
        except OSError:
            continue
    return None


def unique_filename(vault: Path, tipo: str, base: str, exclude: Path | None = None) -> str:
    """Nombre de fichero unico dentro de su tipo, comprobado contra el disco (no
    en memoria): asi una escritura de un solo elemento (Obsi) y un volcado
    completo (migrate_to_obsidian.py) resuelven colisiones igual.

    `exclude` es la ruta que ya tiene esta misma entidad (encontrada por id):
    no cuenta como colision consigo misma, para poder conservar su nombre si
    el titulo no cambio.
    """
    folder = vault / SUBFOLDERS[tipo]
    folder.mkdir(parents=True, exist_ok=True)

    candidato = base
    i = 2
    while True:
        ruta = folder / f"{candidato}.md"
        if not ruta.exists() or ruta == exclude:
            return candidato
        candidato = f"{base}-{i}"
        i += 1


def write_synced(vault: Path, tipo: str, entity_id: str, filename_base: str, body: str) -> tuple[str, str, str | None]:
    """Escribe una nota manteniendo la identidad por `id`, no por nombre.

    1. Busca si la entidad ya tiene nota (por `id` de frontmatter).
    2. Calcula el nombre de fichero para el titulo actual.
    3. Escribe en ese nombre.
    4. Si ya existia con otro nombre (el titulo cambio), borra el fichero viejo.

    Devuelve (ruta_relativa_al_vault, accion, ruta_borrada), accion en
    {"creada", "actualizada"} y ruta_borrada es la ruta relativa de la nota
    huerfana eliminada en el paso 4, o `None` si no hizo falta borrar nada.
    """
    existente = find_by_id(vault, tipo, entity_id)
    nombre = unique_filename(vault, tipo, filename_base, exclude=existente)

    folder = vault / SUBFOLDERS[tipo]
    folder.mkdir(parents=True, exist_ok=True)
    destino = folder / f"{nombre}.md"
    # newline="\n" fuerza LF sin traducir, pase lo que pase en el SO: el vault
    # se comparte por git entre companeros en Windows/Mac (ver memoria del
    # proyecto), y sin esto cada uno generaria un fin de linea distinto para
    # el mismo contenido, ensuciando el diff en cada sincronizacion.
    destino.write_text(body, encoding="utf-8", newline="\n")

    accion = "actualizada" if existente is not None else "creada"

    borrada = None
    if existente is not None and existente != destino:
        existente.unlink(missing_ok=True)
        borrada = f"{SUBFOLDERS[tipo]}/{existente.name}"

    relativa = f"{SUBFOLDERS[tipo]}/{nombre}.md"
    return relativa, accion, borrada


# -------------------------------------------------- construccion de cada nota

# Cada build_* espera un dict `fields` con las columnas ya extraidas de la fila
# de SQLite (no el modelo ORM directamente, para que tanto Obsi como el script
# de migracion -que recorren la BBDD de formas distintas- puedan alimentarlas
# igual) y `related`, una lista de wikilinks ya formateados con `wl()`.
# Devuelven (filename_base, cuerpo_markdown_completo).


def build_nota(fields: dict, related: list[str]) -> tuple[str, str]:
    nid = fields["id"]
    title = fields.get("title") or f"Nota {nid}"
    base = sanitize(title, f"Nota-{nid}")

    fm = frontmatter({
        "id": f"nota-{nid}",
        "tipo": "nota",
        "fecha_actualizacion": to_iso(fields.get("fecha_actualizacion")),
    })
    parts = [fm, "", f"# {title}", ""]

    meta = []
    if fields.get("category"):
        meta.append(f"**Categoría:** {fields['category']}")
    if fields.get("subcategory"):
        meta.append(f"**Subcategoría:** {fields['subcategory']}")
    tags = fields.get("tags") or []
    if tags:
        meta.append("**Tags:** " + ", ".join(f"#{_WS.sub('-', t)}" for t in tags))
    if fields.get("source_file"):
        meta.append(f"**Origen:** {fields['source_file']}")
    if meta:
        parts += meta + [""]

    if fields.get("summary"):
        parts += ["## Resumen", "", fields["summary"], ""]
    if fields.get("content"):
        parts += ["## Contenido", "", fields["content"], ""]
    if related:
        parts += ["## Entidades relacionadas", ""] + related + [""]

    return base, "\n".join(parts)


def build_comando(fields: dict, related: list[str]) -> tuple[str, str]:
    cid = fields["id"]
    base = f"Comando-{cid}"  # los comandos no tienen titulo propio, se nombran por id

    fm = frontmatter({
        "id": f"comando-{cid}",
        "tipo": "comando",
        "fecha_actualizacion": to_iso(fields.get("fecha_actualizacion")),
    })
    titulo = (fields.get("command") or "").strip().splitlines()[0][:70] or f"Comando {cid}"
    parts = [fm, "", f"# {titulo}", ""]

    if fields.get("os"):
        parts.append(f"**SO:** {fields['os']}")
    if fields.get("category"):
        parts.append(f"**Categoría:** {fields['category']}")
    if fields.get("tool_name"):
        parts.append(f"**Herramienta:** {fields['tool_name']}")
    parts.append("")
    parts += ["```bash", (fields.get("command") or "").strip(), "```", ""]
    if fields.get("description"):
        parts += [fields["description"], ""]

    flags = fields.get("flags") or []
    if flags:
        parts += ["**Flags:** " + ", ".join(f"`{f}`" for f in flags), ""]
    if related:
        parts += ["## Entidades relacionadas", ""] + related + [""]

    return base, "\n".join(parts)


def build_cve(fields: dict, related: list[str]) -> tuple[str, str]:
    cve_id = fields["id"]  # fields["id"] es aqui el cve_id (texto), no un numero
    base = sanitize(cve_id, f"CVE-{cve_id}")

    fm = frontmatter({
        "id": f"cve-{cve_id}",
        "tipo": "cve",
        "fecha_actualizacion": to_iso(fields.get("fecha_actualizacion")),
    })
    parts = [fm, "", f"# {cve_id}", ""]

    if fields.get("title"):
        parts += [f"**{fields['title']}**", ""]
    meta = []
    if fields.get("severity"):
        meta.append(f"**Severidad:** {fields['severity']}")
    if fields.get("cvss") is not None:
        meta.append(f"**CVSS:** {fields['cvss']}")
    if fields.get("affected"):
        meta.append(f"**Afectados:** {fields['affected']}")
    if meta:
        parts += meta + [""]
    if fields.get("description"):
        parts += ["## Descripción", "", fields["description"], ""]
    if related:
        parts += ["## Entidades relacionadas", ""] + related + [""]

    return base, "\n".join(parts)


def build_herramienta(fields: dict, related: list[str]) -> tuple[str, str]:
    tid = fields["id"]
    name = fields.get("name") or f"Herramienta {tid}"
    base = sanitize(name, f"Herramienta-{tid}")

    fm = frontmatter({
        "id": f"herramienta-{tid}",
        "tipo": "herramienta",
        "fecha_actualizacion": to_iso(fields.get("fecha_actualizacion")),
    })
    parts = [fm, "", f"# {name}", ""]

    if fields.get("url"):
        parts += [f"**URL:** {fields['url']}", ""]
    meta = []
    if fields.get("category"):
        meta.append(f"**Categoría:** {fields['category']}")
    if fields.get("tool_type"):
        meta.append(f"**Tipo:** {fields['tool_type']}")
    if meta:
        parts += meta + [""]
    if fields.get("description"):
        parts += [fields["description"], ""]
    if fields.get("use_cases"):
        parts += ["## Casos de uso", "", fields["use_cases"], ""]
    if related:
        parts += ["## Entidades relacionadas", ""] + related + [""]

    return base, "\n".join(parts)


def build_tecnica_mitre(fields: dict, related: list[str]) -> tuple[str, str]:
    tid = fields["id"]  # technique_id (texto), p.ej. "T1059.001"
    base = f"Tecnica-MITRE-{sanitize(tid, tid)}"

    fm = frontmatter({
        "id": f"tecnica-mitre-{tid}",
        "tipo": "tecnica-mitre",
        "fecha_actualizacion": to_iso(fields.get("fecha_actualizacion")),
    })
    heading = tid + (f" — {fields['name']}" if fields.get("name") else "")
    parts = [fm, "", f"# {heading}", ""]

    if fields.get("tactic"):
        parts += [f"**Táctica:** {fields['tactic']}", ""]
    parts += [f"**Ver en ATT&CK:** https://attack.mitre.org/techniques/{tid.replace('.', '/')}/", ""]

    snippets = [s for s in (fields.get("snippets") or []) if s]
    if snippets:
        parts += ["## Contexto"]
        for s in snippets:
            parts += ["", f"> {s}"]
        parts.append("")
    if related:
        parts += ["## Entidades relacionadas", ""] + related + [""]

    return base, "\n".join(parts)
