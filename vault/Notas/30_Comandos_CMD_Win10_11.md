---
id: nota-23
tipo: nota
fecha_actualizacion: 2026-05-11T15:53:13.600715
---

# 30_Comandos_CMD_Win10_11

**Categoría:** redes
**Subcategoría:** Diagnóstico y administración de red con CMD Windows
**Tags:** #CMD, #Windows, #networking, #sysadmin, #diagnostico-red, #troubleshooting, #ICMP, #DNS, #DHCP, #netstat, #malware-detection
**Origen:** 30_Comandos_CMD_Win10_11.pdf

## Resumen

Documento educativo sobre 30 comandos esenciales de CMD para Windows 10/11 orientado a SysAdmins e IT Support. Cubre diagnóstico de red, resolución de problemas de conectividad, detección de malware mediante análisis de conexiones activas y administración del sistema. Los comandos incluyen herramientas para verificar conectividad, rastrear rutas, gestionar configuración IP, consultar DNS y monitorizar conexiones de red activas.

## Contenido

30 Comandos CMD
Esenciales
para Windows 10 y 11
Aprende los comandos esenciales de CMD para Windows, cómo usarlos en situaciones reales y aplicar
mejores prácticas de administración de sistemas en tu día a día
Domina ping, ipconfig, netstat y potencia tu carrera como SysAdmin o IT Support

¿Por Qué Dominar CMD?
⚡ 🔍
Automatización Troubleshooting Rápido
Automatiza tareas repetitivas con scripts batch y ahorra horas de Diagnostica problemas de red, sistema y hardware en segundos sin
trabajo manual cada semana necesidad de herramientas gráficas
🎯 📜
Acceso Directo Scripts Batch
Accede a configuraciones avanzadas y funciones del sistema que no Crea scripts reutilizables para configurar equipos nuevos, hacer
están disponibles en la interfaz gráfica backups o ejecutar mantenimiento programado
🌐 👑
Diagnóstico de Red Control Total
Identifica problemas de conectividad, latencia y configuración de red Obtén control completo del sistema operativo y gestiona recursos de
con comandos especializados forma eficiente y profesional
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

1. Ping - Verificar Conectividad
SINTAXIS Y USO EJEMPLO PRÁCTICO - SYSADMIN
COMANDO ESCENARIO
Un usuario reporta que no puede acceder a internet desde su
ping google.com
computadora. Todos los demás usuarios en la oficina tienen internet
funcionando correctamente.
USO PRINCIPAL DIAGNÓSTICO
Verificar si un host está accesible en la red y medir la latencia de 1. Ejecutas (DNS de Google)
ping 8.8.8.8
la conexión. Envía paquetes ICMP Echo Request y espera → Resultado: "Request timed out"
respuestas para confirmar conectividad.
2. Ejecutas (tu router local)
ping 192.168.1.1
VARIANTES COMUNES
→ Resultado: Respuestas exitosas con tiempo < 5ms
ping -t → Ping continuo
ping -n 10 → 10 paquetes 3. Ejecutas
ping google.com
ping -l 1000 → Tamaño 1000 bytes
→ Resultado: "Request timed out"
CONCLUSIÓN
El equipo tiene conectividad local (ping al router funciona) pero no
tiene acceso a internet. El problema es con el ISP o la configuración
del router, no con la red local del usuario.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

2. Tracert - Rastrear Ruta
SINTAXIS Y USO EJEMPLO SYSADMIN / IT SUPPORT
Escenario:
tracert google.com
Usuario reporta que accede lentamente a un servidor remoto.
USO PRINCIPAL
Procedimiento:
Identificar saltos de red (hops) y rastrear la ruta que toman los
1. Ejecutas:
tracert servidor.com
paquetes hacia un destino específico
2. Analizas cada salto (hop)
3. Identificas salto con latencia de
DETALLES TÉCNICOS 500ms
Tracert (Trace Route) envía paquetes ICMP con TTL (Time To
Live) incrementando, mostrando cada router intermedio, su IP y Diagnóstico:
tiempo de respuesta. Útil para identificar dónde se pierde • Salto 1-2: ✓ Normal (< 50ms)
conectividad o se genera latencia. • Salto 3: ✗ Problema (500ms)
• Salto 4-5: ✓ Normal (< 50ms)
Acción:
Contactas al proveedor ISP para que revise ese router específico.
Resultado:
Sin tracert, solo sabrías que "está lento" sin poder identificar el
punto exacto del problema.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

3. Ipconfig - Configuración IP
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
ipconfig /all
Usuario reporta que no puede navegar en internet.
Escenario:
USO PRINCIPAL
Diagnóstico:
Ver configuración de red completa: dirección IP, máscara de
1. Ejecutas
ipconfig
subred, gateway predeterminado, servidores DNS y estado DHCP
2. Ves IP (APIPA - error DHCP)
169.254.x.x
Solución:
1. (liberar IP)
ipconfig /release
2. (obtener nueva IP)
ipconfig /renew
3. Usuario obtiene IP válida y navega correctamente
VARIANTES COMUNES
/all /release
Muestra configuración completa detallada Libera la dirección IP actual (DHCP)
/renew /flushdns
Solicita nueva dirección IP al servidor DHCP Limpia la caché DNS local
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

4. Nslookup - Consulta DNS
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
Escenario:
nslookup google.com
Usuario reporta que algunos sitios web no cargan, pero otros sí
funcionan correctamente.
USO PRINCIPAL
Resolver nombres de dominio a direcciones IP y verificar la
Diagnóstico:
configuración DNS del sistema
1. Ejecutas
nslookup facebook.com
2. Ves error: "DNS request timed out"
VARIANTES COMUNES
3. Ejecutas (Google DNS)
nslookup facebook.com 8.8.8.8
nslookup dominio.com
4. Ahora funciona correctamente
Consulta DNS básica
nslookup dominio.com 8.8.8.8 Conclusión:
Consulta usando servidor DNS específico El problema es el servidor DNS del ISP. Cambias la configuración
DNS del equipo a 8.8.8.8 y 8.8.4.4 (Google DNS) y el problema
se resuelve.
Resultado:
Sin nslookup, habrías perdido tiempo revisando firewall, antivirus
o reinstalando navegadores sin identificar la causa real.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

5. Netstat - Estadísticas de Red
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
Escenario: Sospechas que un equipo tiene malware porque está
netstat -ano
enviando datos a internet sin que el usuario haya abierto ningún
programa.
Procedimiento:
1. Ejecutas netstat -ano
2. Revisas la lista de conexiones activas
USO PRINCIPAL 3. Identificas una conexión sospechosa al puerto 4444 (puerto
común de backdoors)
Ver conexiones activas de red, puertos abiertos en escucha,
4. Anotas el PID (Process ID) de esa conexión
estadísticas de protocolos y procesos que están usando la red
5. Ejecutas tasklist | findstr [PID]
6. Descubres el proceso malicioso
Resultado: Sin netstat, no podrías ver las conexiones ocultas que
hace el malware. Este comando te permite identificar exactamente
qué proceso está comunicándose con servidores externos y tomar
VARIANTES ÚTILES
acción inmediata para eliminarlo.
netstat -a - Todas las conexiones y puertos
netstat -n - Direcciones numéricas (más rápido)
netstat -o - Muestra el PID del proceso
netstat -b - Muestra el ejecutable (requiere admin)
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

6. Pathping - Análisis de Ruta
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
Escenario:
pathping google.com
Usuario con sistema VoIP reporta cortes intermitentes en
llamadas. Ping muestra latencia normal, pero las llamadas se
USO PRINCIPAL
cortan.
Combina las funcionalidades de ping y tracert para realizar un
análisis detallado de pérdida de paquetes en cada salto de la ruta
Diagnóstico:
DETALLES TÉCNICOS 1. Ejecutas
pathping servidor-voip.com
Pathping envía múltiples paquetes a cada salto durante 300 2. Esperas 5 minutos para análisis completo
segundos (por defecto) y calcula estadísticas de pérdida de 3. Revisas estadísticas de cada salto
paquetes y latencia para cada router intermedio. Es más preciso 4. Identificas que el salto 5 tiene 15% de pérdida de paquetes
que tracert para identificar problemas de red.
Acción:
Reportas al ISP el router específico con pérdida de paquetes. El
ISP reemplaza el equipo defectuoso.
Resultado:
Las llamadas VoIP funcionan perfectamente. Sin pathping, solo
sabrías que "a veces falla" sin poder identificar el salto
problemático.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

7. Getmac - Dirección MAC
SINTAXIS Y USO EJEMPLO PRÁCTICO - SYSADMIN
COMANDO
Escenario:
Necesitas configurar filtrado MAC en el router empresarial para
getmac
permitir solo equipos autorizados en la red corporativa. Tienes
50 equipos que necesitan acceso.
USO PRINCIPAL
Obtener las direcciones MAC (Media Access Control) de todos
Procedimiento:
los adaptadores de red del equipo. La dirección MAC es el
1. En cada equipo ejecutas
getmac
identificador físico único de cada tarjeta de red.
2. Obtienes la dirección MAC del adaptador Ethernet
VARIANTES COMUNES 3. Registras la MAC junto con el nombre del equipo
4. Configuras el router con la lista de MACs autorizadas
getmac /v → Modo verbose (detallado)
getmac /fo table → Formato tabla
getmac /s [PC] → MAC de equipo remoto Caso de Uso Adicional:
Un usuario reporta problemas de red. Ejecutas y
getmac
EJEMPLO DE SALIDA
descubres que la MAC está duplicada (clonada) con otro equipo,
causando conflictos en la red.
Dirección física: 00-1A-2B-3C-4D-5E
Nombre de transporte: Ethernet
Resultado:
Sin getmac, tendrías que buscar la MAC manualmente en las
propiedades de red de cada equipo, perdiendo tiempo valioso.
Con este comando, obtienes la información en segundos.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

8. ARP - Tabla de Direcciones
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
Escenario: Sospechas que hay dispositivos no autorizados
arp -a
conectados a la red local de la empresa.
Procedimiento:
1. Ejecutas en tu equipo
arp -a
2. Obtienes lista de IPs y MACs en tu segmento de red
3. Comparas con el inventario de dispositivos autorizados
USO PRINCIPAL 4. Identificas una MAC desconocida:
00:1A:2B:3C:4D:5E
5. Buscas el fabricante por los primeros 6 dígitos (OUI)
Ver y modificar la tabla ARP (Address Resolution Protocol) que
6. Descubres que es un dispositivo personal no autorizado
mapea direcciones IP a direcciones MAC físicas en la red local
Resultado: Localizas el dispositivo físicamente, lo desconectas y
reportas la violación de política de seguridad. Sin ARP, no tendrías
visibilidad de qué dispositivos están realmente conectados a tu red
local.
VARIANTES ÚTILES
- Ver toda la tabla ARP
arp -a
- Eliminar entrada de la tabla
arp -d
- Agregar entrada estática
arp -s IP MAC
- Ver entrada específica
arp -a [IP]
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

9. Route - Tabla de Enrutamiento
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
Escenario:
route print
Tu empresa tiene dos redes: la red principal (192.168.1.0/24) y
USO PRINCIPAL una red remota en otra sucursal (192.168.50.0/24). Los usuarios
Ver y modificar la tabla de enrutamiento de red, que determina no pueden acceder a recursos de la sucursal remota.
cómo el sistema envía paquetes a diferentes destinos de red
Diagnóstico:
VARIANTES COMUNES
1. Ejecutas
route print
route print
2. Verificas que no existe ruta hacia 192.168.50.0
Muestra la tabla de enrutamiento completa
3. El gateway VPN es 192.168.1.254
route add 192.168.2.0 mask 255.255.255.0 192.168.1.1
Agrega una ruta estática
Solución:
route delete 192.168.2.0 Ejecutas:
Elimina una ruta específica
route add 192.168.50.0 mask 255.255.255.0
192.168.1.254 -p
El parámetro hace la ruta permanente (sobrevive reinicios).
-p
Resultado:
Ahora los equipos pueden acceder a la red remota correctamente
a través del gateway VPN.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

10. Netsh - Configuración de Red
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
netsh interface show interface
Escenario 1: Configurar IP Estática
Necesitas configurar una IP fija en un servidor.
USO PRINCIPAL
Herramienta avanzada para configurar red, firewall, WiFi y adaptadores
netsh interface ip set address "Ethernet" static
desde línea de comandos. Permite configuración completa del sistema
192.168.1.100 255.255.255.0 192.168.1.1
de red de Windows.
VARIANTES COMUNES Configura IP estática sin usar la interfaz gráfica.
netsh interface ip show config
Ver configuración IP
Escenario 2: Exportar Configuración WiFi
Usuario cambió de laptop y necesita las contraseñas WiFi.
netsh wlan show profiles
Ver perfiles WiFi guardados
netsh wlan export profile key=clear folder=C:\WiFi
netsh advfirewall show allprofiles
Ver estado del firewall
Exporta todos los perfiles WiFi con contraseñas en texto claro para
migrarlos al nuevo equipo.
Netsh es la navaja suiza de configuración de red en
Resultado:
Windows. Permite automatizar configuraciones complejas que
tomarían muchos clics en la interfaz gráfica.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

11. Chkdsk - Verificar Disco
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
Escenario:
chkdsk C: /f /r
Usuario reporta que algunos archivos no se abren correctamente y
Windows muestra mensajes de error al acceder a ciertos documentos
USO PRINCIPAL
en el disco C:.
Verificar y reparar errores del sistema de archivos en discos duros,
detectar sectores dañados y recuperar información legible
Diagnóstico:
PARÁMETROS IMPORTANTES
1. Abres CMD como administrador
- Repara errores en el disco 2. Ejecutas
/f chkdsk C: /f /r
3. Sistema solicita reinicio (disco en uso)
- Localiza sectores dañados y recupera información
/r
4. Confirmas y reinicias el equipo
5. Durante el arranque, chkdsk analiza el disco
- Desmonta el volumen primero (si es necesario)
/x
6. Detecta 15 sectores dañados y 3 archivos corruptos
⚠ Requiere privilegios de administrador y reinicio si es disco del sistema 7. Repara errores del sistema de archivos
8. Recupera datos de sectores legibles
Resultado:
El sistema arranca correctamente, los archivos que estaban corruptos
se recuperan o se marcan como irrecuperables. El disco funciona de
manera estable nuevamente. Sin chkdsk, el problema habría
empeorado hasta causar pérdida total de datos.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

12. SFC - Verificar Sistema
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
sfc /scannow
Escenario:
Usuario reporta que Windows tiene comportamiento errático:
USO PRINCIPAL
aplicaciones se cierran inesperadamente, mensajes de error al abrir
System File Checker (SFC) verifica la integridad de todos los
el Explorador de archivos, y algunas funciones del sistema no
archivos protegidos del sistema y reemplaza los archivos corruptos
responden.
con versiones correctas desde la caché de Windows.
DETALLES TÉCNICOS
Diagnóstico:
• Requiere permisos de administrador
Sospechas de archivos del sistema corruptos. Decides ejecutar
• Tiempo de ejecución: 15-30 minutos
SFC.
• Repara automáticamente archivos dañados
• Genera log en C:\Windows\Logs\CBS\CBS.log
Procedimiento:
⚠ Si SFC no puede reparar archivos, ejecuta primero DISM para reparar 1. Abres CMD como Administrador
la imagen de Windows
2. Ejecutas:
sfc /scannow
3. Esperas 20 minutos mientras escanea
4. SFC reporta: "Protección de recursos de Windows encontró
archivos dañados y los reparó correctamente"
Resultado:
Después de reiniciar, todas las aplicaciones funcionan
correctamente. SFC reparó archivos críticos del sistema sin
necesidad de reinstalar Windows, ahorrando horas de trabajo.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

13. DISM - Reparar Imagen

14. Diskpart - Gestión de Discos
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
diskpart Necesitas preparar una USB de 32GB para crear un
Escenario:
instalador booteable de Windows.
USO PRINCIPAL
Herramienta interactiva de línea de comandos para particionar,
Procedimiento:
formatear y gestionar discos duros, SSDs y dispositivos de
1. Ejecutas
diskpart
almacenamiento
2. (identificas que la USB es Disk 2)
list disk
COMANDOS INTERNOS CLAVE 3.
select disk 2
list disk - Listar todos los discos 4. clean (borra todo el contenido)
5.
select disk N - Seleccionar disco create partition primary
6.
format fs=fat32 quick
clean - Limpiar disco completamente
7. (asigna letra de unidad)
assign
create partition primary - Crear partición
8. (marca como booteable)
active
format fs=ntfs quick - Formatear rápido
9.
exit
assign - Asignar letra de unidad
USB lista para copiar archivos de instalación de Windows.
Resultado:
⚠ ADVERTENCIA: Diskpart puede borrar datos permanentemente. Verifica Sin diskpart, tendrías que usar herramientas de terceros o la interfaz
siempre el disco seleccionado antes de ejecutar comandos destructivos.
gráfica que no siempre funciona correctamente para crear medios
booteables.
Limpiar completamente un disco antes de vender
Otro Uso Común:
un equipo o reinstalar Windows desde cero.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

15. Powercfg - Energía
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
powercfg /batteryreport
Escenario:
Usuario reporta que la batería de su laptop corporativa dura muy poco
USO PRINCIPAL
tiempo. Antes duraba 8 horas, ahora solo 3 horas.
Gestionar configuración de energía del sistema y generar reportes
detallados de batería y consumo energético
Diagnóstico:
VARIANTES COMUNES 1. Ejecutas
powercfg /batteryreport
- Genera reporte HTML de batería 2. Se genera archivo HTML en C:\Windows\System32
/batteryreport
3. Abres el reporte y revisas:
- Analiza eficiencia energética
/energy
• Capacidad de diseño:
50,000 mWh
/sleepstudy - Analiza consumo en suspensión • Capacidad actual: 22,500 mWh (45%)
• Ciclos de carga:
- Lista planes de energía disponibles 850 ciclos
/list
- Activa modo hibernación
/hibernate on
Conclusión:
La batería está degradada al 45% de su capacidad original.
Recomiendas reemplazo de batería al usuario.
Caso Adicional:
Ejecutas y descubres que una aplicación está
powercfg /energy
impidiendo que el equipo entre en modo de bajo consumo, drenando
batería innecesariamente.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

16. Systeminfo - Información del Sistema
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
systeminfo
Escenario:
Necesitas verificar si un equipo cumple los requisitos para instalar un
USO PRINCIPAL
nuevo software de diseño que requiere: Windows 10 Pro, 8GB RAM
Obtener información detallada del hardware, sistema operativo, red y
mínimo, y procesador de 64 bits.
configuración completa del equipo en formato de texto
INFORMACIÓN CLAVE QUE PROPORCIONA Procedimiento:
1. Ejecutas en el equipo
• Modelo y fabricante del equipo systeminfo
2. Revisas la salida:
• Versión de Windows y build
• Sistema operativo: Windows 10 Pro ✓
• Fecha de instalación del sistema • Memoria física total: 4,096 MB (4GB) ✗
• Tipo de sistema: x64-based PC ✓
• RAM total y disponible
• Procesador y arquitectura
Conclusión:
• Hotfixes instalados El equipo NO cumple requisitos. Tiene solo 4GB de RAM cuando se
requieren 8GB mínimo. Recomiendas upgrade de memoria antes de
• Configuración de red (IPs, gateway)
instalar el software.
• Dominio o grupo de trabajo
Uso Adicional:
Ejecutas para verificar qué
systeminfo | findstr /C:"Hotfix"
parches de seguridad están instalados y asegurar que el equipo está
actualizado.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

17. Tasklist - Listar Procesos
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
tasklist
Escenario:
Usuario reporta que su equipo está extremadamente lento y el
USO PRINCIPAL
ventilador está a máxima velocidad constantemente.
Ver todos los procesos en ejecución en el sistema con su PID (Process
ID), uso de memoria y sesión asociada
Diagnóstico:
VARIANTES ÚTILES 1. Ejecutas para ver todos los procesos
tasklist
- Muestra servicios asociados a cada proceso 2. Revisas la columna de memoria (Mem Usage)
tasklist /svc
3. Identificas: - 4,200,000 K (4.2 GB)
chrome.exe
- Muestra DLLs cargadas por cada proceso
tasklist /m
4. También ves múltiples instancias de chrome.exe
tasklist /fi "memusage gt 500000" - Filtra procesos que usan más de 5. Ejecutas tasklist /fi "imagename eq chrome.exe"
500MB
6. Confirmas que hay 15 procesos de Chrome activos
- Modo verbose con información detallada
tasklist /v
Solución:
Identificas el PID del proceso principal de Chrome y lo terminas con
taskkill. El usuario tenía 50+ pestañas abiertas consumiendo toda la
RAM.
Resultado:
Sistema vuelve a funcionar normalmente. Sin tasklist, no podrías
identificar rápidamente qué proceso está causando el problema de
rendimiento.
ITWizardMX | Sígueme en LinkedIn | www.moddtech.com

18. Taskkill - Terminar Procesos

18. Taskkill - Ejemplos Prácticos
CASOS DE USO DEL DÍA A DÍA - SYSADMIN / IT SUPPORT
Escenario 1: Aplicación Congelada
Usuario reporta que Excel está completamente congelado y no responde. Task Manager no puede cerrarlo.
Solución:
Ejecutas:
taskkill /f /im EXCEL.EXE
El proceso se cierra inmediatamente.
Escenario 2: Malware Persistente
Detectas un proceso sospechoso "svchost.exe" con PID 4532 que consume 90% de CPU y no se puede cerrar normalmente.
Diagnóstico:
1. Ejecutas para confirmar el PID
tasklist
2. Ejecutas
taskkill /f /pid 4532
3. El proceso malicioso se termina forzadamente
Escenario 3: Múltiples Instancias
Chrome tiene 50 procesos abiertos y el equipo está lento.
Solución:
Ejecutas:
taskkill /f /im chrome.exe /t
Cierra Chrome y todos sus procesos hijos.

19. WMIC - Información WMI
COMANDO EJEMPLO SYSADMIN / IT SUPPORT
wmic
Escenario:
Necesitas crear un inventario de hardware 

## Entidades relacionadas

[[netstat]]
[[nslookup]]
[[tracert]]
[[Comando-74]]
[[Comando-75]]
[[Comando-76]]
[[Comando-77]]
[[Comando-78]]
[[Comando-79]]
[[Comando-80]]
[[Comando-81]]
[[Comando-82]]
[[Comando-83]]
[[Comando-84]]
[[Comando-85]]
