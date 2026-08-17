# LTMD-U1 W9 — auditoría de activos Educación Física

Versión: `LTMD_U1_W9_EDUCACION_FISICA_ASSET_AUDIT_0.1`.

- Visores auditados: **4/4**.
- Visores de arquitectura HTML no estándar: **0**.
- Posiciones declaradas: **452**.
- JPEG servidos y hasheados: **448**.
- Candidatos terminales sintéticos estrictos: **4**.
- Posiciones no servidas: **0**.
- Visores `direct_asset_ready`: **4/4**.

## Por visor

| visor | grado | declaradas | JPEG | terminal estricto | no servidas | ready |
|---|---:|---:|---:|---:|---:|---:|
| `H2008P1ED252` | 1 | 115 | 114 | 1 | 0 | 1 |
| `H2008P2ED260` | 2 | 107 | 106 | 1 | 0 | 1 |
| `H2008P5ED280` | 5 | 115 | 114 | 1 | 0 | 1 |
| `H2008P6ED287` | 6 | 115 | 114 | 1 | 0 | 1 |

## Regla
Cada byte servido se recorre sólo para SHA-256 y tamaño; no se persisten JPEG. Un 404 final sólo es `terminal_synthetic_candidate` si **todas** las posiciones anteriores fueron servidas como imagen. Cualquier hueco previo, incluido un subtree ausente, mantiene el final como `internal_unserved`. `direct_asset_ready` es sólo un estado técnico de fuente.

OCR W9 permanece cerrado hasta que una compuerta de admisibilidad reconcilie exactamente alcance, arquitectura, inventario y esta auditoría.
