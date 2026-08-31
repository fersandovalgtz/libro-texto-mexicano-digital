# LTMD-U1 W7 — snapshot de presencia de visores retenidos

Versión: `LTMD_U1_W7_WITHHELD_VIEWER_PRESENCE_0.1`.

Observado UTC: `2026-08-31T19:39:23.438705+00:00`.

- Identidades retenidas verificadas: **5/5**.
- `claves.json` HTTP 200, SHA-256: `7fb55e583ee5190fd2153d95764426114f86946ea93d8545c07d5f03d7674037`.
- El probe **no solicita activos JPEG de páginas**.

## Resultado

| visor | decisión fuente | posiciones gate/live | visor HTTP | bytes HTML | título HTML |
|---|---|---:|---:|---:|---|
| `H2014P5FCA` | `withheld_source_gap` | 225/225 | 200 | 4800 | `Formación Cívica y Ética Grado 5° Generación 2014 .: Comisión Nacional de Libros de Texto Gratuitos :.` |
| `H2018P3FCA` | `withheld_source_subtree_unserved` | 114/114 | 200 | 4969 | `Formación Cívica y Ética.. Grado 3° Generación 2018 .: Comisión Nacional de Libros de Texto Gratuitos :.` |
| `H2018P4FCA` | `withheld_source_subtree_unserved` | 130/130 | 200 | 4969 | `Formación Cívica y Ética.. Grado 4° Generación 2018 .: Comisión Nacional de Libros de Texto Gratuitos :.` |
| `H2018P5FCA` | `withheld_source_subtree_unserved` | 226/226 | 200 | 4978 | `Formación Cívica y Ética .. Grado 5° Generación 2018 .: Comisión Nacional de Libros de Texto Gratuitos :.` |
| `H2018P6FCA` | `withheld_source_subtree_unserved` | 210/210 | 200 | 4969 | `Formación Cívica y Ética.. Grado 6° Generación 2018 .: Comisión Nacional de Libros de Texto Gratuitos :.` |

## Interpretación

Las cinco identidades siguen presentes como objetos de configuración y como visores HTML institucionales en este corte. Este resultado **no levanta ninguna retención de fuente**: la admisibilidad OCR depende de los activos de página, y este snapshot deliberadamente no los solicita. Para los cuatro H2018, presencia del visor y ausencia de servicio del subárbol JPEG son hechos compatibles y deben mantenerse separados.
