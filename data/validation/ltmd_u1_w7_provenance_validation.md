# LTMD-U1 W7 — validación del contrato de procedencia

Versión validada: `LTMD_U1_W7_CIVICS_ETHICS_ASSET_AUDIT_0.1`.

- Estado: **PASS**.
- Visores: **30**.
- Filas del manifiesto: **4,191**.
- Claves `(viewer_key, viewer_page)` únicas: **4,191**.
- Visores `direct_asset_ready`: **29/30**.
- JPEG con tamaño y SHA-256 válidos: **4,161**.
- Candidatos terminales 404: **29**.
- Huecos internos 404: **1**.
- Errores de sondeo persistidos: **0**.

## Invariantes verificadas

La validación exige cobertura exacta del inventario W7, secuencias de página contiguas, URL de sondeo determinista, coherencia entre estado HTTP y estado técnico, tamaño y SHA-256 para cada JPEG servido, semántica estricta para 404 terminales e internos, ausencia de `probe_error` persistidos y recomputación exacta del resumen por visor.

Este PASS valida la integridad interna y la reproducibilidad del registro de procedencia. No demuestra identidad histórica entre ediciones, equivalencia curricular, autoría, completitud semántica ni autorización para OCR.
