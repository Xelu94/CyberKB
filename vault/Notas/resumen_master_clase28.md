---
id: nota-57
tipo: nota
fecha_actualizacion: 2026-06-17T12:26:11.982437
---

# resumen_master_clase28

**Categoría:** explotacion
**Tags:** #NTLM, #LFI, #Responder, #SMB, #NTLMv2, #hash-cracking, #Windows, #HTB, #AWS-S3, #cloud-hacking

## Contenido

La sesión cubre el ataque combinado de LFI (Local File Inclusion) y envenenamiento NTLM usando Responder en la máquina HTB Responder. Se explota un parámetro ?page= sin sanitizar para forzar una conexión SMB a nuestra IP mediante rutas UNC, capturando el hash NTLMv2 del servidor Windows. El hash capturado se crackea offline con John the Ripper usando el diccionario rockyou.txt.
