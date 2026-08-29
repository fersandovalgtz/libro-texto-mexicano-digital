# LTMD-U1 W10 — probe source-first y admisibilidad

Versión: `LTMD_U1_W10_SOURCE_PROBE_0.1`.

## Resultado

- Identidades históricas: **69**.
- Procesables auditadas: **68/68**.
- Excepción final fuera del probe: **1** (`H2014P1ENA`).
- Listas para auditoría directa de activos: **68/68**.
- `SOURCE_ADMISSIBLE`: **68/68**.
- `SOURCE_RETAINED`: **0/68**.
- Posiciones declaradas observadas: **12,005**.
- JPEG fuente servidos y hasheados: **11,937**.
- Candidatos terminales sintéticos: **68**.
- Huecos internos no servidos: **0**.
- Errores operacionales de probe: **0**.
- Alias creados: **0**.
- `text_verified`: **false**.
- `semantic_ready`: **false**.

## Retenciones de fuente

Ninguna.

## Por generación

| generación | procesables | admitidas | retenidas | páginas fuente admitidas |
|---:|---:|---:|---:|---:|
| 1960 | 11 | 11 | 0 | 2,126 |
| 1966 | 19 | 19 | 0 | 3,620 |
| 1972 | 2 | 2 | 0 | 356 |
| 1993 | 32 | 32 | 0 | 5,182 |
| 2008 | 1 | 1 | 0 | 162 |
| 2011 | 2 | 2 | 0 | 330 |
| 2014 | 1 | 1 | 0 | 161 |

## Regla de admisión

Una identidad sólo es `SOURCE_ADMISSIBLE` cuando conserva reconciliación exacta 1:1, arquitectura/configuración oficial verificable, al menos un JPEG fuente servido, cero huecos internos, cero errores operacionales y como máximo un candidato terminal sintético. Los bytes de imagen se transmiten únicamente para computar SHA-256 y tamaño; no se persisten en GitHub.

Cualquier ausencia, 404 o arquitectura no verificable permanece como retención de fuente. No se imputa contenido desde títulos, grados, ediciones, cardinalidades, OCR o libros vecinos.

Si `probe_errors_sum` es distinto de cero, el gate queda operacionalmente inconcluso y no autoriza OCR. Con cero errores, sólo las identidades `SOURCE_ADMISSIBLE` pueden avanzar al procesamiento distribuido; la admisibilidad no implica verificación humana del texto ni preparación semántica.
