# LTMD-U1 W10 — posiciones fuente anómalas

Versión: `LTMD_U1_W10_SOURCE_ANOMALIES_0.1`.

- Posiciones declaradas auditadas: **12,174**.
- Posiciones no clasificadas como `source_jpeg`: **69**.
- `terminal_synthetic_candidate`: **68**.
- `internal_unserved`: **1**.
- `probe_error`: **0**.

## Huecos internos

| visor | página del visor | índice fuente | HTTP | URL observada |
|---|---:|---:|---:|---|
| `H2014P1ENA` | 114 | 114 | 404 | `https://historico.conaliteg.gob.mx/c/H2014P1ENA/114.jpg` |

## Regla
Este producto no reinterpreta 404 ni construye rutas alternativas. Expone exactamente las posiciones no servidas observadas por la auditoría byte a byte para facilitar investigación documental acotada. Los candidatos terminales sintéticos permanecen diferenciados de los huecos internos.
