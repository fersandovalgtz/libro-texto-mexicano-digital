# LTMD-U1 W8 Artes — topología cerrada de procesamiento

Versión: `LTMD_U1_W8_ARTES_PROCESSING_TOPOLOGY_0.1`.

## Contrato ejecutable

- Identidades W8: **20**.
- Objetos canónicos admitidos a OCR: **16**.
- Identidades retenidas por fuente: **4**.
- JPEG fuente canónicos, con SHA-256 y tamaño: **1490**.
- Alias creados: **0**.
- Modo de los admitidos: `direct_canonical`.
- Modo de los retenidos: `withheld_source`.

## Cohorte retenida

`H2018P3EAA`, `H2018P4EAA`, `H2018P5EAA`, `H2018P6EAA`.

Las cuatro identidades retenidas no aportan páginas al manifiesto canónico y no son elegibles para OCR. El constructor aborta si una de ellas aparece como `source_jpeg`, si cambia la partición 16/4 o si deriva la cardinalidad de 1,490 páginas.

## Cobertura admitida por generación

| generación | visores admitidos | páginas fuente |
|---:|---:|---:|
| 2008 | 2 | 204 |
| 2011 | 6 | 558 |
| 2014 | 4 | 364 |
| 2019 | 4 | 364 |

## Regla de procedencia

Cada fila del manifiesto canónico conserva URL oficial, índice de imagen, tamaño y SHA-256 del activo observado por la auditoría W8. La topología no descarga ni relicencia JPEG y no crea equivalencias históricas o semánticas.

Este producto abre exclusivamente la fase técnica OCR/PAGESTRUCT/FRAGSEG para los 16 objetos admitidos. No autoriza todavía inferencias curriculares, pedagógicas, históricas o de continuidad entre generaciones.
