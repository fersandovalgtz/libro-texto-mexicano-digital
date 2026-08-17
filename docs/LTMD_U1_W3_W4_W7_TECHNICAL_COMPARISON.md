# LTMD-U1 — comparación técnica W3 ↔ W4 ↔ W7

Versión: `LTMD_U1_W3_W4_W7_TECHNICAL_COMPARISON_0.2`.

Comparación **estrictamente técnica y descriptiva** entre productos cerrados de PAGESTRUCT, FRAGSEG y reutilización textual exacta. Las tres cohortes tienen dominios, inventarios y coberturas históricas diferentes. Los porcentajes sirven para caracterizar las representaciones computacionales y formular hipótesis posteriores; **no demuestran diferencias curriculares, pedagógicas ni efectos de reformas**.

W7 representa sólo su cohorte fuente-admisible (25 objetos) y mantiene cinco identidades históricas retenidas. W3 incluye 16 aliases explícitos de provenance proyectados sobre 114 canónicos; para W3, las métricas entre generaciones incorporan esa proyección tal como la definió su cierre técnico.

## Escala

| métrica | W3 Español/Lengua | W4 Ciencias Sociales | W7 Cívica/Ética |
|---|---:|---:|---:|
| objetos canónicos procesados | 114 | 14 | 25 |
| identidades retenidas por fuente | 0 | 0 | 5 |
| páginas | 20,765 | 2,414 | 3,261 |
| páginas elegibles | 17,337 (83.49%) | 2,018 (83.60%) | 2,745 (84.18%) |
| fragmentos | 222,490 | 21,380 | 33,451 |
| fragmentos / página elegible | 12.833 | 10.595 | 12.186 |

## PAGESTRUCT

| clase | W3 Español/Lengua | W4 Ciencias Sociales | W7 Cívica/Ética |
|---|---:|---:|---:|
| `textual` | 8,309 (40.01%) | 1,417 (58.70%) | 1,536 (47.10%) |
| `mixed_text_image` | 9,028 (43.48%) | 601 (24.90%) | 1,209 (37.07%) |
| `visual_only` | 1,498 (7.21%) | 179 (7.42%) | 145 (4.45%) |
| `front_matter` | 34 (0.16%) | 1 (0.04%) | 4 (0.12%) |
| `toc_or_navigation` | 409 (1.97%) | 33 (1.37%) | 153 (4.69%) |
| `bibliography_or_credits` | 411 (1.98%) | 34 (1.41%) | 105 (3.22%) |
| `unknown` | 1,076 (5.18%) | 149 (6.17%) | 109 (3.34%) |

## FRAGSEG — tipos candidatos técnicos

| tipo | W3 Español/Lengua | W4 Ciencias Sociales | W7 Cívica/Ética |
|---|---:|---:|---:|
| `activity_candidate` | 4,205 (1.89%) | 136 (0.64%) | 903 (2.70%) |
| `assessment_candidate` | 605 (0.27%) | 5 (0.02%) | 283 (0.85%) |
| `experiment_candidate` | 795 (0.36%) | 69 (0.32%) | 155 (0.46%) |
| `expository_candidate` | 31,149 (14.00%) | 5,450 (25.49%) | 5,455 (16.31%) |
| `instruction_candidate` | 30,694 (13.80%) | 3,145 (14.71%) | 5,185 (15.50%) |
| `project_candidate` | 1,354 (0.61%) | 9 (0.04%) | 141 (0.42%) |
| `question_candidate` | 26,322 (11.83%) | 1,707 (7.98%) | 3,870 (11.57%) |
| `short_residual_candidate` | 127,366 (57.25%) | 10,859 (50.79%) | 17,459 (52.19%) |

## Reutilización textual exacta

| métrica | W3 Español/Lengua | W4 Ciencias Sociales | W7 Cívica/Ética |
|---|---:|---:|---:|
| unidades exactas únicas | 147,375 | 17,735 | 22,651 |
| unidades repetidas | 40,956 (27.79%) | 2,503 (14.11%) | 5,449 (24.06%) |
| unidades en ≥2 visores | 40,118 (27.22%) | 2,454 (13.84%) | 5,313 (23.46%) |
| unidades en ≥2 generaciones | 50,144 (34.02%) | 2,431 (13.71%) | 5,115 (22.58%) |
| pares de visores con reuso exacto | 6,387 | 85 | 300 |

### Nota de schema W3

W3 usa `canonical_occurrence_count`, `canonical_viewer_count` y `represented_catalog_generation_count`; W4/W7 usan el schema posterior `occurrence_count`, `viewer_count` y `catalog_generation_count`. La normalización de W3 es explícita en el script y conserva la semántica de su proyección de aliases. No se renombran columnas de origen ni se reescriben sus productos cerrados.

## Uso permitido

Este producto permite auditar escala, densidad de segmentación, distribución estructural y dependencia textual dentro del pipeline común. Las diferencias observadas pueden motivar preguntas de investigación, pero cualquier interpretación histórica o curricular requiere modelar bibliografía/temporalidad, composición de la cohorte y validación humana por separado.

## Uso no permitido

No se debe interpretar una tasa mayor o menor como evidencia directa de calidad educativa, complejidad pedagógica, efecto de una reforma, continuidad curricular o cambio histórico. Tampoco se deben comparar las generaciones de catálogo como si fueran automáticamente años editoriales.
