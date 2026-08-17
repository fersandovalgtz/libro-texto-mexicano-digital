# LTMD — observaciones bibliográficas reproducibles

Versión: `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4`.

- Observaciones semánticas materializadas: **95**.
- Objetos con ≥1 observación: **26**.
- Filas de evidencia página/SHA: **97**.
- Observaciones añadidas por recuperación OCR estrecha: **2**.

0.4 conserva las 93 observaciones de 0.2 y añade únicamente dos `reprint_history_statement` cuya palabra `reimpresión` fue afectada por la confusión OCR documentada `i→l/I/1`. Cada recuperación tiene ≥2 PSM, página institucional SHA-verificada y año igual al inicio de un ciclo escolar ya observado. **No se habilita fuzzy matching general.**

La procedencia de recovery es ahora `LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2`, que deriva sus cinco targets desde el audit pre-recovery y elimina la dependencia circular con la tabla final de candidatos.

Recuperaciones incorporadas:

- `H2011P5CI326`: `third_reprint:2013` en página 2, SHA `e67c796f1dd5be25…`.
- `H2014P4FCA`: `third_reprint:2017` en página 2, SHA `2c388c68da843a23…`.

## Conteo por campo

- `edition_history_statement`: **66**.
- `first_edition_year`: **1**.
- `isbn_statement`: **8**.
- `reprint_history_statement`: **4**.
- `reprint_statement`: **1**.
- `reprint_year`: **1**.
- `school_cycle`: **1**.
- `school_cycle_statement`: **13**.

## Contrato

- Las declaraciones de edición/reimpresión siguen siendo historia bibliográfica observada, no selección automática de la edición efectiva.
- Las dos recuperaciones 0.4 preservan token OCR bruto, PSM y regla de normalización en el artefacto de recovery.
- `catalog_generation` permanece fuera de la inferencia.
- `human_validated=0` permanece explícito.
- Cualquier otra corrección OCR futura requiere una regla separada, acotada y versionada.

Véanse `data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md`, `docs/DATA_MODEL.md` y `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`.
