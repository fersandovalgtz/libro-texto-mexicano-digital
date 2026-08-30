# LTMD-U1 — cierre global FTRL 0.1

**Fecha efectiva:** 2026-08-30.

## Estado canónico

La capa FTRL de LTMD-U1 queda agotada para todos los objetos con fuente admitida. Las once olas W1–W11 están en `ftrl_status=validated` y `archival_status=archival_complete` para sus identidades procesables.

Sobre el denominador fijo de **542 identidades históricas**, el ledger registra:

- 524 `validated`;
- 5 `final_exception`;
- 13 `blocked_active_retention`;
- 0 `pending` o procesables pendientes.

Las identidades validadas representan **492 objetos canónicos** y **86,549 páginas fuente canónicas**. `corpus_ready=524` y `ocr_available=524` describen disponibilidad técnica, no validación humana del texto.

## Última ola cerrada: W2 Matemáticas

W2 conserva 64 identidades históricas: 60 admitidas, 57 objetos canónicos, 3 alias exactos y 4 retenciones activas DMA 2018. Su corrida distribuida es `33291984081`, sobre `29f31430ab542ed3c9098446e0af9136515dc581`, con evidencia en `data/research/ltmd_u1_w2_archival_closure.json`.

Las retenciones `H2018P3DMA`, `H2018P4DMA`, `H2018P5DMA` y `H2018P6DMA` no se sustituyen con ediciones 2019 sin prueba documental o criptográfica suficiente.

## Límites epistemológicos

Este cierre demuestra que ya no existe trabajo FTRL procesable pendiente bajo las reglas vigentes. No autoriza análisis semántico o histórico automático. El estado canónico mantiene:

- `text_verified_identities = 0`;
- `semantic_ready_identities = 0`;
- `global_closure.eligible = false` por 13 retenciones activas.

Siguen vigentes los guardas `ocr_available != text_verified`, `corpus_ready != semantic_ready`, `search_hit != historical_claim`, `zero_hits != demonstrated_absence` y `computationally_validated != archival_complete`, así como `docs/AUTOMATED_WORK_CEILING_0_1.md`.

## Fuentes estructuradas prevalentes

Los conteos de este documento se derivan de:

- `data/research/ltmd_u1_ftrl_completion_ledger.csv`;
- `data/research/ltmd_u1_ftrl_completion_summary.json`;
- `data/research/ltmd_u1_ftrl_wave_state.json`;
- los registros `data/research/ltmd_u1_w*_archival_closure.json`.

Ante cualquier divergencia futura, esos artefactos estructurados prevalecen sobre esta síntesis.

## Siguiente trabajo legítimo

FTRL-U1 sólo debe reabrirse si aparece evidencia nueva que cambie la admisibilidad de una retención activa. El trabajo automatizable posterior se limita a deudas documentales/bibliográficas, procedencia, validación técnica y preparación para revisión humana.
