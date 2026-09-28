# Investigación — cómo debe conectarse el agente Obsi al vault

Guardado el 2026-09-23 para cuando construyamos el agente **Obsi**. No es código, es
la base de decisión: qué opción usar y por qué, antes de escribir `obsi.py`.

**Actualizado el 2026-09-28** — el diseño del pipeline cambió (ver sección
"Rediseño" más abajo): Obsi ya no escribe en paralelo con Agente-BBDD a partir de
los datos crudos de la pipeline; corre **después**, releyendo de SQLite. La
conclusión de "cómo escribir en el vault" (Opción A, sistema de ficheros) sigue
siendo válida sin cambios — lo que cambia es *cuándo* se dispara y *de dónde* lee,
no *cómo* escribe.

## La pregunta

El pipeline dice que 3b "genera una nota .md dentro del vault de Obsidian, con
frontmatter y wikilinks". Hay tres formas técnicas de hacer eso desde un backend
Python/FastAPI. Las comparé.

## Opción A — Escritura directa en el sistema de ficheros ✅ recomendada

Un vault de Obsidian **es literalmente una carpeta de ficheros Markdown**. Obsidian la
vigila y refresca sola cuando detecta cambios externos — no hace falta ninguna API para
que una nota escrita por otro proceso aparezca en la app.

- **No depende de que Obsidian esté abierto.** Funciona igual si el usuario procesa un
  documento a las 3 de la mañana con Obsidian cerrado.
- **Sin dependencias nuevas.** Ya usamos este patrón en Escritor/Cinéfilo/Agrupador
  para sus `salida/`; aquí es lo mismo pero apuntando a `OBSIDIAN_VAULT_DIR` en vez de
  a una carpeta propia del agente.
- **Es justo el patrón que la comunidad recomienda para automatización en background**:
  se lo conoce como "Filesystem MCP" en el ecosistema de integraciones Obsidian+IA —
  "acceso directo a los ficheros Markdown del vault sin necesidad de plugins […] no
  requiere Obsidian abierto ni plugins adicionales […] mejor para automatización en
  segundo plano" ([awesomeclaude.ai](https://awesomeclaude.ai/how-to/use-obsidian-with-claude)).

**Conclusión: esta es la opción para 3b.** Escribir el `.md` con `pathlib`/`open()`
igual que ya hacen los demás agentes. No usar la REST API para esto (ver Opción B, por
qué no).

## Opción B — Plugin "Local REST API" (con servidor MCP incorporado) ❌ para esta tarea

Existe un plugin comunitario muy maduro,
[obsidian-local-rest-api de coddingtonbear](https://github.com/coddingtonbear/obsidian-local-rest-api)
([documentación interactiva](https://coddingtonbear.github.io/obsidian-local-rest-api/)),
que expone el vault por HTTPS local (puerto `27124`) con autenticación por API key, y
en su versión reciente trae también un servidor MCP incorporado.

Soporta de todo: `PATCH /vault/{path}` para editar solo una sección por heading, bloque
o clave de frontmatter (`replace`/`prepend`/`append`/`delete`), `PATCH /active/` sobre
la nota abierta, `PATCH /periodic/{period}/` para notas periódicas.

Ejemplo (para referencia futura, si alguna vez hiciera falta parchear una nota ya
existente en vez de reescribirla entera):

```python
import requests
requests.patch(
    "https://127.0.0.1:27124/vault/ruta/nota.md",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"targetType": "frontmatter", "target": "status", "operation": "replace", "value": "done"},
    verify=False,  # certificado autofirmado del plugin
)
```

**Por qué NO usarla para 3b**: requiere que **Obsidian esté abierto** en el momento de
la llamada — "el plugin solo sirve peticiones mientras Obsidian está en ejecución; si
lo cierras, las llamadas fallan con conexión rechazada" (confirmado en varias fuentes,
incl. [mcp.directory](https://mcp.directory/blog/obsidian-mcp-complete-guide-2026)). Un
agente de ingesta que depende de que el usuario tenga una app de escritorio abierta no
es fiable para un pipeline automático. Se descarta para 3b.

## Rediseño (2026-09-28) — Obsi pasa a correr después de Agente-BBDD, no en paralelo

Motivo: el 2026-09-28 apareció en el repo (commit de un compañero de equipo,
jcuarterosaez) `scripts/migrate_to_obsidian.py` + un `vault/` de 561 notas ya
generado — un volcado puntual de la BBDD entera a Markdown. Eso fija de facto las
convenciones reales del vault y hace evidente que Obsi necesita la fila **ya
confirmada** en SQLite (con su `id` definitivo y sus relaciones) para escribir una
nota coherente con el resto — no le basta con el JSON que le pasaría el Agrupador
antes de guardar.

**Pipeline nuevo:**

```
Agrupador ──▶ Agente-BBDD (confirma en SQLite) ──▶ Obsi (relee de SQLite, sincroniza el vault)
```

Antes era Agente-BBDD y Obsi en paralelo, ambos alimentados directamente por el
Agrupador. Ahora es secuencial: Obsi depende de que Agente-BBDD haya terminado.

**Qué hace Obsi en cada pasada — sincronización dirigida, no volcado completo:**

- No relee la BBDD entera cada vez (eso sería demasiado coste dentro de una cadena
  síncrona que ya tarda minutos por vídeo). Solo toca las entidades afectadas por
  esa pasada: la nota nueva/actualizada y las entidades relacionadas que tocó
  (herramienta, CVE, comando, técnica MITRE).
- Reutiliza las convenciones ya fijadas por `migrate_to_obsidian.py`: mismo
  `OBSIDIAN_VAULT_DIR` (por defecto `<raíz del repo>/vault`), mismo frontmatter
  (`id`/`tipo`/`fecha_actualizacion`), mismas carpetas
  (`Notas/Comandos/CVEs/Herramientas/Tecnicas-MITRE`), mismo saneado de nombres de
  fichero. Candidato a reutilizar directamente sus funciones (`sanitize()`,
  `frontmatter()`, `to_iso()`, `parse_tags()`) en vez de reimplementarlas.
- **Limpieza de huérfanas/duplicadas**: como el nombre de fichero se deriva del
  título (no del `id`), si el título de una entidad cambia entre pasadas, la nota
  vieja se queda huérfana con el nombre antiguo. Obsi debe localizar la nota
  existente de una entidad por su `id` de frontmatter (no por nombre de fichero) y,
  si el nombre resultante cambió, borrar la antigua al escribir la nueva — nunca
  dejar dos notas para la misma entidad.
- Nombre del agente: se mantiene **Obsi** (no "Agente 4" — ese nombre quedó
  reservado al Indexer de embeddings ya descartado, ver
  [[project-investigacion-obsidian-ia]], sin relación con este rediseño).

**Aún sin cerrar (no construir hasta decidir esto):**

- Formato exacto de la llamada interna Agente-BBDD → Obsi (qué ids le pasa para
  saber qué releer: ¿solo el `note_id`, o también los ids de tool/cve/command/mitre
  que tocó esa pasada?).
- Qué pasa si Obsi falla pero Agente-BBDD ya confirmó en SQLite — ¿la cadena entera
  se marca como error (convención `"Ha habido un error"` ya usada por el resto de
  agentes) aunque el dato ya esté guardado en la BBDD, o el fallo de Obsi es
  "blando" y no tumba la respuesta al frontend?
- Relación entre `migrate_to_obsidian.py` (volcado completo) y Obsi (incremental)
  una vez Obsi esté en producción: ¿el script queda solo como backfill puntual, o
  se sigue pudiendo re-ejecutar en caliente sin pisar lo que escriba Obsi?

## Fuentes

- [Local REST API with MCP — Obsidian Plugin](https://community.obsidian.md/plugins/obsidian-local-rest-api)
- [coddingtonbear/obsidian-local-rest-api (GitHub)](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Documentación interactiva de la API](https://coddingtonbear.github.io/obsidian-local-rest-api/)
- [PATCH Operations and Content Insertion — DeepWiki](https://deepwiki.com/coddingtonbear/obsidian-local-rest-api/6.1-patch-operations)
- [3 Ways to Use Obsidian with Claude Code — Awesome Claude](https://awesomeclaude.ai/how-to/use-obsidian-with-claude)
- [Obsidian MCP Setup 2026: Local REST API Complete Guide — MCP.Directory](https://mcp.directory/blog/obsidian-mcp-complete-guide-2026)
