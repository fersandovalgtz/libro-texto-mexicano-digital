# LTMD-U1 W5 — topología reconciliada de procesamiento Historia

Versión de procesamiento: `LTMD_U1_W5_HISTORY_PROCESSING_0.1`.
Versión del manifiesto de páginas: `LTMD_U1_W5_HISTORY_CANONICAL_PAGE_MANIFEST_0.1`.

- Identidades W5 técnicamente cubiertas: **18/18**.
- Objetos canónicos de procesamiento: **15**.
- Aliases operacionales de ruta 2018→2019: **3**.
- Aliases de libro completo byte-exacto entre fuentes directas: **0**.
- Huecos de fuente persistentes después de reconciliación: **0**.
- Páginas fuente canónicas autorizables para OCR: **2,653**.
- Terminales sintéticos de objetos canónicos excluidos del OCR: **15**.
- Renumeración de páginas: **0**.

## Por generación

| generación | identidades | canónicos | aliases de ruta | páginas OCR canónicas |
|---:|---:|---:|---:|---:|
| 1993 | 3 | 3 | 0 | 510 |
| 2008 | 3 | 3 | 0 | 534 |
| 2011 | 3 | 3 | 0 | 563 |
| 2014 | 3 | 3 | 0 | 523 |
| 2018 | 3 | 0 | 3 | 0 |
| 2019 | 3 | 3 | 0 | 523 |

## Contrato downstream

OCR W5 sólo puede consumir `ltmd_u1_w5_history_canonical_page_manifest.csv`. Cada JPEG debe revalidarse en vivo contra SHA-256 y tamaño antes del OCR. Los tres visores 2018 no generan OCR duplicado: heredan cobertura técnica mediante su relación de ruta 2019, conservando sus viewer_key y provenance independientes.

Este contrato autoriza exclusivamente procesamiento técnico OCR/PAGESTRUCT/FRAGSEG. No autoriza inferencias históricas o semánticas ni convierte la etiqueta operacional `historia` en una ontología curricular validada.
