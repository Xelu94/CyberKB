---
id: comando-288
tipo: comando
fecha_actualizacion: 2026-05-27T10:44:30.361029
---

# find / -path /proc -prune -o -path /sys -prune -o -name '*.py' -o -nam

**SO:** linux
**Categoría:** privesc
**Herramienta:** PrivEsc

```bash
find / -path /proc -prune -o -path /sys -prune -o -name '*.py' -o -name '*.sh' -writable -print 2>/dev/null | head -20
```

Scripts Python/Bash escribibles — puede inyectarse código si los ejecuta root
