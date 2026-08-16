# LTMD-U1 W4 — topología reconciliada de procesamiento Ciencias Sociales

Versión de procesamiento: `LTMD_U1_W4_SOCIAL_SCIENCES_PROCESSING_0.1`.
Versión del manifiesto de páginas: `LTMD_U1_W4_SOCIAL_SCIENCES_CANONICAL_PAGE_MANIFEST_0.1`.

- Identidades W4: **14/14**.
- Identidades OCR-eligible: **14/14**.
- Objetos canónicos independientes a nivel de activos: **14**.
- Aliases de libro completo byte-exacto: **0**.
- Huecos internos persistentes: **0**.
- Páginas fuente canónicas autorizadas para OCR: **2,414**.
- Terminales sintéticos excluidos del OCR: **14**.
- Renumeración de páginas: **0**.

## Por generación

| generación | canónicos | páginas OCR | terminales sintéticos |
|---:|---:|---:|---:|
| 1972 | 6 | 1,054 | 6 |
| 1982 | 3 | 560 | 3 |
| 1988 | 4 | 630 | 4 |
| 2008 | 1 | 170 | 1 |

## Contrato downstream

OCR W4 sólo puede consumir `ltmd_u1_w4_social_sciences_canonical_page_manifest.csv`. Cada JPEG debe revalidarse en vivo contra SHA-256 y tamaño. Los 14 terminales sintéticos no se procesan ni se convierten en páginas. La inexistencia de aliases de libro completo no impide que existan páginas o fragmentos reutilizados parcialmente entre documentos; esas dependencias se medirán por separado.

Este contrato autoriza procesamiento técnico OCR/PAGESTRUCT/FRAGSEG. No autoriza inferencias semánticas históricas ni convierte la etiqueta operacional `ciencias_sociales` en una categoría curricular validada.
