# CyberKB

> Base de conocimiento de ciberseguridad potenciada por IA. Centraliza notas, comandos, herramientas, CVEs, técnicas MITRE ATT&CK y resultados de OSINT en una única aplicación local, con una cadena de agentes que convierte automáticamente cualquier documento o vídeo en conocimiento estructurado.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)
![SQLite](https://img.shields.io/badge/SQLite-local-lightgrey)
![Claude](https://img.shields.io/badge/IA-Claude-orange)
![Obsidian](https://img.shields.io/badge/Grafo-Obsidian-7C3AED)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/versión-5.8-purple)

---

## Equipo de desarrollo

Proyecto desarrollado en el Máster en Ciberseguridad de [Evolve](https://evolve.es).

| | Rol |
|---|---|
| **José Luis Cuartero** | Creador y autor inicial — construyó la aplicación desde su origen: arquitectura, servidor, interfaz e integración con IA |
| **Adrián García-Largo Moreno** | Dirección del proyecto e integración — dirigió el proyecto e inspeccionó la infraestructura inicial y de los agentes |
| **Manuel Valdivielso Rodríguez** | Módulos de seguridad e integración — desarrolló los módulos de seguridad y unificó las tres líneas de trabajo del proyecto |
| **Ignacio Cano Peñalver** | Reorganización del servidor — repartió entre doce módulos independientes las funciones antes concentradas en un único fichero |

---

## ¿Qué es CyberKB?

CyberKB es una aplicación **local** de escritorio para profesionales y estudiantes de ciberseguridad. Se le importa un documento (PDF, ODT, DOCX, HTML, TXT, MD, LOG) o la URL de un vídeo, y una cadena de agentes especializados lo analiza, lo filtra, lo resume y lo clasifica automáticamente en notas, comandos, herramientas, CVEs, técnicas MITRE ATT&CK y entidades relacionadas — sin intervención manual.

Más allá del gestor de conocimiento, integra un flujo ofensivo completo: reconocimiento OSINT, enumeración activa de red y servicios, un módulo dedicado a vulnerabilidades web, threat intelligence en tiempo real, análisis forense automático por hash y generación de informes de auditoría técnicos y ejecutivos.

Todo corre **en local**. La base de datos es un fichero SQLite en tu máquina, y la información solo sale de ella cuando llamas explícitamente a un servicio externo cuya clave hayas configurado tú mismo.

## ¿Qué problema resuelve?

Cuando estudias o trabajas en ciberseguridad acumulas cientos de notas, PDFs, vídeos de clase, comandos y CVEs dispersos en carpetas, Notion, blocs de notas… CyberKB centraliza todo ese conocimiento en una sola herramienta local: lo organiza automáticamente con IA, lo hace buscable, y lo conecta — tanto en su propio grafo visual como en un vault de Obsidian — sin que tengas que clasificar nada a mano.

---

## Arquitectura

CyberKB se compone de cuatro piezas que funcionan en la misma máquina:

- **Interfaz web** — una página que se abre en el navegador (`index.html`, vanilla JS + D3.js, sin dependencias de compilación) desde la que se accede a todas las funciones.
- **Servidor de aplicación** — FastAPI. `main.py` es el punto de composición (configuración, ciclo de vida, servicio de la interfaz); la lógica de cada dominio vive en **12 routers independientes** bajo `layers/routers/` (notas, análisis, OSINT, herramientas, comandos, CVEs, MITRE, grafo, auditorías, chat, settings, forense).
- **Cadena de agentes** — cinco agentes especializados que procesan cada documento o vídeo importado (ver más abajo).
- **Base de datos** — un fichero SQLite local, creado automáticamente en el primer arranque.

El análisis de contenido lo realiza Claude (Anthropic); la transcripción de vídeo puede usar Whisper (OpenAI) como alternativa. Las consultas de OSINT e inteligencia de amenazas se hacen contra servicios públicos, algunos de los cuales requieren clave de API propia.

### La cadena de agentes

Convertir un documento en conocimiento estructurado no es una sola tarea: leer el fichero, descartar lo irrelevante, resumir, clasificar cada dato, guardarlo sin duplicar y, si procede, sincronizarlo con Obsidian. CyberKB reparte ese trabajo en cinco agentes encadenados, cada uno responsable de un único paso — así un fallo queda aislado, cada etapa se prueba por separado, y el paso más costoso (las llamadas al modelo de IA) solo se ejecuta cuando el contenido ya ha demostrado que merece la pena.

```
Entrada        documento o URL de vídeo
   │
Cinéfilo       transcripción (solo vídeos) — subtítulos o Whisper, descarta lo que no es ciberseguridad
   │
Escritor       filtrado y resumen — genera el PDF descargable y el resumen estructurado
   │
Agrupador      extracción y clasificación — notas, herramientas, comandos, CVEs, MITRE, grafo
   │
Agente-BBDD    guardado en la base de datos — determinista, sin IA, evita duplicados
   │
Obsi           copia al vault de Obsidian (opcional) — tampoco usa IA
   │
Resultado      nota disponible en la app + descarga en PDF
```

Si un documento no tiene contenido real (una página en blanco, un escaneo sin texto), el pipeline se detiene en el Escritor sin gastar análisis de IA en vano. Si el proceso falla en cualquier paso, se informa con un error controlado en vez de romper la aplicación.

---

## Módulos

| Módulo | Para qué sirve |
|---|---|
| 📝 **Editor** | Punto de entrada. Sube un documento o pega la URL de un vídeo; lanza la cadena de agentes y guarda la nota resultante |
| ⚙ **Herramientas** | Catálogo de herramientas de pentesting, con un set base siempre disponible (nmap, hydra, sqlmap, Burp Suite, Impacket…) más las que la IA detecta en tus documentos |
| ⌘ **Comandos** | Cheatsheet filtrable por SO (Linux/Windows/PowerShell/Google Dorks/PrivEsc), con generadores: SQLi, reverse shells, estabilización de shell |
| ◎ **OSINT** | 19 herramientas agrupadas por objetivo: dominio, IP/red, email, URL/web y threat intelligence |
| 🗺 **Enumeración** | Reconocimiento activo en tres fases: descubrimiento de red, análisis de servicios por puerto (generador Nmap, Windows/AD) y cheatsheet |
| 🕷 **Vulnerabilidades Web** | Fichas organizadas por OWASP Top 10 (SQLi, XSS, SSTI, SSRF, XXE, LFI, IDOR, Command Injection…), cada una con asistente de explotación por fases |
| ⬡ **Grafo** | Vista que conecta visualmente las entidades de la base de conocimiento |
| ⚠ **CVEs** | Listado con severidad, enriquecimiento contra NVD y aviso de exploit público en Exploit-DB |
| ✓ **Auditorías** | Checklists (Web App, Red, AD, OSINT, Ingeniería Social, Forense, Móvil, WordPress, Metodología Web…) con progreso guardado y generación de informe técnico/ejecutivo |
| ⚡ **MITRE ATT&CK** | Técnicas extraídas automáticamente de tus notas, corregidas contra el catálogo oficial STIX (697 técnicas), organizadas por táctica |
| 🔬 **Forense** | Análisis automático de una muestra por hash (MD5/SHA1/SHA256): VirusTotal + MalwareBazaar en paralelo, Any.run si hay muchas detecciones |
| ✦ **Chat** | Consulta en lenguaje natural sobre el contenido de tu base de conocimiento |

---

## Integración y mejoras del equipo

Tras la etapa fundacional en solitario (versiones v3 → v5.8, ver [Historial de versiones](#historial-de-versiones)), el equipo completo se incorporó y llevó cada módulo de seguridad de un esbozo funcional a una integración real contra las fuentes oficiales:

- **CVEs** — conexión a la API pública de NVD (NIST) para traer la ficha real de cada CVE, con reintentos ante los cortes intermitentes de Exploit-DB tras Cloudflare.
- **MITRE ATT&CK** — catálogo local de las 697 técnicas del STIX oficial (*enterprise-attack v19.2*), usado para corregir automáticamente la táctica que la IA asigna al analizar un documento.
- **Forense** — ajustado con muestras reales; si ningún servicio conoce un hash, la aplicación lo dice explícitamente en vez de dejar que la IA se invente un informe.
- **OSINT** — las 19 herramientas revisadas una por una: descripciones fieles a lo que devuelven de verdad, aviso de qué clave de API necesita cada una.
- **Enumeración** — constructor de Nmap rehecho con objetivo global (rellena la IP en todos los comandos a la vez) y buscador de exploits por versión detectada.
- **Vulnerabilidades Web** — fichas reorganizadas por OWASP Top 10; el generador de SQLi pasó de una lista de payloads a un asistente por fases (detectar → tipo → columnas → explotar) con payloads ciegos (booleanos y por tiempo) adaptados a cada motor de base de datos.
- **Herramientas** — catálogo base sembrado una sola vez (no reaparece si lo borras) y contador de menciones en vez de duplicar una herramienta ya detectada.
- **Reorganización del servidor** — `main.py` pasó de concentrar toda la lógica (≈1.400 líneas, 57 rutas) a ser solo el punto de composición (≈540 líneas), con el resto repartido en 12 routers independientes por dominio bajo `layers/`, migrado de forma incremental sin cambiar ninguna URL de la interfaz.
- **Cadena de agentes** — construida como las cinco piezas independientes descritas arriba (Cinéfilo, Escritor, Agrupador, Agente-BBDD, Obsi) e integrada con el flujo de subida de documentos, el progreso en vivo y el vault de Obsidian.

---

## Historial de versiones

<details>
<summary><strong>v5.8</strong> — Módulo de explotación web</summary>

- **Vulnerabilidades Web**: fichas de Path Traversal/LFI/RFI, XXE, SSRF y SSTI (detección, payloads, bypasses) y ficheros clave a leer
- **Identificador de motor SSTI**: a partir del payload probado y la respuesta observada, sugiere el motor (Jinja2, Tornado, Mako, ERB, FreeMarker, Velocity, Thymeleaf, Twig, Smarty, Nunjucks, Razor) y su payload de RCE
- **Diccionarios y polyglots**: payloads polyglot SSTI/XSS y rutas exactas de SecLists
- 3 técnicas nuevas de escalada de privilegios (binario sobreescribible, bypass de rbash, persistencia SSH)
- Checklist de Metodología Web
- Fix: escapado seguro de comillas/HTML en los botones de copiar/guardar
</details>

<details>
<summary><strong>v5.7</strong> — Herramientas ofensivas interactivas</summary>

- Generador de payloads SQLi (bypass auth, detección, UNION-based, comentar query)
- Sección Windows/AD en Enumeración (SMB, MSSQL/Impacket, post-explotación, tabla Windows vs Linux)
- Catálogo de técnicas de escalada de privilegios en tarjetas (detección + explotación + notas propias)
- Estabilización de shell (TTY upgrade) con aviso de pasos manuales
- Generador de reverse shells (PHP, Bash /dev/tcp, PowerShell) con IP/puerto interpolados
- Checklist de auditoría WordPress
</details>

<details>
<summary><strong>v5.6</strong> — Threat Intelligence, MITRE, Forense e Informes</summary>

- Threat Intelligence: AbuseIPDB y MalwareBazaar junto a VirusTotal
- Extracción automática de técnicas MITRE ATT&CK con tab dedicado por táctica
- Generador de informes de auditoría (técnico + ejecutivo), exportable en Markdown/PDF
- Have I Been Pwned, mejora de subdominios (crt.sh + HackerTarget), LeakRadar (credenciales filtradas)
- Badges de Exploit-DB en CVEs
- Cheatsheet de escalada de privilegios (19 técnicas) con enlaces a GTFOBins/LOLBAS
- Modo Forense: pipeline automático por hash SHA256 con síntesis por IA
- Barras de progreso animadas y rediseño del panel de API Keys
</details>

<details>
<summary><strong>v3</strong> — Versión inicial</summary>

Arquitectura base completa: servidor FastAPI + SQLite, frontend en un único fichero con grafo D3.js, integración con Claude para extracción automática de notas/comandos/herramientas/CVEs, módulo OSINT con 15+ herramientas, base de comandos con detección de SO y Google Dorks precargados, checklists de auditoría, empaquetado como ejecutable de Windows.
</details>

---

## Requisitos

- Python 3.11 o superior
- API key de Anthropic (Claude) — [obtener aquí](https://console.anthropic.com/) — **obligatoria**, es la que da servicio al análisis con IA
- Conexión a internet (para la IA y los servicios externos que configures)
- Para procesar vídeos: `ffmpeg` disponible en el sistema (lo usa `yt-dlp`)

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Xelu94/CyberKB.git
cd CyberKB
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus API keys:

```env
# Obligatoria
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# Opcional — transcripción de vídeo por Whisper (alternativa a subtítulos)
OPENAI_API_KEY=

# Opcionales — dejar vacío para deshabilitar esa herramienta
VIRUSTOTAL_API_KEY=       # gratis — virustotal.com
ABUSEIPDB_API_KEY=        # gratis — abuseipdb.com
MALWAREBAZAAR_API_KEY=    # gratis — bazaar.abuse.ch
HUNTER_API_KEY=           # gratis (25/mes) — hunter.io
HIBP_API_KEY=             # ~3.50$/mes — haveibeenpwned.com
LEAKRADAR_API_KEY=        # DeHashed compatible — dehashed.com
ANYRUN_API_KEY=           # gratis (tier limitado) — any.run
SHODAN_API_KEY=           # de pago — shodan.io
URLSCAN_API_KEY=          # gratis — urlscan.io

# Opcional — vault de Obsidian propio (si se deja vacío, usa ./vault)
OBSIDIAN_VAULT_DIR=
```

> También puedes configurar todas las keys desde la propia app: botón **🔑 API Keys** en la barra superior. Se guardan en `.env` sin reiniciar el servidor.

### 4. Iniciar la aplicación

```bash
# Windows (doble clic)
start.bat

# O directamente
python main.py
```

Se abre automáticamente en `http://localhost:8000`.

---

## Uso rápido

### Importar un documento

1. Pulsa **⊕ Subir doc** en la barra superior
2. Selecciona un PDF, ODT, DOCX, HTML, TXT, MD o LOG
3. La cadena de agentes lo procesa y, si el contenido es válido, lo guarda automáticamente con sus notas, comandos, herramientas, CVEs y técnicas MITRE

### Procesar un vídeo

1. En el módulo **Editor**, pega la URL del vídeo
2. La aplicación obtiene la transcripción (subtítulos oficiales o Whisper) y la trata igual que un documento

### Módulo Enumeración

1. Pestaña **🗺 ENUMERACIÓN**
2. Descubrimiento de red → genera el comando con la herramienta elegida
3. Análisis de servicios → generador Nmap de dos fases, luego consulta el servicio que encuentres abierto
4. Cheatsheet → referencia rápida de todos los flags

### Análisis forense

1. Pestaña **🔬 FORENSE**
2. Introduce un hash (MD5, SHA1 o SHA256)
3. **▶ Analizar** — el pipeline corre en segundo plano y crea una nota con las conclusiones

### OSINT

1. Pestaña **◎ OSINT**
2. Selecciona herramienta por categoría (dominio / IP / email / URL / threat intel)
3. Introduce la consulta → **▶ Ejecutar** — queda en el historial

### Generar informe de auditoría

1. Pestaña **✓ AUDITORÍAS**
2. Elige el tipo de auditoría y completa la lista de verificación
3. **📄 Generar Informe** → técnico o ejecutivo → descarga en Markdown o imprime como PDF

---

## Herramientas OSINT incluidas

| Categoría | Herramienta | API necesaria |
|---|---|---|
| **Dominio** | WHOIS | No |
| | DNS Records | No |
| | Subdominios (crt.sh + HackerTarget) | No |
| | SSL Certificate | No |
| | Wayback Machine | No |
| | DMARC / SPF / DKIM | No |
| | robots.txt | No |
| **IP / Red** | IP Geolocalización | No |
| | Reverse DNS (PTR) | No |
| | Shodan | Sí (pago) |
| **Email** | Verificar Email (MX + SMTP) | No |
| | Have I Been Pwned | Sí (dominio gratis, email pago) |
| | Hunter.io email finder | Sí (gratis) |
| | LeakRadar (credenciales filtradas) | Sí (DeHashed) |
| **URL / Web** | HTTP Headers + seguridad | No |
| | URLscan.io | No / Sí (para enviar) |
| **Threat Intel** | AbuseIPDB | Sí (gratis) |
| | VirusTotal (hash/IP) | Sí (gratis) |
| | MalwareBazaar | Sí (gratis) |

---

## Compilar EXE (Windows)

```bash
pip install pyinstaller
pyinstaller cyberkb.spec --noconfirm
# EXE generado en dist/CyberKB.exe
```

O usando el script incluido:
```bash
build.bat
```

---

## Estructura del proyecto

```
CyberKB/
├── main.py                    # Punto de composición FastAPI: config, ciclo de vida, routers
├── layers/
│   ├── routers/                # 12 routers por dominio (notes, analyze, osint, tools,
│   │                            #  commands, cves, mitre, graph, audits, chat, settings, forensic)
│   └── routers_functions.py    # Funciones auxiliares compartidas entre routers
├── models.py                  # Modelos SQLAlchemy (Note, Command, Tool, CVE, MitreTechnique…)
├── database.py                 # Configuración SQLite
├── claude_service.py           # Integración Claude API (análisis, extracción, informes, forense)
├── osint_tools.py              # 19 herramientas OSINT asíncronas
├── document_parser.py          # Parser PDF / ODT / DOCX / HTML / TXT / MD
├── mitre_reference.json        # Catálogo local de las 697 técnicas MITRE ATT&CK (STIX oficial)
├── index.html                  # Frontend completo (vanilla JS + D3.js, single-file)
├── Agentes-CyberKB/Editor/      # Cadena de agentes de ingesta
│   ├── Cinefilo/                #   transcripción de vídeo
│   ├── Escritor/                #   filtrado y resumen
│   ├── Agrupador/               #   extracción y clasificación
│   ├── Agente-BBDD/             #   guardado determinista en base de datos
│   └── Obsi/                    #   sincronización con el vault de Obsidian
├── scripts/
│   └── migrate_to_obsidian.py  # Migración/regeneración manual del vault completo
├── vault/                      # Vault de Obsidian (generado; grafo nativo sin coste de IA)
├── requirements.txt            # Dependencias Python
├── cyberkb.spec                 # Spec PyInstaller
├── start.bat                   # Script de inicio (Windows)
├── build.bat                    # Script de compilación EXE
├── .env.example                 # Plantilla de variables de entorno (sin keys reales)
├── data/                        # Base de datos SQLite (generada al arrancar)
└── uploads/                     # Documentos subidos (excluidos de git)
```

---

## Stack tecnológico

- **Backend**: FastAPI (arquitectura por capas, 12 routers) · Uvicorn · SQLAlchemy · SQLite
- **IA**: Anthropic Claude (análisis, extracción de entidades, informes, síntesis forense) · OpenAI Whisper (transcripción de vídeo, opcional)
- **Cadena de agentes**: 5 agentes especializados en ingesta — ver [Arquitectura](#arquitectura)
- **Grafo de conocimiento**: D3.js v7 (vista interna) + vault de Obsidian (grafo nativo externo, sin coste de IA)
- **Vídeo**: yt-dlp + ffmpeg
- **Frontend**: Vanilla JS, single-file
- **OSINT**: httpx async · dnspython · python-whois · 10+ APIs públicas y privadas
- **Empaquetado**: PyInstaller (EXE Windows standalone)

---

## Evolución y planes a futuro

El proyecto sigue en desarrollo activo:

- **Chat como asistente diario** — que deje de ser una consulta puntual y pase a orientar en las tareas habituales y en el uso del resto de módulos.
- **Búsqueda semántica** — sobre la base de conocimiento, para encontrar notas, comandos o CVEs relacionados aunque no coincidan las palabras exactas.
- **Optimización para proyectos, máquinas y laboratorios** — agilizar las tareas más frecuentes de una auditoría o un ejercicio práctico.
- **Experiencia de usuario y rendimiento** — más información de progreso para el usuario y mejoras de velocidad.

---

## Licencia

MIT — libre para uso personal y educativo.
Proyecto académico desarrollado durante el Máster en Ciberseguridad de [Evolve](https://evolve.es).
