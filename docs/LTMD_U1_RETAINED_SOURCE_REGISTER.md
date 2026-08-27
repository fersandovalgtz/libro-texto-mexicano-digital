# LTMD-U1 — registro transversal de fuentes retenidas

Versión: `LTMD_U1_RETAINED_SOURCE_REGISTER_0.2`.

## Propósito

Este registro consolida las identidades del universo LTMD-U1 que permanecen fuera de la cobertura técnica efectiva por una deuda de fuente explícita. Distingue dos estados que no deben confundirse: **retenciones activas**, cuya investigación de fuente continúa abierta, y **excepciones técnicas finales**, cuya búsqueda disponible terminó de manera acotada y reproducible sin obtener una representación admisible.

Corte de referencia: **23 de agosto de 2026**.

## Estado agregado

- Universo histórico operativo: **542** identidades.
- Cobertura técnica efectiva: **524/542 (96.68%)**.
- Residual fuera de cobertura efectiva: **18/542 (3.32%)**.
- Retenciones activas: **13/542 (2.40%)**.
- Excepciones técnicas finales: **5/542 (0.92%)**.
- Imputaciones heurísticas autorizadas: **0**.
- Validación semántica humana: **0/542**; este registro no modifica ese estado.

| ola | dominio | residual | ciclo de vida | seguimiento |
|---|---|---:|---|---|
| W2 | Matemáticas | 4 | 4 activas | #4 abierto |
| W7 | Formación Cívica y Ética | 5 | 5 activas | #5 abierto |
| W8 | Artes | 4 | 4 activas | #9 abierto |
| W10 | Integrados / Multiarea | 1 | 1 excepción final | #11 cerrado |
| W11 | Otros / No clasificados | 4 | 4 excepciones finales | #13 y #14 cerrados |
| **Total** |  | **18** | **13 activas + 5 finales** |  |

El archivo canónico, una fila por identidad, es [`data/catalog/ltmd_u1_retained_source_register.csv`](../data/catalog/ltmd_u1_retained_source_register.csv).

## Ledger de intentos de investigación

El estado canónico anterior se complementa con [`data/catalog/ltmd_u1_retained_source_attempts.csv`](../data/catalog/ltmd_u1_retained_source_attempts.csv), cuya metodología se documenta en [`docs/LTMD_U1_RETAINED_SOURCE_RESEARCH_LEDGER.md`](LTMD_U1_RETAINED_SOURCE_RESEARCH_LEDGER.md). Ese segundo artefacto registra intentos individuales sin convertir resultados negativos de descubrimiento en evidencia de inexistencia ni permitir que una búsqueda fallida modifique por sí sola el ciclo de vida.

La versión inicial del ledger incorpora las 13 retenciones activas y conserva explícitamente `state_before=state_after=active_retention` cuando la evidencia no satisface la compuerta de fuente. Las cinco excepciones finales quedan fuera de la búsqueda rutinaria y sólo pueden reabrirse ante evidencia primaria o archivística nueva.

## Estados de ciclo de vida

### `active_retention`

La identidad continúa fuera de cobertura y existe una línea de investigación de fuente todavía abierta o no agotada. Resolverla requiere evidencia suficiente para levantar la compuerta de fuente; hasta entonces no se imputa ni se sustituye.

### `final_exception`

La identidad continúa fuera de cobertura, pero el issue especializado alcanzó su criterio de cierre mediante una búsqueda acotada y reproducible sin recuperación admisible. No significa que el activo inexistente haya sido demostrado como universalmente irrecuperable. Significa que, con la evidencia disponible en el corte, la excepción está metodológicamente cerrada y sólo debe reabrirse ante una representación institucional o archivística nueva y verificable.

En el corte actual son excepciones finales:

- `H2014P1ENA` — #11;
- `H2014P1EAM` y `H2014P2EAM` — #13;
- `H2014P3COL` y `H2014P3MOR` — #14.

## Clases de retención

### `routing_anomaly_all_or_near_all`

El visor y su configuración documental existen, pero la ruta declarada no sirve los activos esperados. Afecta a cuatro visores DMA de Matemáticas 2018.

### `withheld_source_gap`

La secuencia documental es casi completa, pero existe al menos un hueco interno no servido que impide declarar una fuente íntegra. Afecta a `H2014P5FCA`.

### `withheld_source_subtree_unserved`

El visor y la configuración siguen presentes, pero el subárbol de activos de página no se sirve desde la ruta institucional observada. Afecta a cuatro visores de Formación Cívica y Ética 2018.

### `withheld_source_unresolved`

La identidad histórica está preservada, pero no existe todavía una representación fuente reproduciblemente resuelta que satisfaga la compuerta de admisibilidad. Afecta a cuatro visores de Artes 2018.

### `withheld_internal_unserved`

La secuencia oficial es mayoritariamente observable, pero una o más posiciones internas concretas no se sirven. Afecta a `H2014P1ENA` y cuatro identidades W11; las cinco están ya cerradas metodológicamente como excepciones finales en este corte.

## Evidencia de cierre de las excepciones finales

### W10 — `H2014P1ENA`

#11 documentó el hueco exacto en página/índice 114, la ausencia de una configuración oficial vigente sometible a comparación byte-exacta, un sondeo Wayback exacto HTTPS/HTTP sin capturas CDX 200 y la insuficiencia de representaciones secundarias. El issue se cerró expresamente como retención final sin imputación.

### W11 — EAM

#13 verificó los huecos exactos de `H2014P1EAM` y `H2014P2EAM`, obtuvo 0 capturas Wayback candidatas en el sondeo acotado y comprobó que la configuración oficial vigente no ofrece una representación activa equivalente. El issue se cerró como retención final documentada.

### W11 — Colima y Morelos

#14 combinó sondeo Wayback negativo con comparación de representaciones oficiales actuales. Para Morelos no se recuperó una secuencia oficial compatible; para Colima existieron rutas actuales que sirvieron 160/160 posiciones, incluido `130.jpg`, pero **0/160 SHA-256** coincidieron con la secuencia histórica, demostrando que se trata de material documentalmente distinto. El issue quedó cerrado sin sustituir los huecos.

## Evidencia aceptable para levantar una retención

Una identidad sólo deja este registro cuando existe una cadena reproducible que permita actualizar la compuerta de fuente correspondiente. Según el caso, la evidencia puede consistir en una ruta institucional efectiva, una captura archivada de la misma representación con correspondencia posicional inequívoca, una relación institucional explícita de reutilización o una identidad byte-exacta demostrada criptográficamente con otra representación servida.

La resolución debe preservar, cuando sean aplicables, URI o identificador archivístico, posición, tamaño, SHA-256, timestamp, procedencia y relación con la identidad histórica original. Después de resolver una fuente deben recomputarse únicamente las capas downstream afectadas y actualizarse el tablero U1.

## Evidencia que no basta por sí sola

No levantan una retención el título, el año, el grado, la cardinalidad, la cercanía de identificadores, la similitud visual, el OCR, la semejanza textual, la pertenencia a la misma serie editorial ni la existencia de un ejemplar aparentemente equivalente en otra generación. Esas señales pueden orientar una búsqueda, pero no crean identidad documental.

## Regla de sincronización

El número total de filas del registro debe ser igual a `universo U1 - cobertura técnica efectiva` en `data/catalog/ltmd_u1_coverage.md`. La distribución por ola debe coincidir con la columna `restantes`. Además, la versión 0.2 exige exactamente **13 `active_retention`** y **5 `final_exception`**, con las cinco identidades finales explícitamente congeladas. `scripts/validate_u1_retained_source_register.py` convierte estas relaciones en comprobaciones automáticas.

El ledger de investigación añade una segunda invariancia: toda retención activa debe estar representada por al menos un intento y una consolidación de evidencia de partida; los outcomes negativos/de descubrimiento no pueden cambiar el ciclo de vida, y una excepción final sólo puede reabrirse mediante un disparador explícito de evidencia nueva. `scripts/validate_u1_retained_source_attempts.py` automatiza esas reglas.

## Interpretación

El residual de 18 identidades no es una sola lista de pendientes. Trece son trabajo técnico todavía abierto; cinco son resultados negativos ya cerrados metodológicamente. Mantener esa diferencia evita dos errores opuestos: inflar artificialmente la cobertura mediante imputación o mantener indefinidamente como “pendiente” una investigación de fuente que ya alcanzó un cierre reproducible y defendible.
