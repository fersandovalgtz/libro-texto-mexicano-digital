# FTRL LTMD-U1 W3 Español/Lengua — preparación de runtime 0.1

**Fecha:** 24 de agosto de 2026  
**Estado:** runtime preparado, no activado  
**Autoridad superior:** `FTRL_U1_EXHAUSTIVE_EXECUTION_PROTOCOL_0_2.md`

## Regla de activación

Ningún OCR FTRL W3 puede iniciar mientras el ledger maestro no registre las 40 identidades W1 como `validated`, `corpus_ready=1` y `ocr_available=1`. Esta condición es ejecutable mediante `scripts/guard_ftrl_w3_activation.py` y no tiene bypass en `scripts/run_ftrl_w3.py`.

La separación epistemológica se conserva: el gate no exige `text_verified` ni `semantic_ready`; de hecho, una promoción automática de esas capas sería un error metodológico.

## Runtime preparado

`scripts/run_ftrl_w3.py` adapta el pipeline FTRL general a la topología W3 congelada en el preflight:

- 130 identidades documentales;
- 114 objetos canónicos;
- 20,765 páginas fuente canónicas;
- construcción OCR por página;
- SQLite/FTS5;
- validación de cardinalidad;
- manifiesto text-free de ejecución;
- cola QC restringida y resumen QC text-free.

El modo piloto procesa un subconjunto explícito de páginas después de pasar el gate W1. El modo completo existe en el runner, pero **no queda todavía asociado a un sello de activación ni a un workflow integral automático**.

## Por qué la topología completa aún no se congela

W3 contiene 20,765 páginas, aproximadamente tres veces el volumen W1. Antes de decidir si el full run debe ejecutarse en un solo job, con mayor paralelismo o mediante una estrategia particionada reproducible, se requiere evidencia observada de:

1. tiempo total real del full run W1;
2. comportamiento de descarga/OCR bajo el runner hospedado;
3. tiempo y estabilidad de un piloto W3 posterior al cierre W1;
4. límites efectivos de la plataforma y tamaño esperado de los productos restringidos.

No se extrapola una arquitectura de ejecución sin esos datos. Esta decisión evita diseñar una corrida que pueda exceder límites operativos y evita cambiar la topología a mitad de una ejecución científica.

## Preservación obligatoria

Antes de crear cualquier sello que active W3 completo, deberá existir y validarse el mecanismo de preservación privada correspondiente. OCR completo, SQLite/FTS5 y QC detallado deberán terminar en la bóveda privada de Google Drive, cifrados durante cualquier handoff temporal, conforme a `LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md`.

Por tanto, la secuencia futura obligatoria es:

**W1 validado → piloto W3 → decisión de topología completa → workflow de preservación W3 validado → sello de full run W3 → validación → copia privada → `archival_complete`.**

## Estados que permanecen falsos

La preparación del runtime no cambia el ledger de completitud de W3. Hasta una corrida integral validada:

- `ftrl_status=pending`;
- `corpus_ready=0`;
- `ocr_available=0` en sentido FTRL;
- `text_verified=0`;
- `semantic_ready=0`;
- `archival_complete=0`.

`runtime_ready != runtime_activated`  
`preflight_ready != corpus_ready`  
`prior_ocr_anchor != ftrl_validated`  
`computationally_validated != archival_complete`
