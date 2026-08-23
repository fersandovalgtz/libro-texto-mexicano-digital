# LTMD-U1 W10 — compuerta de admisibilidad de fuente

Versión: `LTMD_U1_W10_SOURCE_ADMISSIBILITY_0.1`.

- Identidades evaluadas: **69/69**.
- Fuente admitida para procesamiento técnico: **68/69**.
- Retenidas: **1/69**.

## Estados
- `admitted_direct`: **68**.
- `withheld_internal_unserved`: **1**.

## Regla
`ocr_source_admitted=1` exige simultáneamente al menos un JPEG oficial servido, cero huecos internos, cero errores de probe y `direct_asset_ready=1`. Un terminal sintético estricto puede coexistir con admisibilidad porque no representa una página fuente omitida. Ninguna retención se sustituye por una fuente vecina, por una edición próxima o por similitud.

Esta compuerta autoriza únicamente la construcción de topología canónica y procesamiento técnico. No valida edición bibliográfica, semántica ni interpretación histórica.
