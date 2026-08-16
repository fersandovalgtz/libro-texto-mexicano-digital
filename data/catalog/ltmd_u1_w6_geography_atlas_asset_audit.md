# LTMD-U1 W6 — auditoría de activos Geografía/Atlas

Versión: `LTMD_U1_W6_GEOGRAPHY_ATLAS_ASSET_AUDIT_0.1`.

- Visores auditados: **42/42**.
- Visores de arquitectura HTML no estándar: **1**.
- Posiciones declaradas: **6,160**.
- JPEG servidos y hasheados: **5,256**.
- Candidatos terminales sintéticos: **41**.
- Posiciones internas no servidas: **863**.
- Visores `direct_asset_ready`: **36/42**.

## Por generación

| generación | visores | ready | declaradas | JPEG | terminales | internos no servidos |
|---:|---:|---:|---:|---:|---:|---:|
| 1960 | 4 | 4 | 332 | 328 | 4 | 0 |
| 1966 | 7 | 7 | 805 | 798 | 7 | 0 |
| 1993 | 6 | 6 | 810 | 804 | 6 | 0 |
| 2008 | 5 | 4 | 757 | 751 | 4 | 2 |
| 2011 | 5 | 5 | 858 | 853 | 5 | 0 |
| 2014 | 5 | 5 | 866 | 861 | 5 | 0 |
| 2018 | 5 | 0 | 866 | 0 | 5 | 861 |
| 2019 | 5 | 5 | 866 | 861 | 5 | 0 |

## Visores que requieren resolución adicional
- `H2008P4GE273` (2008, grado 4, UI=standard_x_js): internos=2; terminales=0; JPEG=159/161.
- `H2018P4AMA` (2018, grado 4, UI=standard_x_js): internos=129; terminales=1; JPEG=0/130.
- `H2018P4GEA` (2018, grado 4, UI=standard_x_js): internos=201; terminales=1; JPEG=0/202.
- `H2018P5AGA` (2018, grado 5, UI=standard_x_js): internos=121; terminales=1; JPEG=0/122.
- `H2018P5GEA` (2018, grado 5, UI=standard_x_js): internos=209; terminales=1; JPEG=0/210.
- `H2018P6GEA` (2018, grado 6, UI=standard_x_js): internos=201; terminales=1; JPEG=0/202.

## Regla
Cada byte servido se recorre sólo para SHA-256 y tamaño; no se persisten JPEG. Un 404 final se conserva como candidato terminal y un 404 interno como anomalía. `direct_asset_ready` es un estado técnico de fuente y no acredita independencia documental, continuidad histórica ni equivalencia curricular.

La excepción de arquitectura HTML se conserva explícitamente y no se normaliza de forma ficticia. Coincidencias de título, grado, año o cardinalidad no autorizan aliases. OCR W6 permanece cerrado hasta analizar relaciones exactas entre activos, routing y huecos.
