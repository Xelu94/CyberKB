---
id: comando-295
tipo: comando
fecha_actualizacion: 2026-05-27T10:44:30.361039
---

# reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v Always

**SO:** windows
**Categoría:** privesc
**Herramienta:** PrivEsc

```bash
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

AlwaysInstallElevated — si está a 1, MSI malicioso se ejecuta como SYSTEM
