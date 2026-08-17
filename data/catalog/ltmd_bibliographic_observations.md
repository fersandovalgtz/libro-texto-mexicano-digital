# LTMD — observaciones bibliográficas reproducibles

Versión: `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.2`.

- Observaciones semánticas materializadas: **93**.
- Objetos con ≥1 observación: **26**.
- Filas de evidencia página/SHA: **95**.
- W7 admitidos cubiertos por observaciones fuertes: **25/25**.
- `H2014P5FCA` se conserva mediante la regla primaria específica de 0.1 pese a estar retenido del OCR productivo por su hueco de fuente.

## Semántica

`edition_history_statement` y `reprint_history_statement` significan **declaraciones bibliográficas observadas en el objeto**, no una selección automática de la edición/reimpresión que deba usarse como fecha canónica del visor. `school_cycle_statement` e `isbn_statement` conservan la misma lógica de observación. La resolución a campos de libro como `edition_year` requiere una regla posterior explícita.

## Conteo por campo

- `edition_history_statement`: **66**.
- `first_edition_year`: **1**.
- `isbn_statement`: **8**.
- `reprint_history_statement`: **2**.
- `reprint_statement`: **1**.
- `reprint_year`: **1**.
- `school_cycle`: **1**.
- `school_cycle_statement`: **13**.

## Observaciones

| objeto | cohorte | campo | valor | página primaria | soporte | evidencias |
|---|---:|---|---|---:|---|---:|
| `H2014P5FCA` | 2014 | `first_edition_year` | `2014` | 4 | `strong_custom_ensemble_rule` | 1 |
| `H2014P5FCA` | 2014 | `reprint_statement` | `third_reprint` | 4 | `strong_custom_ensemble_rule` | 1 |
| `H2014P5FCA` | 2014 | `reprint_year` | `2017` | 4 | `strong_custom_ensemble_rule` | 1 |
| `H2014P5FCA` | 2014 | `school_cycle` | `2017-2018` | 4 | `strong_custom_ensemble_rule` | 1 |
| `H2008P1CI250` | 2008 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2008P1CI250` | 2008 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2008P1CI250` | 2008 | `isbn_statement` | `978-607-469-230-3` | 2 | `strong_multipsm` | 1 |
| `H2008P1CI250` | 2008 | `school_cycle_statement` | `2010-2011` | 2 | `strong_multipsm` | 1 |
| `H2008P1CI251` | 2008 | `edition_history_statement` | `first_edition:2008` | 4 | `strong_multipsm` | 1 |
| `H2008P1CI251` | 2008 | `edition_history_statement` | `second_edition:2009` | 4 | `strong_multipsm` | 1 |
| `H2008P1CI251` | 2008 | `isbn_statement` | `978-607-469-108-5` | 4 | `strong_multipsm` | 1 |
| `H2008P2CI257` | 2008 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2008P2CI257` | 2008 | `school_cycle_statement` | `2008-2009` | 6 | `strong_multipsm` | 2 |
| `H2008P2CI258` | 2008 | `edition_history_statement` | `first_edition:2008` | 4 | `strong_multipsm` | 1 |
| `H2008P2CI258` | 2008 | `edition_history_statement` | `second_edition:2009` | 4 | `strong_multipsm` | 1 |
| `H2008P2CI258` | 2008 | `isbn_statement` | `978-607-469-110-8` | 4 | `strong_multipsm` | 1 |
| `H2008P3CI264` | 2008 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2008P3CI264` | 2008 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2008P4CI269` | 2008 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2008P4CI269` | 2008 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2008P4CI269` | 2008 | `isbn_statement` | `978-607-469-112-2` | 2 | `strong_multipsm` | 1 |
| `H2008P5CI278` | 2008 | `school_cycle_statement` | `2008-2009` | 2 | `strong_multipsm` | 1 |
| `H2008P6CI286` | 2008 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2008P6CI286` | 2008 | `isbn_statement` | `978-968-011-738-3` | 2 | `strong_multipsm` | 1 |
| `H2008P6CI286` | 2008 | `school_cycle_statement` | `2008-2009` | 6 | `strong_multipsm` | 2 |
| `H2011P1CI294` | 2011 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2011P1CI294` | 2011 | `edition_history_statement` | `fourth_edition:2013` | 2 | `strong_multipsm` | 1 |
| `H2011P1CI294` | 2011 | `isbn_statement` | `978-607-514-328-6` | 2 | `strong_multipsm` | 1 |
| `H2011P1CI294` | 2011 | `school_cycle_statement` | `2013-2014` | 2 | `strong_multipsm` | 1 |
| `H2011P2CI301` | 2011 | `edition_history_statement` | `fourth_edition:2013` | 2 | `strong_multipsm` | 1 |
| `H2011P2CI301` | 2011 | `school_cycle_statement` | `2013-2014` | 2 | `strong_multipsm` | 1 |
| `H2011P3CI308` | 2011 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2011P3CI308` | 2011 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2011P4CI315` | 2011 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2011P4CI315` | 2011 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2011P4CI315` | 2011 | `school_cycle_statement` | `2013-2014` | 2 | `strong_multipsm` | 1 |
| `H2011P5CI326` | 2011 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2011P5CI326` | 2011 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2011P5CI326` | 2011 | `school_cycle_statement` | `2013-2014` | 2 | `strong_multipsm` | 1 |
| `H2011P6CI336` | 2011 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2011P6CI336` | 2011 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2011P6CI336` | 2011 | `school_cycle_statement` | `2013-2014` | 2 | `strong_multipsm` | 1 |
| `H2014P1FCA` | 2014 | `edition_history_statement` | `fifth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2014P1FCA` | 2014 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2014P1FCA` | 2014 | `edition_history_statement` | `fourth_edition:2013` | 2 | `strong_multipsm` | 1 |
| `H2014P1FCA` | 2014 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2014P1FCA` | 2014 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2014P2FCA` | 2014 | `edition_history_statement` | `fifth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2014P2FCA` | 2014 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2014P2FCA` | 2014 | `edition_history_statement` | `fourth_edition:2013` | 2 | `strong_multipsm` | 1 |
| `H2014P2FCA` | 2014 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2014P2FCA` | 2014 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2014P3FCA` | 2014 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2014P3FCA` | 2014 | `edition_history_statement` | `fourth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2014P3FCA` | 2014 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2014P3FCA` | 2014 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2014P3FCA` | 2014 | `reprint_history_statement` | `third_reprint:2017` | 2 | `strong_multipsm` | 1 |
| `H2014P4FCA` | 2014 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2014P4FCA` | 2014 | `edition_history_statement` | `fourth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2014P4FCA` | 2014 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2014P4FCA` | 2014 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2014P4FCA` | 2014 | `school_cycle_statement` | `2017-2018` | 2 | `strong_multipsm` | 1 |
| `H2014P6FCA` | 2014 | `edition_history_statement` | `first_edition:2014` | 4 | `strong_multipsm` | 1 |
| `H2014P6FCA` | 2014 | `edition_history_statement` | `first_edition:2018` | 4 | `strong_multipsm` | 1 |
| `H2014P6FCA` | 2014 | `reprint_history_statement` | `third_reprint:2017` | 4 | `strong_multipsm` | 1 |
| `H2019P1FCA` | 2019 | `edition_history_statement` | `fifth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2019P1FCA` | 2019 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2019P1FCA` | 2019 | `edition_history_statement` | `fourth_edition:2013` | 2 | `strong_multipsm` | 1 |
| `H2019P1FCA` | 2019 | `edition_history_statement` | `sixth_edition:2019` | 2 | `strong_multipsm` | 1 |
| `H2019P2FCA` | 2019 | `edition_history_statement` | `fifth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2019P2FCA` | 2019 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2019P2FCA` | 2019 | `edition_history_statement` | `fourth_edition:2013` | 2 | `strong_multipsm` | 1 |
| `H2019P2FCA` | 2019 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2019P2FCA` | 2019 | `edition_history_statement` | `sixth_edition:2019` | 2 | `strong_multipsm` | 1 |
| `H2019P2FCA` | 2019 | `isbn_statement` | `978-607-551-234-1` | 2 | `strong_multipsm` | 1 |
| `H2019P3FCA` | 2019 | `edition_history_statement` | `fifth_edition:2019` | 2 | `strong_multipsm` | 1 |
| `H2019P3FCA` | 2019 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2019P3FCA` | 2019 | `edition_history_statement` | `fourth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2019P3FCA` | 2019 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2019P3FCA` | 2019 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2019P4FCA` | 2019 | `edition_history_statement` | `fifth_edition:2019` | 2 | `strong_multipsm` | 1 |
| `H2019P4FCA` | 2019 | `edition_history_statement` | `first_edition:2008` | 2 | `strong_multipsm` | 1 |
| `H2019P4FCA` | 2019 | `edition_history_statement` | `fourth_edition:2014` | 2 | `strong_multipsm` | 1 |
| `H2019P4FCA` | 2019 | `edition_history_statement` | `second_edition:2009` | 2 | `strong_multipsm` | 1 |
| `H2019P4FCA` | 2019 | `edition_history_statement` | `third_edition:2010` | 2 | `strong_multipsm` | 1 |
| `H2019P4FCA` | 2019 | `isbn_statement` | `978-607-551-155-9` | 2 | `strong_multipsm` | 1 |
| `H2019P4FCA` | 2019 | `school_cycle_statement` | `2019-2020` | 2 | `strong_multipsm` | 1 |
| `H2019P5FCA` | 2019 | `edition_history_statement` | `first_edition:2014` | 4 | `strong_multipsm` | 1 |
| `H2019P5FCA` | 2019 | `edition_history_statement` | `second_edition:2019` | 4 | `strong_multipsm` | 1 |
| `H2019P5FCA` | 2019 | `school_cycle_statement` | `2019-2020` | 4 | `strong_multipsm` | 1 |
| `H2019P6FCA` | 2019 | `edition_history_statement` | `first_edition:2014` | 4 | `strong_multipsm` | 1 |
| `H2019P6FCA` | 2019 | `edition_history_statement` | `second_edition:2019` | 4 | `strong_multipsm` | 1 |
| `H2019P6FCA` | 2019 | `school_cycle_statement` | `2019-2020` | 4 | `strong_multipsm` | 1 |

## Contrato

- Cada observación mantiene una página primaria y SHA; la tabla de evidencia conserva todas las páginas fuertes que la corroboran.
- Ningún ISBN con checksum ISBN-13 inválido entra a la capa de observaciones.
- `catalog_generation` se copia sólo como contexto de cohorte y nunca genera el valor observado.
- `human_validated=0` mantiene explícita la ausencia de validación humana de la transcripción OCR.
- Esta capa no resuelve por sí sola cuál declaración histórica corresponde a la edición vigente o al año de circulación del ejemplar.

Véanse `docs/DATA_MODEL.md`, `docs/DATA_GOVERNANCE.md` y `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`.
