---
id: comando-301
tipo: comando
fecha_actualizacion: 2026-05-27T10:44:30.361049
---

# dir /s /b C:\*.config C:\*.xml C:\*.ini C:\*password* 2>nul | findstr 

**SO:** windows
**Categoría:** privesc
**Herramienta:** PrivEsc

```bash
dir /s /b C:\*.config C:\*.xml C:\*.ini C:\*password* 2>nul | findstr /i "pass\|cred\|secret"
```

Buscar ficheros con contraseñas hardcodeadas en disco
