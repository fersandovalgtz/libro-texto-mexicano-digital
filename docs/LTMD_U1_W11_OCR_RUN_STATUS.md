# LTMD-U1 W11 — estado operativo del OCR

Versión del reporte: `LTMD_U1_W11_OCR_RUN_STATUS_0.1`.

> Este documento observa GitHub Actions. **No es evidencia de cierre científico**; el único gate de G5 sigue siendo `docs/LTMD_U1_W11_OCR.md` validado.

## Run seleccionado

- Run ID: **32664121168**.
- Evento: `push`.
- Estado: `pending`.
- Conclusión: `pendiente`.
- Head SHA: `72c4e3235cc4f2aa0e0bb8a04f6eea8446e8b194`.
- Creado: `2026-08-23T20:20:41Z`.
- Actualizado: `2026-08-23T20:20:42Z`.
- Jobs observados: **0**.
- Jobs de matriz OCR detectados: **0**.

### Estados de jobs

### Conclusiones de jobs

### Matriz OCR — estado

### Matriz OCR — conclusión

## Runs recientes

| run | evento | estado | conclusión | head | creado |
|---:|---|---|---|---|---|
| 32664121168 | `push` | `pending` | `pendiente` | `72c4e3235cc4` | 2026-08-23T20:20:41Z |
| 32663389201 | `push` | `completed` | `cancelled` | `8969ee679e06` | 2026-08-23T20:06:37Z |
| 32663190003 | `workflow_run` | `completed` | `cancelled` | `ecab90ec1563` | 2026-08-23T20:03:04Z |
| 32663100831 | `workflow_run` | `queued` | `pendiente` | `ccad68d5ed22` | 2026-08-23T20:01:24Z |
| 32662604095 | `push` | `completed` | `success` | `83138d88d535` | 2026-08-23T19:52:08Z |

## Regla
Un run `completed/success` no promueve G5 por sí solo: debe existir el artefacto consolidado de OCR con cobertura exacta de los canónicos, SHA-256 verificado y cero `unresolved`. Un run fallido se diagnostica por job; no se reejecuta automáticamente desde este reporte.
