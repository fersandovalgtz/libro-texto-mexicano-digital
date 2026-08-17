# LTMD-U1 W7 — auditoría de soporte de candidatos bibliográficos

Versión: `LTMD_U1_W7_BIBLIOGRAPHIC_CANDIDATE_SUPPORT_0.1`.

- Filas fingerprint fuente verificadas: **300/300**.
- Candidatos estructurados auditados: **107**.
- Candidatos con soporte fuerte multímodo: **91**.
- Visores con ≥1 candidato fuerte: **25/25**.
- ISBN rechazados por checksum ISBN-13: **3**.

Regla 0.1: edición, reimpresión y ciclo escolar requieren el mismo candidato en ≥2 modos PSM sobre la misma página SHA-verificada. ISBN requiere además checksum ISBN-13 válido. La regla identifica **observaciones textuales reproducibles**, no decide cuál edición es la “actual” del objeto.

## Clases de soporte

- `cross_line_or_unretained_only`: **3**.
- `invalid_isbn13_checksum`: **3**.
- `single_psm`: **10**.
- `strong_multipsm`: **91**.

## Candidatos fuertes por objeto

| objeto | edición | reimpresión | ciclo | ISBN válido |
|---|---|---|---|---|
| `H2008P1CI250` | `first_edition:2008, third_edition:2010` | `—` | `2010-2011` | `978-607-469-230-3` |
| `H2008P1CI251` | `first_edition:2008, second_edition:2009` | `—` | `—` | `978-607-469-108-5` |
| `H2008P2CI257` | `first_edition:2008` | `—` | `2008-2009` | `—` |
| `H2008P2CI258` | `first_edition:2008, second_edition:2009` | `—` | `—` | `978-607-469-110-8` |
| `H2008P3CI264` | `first_edition:2008, second_edition:2009` | `—` | `—` | `—` |
| `H2008P4CI269` | `first_edition:2008, second_edition:2009` | `—` | `—` | `978-607-469-112-2` |
| `H2008P5CI278` | `—` | `—` | `2008-2009` | `—` |
| `H2008P6CI286` | `first_edition:2008` | `—` | `2008-2009` | `978-968-011-738-3` |
| `H2011P1CI294` | `first_edition:2008, fourth_edition:2013` | `—` | `2013-2014` | `978-607-514-328-6` |
| `H2011P2CI301` | `fourth_edition:2013` | `—` | `2013-2014` | `—` |
| `H2011P3CI308` | `first_edition:2008, third_edition:2010` | `—` | `—` | `—` |
| `H2011P4CI315` | `first_edition:2008, third_edition:2010` | `—` | `2013-2014` | `—` |
| `H2011P5CI326` | `first_edition:2008, third_edition:2010` | `—` | `2013-2014` | `—` |
| `H2011P6CI336` | `first_edition:2008, third_edition:2010` | `—` | `2013-2014` | `—` |
| `H2014P1FCA` | `fifth_edition:2014, first_edition:2008, fourth_edition:2013, second_edition:2009, third_edition:2010` | `—` | `—` | `—` |
| `H2014P2FCA` | `fifth_edition:2014, first_edition:2008, fourth_edition:2013, second_edition:2009, third_edition:2010` | `—` | `—` | `—` |
| `H2014P3FCA` | `first_edition:2008, fourth_edition:2014, second_edition:2009, third_edition:2010` | `third_reprint:2017` | `—` | `—` |
| `H2014P4FCA` | `first_edition:2008, fourth_edition:2014, second_edition:2009, third_edition:2010` | `—` | `2017-2018` | `—` |
| `H2014P6FCA` | `first_edition:2014, first_edition:2018` | `third_reprint:2017` | `—` | `—` |
| `H2019P1FCA` | `fifth_edition:2014, first_edition:2008, fourth_edition:2013, sixth_edition:2019` | `—` | `—` | `—` |
| `H2019P2FCA` | `fifth_edition:2014, first_edition:2008, fourth_edition:2013, second_edition:2009, sixth_edition:2019` | `—` | `—` | `978-607-551-234-1` |
| `H2019P3FCA` | `fifth_edition:2019, first_edition:2008, fourth_edition:2014, second_edition:2009, third_edition:2010` | `—` | `—` | `—` |
| `H2019P4FCA` | `fifth_edition:2019, first_edition:2008, fourth_edition:2014, second_edition:2009, third_edition:2010` | `—` | `2019-2020` | `978-607-551-155-9` |
| `H2019P5FCA` | `first_edition:2014, second_edition:2019` | `—` | `2019-2020` | `—` |
| `H2019P6FCA` | `first_edition:2014, second_edition:2019` | `—` | `2019-2020` | `—` |

## ISBN rechazados

| objeto | página | candidato OCR | soporte PSM |
|---|---:|---|---|
| `H2011P2CI301` | 2 | `978-507-514-927-9` | `` |
| `H2011P6CI336` | 2 | `978-607-460-405-5` | `3;4;11;12` |
| `H2014P6FCA` | 4 | `978-607-514-208-3` | `3;4;11;12` |

## Límite epistemológico

Un candidato `strong_multipsm` demuestra que varios modos de segmentación OCR leen de forma concordante la misma declaración estructurada en una página institucional cuya huella binaria está congelada. No demuestra por sí solo que esa declaración sea la edición vigente del objeto ni reemplaza una futura validación humana de la transcripción. La promoción a observaciones canónicas debe conservar página, SHA y clase de soporte.
