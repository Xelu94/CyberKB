---
id: tecnica-mitre-T1574.001
tipo: tecnica-mitre
fecha_actualizacion: 2026-09-28T10:42:55+00:00
---

# T1574.001 — DLL Search Order Hijacking

**Táctica:** Persistence, Privilege Escalation, Defense Evasion

**Ver en ATT&CK:** https://attack.mitre.org/techniques/T1574/001/

## Contexto

> El nombre DINPUT8.dll asociado a este hash de 10 bytes sugiere hipotéticamente un posible archivo stub utilizado en técnicas de DLL Search Order Hijacking, donde una DLL legítima del sistema es reemplazada por un archivo malicioso en un directorio de mayor prioridad de búsqueda. No confirmado con los datos disponibles.

> El nombre alternativo DINPUT8.dll asociado a este hash evoca la técnica de DLL hijacking, donde un atacante coloca una DLL falsa con el nombre de una librería legítima del sistema en el directorio de trabajo de una aplicación vulnerable. El fichero actual (10 bytes) no es funcional como DLL real, pero el nombre sugiere un posible artefacto de prueba o reconocimiento.

## Entidades relacionadas

[[Análisis forense — 0b894166 — 2025-03-11]]
[[Análisis forense — 0b894166 — 2025-03-11-2]]
