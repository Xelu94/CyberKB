---
id: nota-34
tipo: nota
fecha_actualizacion: 2026-05-12T08:20:43.561316
---

# resumen_master_clase7

**Categoría:** osint
**Subcategoría:** OSINT/HUMINT y scripting Bash para auditorías externas
**Tags:** #osint, #humint, #bash, #scripting, #phishing, #credenciales-filtradas, #maltego, #ingenieria-social, #auditorias-externas, #kali-linux
**Origen:** resumen_master_clase7.odt

## Resumen

La sesión cubre dos bloques: creación de comandos personalizados en Bash (shebang, chmod, PATH) y una introducción práctica a OSINT/HUMINT en auditorías externas. Se demuestra el uso de herramientas como OpenSense, Maltego, HaveIBeenPwned y plataformas de credenciales filtradas para construir perfiles de objetivos, detectar brechas y personalizar ataques de phishing dirigido. Se incluye comparativa de modelos de IA para generación de scripts.

## Contenido

Máster de Ciberseguridad e Inteligencia Artificial – Wolf Academy

La sesión tiene dos bloques principales: la consolidación práctica de comandos personalizados en Bash (con alumnos compartiendo pantalla y creando sus propios comandos en directo) y una introducción aplicada al OSINT/HUMINT con demostración en vivo de las herramientas más utilizadas en auditorías externas.

OSINT (Open Source Intelligence) es la recopilación de inteligencia a partir de fuentes abiertas y públicas de Internet con el objetivo de conocer mejor a una organización o persona antes de perpetrar un ataque.

HUMINT (Human Intelligence) es la variante centrada en personas físicas: construir un perfil social completo de un individuo para personalizar el ataque (ingeniería social, phishing dirigido, suplantación).

¿Cuándo se usa en auditorías? - Siempre en auditorías externas, como punto de partida. - Para identificar empleados y construir el directorio de objetivos antes del phishing. - Para detectar credenciales filtradas que se pueden reutilizar en portales corporativos. - Para localizar documentos internos filtrados que se pueden reportar como hallazgo.

Reflexión clave del profesor: quien personaliza el ataque con información OSINT puede cobrar 10.000 € en vez de 4.000 €, porque la probabilidad de éxito es exponencialmente mayor. Ejemplo real: una campaña de phishing a 1.200 empleados obtuvo un 80% de apertura de correo y un 27% de envío de datos.

Crear el script con nano nombre_comando:

Primera línea: #!/bin/bash (shebang — indica que es un ejecutable Bash).

Contenido: comandos de terminal o lógica.

Dar permisos de ejecución: chmod +x nombre_comando

Moverlo al PATH (con sudo porque las rutas del PATH son de root):

sudo mv nombre_comando /usr/local/sbin/nombre_comando

Invocar desde cualquier parte del sistema simplemente escribiendo el nombre.

Script que muestra un Rick Roll en ASCII art en la terminal, utilizando curl:

#!/bin/bash

curl ascii.live/rick

Variante mejorada: pasar por parámetro $1 el número de segundos que debe durar, usando timeout:

#!/bin/bash

timeout $1 curl ascii.live/rick

Uso: rickroll 10 → reproduce el Rick Roll durante 10 segundos y para automáticamente.

* en lugar de # al inicio del shebang: el * se interpreta como comodín, no como inicio de comentario/shebang. Siempre usar #!.

No meter el script en el PATH: el script funciona si se ejecuta con ./nombre desde su carpeta, pero no es un “comando” hasta que se mueve a una ruta del PATH.

Ruta incorrecta al mover: escribir mal la ruta destino (ej. bin en vez de .local/bin o usr/local/sbin) hace que el comando no aparezca. Usar echo $PATH para confirmar las rutas disponibles.

sudo su innecesario: no hace falta cambiar a root permanentemente; basta con usar sudo delante del comando específico que lo requiere.

Las versiones más nuevas de Kali usan ZSH por defecto en lugar de Bash. Sin embargo: - El 99% de los servidores que se auditarán en entornos reales usan Bash (Linux de versiones antiguas). - Especificar #!/bin/bash en el shebang garantiza que el script se interprete como Bash independientemente del shell activo. - El profesor prefiere Bash por ser más universal y estable.

Se debatió sobre qué modelo de IA usar para generar scripts: - Claude (Anthropic): favorito del profesor. Usa Claude Sonnet y Opus. Para proyectos complejos usa Claude Code con agentes y redes neuronales vectoriales para ahorro de tokens. - ChatGPT (OpenAI): el nuevo modelo o3 (Cortex) es muy competente para código; la batalla con Sonnet es constante. - Cursor (IDE): IDE de programación con modelos integrados (Sonnet, Haiku, GPT-4, Grok). Muy útil para proyectos de desarrollo. No necesita red neuronal ni agentes propios. - Gemini: gratis para estudiantes durante un año (incluye 5 TB y la versión Pro). Interesante como alternativa gratuita. - Herramienta clave para automatización de clics: Playwright — permite controlar un navegador Chromium programáticamente. El profesor lo combina con Claude para automatizar cualquier tarea que no tenga API (ej. formularios en Power Automate, creación de flujos sin API).

OpenSense es la alternativa moderna a Maltego: correlación de nodos mediante grafos con motor de IA integrado. Permite partir de un correo electrónico e ir iterando para descubrir: - Aliases y perfiles en GitHub, Twitter, foros. - Correos alternativos vinculados al mismo usuario. - Hashes de contraseñas extraídos de bases de datos filtradas. - Conexiones entre personas (colaboradores, proyectos compartidos).

Demostración en clase: buscando el correo del profesor, OpenSense encontró en minutos: alias keyadimundi, perfil en GitHub con proyecto compartido con un amigo del colegio de hace 15 años, correo antiguo de Hotmail, presencia en BreachForums, y varios hashes de contraseñas filtradas de múltiples brechas.

Herramienta de correlación de nodos OSINT de referencia en el sector (~5.000€/mes en licencia completa). Disponible en versión gratuita con correos temporales: - Descarga desde maltego.com/downloads. - Se puede crear cuentas ilimitadas usando emails de un solo uso (10minutemail, tempmail, etc.). - Se conecta mediante APIs a fuentes externas: VirusTotal, Hunter.io, bases de datos de personas, fuentes corporativas, etc. - Plugins gratuitos recomendados: CasaFile Entities, CyberStreet Intelligence, Corporate Intelligence (500+ transformaciones). - Advertencia: la versión de Kali Linux de Maltego es muy lenta; recomendable instalarlo en Windows.

Servicio gratuito que comprueba si un correo ha aparecido en brechas de datos conocidas. Muestra el servicio donde se filtró, la fecha y el tipo de datos comprometidos. Importante aclarar al cliente: no significa que le hayan hackeado el correo, sino que los servicios donde está registrado fueron comprometidos.

Plataforma de pago (~7€/mes) que muestra las contraseñas en texto claro de brechas filtradas. Usos en auditorías: - Buscar por dominio corporativo (ej. repsol.com) y obtener usuarios y contraseñas potenciales. - Probar esas contraseñas en portales no corporativos (Amazon, Canva) para verificar si el usuario reutiliza contraseña → si funciona, usar esa contraseña en el portal VPN o Microsoft de la empresa. - Extraer el fichero CSV y usarlo como diccionario en un ataque de fuerza bruta o password spraying. - Identificar patrones de contraseñas para crear diccionarios personalizados.

Caso real en clase: búsqueda de contraseñas de la Policía Nacional encontró contraseñas tipo “tortosa”, “tortogol” — contraseñas triviales que no cumplen ninguna política de seguridad. La IP 127.0.0.1 en la base de datos indica que la filtración fue interna (un ntds.dit extraído desde dentro de la red).

Recomendación: usar una cuenta de correo anónima (ProtonMail) para Dehashed; pagos con criptomonedas para mayor anonimato. No usar correo temporal porque los pagos requieren cuenta persistente.

Herramienta que indexa bases de datos de números de teléfono recopiladas de agendas robadas por aplicaciones maliciosas (el clásico ejemplo de la linterna que pide acceso a contactos). Permite buscar un número de teléfono y obtener el nombre con el que está guardado en otras agendas. Demostración en vivo con números de teléfono de los alumnos → el profesor encontró cómo tenían guardado su número en las agendas de otras personas (apodos, nombres completos, etc.).

Para extraer metadatos de imágenes (ubicación GPS, dispositivo, fecha/hora). Actualmente en desuso porque iOS y Android eliminan los metadatos EXIF por defecto al subir imágenes a redes sociales.

1. Buscar el dominio en Dehashed/OpenSense → credenciales filtradas

2. Verificar credenciales en servicios no corporativos (Amazon, Canva)

3. Si funciona → probarla en portal VPN/Microsoft de la empresa

4. Si entra → estamos dentro de la red corporativa sin explotar ninguna vulnerabilidad

El HUMINT (stalking de perfiles) permite construir un perfil psicológico de la víctima a partir de sus últimos 30 “me gusta” en redes sociales. Estudio psicológico citado: con solo 30 likes de Facebook se puede predecir la personalidad con más precisión que la propia familia. Aplicación ofensiva: personalizar el pretexto del ataque de ingeniería social con los gustos, intereses y rutinas de la víctima.

Serie recomendada para entender el OSINT aplicado a personas: You (Netflix) — muestra cómo a partir de una foto y OSINT se puede trazar la dirección, rutina y círculo social de una persona.

Semanas

Contenido

Semanas 1-4

Bases de informática, terminal Linux y Windows, redes, OSINT

~Semana 5-6

Primeros ataques en máquina vulnerable (Metasploitable)

~Semanas 7-8

Módulo de hacking web completo

~Mes 2.5

Full Hack The Box (máquinas reales)

Últimos 2 meses

Práctica 3: entorno Active Directory, pivoting avanzado

Término en la transcripción

Corrección / Aclaración

UMINT / umint

HUMINT (Human Intelligence) – inteligencia basada en personas

Open Sense / OpenSense

OpenSense – herramienta de correlación OSINT con motor de IA

Maldego / Maltego

Maltego – herramienta estándar de correlación OSINT en grafos

Haunter.io / Hounder.io

Hunter.io – herramienta para buscar correos electrónicos corporativos

Half-Time Impounded / Half-fiving

Have I Been Pwned (haveibeenpwned.com) – verificador de filtraciones de datos

Hasset / Dehashed

Dehashed – plataforma de contraseñas filtradas

Bridge Forums / BridgeForums

BreachForums – foro principal de la Deep Web para filtración de datos

Virus Total

VirusTotal – plataforma de análisis de malware con múltiples motores antivirus

Exit Tool

ExifTool – herramienta de extracción de metadatos de imágenes

Cortex / el nuevo de GPT

GPT o3 (“Cortex”) – modelo avanzado de OpenAI para código y razonamiento

Sonnet / Opus 4.7

Claude Sonnet / Claude Opus – modelos de lenguaje de Anthropic

Cloud de Code / Claudio

Claude Code – herramienta de Anthropic para desarrollo asistido por IA

Cursor

Cursor – IDE de programación con integración de múltiples modelos de IA

Playwright

Playwright – librería para automatización de navegador (clics, formularios, scraping)

Power Automate

Microsoft Power Automate – herramienta de automatización de flujos de trabajo

ñ de temp / el símbolo

Alt Gr + 4 + Espacio → ~ (tilde, símbolo del directorio home en Linux)

nntdc.dip

ntds.dit – base de datos del Active Directory con todos los hashes de contraseñas

ascii.live/rick

curl ascii.live/rick – URL que muestra el Rick Roll en ASCII art en terminal

Bounsert Digital

Bouncer Digital – empresa del profesor orientada a protección del menor en Internet

un USCP

OSCP (Offensive Security Certified Professional) – certificación premium de pentesting

Resumen elaborado para uso académico en el Máster de Ciberseguridad e Inteligencia Artificial – Wolf Academy.

6 

## Entidades relacionadas

[[OpenSense]]
[[Maltego]]
[[HaveIBeenPwned]]
[[Playwright]]
[[Claude (Anthropic)]]
[[Cursor]]
[[curl]]
[[nano]]
[[Comando-266]]
[[Comando-267]]
[[Comando-268]]
[[Comando-269]]
[[Comando-270]]
