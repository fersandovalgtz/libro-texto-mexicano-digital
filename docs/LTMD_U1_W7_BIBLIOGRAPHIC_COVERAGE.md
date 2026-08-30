# LTMD-U1 W7 — cobertura bibliográfica y readiness

Versión: `LTMD_U1_W7_BIBLIOGRAPHIC_COVERAGE_0.2`.

- Universo histórico preservado: **30/30 identidades**.
- Fuente admitida: **25/30**; retenida: **5/30**.
- Objetos en capa de observaciones: **26**.
- Candidatos técnicos de instancia: **11** en total; **10** sobre fuente admitida y **1** (`H2014P5FCA`) sobre objeto parcialmente retenido.
- `human_validated=0` para toda la capa bibliográfica técnica actual.

La matriz separa dos ejes de completitud: **fuente** y **cronología bibliográfica**. Un objeto puede tener fuente admitida y carecer de ciclo/fecha candidata; también puede, como `H2014P5FCA`, poseer evidencia bibliográfica fuerte pero permanecer retenido del OCR productivo por un hueco de fuente.

## Readiness global

- `bibliographic_observations_no_cycle`: **12**.
- `cycle_observed_no_instance_candidate`: **3**.
- `source_withheld_partial_gap`: **1**.
- `source_withheld_subtree_unserved`: **4**.
- `technical_instance_candidate_available`: **10**.

## Búsqueda bibliográfica externa acotada — 2026-08-30

La versión 0.2 incorpora una pasada documental externa reproducible sobre los **15 objetos** que motivaron la issue #6: los 12 con fuente admitida y observaciones bibliográficas pero sin ciclo fuerte, más los 3 con ciclo observado y sin candidato de instancia.

Artefacto: `data/catalog/ltmd_u1_w7_external_bibliographic_search_2026-08-30.csv`.

Método acotado:

1. abrir el viewer institucional exacto de CONALITEG para cada `viewer_key` y corroborar únicamente identidad del viewer, título, grado y `catalog_generation`;
2. buscar registros por título/grado en fuentes institucionales o académicas de mayor autoridad disponibles públicamente —SEP, Biblioteca Gregorio Torres Quintero/UPN y SIIA-Humanindex/UNAM— y conservar también hallazgos secundarios sólo como pistas;
3. clasificar como evidencia de manifestación exacta únicamente aquello que enlace inequívocamente el registro al viewer; título, grado, ISBN de familia o coincidencia de generación no bastan;
4. detener la búsqueda cuando el conjunto acotado de fuentes queda agotado; no ampliar OCR ni seleccionar una fecha por conveniencia.

Resultado:

- identidad institucional exacta del viewer corroborada: **15/15**;
- nuevos candidatos técnicos de instancia promovidos: **0**;
- cambios a `school_cycle_statement`: **0**;
- cambios a `catalog_generation`: **0**;
- objetos clasificados al cierre de esta búsqueda como `documented_no_resolution`: **15/15**.

La búsqueda produjo evidencia bibliográfica externa útil a nivel de familia —por ejemplo, registros institucionales que documentan ciclos 2008-2009, 2014-2015 o 2019-2020 para algunas combinaciones título/grado—, pero no encontró un enlace de manifestación suficientemente fuerte para asignar esos ciclos a los viewers pendientes. En varios casos aparecieron además múltiples manifestaciones posibles, lo que refuerza la prohibición de seleccionar automáticamente una edición.

Para `H2011P4CI315` y `H2011P6CI336` se conserva sin alteración la tensión ya documentada: ciclo observado `2013-2014` frente a página legal con `reimpresión 2012`. La búsqueda externa no produjo una nueva página primaria enlazada al viewer con página + SHA que permita crear un candidato compatible. Para `H2008P5CI278` tampoco apareció una nueva declaración primaria enlazada al viewer; su ciclo observado `2008-2009` permanece sin candidato técnico de instancia.

Este resultado **cierra la deuda de búsqueda externa acotada**, no la incertidumbre histórica. Los 15 casos pueden quedar cerrados administrativamente bajo la clase permitida por la issue #6 `ausencia/no resolución documentada`, manteniendo abierta únicamente una futura validación humana/documental si aparece nueva evidencia primaria. No se reabre OCR por defecto.

## Cobertura por generación de catálogo

| generación | identidades | fuente admitida | con ciclo | con candidato | candidatos ≠ cohorte | retenidas |
|---:|---:|---:|---:|---:|---:|---:|
| 2008 | 8 | 8 | 4 | 3 | 1 | 0 |
| 2011 | 6 | 6 | 5 | 3 | 3 | 0 |
| 2014 | 6 | 5 | 2 | 2 | 2 | 1 |
| 2018 | 4 | 0 | 0 | 0 | 0 | 4 |
| 2019 | 6 | 6 | 3 | 3 | 0 | 0 |

## Objeto por objeto

| objeto | cohorte | grado | fuente | observaciones | ciclo | candidato | tier | readiness |
|---|---:|---:|---|---:|---|---:|---|---|
| `H2008P1CI250` | 2008 | 1 | `admitida` | 4 | `2010-2011` | 2010 | `C_joint_same_page_only` | `technical_instance_candidate_available` |
| `H2008P1CI251` | 2008 | 1 | `admitida` | 3 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2008P2CI257` | 2008 | 2 | `admitida` | 2 | `2008-2009` | 2008 | `B_joint_plus_extra_page_corroboration` | `technical_instance_candidate_available` |
| `H2008P2CI258` | 2008 | 2 | `admitida` | 3 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2008P3CI264` | 2008 | 3 | `admitida` | 2 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2008P4CI269` | 2008 | 4 | `admitida` | 3 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2008P5CI278` | 2008 | 5 | `admitida` | 1 | `2008-2009` | — | `—` | `cycle_observed_no_instance_candidate` |
| `H2008P6CI286` | 2008 | 6 | `admitida` | 3 | `2008-2009` | 2008 | `B_joint_plus_extra_page_corroboration` | `technical_instance_candidate_available` |
| `H2011P1CI294` | 2011 | 1 | `admitida` | 4 | `2013-2014` | 2013 | `C_joint_same_page_only` | `technical_instance_candidate_available` |
| `H2011P2CI301` | 2011 | 2 | `admitida` | 2 | `2013-2014` | 2013 | `C_joint_same_page_only` | `technical_instance_candidate_available` |
| `H2011P3CI308` | 2011 | 3 | `admitida` | 2 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2011P4CI315` | 2011 | 4 | `admitida` | 3 | `2013-2014` | — | `—` | `cycle_observed_no_instance_candidate` |
| `H2011P5CI326` | 2011 | 5 | `admitida` | 4 | `2013-2014` | 2013 | `C_joint_same_page_only` | `technical_instance_candidate_available` |
| `H2011P6CI336` | 2011 | 6 | `admitida` | 3 | `2013-2014` | — | `—` | `cycle_observed_no_instance_candidate` |
| `H2014P1FCA` | 2014 | 1 | `admitida` | 5 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2014P2FCA` | 2014 | 2 | `admitida` | 5 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2014P3FCA` | 2014 | 3 | `admitida` | 5 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2014P4FCA` | 2014 | 4 | `admitida` | 6 | `2017-2018` | 2017 | `C_joint_same_page_only` | `technical_instance_candidate_available` |
| `H2014P5FCA` | 2014 | 5 | `retenida` | 4 | `2017-2018` | 2017 | `C_joint_same_page_only` | `source_withheld_partial_gap` |
| `H2014P6FCA` | 2014 | 6 | `admitida` | 3 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2018P3FCA` | 2018 | 3 | `retenida` | 0 | `—` | — | `—` | `source_withheld_subtree_unserved` |
| `H2018P4FCA` | 2018 | 4 | `retenida` | 0 | `—` | — | `—` | `source_withheld_subtree_unserved` |
| `H2018P5FCA` | 2018 | 5 | `retenida` | 0 | `—` | — | `—` | `source_withheld_subtree_unserved` |
| `H2018P6FCA` | 2018 | 6 | `retenida` | 0 | `—` | — | `—` | `source_withheld_subtree_unserved` |
| `H2019P1FCA` | 2019 | 1 | `admitida` | 4 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2019P2FCA` | 2019 | 2 | `admitida` | 6 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2019P3FCA` | 2019 | 3 | `admitida` | 5 | `—` | — | `—` | `bibliographic_observations_no_cycle` |
| `H2019P4FCA` | 2019 | 4 | `admitida` | 7 | `2019-2020` | 2019 | `C_joint_same_page_only` | `technical_instance_candidate_available` |
| `H2019P5FCA` | 2019 | 5 | `admitida` | 3 | `2019-2020` | 2019 | `C_joint_same_page_only` | `technical_instance_candidate_available` |
| `H2019P6FCA` | 2019 | 6 | `admitida` | 3 | `2019-2020` | 2019 | `C_joint_same_page_only` | `technical_instance_candidate_available` |

## Límite epistemológico

Readiness no es calidad ni validez histórica. `technical_instance_candidate_available` significa únicamente que el objeto cumple la regla técnica vigente de candidato. No transforma Tier B/C en validación humana ni convierte `catalog_generation` en año editorial. Las cinco retenciones de fuente continúan gobernadas por su gate independiente.

La capa de búsqueda externa 2026-08-30 tampoco transforma un registro de catálogo de familia en evidencia de manifestación. `documented_no_resolution` significa que una búsqueda acotada y reproducible terminó sin evidencia suficiente para promover el objeto; no equivale a demostrar ausencia histórica ni autoriza imputación.