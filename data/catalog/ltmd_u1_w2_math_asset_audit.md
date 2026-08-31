# LTMD-U1 W2 — auditoría de activos de Matemáticas

Versión: `LTMD_U1_W2_MATH_ASSET_AUDIT_0.1`.

- Visores auditados: **64/64**.
- Posiciones declaradas: **13,656**.
- JPEG servidos y hasheados: **13,591**.
- Candidatos terminales sintéticos (404 sólo en posición final): **63**.
- Posiciones internas no servidas: **2**.
- Visores `direct_asset_ready`: **63/64**.

## Por generación

| generación | visores | ready | declaradas | JPEG | internos no servidos |
|---:|---:|---:|---:|---:|---:|
| 1972 | 6 | 6 | 1,350 | 1,344 | 0 |
| 1982 | 4 | 4 | 1,032 | 1,028 | 0 |
| 1988 | 4 | 4 | 1,018 | 1,014 | 0 |
| 1993 | 10 | 10 | 1,724 | 1,714 | 0 |
| 2008 | 6 | 5 | 1,224 | 1,217 | 2 |
| 2011 | 6 | 6 | 1,140 | 1,134 | 0 |
| 2014 | 12 | 12 | 2,760 | 2,748 | 0 |
| 2018 | 8 | 8 | 1,704 | 1,696 | 0 |
| 2019 | 8 | 8 | 1,704 | 1,696 | 0 |

## Visores que requieren resolución adicional
- `H2008P4MA276` (2008, grado 4): internos no servidos=2; terminales=0; JPEG=207/209.

## Regla
Cada posición declarada se prueba empíricamente y los bytes servidos se recorren sólo para SHA-256. Un 404 final se registra como candidato a terminal sintético; un 404 interno permanece como anomalía y requiere resolución/alias. Ningún JPEG se persiste en Git.
