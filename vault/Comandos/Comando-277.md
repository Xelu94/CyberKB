---
id: comando-277
tipo: comando
fecha_actualizacion: 2026-05-27T10:44:30.361011
---

# find / -writable -type f 2>/dev/null | grep -v proc | grep -v sys

**SO:** linux
**Categoría:** privesc
**Herramienta:** PrivEsc

```bash
find / -writable -type f 2>/dev/null | grep -v proc | grep -v sys
```

Ficheros escribibles por el usuario actual (excluye /proc y /sys)
