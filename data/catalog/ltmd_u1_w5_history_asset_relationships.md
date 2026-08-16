# LTMD-U1 W5 — relaciones exactas de activos y readiness fuente Historia

Versión: `LTMD_U1_W5_HISTORY_ASSET_REL_0.1`.

- Visores analizados: **18/18**.
- `full_direct_source`: **15**.
- `partial_internal_unserved`: **0**.
- `no_source_jpegs`: **3**.
- Pares con secuencia completa de activos servidos byte-idéntica: **0**.
- Pares byte-idénticos entre generaciones: **0**.
- Pares byte-idénticos entre generaciones y mismo grado: **0**.
- Pares exactos restringidos a generaciones 2014/2018/2019: **0**.

## Relaciones exactas

- No se detectaron pares con secuencia completa byte-idéntica.

## Excepciones que requieren reconciliación antes de OCR

- `H2018P4HIA`: estado `no_source_jpegs`, JPEG=0/194, internos no servidos=193, terminales candidatos=1.
- `H2018P5HIA`: estado `no_source_jpegs`, JPEG=0/194, internos no servidos=193, terminales candidatos=1.
- `H2018P6HIA`: estado `no_source_jpegs`, JPEG=0/138, internos no servidos=137, terminales candidatos=1.

## Límite de interpretación

Una relación `full_served_asset_sequence_byte_exact` prueba igualdad byte a byte de la secuencia completa de JPEG servidos registrada por la auditoría, pero no fusiona identidades de catálogo ni demuestra identidad bibliográfica, continuidad histórica, equivalencia curricular, pedagógica o semántica. La elección posterior de un canónico operacional debe conservar provenance hacia cada identidad representada.

Este informe no autoriza por sí solo OCR W5. Antes debe existir una reconciliación explícita que resuelva parcialidad/routing y decida cómo representar pares exactos sin deduplicación destructiva.
