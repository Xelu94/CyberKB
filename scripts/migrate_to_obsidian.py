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
    2. variable de entorno OBSIDIAN_VAULT_DIR   (misma convención que usa el
       agente Obsi; ponla en tu .env si quieres tu vault fuera del repo)
    3. ./vault                       (por defecto, dentro del proyecto)

Re-ejecutar es seguro con el agente Obsi ya en producción (2026-09-28, Opción C):
este script comparte con Obsi la misma lógica de sincronización por `id` de
`Agentes-CyberKB/Editor/Obsi/vault_lib.py` (repo hermano) — localiza cada nota por
su `id` de frontmatter, no por nombre de fichero, y borra la nota vieja si el
título cambió. No sobrescribe a ciegas ni deja duplicados, se re-ejecute cuando se
re-ejecute.
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

# vault_lib.py vive en el repo hermano de agentes (mismo patrón que usa main.py
# para importar los agentes, aplicado al revés: un script de la app importando
# algo del repo de agentes).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT.parent / "Agentes-CyberKB" / "Editor" / "Obsi"))
import vault_lib as vl  # noqa: E402

DEFAULT_DB = PROJECT_ROOT / "data" / "cyberkb.db"
DEFAULT_VAULT = Path(os.getenv("OBSIDIAN_VAULT_DIR") or (PROJECT_ROOT / "vault"))


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

    # ── Nombres de wikilink (para las relaciones) ─────────────────────────────────
    # El nombre final de fichero lo decide vault_lib.write_synced() en el momento
    # de escribir (unicidad contra disco); aqui solo se necesita un nombre estable
    # para construir los wikilinks de "Entidades relacionadas" antes de escribir.
    note_link = {n["id"]: vl.sanitize(n["title"], f"Nota-{n['id']}") for n in notes}
    tool_link = {t["id"]: vl.sanitize(t["name"], f"Herramienta-{t['id']}") for t in tools}
    tool_by_name = {
        t["name"].strip().lower(): tool_link[t["id"]] for t in tools if t["name"]
    }
    mitre_ids_por_tecnica = {}
    for m in mitres:
        tid = (m["technique_id"] or f"T-{m['id']}").strip()
        mitre_ids_por_tecnica.setdefault(tid, f"Tecnica-MITRE-{vl.sanitize(tid, tid)}")

    # ── Índices de relaciones ─────────────────────────────────────────────────────
    tools_of_note, notes_of_tool = {}, {}
    for tn in tool_notes:
        tools_of_note.setdefault(tn["note_id"], []).append(tn["tool_id"])
        notes_of_tool.setdefault(tn["tool_id"], []).append(tn["note_id"])

    cves_of_note, cmds_of_note = {}, {}
    for c in cves:
        if c["note_id"]:
            cves_of_note.setdefault(c["note_id"], []).append(c)
    for c in commands:
        if c["note_id"]:
            cmds_of_note.setdefault(c["note_id"], []).append(c)

    # MITRE: una nota por technique_id único (agrega las notas que lo referencian)
    mitre_by_tech = {}
    for m in mitres:
        tid = (m["technique_id"] or f"T-{m['id']}").strip()
        entry = mitre_by_tech.setdefault(tid, {"name": m["technique_name"], "tactic": m["tactic"], "snippets": [], "note_ids": []})
        if m["context_snippet"]:
            entry["snippets"].append(m["context_snippet"])
        if m["note_id"]:
            entry["note_ids"].append(m["note_id"])

    counts = {"nota": 0, "comando": 0, "cve": 0, "herramienta": 0, "tecnica-mitre": 0}

    # ── NOTAS ─────────────────────────────────────────────────────────────────────
    for n in notes:
        nid = n["id"]
        rel = (
            [vl.wl(tool_link[tid]) for tid in tools_of_note.get(nid, []) if tid in tool_link]
            + [vl.wl(vl.sanitize(c["cve_id"], f"CVE-{c['id']}")) for c in cves_of_note.get(nid, [])]
            + [vl.wl(mitre_ids_por_tecnica[tid]) for tid, e in mitre_by_tech.items() if nid in e["note_ids"]]
            + [vl.wl(f"Comando-{c['id']}") for c in cmds_of_note.get(nid, [])]
        )
        fields = {
            "id": nid,
            "title": n["title"],
            "category": n["category"],
            "subcategory": n["subcategory"],
            "tags": vl.parse_tags(n["tags"]),
            "source_file": n["source_file"],
            "summary": n["summary"],
            "content": n["content"],
            "fecha_actualizacion": n["updated_at"] or n["created_at"],
        }
        base, body = vl.build_nota(fields, rel)
        vl.write_synced(vault, "nota", f"nota-{nid}", base, body)
        counts["nota"] += 1

    # ── COMANDOS ──────────────────────────────────────────────────────────────────
    for c in commands:
        cid = c["id"]
        rel = []
        if c["note_id"] and c["note_id"] in note_link:
            rel.append(vl.wl(note_link[c["note_id"]]))
        if c["tool_name"]:
            link = tool_by_name.get(c["tool_name"].strip().lower())
            if link:
                rel.append(vl.wl(link))

        fields = {
            "id": cid,
            "command": c["command"],
            "os": c["os"],
            "category": c["category"],
            "tool_name": c["tool_name"],
            "description": c["description"],
            "flags": vl.parse_tags(c["flags"]),
            "fecha_actualizacion": c["created_at"],
        }
        base, body = vl.build_comando(fields, rel)
        vl.write_synced(vault, "comando", f"comando-{cid}", base, body)
        counts["comando"] += 1

    # ── CVEs ──────────────────────────────────────────────────────────────────────
    for c in cves:
        rel = []
        if c["note_id"] and c["note_id"] in note_link:
            rel.append(vl.wl(note_link[c["note_id"]]))

        fields = {
            "id": c["cve_id"],
            "title": c["title"],
            "severity": c["severity"],
            "cvss": c["cvss"],
            "affected": c["affected"],
            "description": c["description"],
            "fecha_actualizacion": c["created_at"],
        }
        base, body = vl.build_cve(fields, rel)
        vl.write_synced(vault, "cve", f"cve-{c['cve_id']}", base, body)
        counts["cve"] += 1

    # ── HERRAMIENTAS ──────────────────────────────────────────────────────────────
    for t in tools:
        tid = t["id"]
        rel = [vl.wl(note_link[nid]) for nid in notes_of_tool.get(tid, []) if nid in note_link]

        fields = {
            "id": tid,
            "name": t["name"],
            "url": t["url"],
            "category": t["category"],
            "tool_type": t["tool_type"],
            "description": t["description"],
            "use_cases": t["use_cases"],
            "fecha_actualizacion": t["updated_at"] or t["created_at"],
        }
        base, body = vl.build_herramienta(fields, rel)
        vl.write_synced(vault, "herramienta", f"herramienta-{tid}", base, body)
        counts["herramienta"] += 1

    # ── TÉCNICAS MITRE ────────────────────────────────────────────────────────────
    for tid, e in mitre_by_tech.items():
        rel = [vl.wl(note_link[nid]) for nid in e["note_ids"] if nid in note_link]

        fields = {
            "id": tid,
            "name": e["name"],
            "tactic": e["tactic"],
            "snippets": e["snippets"],
            "fecha_actualizacion": None,  # las tecnicas no tienen fecha propia en la BBDD
        }
        base, body = vl.build_tecnica_mitre(fields, rel)
        vl.write_synced(vault, "tecnica-mitre", f"tecnica-mitre-{tid}", base, body)
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
