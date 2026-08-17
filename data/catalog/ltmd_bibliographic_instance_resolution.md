# LTMD — resolución estricta de instancia bibliográfica

Versión: `LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1`.

- Objetos evaluados: **26**.
- Objetos resueltos por coincidencia exacta declaración↔inicio de ciclo: **9**.
- Objetos no resueltos/ambiguos: **17**.

Regla 0.1: una declaración explícita de edición/reimpresión y un `school_cycle` del mismo objeto deben coincidir exactamente en el año inicial del ciclo. `catalog_generation` no participa. La regla no selecciona el año máximo ni el ordinal máximo.

## Estados

- `resolved_cycle_start_exact_match`: **9**.
- `unresolved_no_school_cycle`: **12**.
- `unresolved_no_statement_matches_cycle_start`: **5**.

## Objetos resueltos

| objeto | cohorte catálogo | ciclo | declaración resuelta | año efectivo | evidencia |
|---|---:|---|---|---:|---|
| `H2008P1CI250` | 2008 | `2010-2011` | `third_edition:2010` | 2010 | pág. `2` |
| `H2008P2CI257` | 2008 | `2008-2009` | `first_edition:2008` | 2008 | pág. `2;6` |
| `H2008P6CI286` | 2008 | `2008-2009` | `first_edition:2008` | 2008 | pág. `2;6` |
| `H2011P1CI294` | 2011 | `2013-2014` | `fourth_edition:2013` | 2013 | pág. `2` |
| `H2011P2CI301` | 2011 | `2013-2014` | `fourth_edition:2013` | 2013 | pág. `2` |
| `H2014P5FCA` | 2014 | `2017-2018` | `third_reprint:2017` | 2017 | pág. `4` |
| `H2019P4FCA` | 2019 | `2019-2020` | `fifth_edition:2019` | 2019 | pág. `2` |
| `H2019P5FCA` | 2019 | `2019-2020` | `second_edition:2019` | 2019 | pág. `4` |
| `H2019P6FCA` | 2019 | `2019-2020` | `second_edition:2019` | 2019 | pág. `4` |

## No resueltos

| objeto | cohorte | estado | ciclo observado |
|---|---:|---|---|
| `H2008P1CI251` | 2008 | `unresolved_no_school_cycle` | `—` |
| `H2008P2CI258` | 2008 | `unresolved_no_school_cycle` | `—` |
| `H2008P3CI264` | 2008 | `unresolved_no_school_cycle` | `—` |
| `H2008P4CI269` | 2008 | `unresolved_no_school_cycle` | `—` |
| `H2008P5CI278` | 2008 | `unresolved_no_statement_matches_cycle_start` | `2008-2009` |
| `H2011P3CI308` | 2011 | `unresolved_no_school_cycle` | `—` |
| `H2011P4CI315` | 2011 | `unresolved_no_statement_matches_cycle_start` | `2013-2014` |
| `H2011P5CI326` | 2011 | `unresolved_no_statement_matches_cycle_start` | `2013-2014` |
| `H2011P6CI336` | 2011 | `unresolved_no_statement_matches_cycle_start` | `2013-2014` |
| `H2014P1FCA` | 2014 | `unresolved_no_school_cycle` | `—` |
| `H2014P2FCA` | 2014 | `unresolved_no_school_cycle` | `—` |
| `H2014P3FCA` | 2014 | `unresolved_no_school_cycle` | `—` |
| `H2014P4FCA` | 2014 | `unresolved_no_statement_matches_cycle_start` | `2017-2018` |
| `H2014P6FCA` | 2014 | `unresolved_no_school_cycle` | `—` |
| `H2019P1FCA` | 2019 | `unresolved_no_school_cycle` | `—` |
| `H2019P2FCA` | 2019 | `unresolved_no_school_cycle` | `—` |
| `H2019P3FCA` | 2019 | `unresolved_no_school_cycle` | `—` |

## Límite epistemológico

Una resolución 0.1 significa que dos declaraciones bibliográficas independientes dentro de la capa observacional convergen temporalmente. No demuestra por sí sola circulación nacional en ese ciclo ni reemplaza validación humana de la transcripción OCR. Los objetos no resueltos permanecen explícitamente sin año efectivo; no se imputan desde la cohorte de catálogo.
