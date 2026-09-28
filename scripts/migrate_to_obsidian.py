#!/usr/bin/env python3
"""
Migración CyberKB (SQLite) → Vault de Obsidian.

Lee la base de datos actual (data/cyberkb.db) y genera una nota Markdown por cada
registro de las tablas notes, commands, cves, mitre_techniques y tools, con
frontmatter YAML y wikilinks [[...]] entre entidades relacionadas.

El grafo nativo de Obsidian se construye a partir de esos wikilinks, sustituyendo
al grafo D3.js generado por IA.

Uso:
    python scripts/migrate_to_obsidian.py

Opcional:
    python scripts/migrate_to_obsidian.py --db ruta/a.db --out ruta/al/vault

Dónde se escribe el vault (en este orden de prioridad):
    1. --out ruta/al/vault           (flag explícito)
    2. variable de entorno OBSIDIAN_VAULT_DIR   (misma convención que usará el
       agente 3b — Obsi; ponla en tu .env si quieres tu vault fuera del repo)
    3. ./vault                       (por defecto, dentro del proyecto)

Re-ejecutar sobreescribe las notas generadas (no borra ficheros manuales que
hayas creado tú dentro del vault).
"""

import argparse
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# ── Rutas por defecto (relativas a la raíz del proyecto; nunca hardcodear rutas
#    de un usuario concreto — cada persona configura la suya vía --out o
#    OBSIDIAN_VAULT_DIR) ──────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = PROJECT_ROOT / "data" / "cyberkb.db"
DEFAULT_VAULT = Path(os.getenv("OBSIDIAN_VAULT_DIR") or (PROJECT_ROOT / "vault"))

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


def sanitize(name: str, fallback: str) -> str:
    """Nombre de fichero/wikilink seguro y legible."""
    if not name:
        return fallback
    name = _BAD_CHARS.sub(" ", str(name))
    name = _WS.sub(" ", name).strip(" .")
    if not name:
        return fallback
    return name[:80].strip()


class NameAllocator:
    """Garantiza nombres de wikilink únicos dentro de un mismo tipo."""

    def __init__(self):
        self._used = set()

    def take(self, base: str) -> str:
        candidate = base
        i = 2
        low = candidate.lower()
        while low in self._used:
            candidate = f"{base}-{i}"
            low = candidate.lower()
            i += 1
        self._used.add(low)
        return candidate


def to_iso(value) -> str:
    """Convierte una fecha de SQLite a ISO 8601. Si falta, usa 'ahora'."""
    if not value:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    s = str(value).strip().replace(" ", "T", 1)
    return s


def parse_tags(raw) -> list:
    if not raw:
        return []
    try:
        val = json.loads(raw)
        if isinstance(val, list):
            return [str(t) for t in val if t]
    except (json.JSONDecodeError, TypeError):
        # Puede venir como cadena separada por comas
        return [t.strip() for t in str(raw).split(",") if t.strip()]
    return []


def frontmatter(fields: dict) -> str:
    lines = ["---"]
    for k, v in fields.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def write_note(vault: Path, tipo: str, filename: str, body: str):
    folder = vault / SUBFOLDERS[tipo]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{filename}.md").write_text(body, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Migra CyberKB SQLite a un vault de Obsidian.")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="Ruta a la base de datos SQLite")
    ap.add_argument("--out", default=str(DEFAULT_VAULT), help="Carpeta destino del vault")
    args = ap.parse_args()

    db_path = Path(args.db)
    vault = Path(args.out)
    if not db_path.exists():
        raise SystemExit(f"No se encuentra la base de datos: {db_path}")

    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # ── Cargar filas ────────────────────────────────────────────────────────────
    notes = list(cur.execute("SELECT * FROM notes"))
    commands = list(cur.execute("SELECT * FROM commands"))
    cves = list(cur.execute("SELECT * FROM cves"))
    mitres = list(cur.execute("SELECT * FROM mitre_techniques"))
    tools = list(cur.execute("SELECT * FROM tools"))
    tool_notes = list(cur.execute("SELECT tool_id, note_id FROM tool_notes"))

    # ── Asignar nombres de wikilink únicos por tipo ───────────────────────────────
    note_alloc, tool_alloc, cmd_alloc = NameAllocator(), NameAllocator(), NameAllocator()

    note_link = {}   # note_id -> wikilink name
    for n in notes:
        base = sanitize(n["title"], f"Nota-{n['id']}")
        note_link[n["id"]] = note_alloc.take(base)

    tool_link = {}   # tool_id -> wikilink name
    tool_by_name = {}  # nombre lower -> wikilink (para enlazar comandos por tool_name)
    for t in tools:
        base = sanitize(t["name"], f"Herramienta-{t['id']}")
        link = tool_alloc.take(base)
        tool_link[t["id"]] = link
        if t["name"]:
            tool_by_name.setdefault(t["name"].strip().lower(), link)

    cve_link = {c["id"]: sanitize(c["cve_id"], f"CVE-{c['id']}") for c in cves}

    # MITRE: una nota por technique_id único (agrega las notas que lo referencian)
    mitre_by_tech = {}  # technique_id -> {name, tactic, snippets[], note_ids[]}
    for m in mitres:
        tid = (m["technique_id"] or f"T-{m['id']}").strip()
        entry = mitre_by_tech.setdefault(tid, {"name": m["technique_name"], "tactic": m["tactic"], "snippets": [], "note_ids": []})
        if m["context_snippet"]:
            entry["snippets"].append(m["context_snippet"])
        if m["note_id"]:
            entry["note_ids"].append(m["note_id"])
    mitre_link = {tid: f"Tecnica-MITRE-{sanitize(tid, tid)}" for tid in mitre_by_tech}

    cmd_link = {}
    for c in commands:
        cmd_link[c["id"]] = cmd_alloc.take(f"Comando-{c['id']}")

    # ── Índices de relaciones ─────────────────────────────────────────────────────
    tools_of_note, notes_of_tool = {}, {}
    for tn in tool_notes:
        tools_of_note.setdefault(tn["note_id"], []).append(tn["tool_id"])
        notes_of_tool.setdefault(tn["tool_id"], []).append(tn["note_id"])

    cves_of_note, cmds_of_note = {}, {}
    for c in cves:
        if c["note_id"]:
            cves_of_note.setdefault(c["note_id"], []).append(c["id"])
    for c in commands:
        if c["note_id"]:
            cmds_of_note.setdefault(c["note_id"], []).append(c["id"])

    mitres_of_note = {}
    for tid, e in mitre_by_tech.items():
        for nid in e["note_ids"]:
            mitres_of_note.setdefault(nid, []).append(tid)

    counts = {"nota": 0, "comando": 0, "cve": 0, "herramienta": 0, "tecnica-mitre": 0}

    def wl(name):
        return f"[[{name}]]"

    # ── NOTAS ─────────────────────────────────────────────────────────────────────
    for n in notes:
        nid = n["id"]
        fm = frontmatter({
            "id": f"nota-{nid}",
            "tipo": "nota",
            "fecha_actualizacion": to_iso(n["updated_at"] or n["created_at"]),
        })
        parts = [fm, "", f"# {n['title'] or f'Nota {nid}'}", ""]
        meta = []
        if n["category"]:
            meta.append(f"**Categoría:** {n['category']}")
        if n["subcategory"]:
            meta.append(f"**Subcategoría:** {n['subcategory']}")
        tags = parse_tags(n["tags"])
        if tags:
            meta.append("**Tags:** " + ", ".join(f"#{_WS.sub('-', t)}" for t in tags))
        if n["source_file"]:
            meta.append(f"**Origen:** {n['source_file']}")
        if meta:
            parts += meta + [""]
        if n["summary"]:
            parts += ["## Resumen", "", n["summary"], ""]
        if n["content"]:
            parts += ["## Contenido", "", n["content"], ""]

        rel = []
        for tid in tools_of_note.get(nid, []):
            if tid in tool_link:
                rel.append(wl(tool_link[tid]))
        for cid in cves_of_note.get(nid, []):
            rel.append(wl(cve_link[cid]))
        for tech in mitres_of_note.get(nid, []):
            rel.append(wl(mitre_link[tech]))
        for cmid in cmds_of_note.get(nid, []):
            rel.append(wl(cmd_link[cmid]))
        if rel:
            parts += ["## Entidades relacionadas", ""] + rel + [""]

        write_note(vault, "nota", note_link[nid], "\n".join(parts))
        counts["nota"] += 1

    # ── COMANDOS ──────────────────────────────────────────────────────────────────
    for c in commands:
        cid = c["id"]
        fm = frontmatter({
            "id": f"comando-{cid}",
            "tipo": "comando",
            "fecha_actualizacion": to_iso(c["created_at"]),
        })
        title = (c["command"] or "").strip().splitlines()[0][:70] or f"Comando {cid}"
        parts = [fm, "", f"# {title}", ""]
        if c["os"]:
            parts.append(f"**SO:** {c['os']}")
        if c["category"]:
            parts.append(f"**Categoría:** {c['category']}")
        if c["tool_name"]:
            parts.append(f"**Herramienta:** {c['tool_name']}")
        parts.append("")
        parts += ["```bash", (c["command"] or "").strip(), "```", ""]
        if c["description"]:
            parts += [c["description"], ""]
        flags = parse_tags(c["flags"])
        if flags:
            parts += ["**Flags:** " + ", ".join(f"`{f}`" for f in flags), ""]

        rel = []
        if c["note_id"] and c["note_id"] in note_link:
            rel.append(wl(note_link[c["note_id"]]))
        if c["tool_name"]:
            link = tool_by_name.get(c["tool_name"].strip().lower())
            if link:
                rel.append(wl(link))
        if rel:
            parts += ["## Entidades relacionadas", ""] + rel + [""]

        write_note(vault, "comando", cmd_link[cid], "\n".join(parts))
        counts["comando"] += 1

    # ── CVEs ──────────────────────────────────────────────────────────────────────
    for c in cves:
        fm = frontmatter({
            "id": f"cve-{c['cve_id']}",
            "tipo": "cve",
            "fecha_actualizacion": to_iso(c["created_at"]),
        })
        parts = [fm, "", f"# {c['cve_id']}", ""]
        if c["title"]:
            parts += [f"**{c['title']}**", ""]
        meta = []
        if c["severity"]:
            meta.append(f"**Severidad:** {c['severity']}")
        if c["cvss"] is not None:
            meta.append(f"**CVSS:** {c['cvss']}")
        if c["affected"]:
            meta.append(f"**Afectados:** {c['affected']}")
        if meta:
            parts += meta + [""]
        if c["description"]:
            parts += ["## Descripción", "", c["description"], ""]

        rel = []
        if c["note_id"] and c["note_id"] in note_link:
            rel.append(wl(note_link[c["note_id"]]))
        if rel:
            parts += ["## Entidades relacionadas", ""] + rel + [""]

        write_note(vault, "cve", cve_link[c["id"]], "\n".join(parts))
        counts["cve"] += 1

    # ── HERRAMIENTAS ──────────────────────────────────────────────────────────────
    for t in tools:
        tid = t["id"]
        fm = frontmatter({
            "id": f"herramienta-{tid}",
            "tipo": "herramienta",
            "fecha_actualizacion": to_iso(t["updated_at"] or t["created_at"]),
        })
        parts = [fm, "", f"# {t['name'] or f'Herramienta {tid}'}", ""]
        if t["url"]:
            parts += [f"**URL:** {t['url']}", ""]
        meta = []
        if t["category"]:
            meta.append(f"**Categoría:** {t['category']}")
        if t["tool_type"]:
            meta.append(f"**Tipo:** {t['tool_type']}")
        if meta:
            parts += meta + [""]
        if t["description"]:
            parts += [t["description"], ""]
        if t["use_cases"]:
            parts += ["## Casos de uso", "", t["use_cases"], ""]

        rel = [wl(note_link[nid]) for nid in notes_of_tool.get(tid, []) if nid in note_link]
        if rel:
            parts += ["## Entidades relacionadas", ""] + rel + [""]

        write_note(vault, "herramienta", tool_link[tid], "\n".join(parts))
        counts["herramienta"] += 1

    # ── TÉCNICAS MITRE ────────────────────────────────────────────────────────────
    for tid, e in mitre_by_tech.items():
        fm = frontmatter({
            "id": f"tecnica-mitre-{tid}",
            "tipo": "tecnica-mitre",
            "fecha_actualizacion": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        heading = f"{tid}" + (f" — {e['name']}" if e["name"] else "")
        parts = [fm, "", f"# {heading}", ""]
        if e["tactic"]:
            parts += [f"**Táctica:** {e['tactic']}", ""]
        parts += [f"**Ver en ATT&CK:** https://attack.mitre.org/techniques/{tid.replace('.', '/')}/", ""]
        snippets = [s for s in e["snippets"] if s]
        if snippets:
            parts += ["## Contexto"]
            for s in snippets:
                parts += ["", f"> {s}"]
            parts.append("")

        rel = [wl(note_link[nid]) for nid in e["note_ids"] if nid in note_link]
        if rel:
            parts += ["## Entidades relacionadas", ""] + rel + [""]

        write_note(vault, "tecnica-mitre", mitre_link[tid], "\n".join(parts))
        counts["tecnica-mitre"] += 1

    con.close()

    total = sum(counts.values())
    print("Vault generado en:", vault)
    print(f"  Notas:          {counts['nota']}")
    print(f"  Comandos:       {counts['comando']}")
    print(f"  CVEs:           {counts['cve']}")
    print(f"  Herramientas:   {counts['herramienta']}")
    print(f"  Técnicas MITRE: {counts['tecnica-mitre']}")
    print(f"  TOTAL notas .md: {total}")


if __name__ == "__main__":
    main()
