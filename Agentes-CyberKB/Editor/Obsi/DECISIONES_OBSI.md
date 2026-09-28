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
Obsi tenga que recalcular relaciones.

**Implementado (2026-09-28) en `agente_bbdd.py`/`_procesar()`**: la respuesta de
Agente-BBDD ya incluye estos campos, con los mismos nombres e identificadores que
recibirá Obsi (ver `Editor/Agente-BBDD/README.md`, sección "Salidas"):

```json
{
  "nota_id": 123,
  "herramientas_ids": [4, 7],
  "comandos_ids": [55, 56],
  "cves_ids": ["CVE-2021-44228"],
  "mitre_ids": ["T1059", "T1059.001"]
}
```

Los identificadores **no son homogéneos a propósito**: `herramientas_ids` y
`comandos_ids` son el `id` numérico de fila (`tools.id`/`commands.id`), pero
`cves_ids` y `mitre_ids` son `cve_id`/`technique_id` (texto) — porque así es como el
vault ya identifica a un CVE o una técnica MITRE (`migrate_to_obsidian.py` no genera
una nota por fila para estos dos tipos, sino una por identificador único; varias
filas pueden compartir el mismo CVE o la misma técnica). Obsi tiene que usar el tipo
de identificador correcto según la entidad, no asumir que todos son ids numéricos.

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

**Decidido (2026-09-28): esta lógica se comparte con `migrate_to_obsidian.py`, no se
reimplementa por separado** (cierra el punto que quedaba abierto en el §8 antiguo —
ver más abajo, "Historial", y el nuevo §8 con el diseño concreto).

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

### Contrato de `POST /api/obsi/sync` — decidido (2026-09-28)

**Entrada**: exactamente el mismo `ids_obsi` que ya devuelve/envía Agente-BBDD
(§2, ya implementado):

```json
{
  "nota_id": 123,
  "herramientas_ids": [4, 7],
  "comandos_ids": [55, 56],
  "cves_ids": ["CVE-2021-44228"],
  "mitre_ids": ["T1059"]
}
```

**Salida**:

```json
{
  "sincronizado": true,
  "notas_creadas": ["Notas/Mi-nota.md"],
  "notas_actualizadas": ["Herramientas/Nmap.md"],
  "notas_borradas": ["Comandos/Comando-antiguo.md"]
}
```

- `sincronizado`: `true`/`false` — si todo el lote se escribió sin errores de disco.
- `notas_creadas`/`notas_actualizadas`/`notas_borradas`: rutas relativas dentro del
  vault, para que quien llame (Agente-BBDD, o el frontend en un reintento aislado)
  pueda mostrar o loguear qué se tocó exactamente — `notas_borradas` es la limpieza
  de huérfanas del §6.
- **Actualizado (2026-09-28, prompt del usuario): Obsi NO usa el `"Ha habido un
  error"` genérico.** Cualquier error de escritura responde `500` +
  `"El grafo no ha podido actualizarse"` — mensaje propio, porque el frontend debe
  poder ofrecer un botón **"Reintentar"** específico para la sincronización del
  grafo/vault, distinto del reintento de la cadena entera. Agente-BBDD, de todas
  formas, trata cualquier fallo de este endpoint (HTTP error o timeout) como fallo
  blando (arriba) — no le importa el texto del mensaje, solo si respondió 2xx o no.

---

## 8. Relación con `migrate_to_obsidian.py` — decidido (Opción C, 2026-09-28)

**Ya no queda ningún punto abierto.** Se decidió la Opción C: `migrate_to_obsidian.py`
sigue siendo re-ejecutable en caliente aunque Obsi ya esté en producción, pero
adoptando la **misma lógica de "buscar por `id`, no por título"** que usa Obsi para
limpiar huérfanas (§6) — así los dos son coherentes entre sí y no hay riesgo de que
uno pise o duplique lo que escribió el otro.

**Qué hace falta para esto (nuevo, no existe hoy en ningún sitio):**

1. **Función de búsqueda por `id`**: recorre la subcarpeta del tipo (`Notas/`,
   `Comandos/`, etc.), lee la línea `id: <tipo>-<id>` del frontmatter de cada `.md`
   (no hace falta una librería YAML — el frontmatter es fijo a 3 campos, basta con
   leer las primeras líneas) y devuelve la ruta que coincida.
2. **Unicidad de nombre resuelta contra el disco, no en memoria**: hoy el script usa
   un `NameAllocator` en memoria, válido solo dentro de una misma ejecución completa.
   Pasa a comprobarse contra los ficheros que ya existen en la carpeta del tipo en
   ese momento — mismo criterio para el script y para Obsi, da igual si uno procesa
   toda la BBDD de golpe y el otro una entidad a la vez.
3. **Escritura sincronizada**: antes de escribir, buscar la nota existente por `id`
   (paso 1), calcular el nombre deseado para el título actual, y si ya existía con
   otro nombre, borrar el fichero viejo al escribir el nuevo.

**Dónde vive este código compartido — decidido: Opción 1.** Nuevo módulo
`Agentes-CyberKB/Editor/Obsi/vault_lib.py` (junto a Obsi, no dentro del repo de la
app), con `sanitize()`, `frontmatter()`, `to_iso()`, `parse_tags()` (migradas desde
`scripts/migrate_to_obsidian.py`, ver §4) más las tres funciones nuevas de arriba.
`scripts/migrate_to_obsidian.py`, que vive en el repo de la app, lo importa añadiendo
la carpeta hermana a `sys.path` — el mismo patrón que ya usa `main.py` para importar
los agentes, aplicado en sentido inverso (un script de la app importando algo del
repo de agentes).

**[HECHO 2026-09-28]** Construido y probado contra la BBDD real:
`Editor/Obsi/vault_lib.py` (funciones migradas + `find_by_id`/`unique_filename`/
`write_synced`), `scripts/migrate_to_obsidian.py` actualizado para usarlo (verificado
idempotente: dos pasadas seguidas no duplican nada), y `Editor/Obsi/obsi.py` en sí.

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
