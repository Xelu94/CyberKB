# Mejoras a futuro

Cosas que se han identificado, discutido o encontrado durante el trabajo del
Editor/agentes pero que se han dejado conscientemente para más adelante — no
son bugs urgentes, son decisiones o trabajo pendiente. Añadir aquí (fecha +
contexto) en vez de perderlo en el historial de conversación.

---

## Ampliar Agrupador con clasificación de incidentes (INCIBE/ATT&CK/CSF/ISO/normativa)

**2026-09-25, sin terminar.** Hay una actualización planeada para que Agrupador
sepa clasificar y organizar *incidentes* de seguridad (no solo extraer tools/
comandos/CVEs/entidades de documentos), conectando varios marcos a la vez:

- **Taxonomía INCIBE** (10 clases + tipos de incidente, basada en RSIT).
- **MITRE ATT&CK** (15 tácticas, más allá de las técnicas puntuales que ya
  extrae hoy).
- **NIST CSF 2.0** (6 funciones, 22 categorías).
- **ISO/IEC 27002:2022** (93 controles).
- **Normativa**: GDPR (cuándo aplica y notificación a AEPD en 72h), LSSI-CE,
  NIS2 (si afecta a "operador esencial"), ENS (categoría BÁSICA/MEDIA/ALTA si
  es AAPP).

Material de entrenamiento ya preparado (en la raíz de `Agentes-CyberKB/`, no
dentro de `Editor/`, sin terminar — checklists sin marcar):
- `material_entrenamiento_agrupador.md` — la base de conocimiento (qué es
  cada marco, cómo conectan, 5 ejemplos reales).
- `prompt_entrenamiento_agrupador.md` — el prompt de instrucción base para
  esta capa de clasificación.
- `entrenamiento_capas_adicionales.md` — capa 4, ISO 27002 + normativa.
- `INICIO_RAPIDO_AGRUPADOR.md` — guía de cómo usar los tres anteriores para
  entrenar/validar al agente.

Pendiente: decidir cómo encaja esto con el Agrupador real que ya está
construido y en producción (`Editor/Agrupador/agrupador.py`) — si es una
ampliación del mismo esquema (`ESQUEMA`/`prompt.md`), un modo/endpoint
distinto, o un agente nuevo aparte. Ninguno de los 4 ficheros está
referenciado hoy desde `Editor/` ni desde el código real.

---

## Modo Forense sigue sin unificar con Agrupador

**2026-09-28.** `/api/forensic/analyze` es la única llamada que queda a
`ai.extract_entities()` (el mecanismo viejo, con un modelo desactualizado y sin
structured output real) — todo lo demás (`/api/upload`, `/api/analyze`,
`/api/notes/{id}/extract`, `/api/graph/reindex-all`) ya pasa por Agrupador.

No se tocó a propósito: Agente-BBDD reconocería la nota forense por su
`título`+`source_file` (`"forensic:<hash>"`) y la actualizaría con la
categoría/tags que Agrupador adivine por su cuenta, pisando la categorización
especializada que ya hace `ai.generate_forensic_note()` a partir de
VT/MalwareBazaar/Any.run (más precisa para malware que la clasificación
genérica de Agrupador).

**Opciones sobre la mesa** (preguntadas una vez, sin respuesta del usuario):
1. Dejarlo como está — dos mecanismos de extracción de entidades conviven.
2. Unificar aceptando el riesgo de que se pise la categorización especializada.
3. Blindarlo: nota temporal separada para la extracción, luego reenlazar las
   entidades a la nota forense real (más trabajo, sin riesgo).

---

## Agrupador no puede bajar de Opus — coste de `reindex-all`

**2026-09-28.** `POST /api/graph/reindex-all` (botón "Reindexar todo") ahora
reanaliza cada nota entera vía Agrupador (Opus, con thinking activado, 8000
tokens de salida) en vez de solo entidades con el `ai.extract_entities()` viejo
(Sonnet-4-6, sin thinking, 2000 tokens). Es la operación más cara de toda la
app en tokens, y escala con el número de notas.

Se probó bajar Agrupador a Sonnet (con y sin `fallbacks`) contra contenido
técnico real (Kerberoasting: Impacket/Hashcat/CrackMapExec) — **Sonnet rechazó
la tarea por completo** (`stop_reason: refusal`) mientras que Opus la resolvió
sin problema. Además, `claude-sonnet-5` **no admite el parámetro `fallbacks`**
en esta cuenta (`allowed_fallback_models: []`, confirmado por la API real) —
ni siquiera se le puede poner una red de seguridad.

**Decisión (2026-09-28): se queda en Opus.** Revisar en el futuro solo si
aparece un modelo intermedio (más barato que Opus) que no sufra este problema
de refusal con comandos de explotación reales — probarlo con el mismo
contenido de Kerberoasting antes de aplicarlo a producción.

---

## Frontend del Editor — Parte 3 del plan, sin construir

**Backend completo desde el 2026-09-28** (agentes enganchados, `/api/upload`/
`/api/analyze` migrados), pero el frontend real de `index.html` para la
pestaña `✎ EDITOR` sigue siendo solo mockup (Artifact "CyberKB Editor —
mockup pipeline agentes"). Falta construir, según
`PLAN_COMANDOS_Y_FRONTEND_BACKEND.md` Parte 3.1:

1. Campo de URL de vídeo (`▶ Transcribir` → `/api/cinefilo/transcribir`) —
   hoy no existe ningún input de vídeo en la pestaña Editor.
2. Tira de progreso por etapas, reutilizando el patrón `#forensicPipeline`
   (Transcribir → Resumir → Extraer → Guardar en BBDD → Sincronizar
   Obsidian — Obsi como paso secuencial, no en paralelo).
3. Dos chips de estado nuevos en el resultado: `✓/✗ Guardado en BBDD`
   (`bbdd_entregado`) y `✓/✗ Sincronizado con Obsidian` (`obsi_entregado`).
4. Dos mecanismos de reintento distintos: uno genérico que repite toda la
   cadena, y uno aislado para Obsi (`POST /api/obsi/sync` con los ids ya
   recibidos), con su propio mensaje de error
   (`"El grafo no ha podido actualizarse"`).

El modal rápido "⊕ Subir doc" (Parte 3.2) ya no depende de una decisión
pendiente — la Parte 2.4 se resolvió (Migración) — pero su UI sigue sin
adaptarse a que ahora siempre pasa por la cadena completa de agentes (el
checkbox de auto-guardado ya se quitó del backend/frontend base, pero el resto
del flujo visual de "subir vídeo" no se ha tocado porque no existe todavía).

---

## Borrar una nota no limpia en cascada sus entidades del grafo

**2026-09-28.** `DELETE /api/notes/{id}` borra la `Note` pero deja huérfanas
las filas de `graph_entities`/`entity_relations`/`entity_note_map` que
apuntaban a ella — comportamiento preexistente de la app, no introducido por
la migración de hoy, encontrado al limpiar datos de prueba tras verificar que
`_persist_entities` seguía funcionando. No se ha arreglado. Si se hace, hay
que decidir si se borran las entidades huérfanas del todo o solo se
desvinculan (una entidad puede estar compartida por varias notas).

---

## Esquema de Agrupador sin categoría de "seguridad de la IA"

**2026-09-24, investigación en `INVESTIGACION_IA_CIBERSEGURIDAD.md`.** Las 16
categorías fijas de Agrupador y las 14 tácticas MITRE ATT&CK que extrae son
del pentesting/red-team clásico. Existe un campo paralelo, ya consolidado y
con autoridades propias (OWASP Top 10 for LLM Applications, MITRE ATLAS, NIST
AI RMF), que hoy no tiene representación en el esquema — un documento sobre
prompt injection o jailbreaks de un modelo, por ejemplo, no tiene categoría ni
técnica MITRE propia donde encajar bien.

Investigado a fondo (fuentes primarias: OWASP, MITRE, NIST), pero **sin
decidir nada** — es información para decidir más adelante si se amplía el
esquema, no una recomendación de hacerlo ya. (Aparte y ya resuelto: Cinéfilo/
Escritor sí tienen desde el 24-09 una categoría "Seguridad de la IA" en su
propio filtro de "qué cuenta como ciberseguridad" — eso es solo el filtro de
entrada, no toca el esquema fijo de 16 categorías/14 tácticas de Agrupador.)

---

## Rama `capas` sigue sin fusionar (riesgo de reconciliación futura)

Ver `project-seguimiento-github-cyberkb` en memoria para el detalle
actualizado. La rama `capas` (refactor de `main.py` en `layers/routers/*.py`,
autor nacho4xyz80) sigue sin fusionar a `main` y cada vez está más
desincronizada — no tiene Obsi, ni el enganche de agentes, ni la migración de
`/api/upload`/`/api/analyze` de hoy. Cuantos más commits se acumulen en `main`
sin que `capas` los incorpore, más dolorosa será la fusión si algún día se
decide hacerla.
