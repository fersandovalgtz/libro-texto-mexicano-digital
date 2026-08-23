# LTMD-U1 W11 — auditoría contractual del pipeline

Versión: `LTMD_U1_W11_PIPELINE_AUDIT_0.1`.

Esta auditoría valida contratos e invariantes ya publicados; no ejecuta OCR ni modifica cobertura.

## Resultado
- Scripts Python auditados sintácticamente: **13/13**.
- Workflows downstream con `workflow_run` explícito: **5/5**.
- Identidades W11 reconciliadas: **111/111**.
- Fuente admitida: **107/111**.
- Retenidas: **4/111**.
- Objetos canónicos: **106**.
- Aliases byte-exactos: **1**.
- Páginas canónicas: **19,862**.
- Huecos internos materializados: **5/5**.
- Cobertura W11 promovida: **no; correctamente bloqueada hasta el cierre**.
- Rasters fuente/transitorios rastreados bajo `data/`: **0**.

## Estados de fuente
- `admitted_direct`: **107**.
- `withheld_internal_unserved`: **4**.

## Límite
El resultado `PASS` de esta auditoría demuestra coherencia interna del contrato técnico W11 en el corte auditado. No demuestra que OCR/PAGESTRUCT/FRAGSEG hayan terminado si sus artefactos finales aún no existen, ni convierte `otros_no_clasificados` en categoría semántica. `WAITING_HUMAN_REFERENCE` continúa vigente.

**Estado: PASS**
