---
id: comando-285
tipo: comando
fecha_actualizacion: 2026-05-27T10:44:30.361024
---

# find / -name '*.conf' -readable 2>/dev/null | xargs grep -l 'password\

**SO:** linux
**Categoría:** privesc
**Herramienta:** PrivEsc

```bash
find / -name '*.conf' -readable 2>/dev/null | xargs grep -l 'password\|passwd\|secret' 2>/dev/null | head -20
```

Buscar contraseñas en ficheros de configuración legibles
