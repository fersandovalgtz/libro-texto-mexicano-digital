# LTMD-U1 W7 — topología reconciliada de procesamiento Cívica/Ética

Versión de procesamiento: `LTMD_U1_W7_PROCESSING_0.1`.
Versión del manifiesto de páginas: `LTMD_U1_W7_CANONICAL_PAGE_MANIFEST_0.1`.

- Identidades históricas W7 preservadas: **30/30**.
- Identidades OCR elegibles: **25/30**.
- Objetos canónicos independientes a nivel de activos: **25**.
- Aliases de libro completo byte-exacto entre admitidos: **0**.
- Identidades retenidas por fuente: **5**.
- Páginas fuente canónicas autorizadas para OCR: **3,261**.
- Terminales sintéticos excluidos del OCR: **25**.
- Renumeración de páginas: **0**.

## Por generación

| generación | identidades | canónicos OCR | retenidos | páginas OCR |
|---:|---:|---:|---:|---:|
| 2008 | 8 | 8 | 0 | 692 |
| 2011 | 6 | 6 | 0 | 814 |
| 2014 | 6 | 5 | 1 | 765 |
| 2018 | 4 | 0 | 4 | 0 |
| 2019 | 6 | 6 | 0 | 990 |

## Contrato downstream

El OCR W7 sólo puede consumir `ltmd_u1_w7_canonical_page_manifest.csv` y únicamente visores marcados `ocr_identity_eligible=1` en `ltmd_u1_w7_processing_inventory.csv`. Cada JPEG debe descargarse temporalmente y revalidarse contra tamaño y SHA-256 antes del OCR; no se persisten imágenes fuente.

Los cinco visores retenidos siguen siendo identidades históricas del alcance W7. Su ausencia del manifiesto OCR expresa una restricción de fuente, no una inferencia de inexistencia documental ni equivalencia con otra edición.
