# LTMD-U1 — registro transversal de fuentes retenidas

Versión: `LTMD_U1_RETAINED_SOURCE_REGISTER_0.1`.

## Propósito

Este registro consolida las identidades del universo LTMD-U1 que permanecen fuera de la cobertura técnica efectiva por una deuda de fuente explícita. No sustituye los reportes de cada ola ni los issues especializados: funciona como una vista transversal, reproducible y auditable del residual técnico que queda después del cierre de las cohortes fuente-admitidas.

Corte de referencia: **23 de agosto de 2026**.

## Estado agregado

- Universo histórico operativo: **542** identidades.
- Cobertura técnica efectiva: **524/542 (96.68%)**.
- Identidades retenidas por fuente: **18/542 (3.32%)**.
- Imputaciones heurísticas autorizadas para cerrar retenciones: **0**.
- Validación semántica humana: **0/542**; este registro no modifica ese estado.

| ola | dominio | retenidas | seguimiento |
|---|---|---:|---|
| W2 | Matemáticas | 4 | #4 |
| W7 | Formación Cívica y Ética | 5 | #5 |
| W8 | Artes | 4 | #9 |
| W10 | Integrados / Multiarea | 1 | #11 |
| W11 | Otros / No clasificados | 4 | #13, #14 |
| **Total** |  | **18** |  |

El archivo canónico, una fila por identidad, es [`data/catalog/ltmd_u1_retained_source_register.csv`](../data/catalog/ltmd_u1_retained_source_register.csv).

## Clases de retención

### `routing_anomaly_all_or_near_all`

El visor y su configuración documental existen, pero la ruta declarada no sirve los activos esperados. La mera coincidencia de cardinalidad, título o estructura con otra generación no acredita identidad. Afecta a cuatro visores DMA de Matemáticas 2018.

### `withheld_source_gap`

La secuencia documental es casi completa, pero existe al menos un hueco interno no servido que impide declarar una fuente íntegra. Afecta a `H2014P5FCA`.

### `withheld_source_subtree_unserved`

El visor y la configuración siguen presentes, pero el subárbol de activos de página no se sirve desde la ruta institucional observada. Afecta a cuatro visores de Formación Cívica y Ética 2018.

### `withheld_source_unresolved`

La identidad histórica está preservada, pero no existe todavía una representación fuente reproduciblemente resuelta que satisfaga la compuerta de admisibilidad. Afecta a cuatro visores de Artes 2018.

### `withheld_internal_unserved`

La secuencia oficial es mayoritariamente observable, pero una o más posiciones internas concretas no se sirven. Afecta a `H2014P1ENA` y cuatro identidades W11.

## Evidencia aceptable para levantar una retención

Una identidad sólo deja este registro cuando existe una cadena reproducible que permita actualizar la compuerta de fuente correspondiente. Según el caso, la evidencia puede consistir en una ruta institucional efectiva, una captura archivada de la misma representación con correspondencia posicional inequívoca, una relación institucional explícita de reutilización o una identidad byte-exacta demostrada criptográficamente con otra representación servida.

La resolución debe preservar, cuando sean aplicables, URI o identificador archivístico, posición, tamaño, SHA-256, timestamp, procedencia y relación con la identidad histórica original. Después de resolver una fuente deben recomputarse únicamente las capas downstream afectadas y actualizarse el tablero U1.

## Evidencia que no basta por sí sola

No levantan una retención el título, el año, el grado, la cardinalidad, la cercanía de identificadores, la similitud visual, el OCR, la semejanza textual, la pertenencia a la misma serie editorial ni la existencia de un ejemplar aparentemente equivalente en otra generación. Esas señales pueden orientar una búsqueda, pero no crean identidad documental.

## Regla de sincronización

El número de filas activas de este registro debe ser igual a `universo U1 - cobertura técnica efectiva` en `data/catalog/ltmd_u1_coverage.md`. La distribución por ola debe coincidir con la columna `restantes` del tablero. `scripts/validate_u1_retained_source_register.py` convierte esta relación en una comprobación automática.

## Interpretación

Las 18 retenciones no deben leerse como fallas que deban ocultarse para alcanzar artificialmente 100%. Son parte del resultado científico: documentan límites observables de las fuentes y evitan que una infraestructura histórica aparente más completitud de la que puede demostrar. El objetivo es resolverlas cuando exista evidencia suficiente o conservarlas como excepciones explícitas si una búsqueda acotada y reproducible no produce una cadena de procedencia admisible.
