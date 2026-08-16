# LTMD-U1 W3 — plan determinista de batches

Versión: `LTMD_U1_W3_BATCH_PLAN_0.1`.

- Visores: **130**.
- Techo operativo por batch: **2,500 posiciones declaradas**.
- Batches: **14**.

| batch | generación | visores | posiciones declaradas |
|---|---:|---:|---:|
| W3-G1960-B01 | 1960 | 3 | 479 |
| W3-G1966-B01 | 1966 | 8 | 1,542 |
| W3-G1972-B01 | 1972 | 11 | 2,263 |
| W3-G1972-B02 | 1972 | 5 | 995 |
| W3-G1982-B01 | 1982 | 11 | 2,149 |
| W3-G1988-B01 | 1988 | 8 | 1,472 |
| W3-G1993-B01 | 1993 | 14 | 2,475 |
| W3-G1993-B02 | 1993 | 7 | 1,281 |
| W3-G2008-B01 | 2008 | 9 | 1,659 |
| W3-G2011-B01 | 2011 | 12 | 2,016 |
| W3-G2014-B01 | 2014 | 12 | 2,375 |
| W3-G2014-B02 | 2014 | 2 | 348 |
| W3-G2018-B01 | 2018 | 14 | 2,420 |
| W3-G2019-B01 | 2019 | 14 | 2,420 |

Los batches no mezclan generaciones. La partición es logística y reproducible; no modifica el denominador W3 ni implica independencia histórica entre visores. Las auditorías de alias/dependencia deberán realizarse antes de OCR productivo.
