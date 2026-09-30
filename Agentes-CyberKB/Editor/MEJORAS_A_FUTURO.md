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

## Modo Forense — UNIFICADO (2026-09-29)

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

**Prueba real (2026-09-29), sin aplicar — se queda apartada.** Se recreó una
nota forense realista a mano (misma forma exacta que produce
`/api/forensic/analyze`: categoría `forense`, subcategoría `malware-analysis`,
un CVE real y 2 técnicas MITRE, sobre un caso de LockBit 3.0/Citrix Bleed) y se
ejecutó `/api/notes/{id}/extract` sobre ella (el mismo mecanismo que se usaría
si Forense se unificara). El riesgo resultó **mucho menor de lo esperado**,
gracias al arreglo del punto "Riesgo 5" (más abajo, ya aplicado):

- Categoría/subcategoría/tags: **se conservaron** — ya no se pisan.
- El CVE existente se **enriqueció** (título, severidad, productos afectados)
  sin duplicarse.
- Las técnicas MITRE: sin cambios, sin duplicar.
- Único efecto secundario real: Agrupador añadió `VirusTotal` como fila en
  `tools`, porque el texto lo menciona como fuente de detección — ruido, no
  daño (VirusTotal no es una herramienta que el analista use activamente en el
  sentido que Agrupador normalmente captura).

**Decisión (2026-09-29): unificado.** Con el riesgo real ya medido y bajo, se
aplicó — `/api/forensic/analyze` ahora llama a `_reanalizar_con_agrupador(n, db)`
igual que `/api/notes/{id}/extract` y `/api/graph/reindex-all`, en vez de
`ai.extract_entities()` (que queda sin ningún llamador y se eliminó de
`main.py`, junto con `_persist_entities()`). La categorización especializada
(`ai.generate_forensic_note()`) y la persistencia inicial de CVEs/MITRE desde
VT/MalwareBazaar/Any.run **no se tocaron** — Agrupador solo enriquece/añade
por encima, no sustituye ese primer paso. Ruido conocido y aceptado: puede
colarse alguna fuente de datos (VirusTotal, MalwareBazaar) como fila en
`tools`.

**Probado de punta a punta el mismo día (2026-09-29), sin claves de VT/
MalwareBazaar/Any.run** (`hash_vt`/`hash_malwarebazaar`/`anyrun_lookup`
degradan con un dict de error en vez de fallar, así que el endpoint real se
pudo ejecutar igualmente) — y esto destapó un bug real en el propio arreglo
de arriba:

**Bug encontrado**: la primera implementación "restauraba" category/
subcategory/tags en `main.py` *después* de llamar a Agrupador
(`db.refresh(n)` + reasignar + `db.commit()`). Funcionaba en pruebas cortas,
pero era una **carrera de tiempos**: si Agente-BBDD tardaba más que el
timeout del llamador (Agrupador→BBDD, 60s) y Agrupador se rendía
(`bbdd_entregado: false`), Agente-BBDD seguía terminando en segundo plano
(mismo patrón de "se completa tarde" que el de Escritor→Agrupador de por la
mañana) y su commit tardío volvía a pisar la restauración — sin que
`main.py` se enterara ni tuviera forma de reaccionar. Reproducido dos veces
con el hash real de EICAR: `category` acababa en `malware` en vez de
`forense`, aunque los logs de depuración mostraban la restauración
ejecutándose correctamente *en el momento* (el problema era el commit
posterior de BBDD, no la lógica de `main.py`).

**Arreglo real, en el origen**: `Agente-BBDD/agente_bbdd.py::_nota()` ahora
comprueba `datos.source` — si es `"app-reextract"` (lo que manda
`_reanalizar_con_agrupador`), **no toca** `category`/`subcategory`/`tags` de
una nota existente, sea cual sea el orden o el timing en que lleguen los
commits. Se quitó el código de restauración de `main.py` (ya no hace falta).
De paso se subieron también los timeouts `Agrupador→BBDD` y
`Agente-BBDD→Obsi` de 60s a 120s (mismo motivo que el de
`Escritor→Agrupador` por la mañana), aunque el arreglo real ya no depende de
que el timeout sea suficiente.

**Verificado con el hash real de EICAR tras el arreglo**: `category='forense'`,
`subcategory='malware-analysis'` preservados, 5 tools y 4 técnicas MITRE
extraídas por Agrupador, 1 sola nota (sin duplicar), petición completa en
~3m30s.

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

## Rama `capas` — contenido de valor fusionado (2026-09-29); la reestructuración sigue sin adoptar

Ver `project-seguimiento-github-cyberkb` en memoria para el detalle
actualizado. `capas` (autor nacho4xyz80) resultó ser dos cosas mezcladas: (A)
mejoras reales de funcionalidad — que en realidad venían todas de
`feat/tools-mejoras` (autor 17Manu11) y `capas` solo las había absorbido vía
merge — y (B) una reestructuración de `main.py` en `layers/routers/*.py`
propia de `capas`, sin relación con (A).

**Decisión (2026-09-29, pedida al usuario): fusionar solo (A), no (B).**
Se hizo `git merge origin/feat/tools-mejoras` directamente a `main` (sin pasar
por `capas`, que sólo habría añadido la reestructuración sin aportar nada
nuevo). Merge automático, sin conflictos, no toca `Agentes-CyberKB/` ni el
enganche de agentes de hoy. Contenido incorporado: SSTI (RCE real por motor),
Enum (UI + guardar CVE desde exploit conocido + EDB más robusto), CVEs (borrar
de la KB), MITRE (buscador de referencia ATT&CK v19), Herramientas
(crear/borrar/sembrar), Forense (acepta MD5/SHA1, avisa si faltan API keys
antes de gastar la IA, nota honesta "sin datos" en vez de alucinar). Probado
en local (servidor arrancado, Forense/MITRE/Herramientas/SSTI verificados en
navegador) antes de comprometer el merge. Pendiente de `push` — a confirmar.

**Sigue abierto:** la reestructuración de `main.py` en `layers/routers/*.py`
(B) de `capas` no se adoptó — se consideró más riesgo (chocaría con el
enganche de agentes de hoy) que beneficio inmediato. Si se decide adoptarla
más adelante, revisar el estado de `capas` de nuevo en ese momento (seguirá
divergiendo de `main` mientras tanto, pero ya sin la mayoría del contenido de
valor que la motivaba a corto plazo).


---

## Frontend real del Editor — pendientes tras construirlo (2026-09-30)

Lista de trabajo del frontend real ya construido (vídeo/documento/texto vía
agentes, progreso en vivo, ver/descargar notas). Complementa la sección
"Frontend del Editor — Parte 3" de más arriba, que ya está mayormente hecha.



- **Botón "+ Nueva"** (`index.html`, toolbar del Editor): oculto por ahora
  (`style="display:none"`, sigue llamando a `newNote()` si se reactiva). Hay
  que mirar qué hace exactamente hoy (limpia título/contenido/categoría/tags,
  oculta la tarjeta IA y el botón borrar, pone foco en el título) y decidir si
  eso sigue teniendo sentido con el nuevo flujo (vídeo/documento vía agentes)
  o si hay que cambiarlo.

- **Botón "Guardar"** (`index.html`, toolbar del Editor): eliminado del HTML y
  su backend `POST /api/notes` (`create_note` en `main.py`) borrado. Queda
  pendiente la función `saveNote()` en el frontend: su rama de crear nota
  llama a un POST que ya no existe (la rama `PUT /api/notes/{id}` sí sigue
  viva). Hay que decidir si se borra `saveNote()`, si se deja solo para
  editar notas existentes, o si guardar lo harán ya los agentes (BBDD/Obsi).

- **Botón "Cancelar" para procesos en curso** (`index.html` + backend): falta
  poder cancelar una transcripción de vídeo o una subida de documento mientras
  está "En curso". Se llegó a montar y se revirtió a propósito, porque una
  cancelación honesta necesita decidir el alcance:
  - **Front (fácil, ya probado):** un `AbortController` por petición y un botón
    "✕ Cancelar" en la tarjeta de "En curso". Aborta la ESPERA y devuelve la
    interfaz al instante, pero **no detiene el backend**: la cadena es una sola
    petición síncrona (`/api/cinefilo/transcribir`, `/api/upload`) y los agentes
    siguen procesando esa vuelta por detrás (la nota puede acabar creándose).
    Pasos: `API.post(path,data,opts)` con `signal`; `AbortController` en
    `transcribeVideo()` y `uploadDocPipeline()`; tratar `AbortError` en el catch
    (volver a "inicial" + aviso); botón en la rama `curso` de `_edPreview()`.
  - **Backend (de verdad, pendiente de decidir):** para parar el proceso real
    haría falta cancelación cooperativa en la cadena (Cinéfilo → Escritor →
    Agrupador → BBDD → Obsi): un id de trabajo, un flag de cancelación que cada
    agente consulte entre pasos, y limpiar lo ya escrito (JSON en disco, filas
    parciales). Es rework de los agentes; decidir si merece la pena o si basta
    con el cancelar de front + avisar de que el servidor puede seguir.
  - Decidir el alcance antes de reimplementar. Referencia: se hizo y revirtió
    en la sesión del 2026-09-29.

- **Categoría (select `#noteCat`) y Tags (`#noteTags`)** (`index.html`,
  toolbar del Editor): ocultos por ahora (`style="display:none"`), no
  borrados, porque los siguen usando `newNote()`, `loadNote()`, `saveNote()`,
  `analyzeNote()` y la subida de documentos. Hay que mirar si con el flujo de
  agentes (el Agrupador ya decide categoría y tags) tienen sentido: quitarlos
  del todo, dejarlos solo de lectura para mostrar lo que decidió el agente, o
  mantenerlos para corregir a mano.
