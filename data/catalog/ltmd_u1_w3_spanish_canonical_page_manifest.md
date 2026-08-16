# LTMD-U1 W3 — manifiesto canónico de páginas Español/Lengua

Versión: `LTMD_U1_W3_SPANISH_CANONICAL_PAGE_MANIFEST_0.1`.

- Identidades institucionales cubiertas operacionalmente: **130/130**.
- Objetos canónicos únicos: **114**.
- Páginas fuente canónicas autorizadas para OCR: **20,765**.
- Huecos internos persistentes preservados fuera del manifiesto OCR: **8**.
- Aliases excluidos del cómputo duplicado: **16**.
- Filas no `source_jpeg` en el manifiesto OCR: **0**.
- Renumeración de páginas: **0**.

## Por generación

| generación | canónicos | páginas OCR | huecos persistentes |
|---:|---:|---:|---:|
| 1960 | 3 | 476 | 0 |
| 1966 | 8 | 1,534 | 0 |
| 1972 | 16 | 3,242 | 0 |
| 1982 | 3 | 470 | 0 |
| 1988 | 8 | 1,464 | 0 |
| 1993 | 21 | 3,734 | 1 |
| 2008 | 9 | 1,648 | 5 |
| 2011 | 12 | 2,004 | 1 |
| 2014 | 14 | 2,709 | 1 |
| 2018 | 6 | 1,078 | 0 |
| 2019 | 14 | 2,406 | 0 |

## Contrato downstream
OCR sólo puede consumir `ltmd_u1_w3_spanish_canonical_page_manifest.csv`. Cada fila debe revalidarse en vivo contra `sha256` y `byte_size` antes de reconocimiento. Los 16 aliases heredan productos del canónico mediante provenance; los ocho huecos persistentes quedan explícitos en `ltmd_u1_w3_spanish_canonical_gap_manifest.csv` y nunca se rellenan ni renumeran.
