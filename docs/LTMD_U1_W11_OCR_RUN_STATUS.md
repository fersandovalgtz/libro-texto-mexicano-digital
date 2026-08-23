# LTMD-U1 W11 — estado operativo del OCR

Versión: `LTMD_U1_W11_OCR_RUN_STATUS_0.3`. Observado: **2026-08-23T20:36:42.053142Z**.

> Estado operativo solamente; G5 cierra únicamente con el OCR consolidado validado.

- Run con matriz: **32663100831**.
- Matriz: **106/106** jobs.
- Exitosos: **70/106 (66.04%)**.
- Fallidos: **0**.
- Cancelados: **0**.
- Aún no completados: **36**.

## Estado global de jobs
- `completed`: **71**.
- `in_progress`: **8**.
- `queued`: **28**.

## Runs activos inspeccionados

| run | estado API | jobs | OCR |
|---:|---|---:|---:|
| 32664121168 | `pending` | 0 | 0 |
| 32663100831 | `queued` | 107 | 106 |

## Regla
No se mezclan shards entre runs. El porcentaje indica jobs terminados con éxito, no páginas ni cobertura científica. Sólo el combine del mismo run puede demostrar 19,862/19,862 páginas, SHA verificado y cero `unresolved`.
