# Vault de Obsidian — CyberKB

Este vault sustituye al grafo de conocimiento D3.js generado por IA. En lugar de
calcular nodos y relaciones con la API de Claude (coste en tokens que crece con el
tamaño), el grafo se construye **de forma nativa y gratuita** a partir de los
wikilinks `[[...]]` entre notas Markdown.

## Cómo abrir el vault en Obsidian

1. Abre Obsidian.
2. `Abrir carpeta como almacén` (Open folder as vault).
3. Selecciona esta carpeta: `D:\CyberKB\vault`.
4. Abre la vista de grafo (icono de grafo en la barra lateral, o `Ctrl+G`) para ver
   las relaciones entre notas, herramientas, CVEs y técnicas MITRE.

La primera vez, Obsidian creará una subcarpeta `.obsidian/` con su configuración.

## Cómo se genera / actualiza

El vault se genera desde la base de datos SQLite de CyberKB (`data/cyberkb.db`)
con el script de migración:

```bash
python scripts/migrate_to_obsidian.py
```

Opciones:

```bash
python scripts/migrate_to_obsidian.py --db data/cyberkb.db --out vault
```

Re-ejecutar **sobreescribe** las notas generadas con el estado actual de la base de
datos. No borra ficheros que hayas creado tú manualmente dentro del vault.

## Estructura de carpetas

| Carpeta | Contenido |
|---|---|
| `Notas/` | Una nota por cada resumen/documento procesado (tabla `notes`) |
| `Comandos/` | Comandos destacados (tabla `commands`) |
| `CVEs/` | CVEs relevantes (tabla `cves`) |
| `Herramientas/` | Herramientas mencionadas (tabla `tools`) |
| `Tecnicas-MITRE/` | Técnicas MITRE ATT&CK (tabla `mitre_techniques`, una por `technique_id`) |

## Formato de nota

Cada nota lleva frontmatter YAML y wikilinks a sus entidades relacionadas:

```markdown
---
id: <identificador-estable>
tipo: nota | comando | cve | herramienta | tecnica-mitre
fecha_actualizacion: <ISO 8601>
---

# Título de la nota

Contenido...

## Entidades relacionadas
[[Nombre-Herramienta]]
[[CVE-XXXX-XXXXX]]
[[Tecnica-MITRE-TXXXX]]
```

Los wikilinks son lo que Obsidian usa para dibujar su grafo. Este formato es el
que interpretará el agente **3b — Obsidian** del pipeline del Editor.

## Relaciones representadas

- **Nota** → sus herramientas, CVEs, técnicas MITRE y comandos
- **Comando** → su nota de origen y su herramienta
- **CVE** → su nota de origen
- **Herramienta** → las notas que la mencionan
- **Técnica MITRE** → las notas que la referencian
