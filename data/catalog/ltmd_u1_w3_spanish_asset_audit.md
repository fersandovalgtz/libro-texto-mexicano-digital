# LTMD-U1 W3 — auditoría de activos Español/Lengua

Versión: `LTMD_U1_W3_SPANISH_ASSET_AUDIT_0.1`.

- Visores auditados: **130/130**.
- Visores UI horizontal: **4**.
- Posiciones declaradas: **23,894**.
- JPEG servidos y hasheados: **22,433**.
- Candidatos terminales sintéticos: **125**.
- Posiciones internas no servidas: **1336**.
- Visores `direct_asset_ready`: **115/130**.

## Por generación

| generación | visores | ready | declaradas | JPEG | internos no servidos |
|---:|---:|---:|---:|---:|---:|
| 1960 | 3 | 3 | 479 | 476 | 0 |
| 1966 | 8 | 8 | 1,542 | 1,534 | 0 |
| 1972 | 16 | 16 | 3,258 | 3,242 | 0 |
| 1982 | 11 | 11 | 2,149 | 2,138 | 0 |
| 1988 | 8 | 8 | 1,472 | 1,464 | 0 |
| 1993 | 21 | 20 | 3,756 | 3,734 | 1 |
| 2008 | 9 | 5 | 1,659 | 1,648 | 5 |
| 2011 | 12 | 11 | 2,016 | 2,004 | 1 |
| 2014 | 14 | 13 | 2,723 | 2,709 | 1 |
| 2018 | 14 | 6 | 2,420 | 1,078 | 1328 |
| 2019 | 14 | 14 | 2,420 | 2,406 | 0 |

## Visores que requieren resolución adicional
- `H1993P4ES193` (1993, grado 4, UI=standard_x_js): internos=1; terminales=1; JPEG=237/239.
- `H2008P3ES265` (2008, grado 3, UI=standard_x_js): internos=1; terminales=0; JPEG=209/210.
- `H2008P3ES266` (2008, grado 3, UI=standard_x_js): internos=1; terminales=0; JPEG=225/226.
- `H2008P4ES271` (2008, grado 4, UI=standard_x_js): internos=1; terminales=1; JPEG=237/239.
- `H2008P4ES272` (2008, grado 4, UI=standard_x_js): internos=2; terminales=0; JPEG=255/257.
- `H2011P2ES305` (2011, grado 2, UI=standard_x_js): internos=1; terminales=0; JPEG=105/106.
- `H2014P2ESA` (2014, grado 2, UI=standard_x_js): internos=1; terminales=0; JPEG=256/257.
- `H2018P3ESA` (2018, grado 3, UI=standard_x_js): internos=161; terminales=1; JPEG=0/162.
- `H2018P3LEA` (2018, grado 3, UI=standard_x_js): internos=161; terminales=1; JPEG=0/162.
- `H2018P4ESA` (2018, grado 4, UI=standard_x_js): internos=161; terminales=1; JPEG=0/162.
- `H2018P4LEA` (2018, grado 4, UI=standard_x_js): internos=161; terminales=1; JPEG=0/162.
- `H2018P5ESA` (2018, grado 5, UI=standard_x_js): internos=177; terminales=1; JPEG=0/178.
- `H2018P5LEA` (2018, grado 5, UI=standard_x_js): internos=161; terminales=1; JPEG=0/162.
- `H2018P6ESA` (2018, grado 6, UI=standard_x_js): internos=185; terminales=1; JPEG=0/186.
- `H2018P6LEA` (2018, grado 6, UI=standard_x_js): internos=161; terminales=1; JPEG=0/162.

## Regla
Los activos se solicitan mediante el `ag_clave` publicado en `claves.json`. Cada byte servido se recorre sólo para SHA-256; no se persisten JPEG. Un 404 final se conserva como candidato terminal y un 404 interno como anomalía. La interfaz horizontal no altera este contrato de fuente.
