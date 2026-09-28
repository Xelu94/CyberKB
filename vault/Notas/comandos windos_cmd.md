---
id: nota-29
tipo: nota
fecha_actualizacion: 2026-05-11T15:56:14.229507
---

# comandos windos_cmd

**Categoría:** comandos
**Subcategoría:** Windows CMD Command Reference
**Tags:** #CMD, #Windows, #batch, #enumeracion, #administracion-sistemas, #red, #procesos, #usuarios
**Origen:** comandos windos_cmd.pdf

## Resumen

Referencia completa de comandos CMD de Windows que cubre operaciones básicas de sistema de archivos, administración de red, gestión de procesos y usuarios, y automatización mediante scripts batch. Incluye comandos relevantes para reconocimiento y enumeración de sistemas Windows como ipconfig, netstat, systeminfo, tasklist y net user. Útil tanto para administración de sistemas como para operaciones de seguridad ofensiva y defensiva en entornos Windows.

## Contenido

Chuleta Completa de Comandos CMD
1. Comandos Básicos
- dir: Lista archivos y carpetas en el directorio actual.
Ejemplo: dir
- cd: Cambia de directorio.
Ejemplo: cd Documentos
- mkdir: Crea una nueva carpeta.
Ejemplo: mkdir NuevaCarpeta
- rmdir: Elimina una carpeta.
Ejemplo: rmdir Carpeta
- copy: Copia archivos.
Ejemplo: copy archivo.txt D:\Backup\
- move: Mueve o renombra archivos.
Ejemplo: move archivo.txt C:\Destino\
- del: Elimina archivos.
Ejemplo: del archivo.txt
- rename: Cambia el nombre de un archivo.
Ejemplo: rename viejo.txt nuevo.txt
- cls: Limpia la pantalla.
Ejemplo: cls
- tree: Muestra estructura de carpetas.
Ejemplo: tree /f
2. Comandos Intermedios
- ipconfig: Muestra configuración de red.
Ejemplo: ipconfig /all
- ping: Verifica conexión con un host.
Ejemplo: ping google.com
- tracert: Muestra la ruta hacia un host.
Ejemplo: tracert google.com
- netstat: Muestra conexiones de red activas.
Ejemplo: netstat -ano
- systeminfo: Muestra información del sistema.
Ejemplo: systeminfo

Chuleta Completa de Comandos CMD
- tasklist: Lista procesos activos.
Ejemplo: tasklist
- taskkill: Finaliza procesos.
Ejemplo: taskkill /IM notepad.exe /F
- chkdsk: Verifica errores en el disco.
Ejemplo: chkdsk C:
- sfc /scannow: Repara archivos del sistema.
Ejemplo: sfc /scannow
- wmic: Información avanzada del sistema.
Ejemplo: wmic computersystem get model
3. Comandos Avanzados
- set: Muestra o establece variables de entorno.
Ejemplo: set PATH
- setx: Establece variables de entorno permanentemente.
Ejemplo: setx PATH "C:\MiRuta"
- echo: Muestra mensajes o variables.
Ejemplo: echo %USERNAME%
- type: Muestra contenido de un archivo.
Ejemplo: type archivo.txt
- find: Busca texto en archivos.
Ejemplo: find "error" log.txt
- fc: Compara archivos.
Ejemplo: fc archivo1.txt archivo2.txt
- path: Muestra o establece rutas de búsqueda.
Ejemplo: path
- attrib: Muestra o cambia atributos de archivos.
Ejemplo: attrib +h archivo.txt
- shutdown: Apaga o reinicia el sistema.
Ejemplo: shutdown /s /t 0
- net user: Administra usuarios.
Ejemplo: net user
- net localgroup: Administra grupos locales.
Ejemplo: net localgroup administrators Cesar /add

Chuleta Completa de Comandos CMD
- powershell: Ejecuta comandos de PowerShell.
Ejemplo: powershell Get-Process
- Redirecciones: > (sobrescribe), >> (agrega), < (entrada)
Ejemplo: dir > salida.txt
- Pipes: Conecta comandos.
Ejemplo: ipconfig | find "IPv4"
- Variables: Uso de %VAR%
Ejemplo: set MI_VAR=Hola
- Batch básico: Archivos .bat con secuencia de comandos.
4. Tablas Comparativas de Comandos
Comando Descripción Ejemplo
dir Lista archivos dir
cd Cambiar carpeta cd Documentos
mkdir Crear carpeta mkdir Nueva
del Eliminar archivo del archivo.txt
ping Probar conexión ping google.com
taskkill Cerrar proceso taskkill /IM app.exe /F
5. Trucos Útiles
- TAB: Autocompleta nombres de archivos y carpetas.
- F7: Muestra historial de comandos.
- Ejecutar como administrador: Click derecho > Ejecutar como administrador.
- Rutas relativas: cd .. para subir un nivel.
- Rutas absolutas: cd C:\Usuarios\Cesar\Documentos
6. Notas Finales
- Evita usar 'del /s /q *.*' sin saber qué haces: puede borrar todo.
- Siempre verifica rutas antes de ejecutar comandos destructivos.
- Usa 'help comando' para ver opciones disponibles.
- Puedes crear archivos .bat para automatizar tareas repetitivas.
- CMD no distingue mayúsculas de minúsculas.

## Entidades relacionadas

[[netstat]]
[[WMIC]]
[[PowerShell]]
[[net]]
[[Comando-133]]
[[Comando-134]]
[[Comando-135]]
[[Comando-136]]
[[Comando-137]]
[[Comando-138]]
[[Comando-139]]
[[Comando-140]]
[[Comando-141]]
[[Comando-142]]
[[Comando-143]]
[[Comando-144]]
[[Comando-145]]
[[Comando-146]]
[[Comando-147]]
