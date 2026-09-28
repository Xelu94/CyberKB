---
id: comando-297
tipo: comando
fecha_actualizacion: 2026-05-27T10:44:30.361043
---

# wmic service get name,startname,pathname,startmode | findstr /i "auto"

**SO:** windows
**Categoría:** privesc
**Herramienta:** PrivEsc

```bash
wmic service get name,startname,pathname,startmode | findstr /i "auto"
```

Servicios en autostart con ruta y usuario que los ejecuta
