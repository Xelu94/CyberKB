# Obsi — decisiones de diseño (consolidado)

Documento único con todo lo decidido/investigado sobre el agente **Obsi** hasta
ahora, recogido de `investigacion-conexion.md`, `PLAN_COMANDOS_Y_FRONTEND_BACKEND.md`
y las conversaciones con el usuario. Sigue siendo **solo documentación — no
construir código todavía**, quedan puntos sin cerrar (ver el final).

Última actualización: 2026-09-28.

---

## 1. Qué es Obsi

El último eslabón de la cadena de ingesta (Cinéfilo → Escritor → Agrupador →
Agente-BBDD → **Obsi**): mantiene un vault de Obsidian sincronizado con lo que hay
en la BBDD SQLite de la app, sin que nadie tenga que ejecutar nada a mano.

**Nombre fijado: Obsi.** No se llama "Agente 4" — ese nombre quedó reservado para
un Indexer de embeddings que se planteó y se descartó (2026-09-26, ver memoria del
proyecto `project_investigacion_obsidian_ia`); es un concepto sin relación con esto,
y se evita reutilizar el nombre para no confundir el historial.

---

## 2. Dónde encaja en el pipeline — secuencial, no en paralelo

**Diseño original (2026-09-23/24, ya descartado):** Agrupador llamaba en paralelo a
Agente-BBDD y a Obsi, cada uno con los datos crudos que devolvía el Agrupador.

**Rediseño (2026-09-28):**

```
Agrupador ──▶ Agente-BBDD (confirma en SQLite) ──▶ Obsi (relee de SQLite, sincroniza el vault)
```

Obsi corre **después** de Agente-BBDD, no en paralelo. Motivo: así Obsi trabaja
sobre filas ya confirmadas (con `id` definitivo y relaciones reales), igual que hace
`scripts/migrate_to_obsidian.py`, en vez de tener que reconstruir eso a mano desde
el JSON transitorio del Agrupador.

Consecuencia de rendimiento: la cadena entera sigue siendo síncrona de punta a
punta (una sola petición HTTP hasta el frontend), y ahora tiene un tramo secuencial
más — ligeramente más lento que el diseño en paralelo, aceptado a cambio de
simplicidad y consistencia de datos.

### Qué ids recibe Obsi (decidido: Opción B)

Agente-BBDD, justo después de persistir, ya tiene a mano todos los ids que acaba de
escribir. Se los pasa explícitamente a Obsi en la llamada interna, en vez de que
Obsi tenga que recalcular relaciones:

```json
{
  "note_id": 123,
  "tool_ids": [4, 7],
  "cve_ids": [12],
  "command_ids": [55, 56],
  "mitre_technique_ids": ["T1059", "T1059.001"]
}
```

Obsi relee exactamente esas filas por id — no hace `SELECT *` de toda la tabla.

---

## 3. Cómo escribe Obsi en el vault

**Decidido (investigación 2026-09-23): escritura directa por sistema de ficheros**
(`pathlib`/`open()`), el mismo patrón que ya usan Escritor/Cinéfilo/Agrupador para
sus carpetas `salida/`, aquí apuntando a `OBSIDIAN_VAULT_DIR`.

Un vault de Obsidian es literalmente una carpeta de `.md` — Obsidian la vigila y
refresca sola cuando detecta cambios externos, no hace falta ninguna API.

**Descartado: plugin "Local REST API" / servidor MCP incorporado.** Es potente
(`PATCH` por heading/bloque/frontmatter) pero **requiere que Obsidian esté abierto**
en el momento de la llamada — inviable para un agente de ingesta en background que
puede correr con la app cerrada. Ver fuentes al final.

---

## 4. Convenciones del vault — heredadas de `scripts/migrate_to_obsidian.py`

El 2026-09-28 apareció en el repo (commit de jcuarterosaez, no relacionado con nuestro
plan) un script que vuelca toda la BBDD a un vault de Obsidian ya generado (561
notas de ejemplo). Fija de facto las convenciones que Obsi **debe seguir para no
crear un vault incoherente**, en vez de inventar las suyas:

- **Ruta del vault** — `OBSIDIAN_VAULT_DIR` (variable de entorno), por defecto
  `<raíz del repo>/vault`. (Antes se asumía el patrón de los demás agentes,
  `Editor/Obsi/vault/` — **ya no aplica**, escribir ahí crearía un vault distinto al
  que ya existe.)
- **Frontmatter YAML**, exactamente estos campos:
  ```yaml
  ---
  id: nota-123          # <tipo>-<id>
  tipo: nota             # nota | comando | cve | herramienta | tecnica-mitre
  fecha_actualizacion: 2026-09-28T12:43:49
  ---
  ```
- **Carpetas por tipo**: `Notas/`, `Comandos/`, `CVEs/`, `Herramientas/`,
  `Tecnicas-MITRE/`.
- **Nombre de fichero / wikilink**: saneado (sin `\ / : * ? " < > | [ ] #`, máx. 80
  caracteres) y único dentro de su tipo (sufijo `-2`, `-3`... si colisiona).
- **Wikilinks** `[[...]]` en una sección `## Entidades relacionadas` al final de
  cada nota, hacia las entidades vinculadas (nota ↔ comando/CVE/herramienta/técnica
  MITRE) — así el grafo nativo de Obsidian se construye solo, sin coste de tokens.

**Candidato a reutilizar directamente** (no reimplementar): las funciones
`sanitize()`, `frontmatter()`, `to_iso()`, `parse_tags()` de
`scripts/migrate_to_obsidian.py`, para garantizar formato idéntico byte a byte.

---

## 5. Alcance de cada pasada — sincronización dirigida, no volcado completo

**Decidido.** Obsi no relee la BBDD entera en cada pasada (a diferencia de
`migrate_to_obsidian.py`, que sí hace un volcado completo). Con la cadena ya síncrona
y tardando minutos por vídeo, un resync completo en cada llamada sería demasiado
coste. Obsi solo crea/actualiza las notas de las entidades que recibió por id (ver
§2) — la nota nueva/actualizada y sus relacionadas.

---

## 6. Limpieza de huérfanas/duplicadas

**Decidido.** El nombre de fichero se deriva del título, no del `id`. Si el título
de una entidad cambia entre pasadas (p. ej. se re-analiza una nota y cambia el
`title`), el fichero antiguo se queda huérfano con el nombre viejo — sería una nota
duplicada si no se limpia.

Obsi debe:
1. Localizar la nota existente de una entidad **por su `id` de frontmatter**, no por
   nombre de fichero (buscar dentro de la subcarpeta del tipo qué fichero tiene ese
   `id:` en el YAML).
2. Si el nombre de fichero resultante para la versión nueva es distinto al que ya
   existía, borrar el fichero antiguo al escribir el nuevo — nunca dejar dos notas
   para la misma entidad.

---

## 7. Manejo de fallos — fallo blando + reintento aislado desde el frontend

**Decidido.** A diferencia del resto de la cadena (que responde
`"Ha habido un error"` si falla cualquier tramo), un fallo de Obsi es distinto:
cuando Obsi falla, el dato **ya está guardado** en la BBDD (Agente-BBDD terminó
bien) — no tiene sentido tratarlo como si no se hubiera guardado nada.

- **Fallo "blando" solo para Obsi**: la respuesta al frontend sigue siendo éxito
  (la BBDD sí se guardó), con un chip `✗ No sincronizado con Obsidian` en vez de
  `✓ Sincronizado con Obsidian` (mismo patrón que `agrupador_entregado` /
  `escritor_entregado`).
- **Obsi necesita su propio endpoint** (p. ej. `POST /api/obsi/sync`) que acepte los
  mismos ids del §2, para poder invocarse solo — sin repetir Cinéfilo/Escritor/
  Agrupador/Agente-BBDD ni volver a llamar a Claude.
- El frontend, al ver el chip en rojo, ofrece un botón "↺ Reintentar Obsidian" que
  llama solo a ese endpoint con los ids que ya vinieron en la respuesta original.
- **Implicación de diseño de respuesta**: los ids (§2) tienen que viajar en el JSON
  de respuesta de la cadena aunque Obsi haya fallado, para que el frontend los tenga
  a mano para el reintento.

---

## 8. Sin cerrar todavía (no construir hasta decidirlo)

- **Relación entre `migrate_to_obsidian.py` y Obsi una vez Obsi esté en
  producción**: ¿el script pasa a ser solo backfill puntual (se ejecutó una vez,
  no se vuelve a tocar), o se puede seguir re-ejecutando en caliente sin pisar lo
  que Obsi ya haya escrito incrementalmente? Riesgo si se re-ejecuta: al nombrar por
  título y no por id, podría sobreescribir o duplicar una nota que Obsi ya gestiona.

---

## 9. Fuentes (investigación de la Opción A vs B, 2026-09-23)

- [Local REST API with MCP — Obsidian Plugin](https://community.obsidian.md/plugins/obsidian-local-rest-api)
- [coddingtonbear/obsidian-local-rest-api (GitHub)](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Documentación interactiva de la API](https://coddingtonbear.github.io/obsidian-local-rest-api/)
- [PATCH Operations and Content Insertion — DeepWiki](https://deepwiki.com/coddingtonbear/obsidian-local-rest-api/6.1-patch-operations)
- [3 Ways to Use Obsidian with Claude Code — Awesome Claude](https://awesomeclaude.ai/how-to/use-obsidian-with-claude)
- [Obsidian MCP Setup 2026: Local REST API Complete Guide — MCP.Directory](https://mcp.directory/blog/obsidian-mcp-complete-guide-2026)

## Ver también

- `investigacion-conexion.md` — investigación original + sección "Rediseño 2026-09-28"
- `../PLAN_COMANDOS_Y_FRONTEND_BACKEND.md` — plan de integración del pipeline completo
- Memoria del proyecto: `project_investigacion_obsidian_ia`,
  `project_seguimiento_github_cyberkb` (commit de jcuarterosaez con el vault/script)
