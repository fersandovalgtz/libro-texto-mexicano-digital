# LTMD-U1 W11 — estado operativo del OCR

Versión del reporte: `LTMD_U1_W11_OCR_RUN_STATUS_0.2`.

> Este documento observa GitHub Actions. **No es evidencia de cierre científico**; G5 sólo cierra con `docs/LTMD_U1_W11_OCR.md` validado.

## Run con matriz materializada

- Run ID: **32663100831**.
- Evento: `workflow_run`.
- Estado reportado por Actions: `queued`.
- Conclusión: `pendiente`.
- Head SHA: `ccad68d5ed22f7b2a7016d68aebbd69cdf45ba46`.
- Jobs observados: **107**.
- Jobs de matriz OCR detectados: **106**.
- OCR exitosos: **63**.
- OCR fallidos: **0**.
- OCR cancelados: **0**.
- OCR aún no completados: **43**.

### Estados de jobs
- `completed`: **64**.
- `in_progress`: **8**.
- `queued`: **35**.

### Conclusiones de la matriz OCR
- `pending`: **43**.
- `success`: **63**.

## Runs activos inspeccionados

| run | estado API | jobs | jobs OCR |
|---:|---|---:|---:|
| 32664121168 | `pending` | 0 | 0 |
| 32663100831 | `queued` | 107 | 106 |

## Runs recientes

| run | evento | estado | conclusión | head | creado |
|---:|---|---|---|---|---|
| 32664121168 | `push` | `pending` | `pendiente` | `72c4e3235cc4` | 2026-08-23T20:20:41Z |
| 32663389201 | `push` | `completed` | `cancelled` | `8969ee679e06` | 2026-08-23T20:06:37Z |
| 32663190003 | `workflow_run` | `completed` | `cancelled` | `ecab90ec1563` | 2026-08-23T20:03:04Z |
| 32663100831 | `workflow_run` | `queued` | `pendiente` | `ccad68d5ed22` | 2026-08-23T20:01:24Z |
| 32662604095 | `push` | `completed` | `success` | `83138d88d535` | 2026-08-23T19:52:08Z |

## Regla
Los artefactos de jobs exitosos permanecen subordinados al combine del mismo run. No se mezclan shards de runs diferentes. Un run `success` sólo promueve G5 después de que el combiner demuestre cobertura exacta de los 106 canónicos/19,862 páginas, SHA-256 verificado y cero `unresolved`.
