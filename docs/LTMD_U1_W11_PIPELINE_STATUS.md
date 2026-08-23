# LTMD-U1 W11 — estado operativo de la cadena downstream

Versión: `LTMD_U1_W11_PIPELINE_STATUS_0.1`. Observado: **2026-08-23T20:57:04.579811Z**.

> Observación operativa; no sustituye los reportes científicos de cada compuerta.

| etapa | run | estado | conclusión | jobs | en curso | cola | fallos |
|---|---:|---|---|---:|---:|---:|---:|
| G5 OCR | 32664121168 | `completed` | `success` | 3 | 0 | 0 | 0 |
| G6 PAGESTRUCT | 32665919946 | `queued` | `pendiente` | 107 | 8 | 90 | 0 |
| G6 FRAGSEG | 32664240478 | `completed` | `success` | 3 | 0 | 0 | 0 |
| G6 exact reuse | 32664253728 | `completed` | `success` | 1 | 0 | 0 | 0 |
| G7 completion | 32664265395 | `completed` | `success` | 1 | 0 | 0 | 0 |

## Regla

Un estado `success` sólo indica que Actions terminó el workflow. El cierre científico de cada etapa requiere que su artefacto final exista y pase las verificaciones de cardinalidad, procedencia, hashes y estados definidos por el pipeline.
