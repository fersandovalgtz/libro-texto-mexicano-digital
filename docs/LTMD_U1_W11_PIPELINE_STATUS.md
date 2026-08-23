# LTMD-U1 W11 — estado operativo de la cadena downstream

Versión: `LTMD_U1_W11_PIPELINE_STATUS_0.2`. Observado: **2026-08-23T22:13:41.428652Z**.

> Observación operativa; no sustituye los reportes científicos de cada compuerta.

- Run observador: **32669933425**; job observador: **—**.

| etapa | run | estado API | conclusión | jobs | éxito | en curso | cola | fallos |
|---|---:|---|---|---:|---:|---:|---:|---:|
| G5 OCR | 32663100831 | `completed` | `success` | 108 | 108 | 0 | 0 | 0 |
| G6 PAGESTRUCT | 32665919946 | `completed` | `success` | 108 | 108 | 0 | 0 | 0 |
| G6 FRAGSEG | 32666722394 | `completed` | `success` | 108 | 108 | 0 | 0 | 0 |
| G6 exact reuse | 32669154481 | `completed` | `success` | 1 | 1 | 0 | 0 | 0 |
| G7 completion | 32669912469 | `completed` | `success` | 1 | 1 | 0 | 0 | 0 |

## Regla

El observador selecciona el run con trabajo materializado cuando coexist(en) shells/no-op más nuevos. Un estado `success` sólo indica que Actions terminó el workflow. El cierre científico requiere que el artefacto final de la etapa exista y pase verificaciones de cardinalidad, procedencia, hashes y estados.
