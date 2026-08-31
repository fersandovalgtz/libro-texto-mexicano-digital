# LTMD-U1 W6 — relaciones exactas de activos y readiness fuente Geografía/Atlas

Versión: `LTMD_U1_W6_GEOGRAPHY_ATLAS_ASSET_REL_0.1`.

- Visores analizados: **42/42**.
- `full_direct_source`: **41**.
- `partial_internal_unserved`: **1**.
- `no_source_jpegs`: **0**.
- Pares con secuencia completa de activos servidos byte-idéntica: **0**.
- Pares exactos entre generaciones: **0**.
- Pares exactos entre generaciones y mismo grado: **0**.

## Relaciones exactas

- No se detectaron pares con secuencia completa byte-idéntica.

## Excepciones que requieren reconciliación antes de OCR

- `H2008P4GE273`: estado `partial_internal_unserved`, UI=`standard_x_js`, JPEG=159/161, internos no servidos=2, terminales candidatos=0.

## Límite de interpretación

Una relación `full_served_asset_sequence_byte_exact` prueba igualdad byte a byte de la secuencia completa de JPEG servidos registrada por la auditoría, pero no fusiona identidades de catálogo ni demuestra identidad bibliográfica, continuidad histórica, equivalencia curricular, pedagógica o semántica. La excepción HTML de W6 permanece como provenance incluso si sus activos fueran completos.

Este informe no autoriza por sí solo OCR W6. Antes debe existir una reconciliación explícita que resuelva parcialidad/routing y decida cómo representar pares exactos sin deduplicación destructiva.
