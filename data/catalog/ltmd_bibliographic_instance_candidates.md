# LTMD — candidatos de instancia bibliográfica

Versión: `LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.3`.

- Objetos evaluados: **26**.
- Candidatos técnicos con año: **11**.
- Sin candidato estricto: **15**.
- Tier A, páginas independientes: **0**.
- Tier B, declaración conjunta + página corroborante adicional: **2**.
- Tier C, declaración conjunta en una sola página: **9**.
- Candidatos cuyo año difiere de `catalog_generation`: **6/11**.

0.3 se reconstruye directamente desde `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4`; ya no depende de la tabla de “resolution” 0.1. Las dos recuperaciones OCR estrechas, ahora procedentes de la cadena causal `candidate-support 0.1 → recovery 0.2 → observations 0.4`, elevan la cobertura de **9 a 11** candidatos sin cambiar la regla temporal.

## Candidatos

| objeto | cohorte | ciclo | declaración | año candidato | tier | difiere de cohorte |
|---|---:|---|---|---:|---|---|
| `H2008P1CI250` | 2008 | `2010-2011` | `third_edition:2010` | 2010 | `C_joint_same_page_only` | sí |
| `H2008P2CI257` | 2008 | `2008-2009` | `first_edition:2008` | 2008 | `B_joint_plus_extra_page_corroboration` | no |
| `H2008P6CI286` | 2008 | `2008-2009` | `first_edition:2008` | 2008 | `B_joint_plus_extra_page_corroboration` | no |
| `H2011P1CI294` | 2011 | `2013-2014` | `fourth_edition:2013` | 2013 | `C_joint_same_page_only` | sí |
| `H2011P2CI301` | 2011 | `2013-2014` | `fourth_edition:2013` | 2013 | `C_joint_same_page_only` | sí |
| `H2011P5CI326` | 2011 | `2013-2014` | `third_reprint:2013` | 2013 | `C_joint_same_page_only` | sí |
| `H2014P4FCA` | 2014 | `2017-2018` | `third_reprint:2017` | 2017 | `C_joint_same_page_only` | sí |
| `H2014P5FCA` | 2014 | `2017-2018` | `third_reprint:2017` | 2017 | `C_joint_same_page_only` | sí |
| `H2019P4FCA` | 2019 | `2019-2020` | `fifth_edition:2019` | 2019 | `C_joint_same_page_only` | no |
| `H2019P5FCA` | 2019 | `2019-2020` | `second_edition:2019` | 2019 | `C_joint_same_page_only` | no |
| `H2019P6FCA` | 2019 | `2019-2020` | `second_edition:2019` | 2019 | `C_joint_same_page_only` | no |

## Sin candidato estricto

| objeto | cohorte | estado | ciclo observado |
|---|---:|---|---|
| `H2008P1CI251` | 2008 | `no_candidate_no_school_cycle` | `—` |
| `H2008P2CI258` | 2008 | `no_candidate_no_school_cycle` | `—` |
| `H2008P3CI264` | 2008 | `no_candidate_no_school_cycle` | `—` |
| `H2008P4CI269` | 2008 | `no_candidate_no_school_cycle` | `—` |
| `H2008P5CI278` | 2008 | `no_candidate_no_statement_matches_cycle_start` | `2008-2009` |
| `H2011P3CI308` | 2011 | `no_candidate_no_school_cycle` | `—` |
| `H2011P4CI315` | 2011 | `no_candidate_no_statement_matches_cycle_start` | `2013-2014` |
| `H2011P6CI336` | 2011 | `no_candidate_no_statement_matches_cycle_start` | `2013-2014` |
| `H2014P1FCA` | 2014 | `no_candidate_no_school_cycle` | `—` |
| `H2014P2FCA` | 2014 | `no_candidate_no_school_cycle` | `—` |
| `H2014P3FCA` | 2014 | `no_candidate_no_school_cycle` | `—` |
| `H2014P6FCA` | 2014 | `no_candidate_no_school_cycle` | `—` |
| `H2019P1FCA` | 2019 | `no_candidate_no_school_cycle` | `—` |
| `H2019P2FCA` | 2019 | `no_candidate_no_school_cycle` | `—` |
| `H2019P3FCA` | 2019 | `no_candidate_no_school_cycle` | `—` |

## Interpretación

Estos años son **candidatos técnicos de cronología de ejemplar**, no fechas humanas validadas. Tier B incluye una página adicional que corrobora parte de la declaración temporal; Tier C no. Actualmente no existe ningún Tier A con declaración editorial y ciclo respaldados por páginas completamente independientes.

Los 15 objetos sin candidato permanecen sin año efectivo. En particular, tres tienen ciclo escolar pero ninguna declaración editorial/reimpresión compatible aun después de la recuperación OCR estrecha; doce carecen de ciclo escolar fuerte en la ventana bibliográfica auditada.
