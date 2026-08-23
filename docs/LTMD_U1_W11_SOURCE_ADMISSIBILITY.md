# LTMD-U1 W11 — compuerta consolidada de admisibilidad de fuente

Versión: `LTMD_U1_W11_SOURCE_ADMISSIBILITY_0.1`.

- Identidades evaluadas: **111/111**.
- Fuente admitida para procesamiento técnico: **107/111**.
- Retenidas: **4/111**.

## Rutas técnicas evaluadas
- `nonstandard_html_diagnostics`: **11** identidades.
- `standard_dynamic_claves`: **100** identidades.

## Estados
- `admitted_direct`: **107**.
- `withheld_internal_unserved`: **4**.

## Retenciones explícitas
- Ninguna.

## Regla
`ocr_source_admitted=1` exige al menos un JPEG oficial servido, cero huecos internos, cero errores de probe y `direct_asset_ready=1`. Un terminal sintético estricto puede coexistir con admisibilidad porque no representa una página fuente omitida. La anomalía de HTML de la ruta no estándar permanece documentada y no invalida por sí sola una secuencia fuente que `claves.json` declara y la auditoría verifica posición por posición. Ninguna retención se sustituye por semejanza de título, año, grado, OCR o apariencia visual.

`WAITING_HUMAN_REFERENCE` continúa vigente. Esta compuerta sólo autoriza topología canónica y procesamiento técnico.
