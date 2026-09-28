---
id: comando-299
tipo: comando
fecha_actualizacion: 2026-05-27T10:44:30.361046
---

# icacls "C:\Program Files" /findsid Everyone /t 2>nul | findstr "(W)\|(

**SO:** windows
**Categoría:** privesc
**Herramienta:** PrivEsc

```bash
icacls "C:\Program Files" /findsid Everyone /t 2>nul | findstr "(W)\|(F)\|(M)"
```

Directorios de Program Files escribibles por Everyone (DLL hijacking / binary planting)
