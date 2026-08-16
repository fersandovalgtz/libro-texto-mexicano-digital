# LTMD-U1 W5 — auditoría de activos Historia

Versión: `LTMD_U1_W5_HISTORY_ASSET_AUDIT_0.1`.

- Visores auditados: **18/18**.
- Visores de arquitectura no estándar: **0**.
- Posiciones declaradas: **3,194**.
- JPEG servidos y hasheados: **2,653**.
- Candidatos terminales sintéticos: **18**.
- Posiciones internas no servidas: **523**.
- Visores `direct_asset_ready`: **15/18**.

## Por generación

| generación | visores | ready | declaradas | JPEG | internos no servidos |
|---:|---:|---:|---:|---:|---:|
| 1993 | 3 | 3 | 513 | 510 | 0 |
| 2008 | 3 | 3 | 537 | 534 | 0 |
| 2011 | 3 | 3 | 566 | 563 | 0 |
| 2014 | 3 | 3 | 526 | 523 | 0 |
| 2018 | 3 | 0 | 526 | 0 | 523 |
| 2019 | 3 | 3 | 526 | 523 | 0 |

## Visores que requieren resolución adicional
- `H2018P4HIA` (2018, grado 4, UI=standard_x_js): internos=193; terminales=1; JPEG=0/194.
- `H2018P5HIA` (2018, grado 5, UI=standard_x_js): internos=193; terminales=1; JPEG=0/194.
- `H2018P6HIA` (2018, grado 6, UI=standard_x_js): internos=137; terminales=1; JPEG=0/138.

## Regla
Cada byte servido se recorre sólo para SHA-256 y tamaño; no se persisten JPEG. Un 404 final se conserva como candidato terminal y un 404 interno como anomalía. `direct_asset_ready` es un estado técnico de fuente y no acredita independencia documental, continuidad histórica ni equivalencia curricular.

Las coincidencias de cardinalidad entre 2014, 2018 y 2019 no autorizan aliases. OCR W5 permanece cerrado hasta analizar identidad exacta entre activos, routing y huecos internos.
