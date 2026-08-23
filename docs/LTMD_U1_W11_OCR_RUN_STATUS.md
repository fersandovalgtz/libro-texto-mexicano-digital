# LTMD-U1 W11 — estado operativo del OCR

Versión: `LTMD_U1_W11_OCR_RUN_STATUS_0.4`. Observado: **2026-08-23T20:53:00.936007Z**.

> Estado operativo solamente; G5 cierra únicamente con el OCR consolidado validado.

- Run observador: **32665037961**; job observador: **97258791163**.
- Run con matriz: **32663100831**.
- Matriz: **106/106** jobs.
- Exitosos: **103/106 (97.17%)**.
- Fallidos: **0**.
- Cancelados: **0**.
- Aún no completados: **3**.

## Estado global de jobs
- `completed`: **104**.
- `in_progress`: **3**.

## Runs activos inspeccionados

| run | estado API | jobs | OCR |
|---:|---|---:|---:|
| 32664121168 | `pending` | 0 | 0 |
| 32663100831 | `in_progress` | 107 | 106 |

## Regla
El job observador puede reejecutarse para obtener un nuevo corte sin tocar OCR. No se mezclan shards entre runs. Sólo el combine del mismo run puede demostrar 19,862/19,862 páginas, SHA verificado y cero `unresolved`.
