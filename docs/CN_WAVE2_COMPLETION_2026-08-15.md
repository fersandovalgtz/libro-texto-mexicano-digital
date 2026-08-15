# Cierre técnico de la Ola 2 — Ciencias Naturales

Fecha de corte: 2026-08-15

## Alcance

La Ola 2 incorpora 19 objetos nuevos de la familia estricta *Ciencias Naturales* que tenían `asset_readiness=full_direct` y que no formaban parte del piloto CN5 ni de la expansión CN4/CN6 previa. Se excluyeron deliberadamente los cuatro visores 2018, porque son alias byte-idénticos de los activos 2019, y los dos objetos parciales de 2008 con tres posiciones internas no servidas.

## Procedencia

- libros: **19**;
- JPEG fuente: **3,177**;
- 3,177/3,177 páginas con URL y SHA-256 congelados antes del procesamiento;
- ninguna imagen fuente ni transcripción OCR completa se persiste en el repositorio.

## OCR técnico

Versión: `CN_WAVE2_OCR_0.1`.

- JPEG procesados: **3,177**;
- SHA-256 verificados antes del OCR: **3,177/3,177**;
- texto detectado: **3,164/3,177 (99.59%)**;
- `no_text_detected`: **13**;
- `unresolved`: **0**.

`text_detected` representa cobertura técnica, no exactitud CER/WER ni validez semántica.

## PAGESTRUCT

Versión: `PAGESTRUCT_CN_WAVE2_0.1`.

- páginas clasificadas: **3,177**;
- `textual`: **1,459**;
- `mixed_text_image`: **1,069**;
- `visual_only`: **300**;
- `front_matter`: **1**;
- `toc_or_navigation`: **118**;
- `bibliography_or_credits`: **80**;
- `unknown`: **150**;
- elegibles para FRAGSEG: **2,528**.

Se conserva la lógica estructural utilizada en la expansión CN4/CN6 y la unidad documental sigue siendo `book_id`.

## FRAGSEG

Versión: `FRAGSEG_CN_WAVE2_0.1`.

- páginas elegibles: **2,528**;
- páginas con al menos un fragmento: **2,528**;
- páginas elegibles sin fragmentos: **0**;
- fragmentos: **36,195**;
- IDs únicos: **36,195**;
- páginas con huecos legítimos de secuencia: **80**;
- slots de candidatos de 0 tokens omitidos: **97**.

### Tipos candidatos

- `short_residual_candidate`: **18,423**;
- `question_candidate`: **5,990**;
- `expository_candidate`: **4,897**;
- `instruction_candidate`: **4,720**;
- `activity_candidate`: **1,096**;
- `experiment_candidate`: **446**;
- `project_candidate`: **432**;
- `assessment_candidate`: **191**.

Los huecos de `fragment_sequence` se conservan y auditan; los identificadores no se renumeran retrospectivamente.

## Incidencia de ejecución

Un runner de GitHub quedó detenido durante la instalación del runtime al procesar las banderas estructurales de `LTMD-CN3-G2019`. Se creó una recuperación limitada: se reconstruyó sólo ese shard, se reutilizaron los otros 18 artifacts ya válidos y PAGESTRUCT se ensambló sin recalcularlos. La incidencia se clasifica como fallo de infraestructura de ejecución, no como fallo del corpus.

FRAGSEG fue convertido en idempotente: una vez presente `FRAGSEG_CN_WAVE2_0.1`, nuevas activaciones se detienen en preflight y no reprocesan la ola completa.

## Nuevo tamaño técnico

La expansión CN4/CN6 previa contiene **19,067** fragmentos y la Ola 2 añade **36,195**. Juntas suman **55,262 ocurrencias de fragmento técnico** fuera del piloto CN5, antes de cualquier clasificación semántica productiva.

Si se añade el manifiesto congelado del piloto CN5 (**9,594 fragmentos**), LTMD dispone ahora de **64,856 ocurrencias de fragmento segmentadas** en sus capas técnicas actualmente materializadas.

Este total es una cardinalidad de infraestructura, no un tamaño muestral independiente para inferencia histórica: existen relaciones de reutilización, revisión y alias que deben modelarse mediante las vistas de objeto, contenido único y revisión.

## Límite epistemológico

La Ola 2 es `corpus_ready` hasta FRAGSEG. **No es `semantic_ready`.** No se ejecutaron Rule A, SEMB 0.2 ni candidatos SEMB 0.3 sobre estos 19 objetos. SEMB 0.3 permanece bloqueado a referencia humana y sus criterios de aceptación congelados.
