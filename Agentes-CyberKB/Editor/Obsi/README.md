# Agente Obsi

> **Estado (2026-09-28): construido, sin enganchar a `main.py`.** `obsi.py` y
> `vault_lib.py` ya existen y están probados contra la BBDD real. Falta que alguien
> decida registrar su router en `main.py` (no se hace solo, por norma del repo). El
> detalle de cómo se llegó a cada decisión está en
> [DECISIONES_OBSI.md](DECISIONES_OBSI.md).

Mantiene el vault de Obsidian de la app sincronizado con lo que hay en la BBDD SQLite,
sin que nadie tenga que ejecutar nada a mano. Es el último eslabón de la cadena de
ingesta.

```
Agrupador ──JSON──> Agente-BBDD ──(commit)──> Obsi ──> vault/Notas · Comandos · CVEs
                                                        Herramientas · Tecnicas-MITRE
```

No tiene `prompt.md`: **no consulta a ningún modelo**. Como Agente-BBDD, es
determinista — lee filas ya validadas de SQLite (nunca las recibe en crudo de la
pipeline) y escribe ficheros Markdown.

## Entradas

| Endpoint | Origen | Cuerpo |
|---|---|---|
| `POST /api/obsi/sync` | Agente-BBDD (tras confirmar en SQLite), o el frontend en un reintento aislado | `application/json`, ver abajo |

```json
{
  "nota_id": 123,
  "herramientas_ids": [4, 7],
  "comandos_ids": [55, 56],
  "cves_ids": ["CVE-2021-44228"],
  "mitre_ids": ["T1059"]
}
```

Los identificadores **no son homogéneos a propósito**: `herramientas_ids` y
`comandos_ids` son el `id` numérico de fila; `cves_ids` y `mitre_ids` son
`cve_id`/`technique_id` (texto), porque así es como el vault ya identifica a un CVE o
una técnica MITRE — no hay una nota por fila para estos dos tipos, sino una por
identificador único.

## Ciclo de trabajo

1. **Recibir** los ids del §Entradas.
2. **Releer** de SQLite exactamente esas filas (nunca `SELECT *` de toda la tabla) —
   así hereda las relaciones reales, igual que hace `migrate_to_obsidian.py`.
3. **Sincronizar** el vault, solo para las entidades recibidas:
   - localizar la nota existente de cada entidad por su `id` de frontmatter (no por
     nombre de fichero) usando `vault_lib.py`;
   - crearla si no existe, o actualizarla si ya existía;
   - si el nombre de fichero resultante cambió (p. ej. el título cambió), borrar el
     fichero antiguo — nunca dejar dos notas para la misma entidad.
4. **Responder**, ver abajo.

## Salidas

```json
{
  "sincronizado": true,
  "notas_creadas": ["Notas/Mi-nota.md"],
  "notas_actualizadas": ["Herramientas/Nmap.md"],
  "notas_borradas": ["Comandos/Comando-antiguo.md"]
}
```

`notas_borradas` son las huérfanas limpiadas en el paso 3 (nunca notas que el usuario
haya podido crear a mano en el vault fuera de las carpetas gestionadas).

## Reglas

1. **Cualquier fallo responde `"El grafo no ha podido actualizarse"`** (código
   `500`) — mensaje propio de Obsi, no el genérico `"Ha habido un error"` del resto
   de agentes, porque el frontend debe poder ofrecer un botón **"Reintentar"**
   específico para la sincronización del grafo/vault, distinto del reintento de la
   cadena entera.
2. **Quien llama a este endpoint (Agente-BBDD) trata el fallo como blando**: la BBDD
   ya está guardada cuando Obsi corre, así que un fallo aquí no debe deshacer nada ni
   hacer fallar la cadena entera. Ver `Editor/Obsi/DECISIONES_OBSI.md` §7.
3. **La sincronización es dirigida, no un volcado completo.** Solo toca las
   entidades recibidas en la llamada — con la cadena ya síncrona y tardando minutos
   por vídeo, releer/reescribir todo el vault en cada pasada sería demasiado coste.
4. **El vault vive en `/vault`** (raíz del repo de la app), salvo que
   `OBSIDIAN_VAULT_DIR` diga otra cosa — regla explícita del usuario, no solo un
   valor por defecto.

## Convenciones del vault

Heredadas de `scripts/migrate_to_obsidian.py` (repo de la app) — Obsi **no** inventa
las suyas, para que el vault sea coherente venga de donde venga cada nota. Ver
[DECISIONES_OBSI.md](DECISIONES_OBSI.md) §4 para el detalle completo (carpetas,
frontmatter, saneado de nombres, wikilinks).

## Configuración

Todo lo ajustable vive en [config.json](config.json).

### Variables de entorno

| Variable | Uso |
|---|---|
| `OBSIDIAN_VAULT_DIR` | Ruta del vault. Por defecto `<raíz del repo de la app>/vault` — misma convención que `migrate_to_obsidian.py`. |

## Ver también

- [DECISIONES_OBSI.md](DECISIONES_OBSI.md) — todas las decisiones de diseño, con el
  porqué de cada una.
- [investigacion-conexion.md](investigacion-conexion.md) — investigación original de
  cómo escribir en el vault (Opción A vs B) y el rediseño del pipeline.
- `Editor/Agente-BBDD/README.md` — quien llama a este agente.
