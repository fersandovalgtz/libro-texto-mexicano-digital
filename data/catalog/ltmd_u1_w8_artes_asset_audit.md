# LTMD-U1 W8 — auditoría de activos Artes

Versión: `LTMD_U1_W8_ARTES_ASSET_AUDIT_0.2`.

- Visores auditados: **20/20**.
- Visores de arquitectura HTML no estándar: **0**.
- Posiciones declaradas: **1,874**.
- JPEG servidos y hasheados: **1,490**.
- Candidatos terminales sintéticos estrictos: **16**.
- Posiciones no servidas: **368**.
- Visores `direct_asset_ready`: **16/20**.

## Por generación

| generación | visores | ready | declaradas | JPEG | terminales estrictos | no servidos |
|---:|---:|---:|---:|---:|---:|---:|
| 2008 | 2 | 2 | 206 | 204 | 2 | 0 |
| 2011 | 6 | 6 | 564 | 558 | 6 | 0 |
| 2014 | 4 | 4 | 368 | 364 | 4 | 0 |
| 2018 | 4 | 0 | 368 | 0 | 0 | 368 |
| 2019 | 4 | 4 | 368 | 364 | 4 | 0 |

## Visores que requieren resolución adicional
- `H2018P3EAA` (2018, grado 3, UI=standard_x_js): no_servidos=90; terminales=0; JPEG=0/90.
- `H2018P4EAA` (2018, grado 4, UI=standard_x_js): no_servidos=90; terminales=0; JPEG=0/90.
- `H2018P5EAA` (2018, grado 5, UI=standard_x_js): no_servidos=90; terminales=0; JPEG=0/90.
- `H2018P6EAA` (2018, grado 6, UI=standard_x_js): no_servidos=98; terminales=0; JPEG=0/98.

## Regla
Cada byte servido se recorre sólo para SHA-256 y tamaño; no se persisten JPEG. Un 404 final sólo puede clasificarse como `terminal_synthetic_candidate` cuando todas las posiciones declaradas anteriores fueron servidas como imagen. Si existe cualquier hueco previo —incluido un subárbol totalmente ausente— el 404 final permanece `internal_unserved`. `direct_asset_ready` es un estado técnico de fuente y no acredita independencia documental, continuidad histórica ni equivalencia curricular.

Coincidencias de título, grado, generación o cardinalidad no autorizan aliases. OCR W8 permanece cerrado hasta analizar relaciones exactas entre activos, routing y huecos.
