# LTMD-U1 W11 — estado operativo del OCR

Versión: `LTMD_U1_W11_OCR_RUN_STATUS_0.4`. Observado: **2026-08-23T20:49:53.976999Z**.

> Estado operativo solamente; G5 cierra únicamente con el OCR consolidado validado.

- Run observador: **32665037961**; job observador: **97258397862**.
- Run con matriz: **32663100831**.
- Matriz: **106/106** jobs.
- Exitosos: **96/106 (90.57%)**.
- Fallidos: **0**.
- Cancelados: **0**.
- Aún no completados: **10**.

## Estado global de jobs
- `completed`: **97**.
- `in_progress`: **8**.
- `queued`: **2**.

## Runs activos inspeccionados

| run | estado API | jobs | OCR |
|---:|---|---:|---:|
| 32664121168 | `pending` | 0 | 0 |
| 32663100831 | `queued` | 107 | 106 |

## Regla
El job observador puede reejecutarse para obtener un nuevo corte sin tocar OCR. No se mezclan shards entre runs. Sólo el combine del mismo run puede demostrar 19,862/19,862 páginas, SHA verificado y cero `unresolved`.
