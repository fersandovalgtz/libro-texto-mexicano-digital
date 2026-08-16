# LTMD-U1 W7 — gate de admisibilidad de fuente para OCR

Versión: `LTMD_U1_W7_SOURCE_ADMISSIBILITY_0.1`.

Este gate separa la integridad del alcance histórico de la disponibilidad técnica de fuente. No elimina visores del corpus W7: decide únicamente cuáles pueden entrar al OCR productivo sin sustitución heurística.

- Visores W7: **30**.
- Admitidos para OCR de fuente: **25/30**.
- Retenidos por evidencia de fuente incompleta/no servida: **5/30**.
- Retenido por hueco interno aislado 2014: **1**.
- Retenidos por subárbol oficial 2018 no servido: **4**.

## Por generación

| generación | visores | admitidos | retenidos |
|---:|---:|---:|---:|
| 2008 | 8 | 8 | 0 |
| 2011 | 6 | 6 | 0 |
| 2014 | 6 | 5 | 1 |
| 2018 | 4 | 0 | 4 |
| 2019 | 6 | 6 | 0 |

## Visores retenidos

| visor | generación | grado | decisión | causa |
|---|---:|---:|---|---|
| `H2014P5FCA` | 2014 | 5 | `withheld_source_gap` | `isolated_internal_unserved` |
| `H2018P3FCA` | 2018 | 3 | `withheld_source_subtree_unserved` | `official_route_sample_3of3_404` |
| `H2018P4FCA` | 2018 | 4 | `withheld_source_subtree_unserved` | `official_route_sample_3of3_404` |
| `H2018P5FCA` | 2018 | 5 | `withheld_source_subtree_unserved` | `official_route_sample_3of3_404` |
| `H2018P6FCA` | 2018 | 6 | `withheld_source_subtree_unserved` | `official_route_sample_3of3_404` |

## Regla de operación

El OCR productivo W7 puede ejecutarse únicamente sobre filas con `ocr_source_admitted=1`. Los cinco visores retenidos conservan su identidad de catálogo y permanecen dentro del alcance científico W7, pero no pueden ser sustituidos por ediciones 2019 ni por otras claves sin evidencia documental/criptográfica independiente.

Este gate autoriza una cohorte técnica parcial; no declara W7 históricamente completo ni convierte ausencia de fuente en ausencia de obra.
