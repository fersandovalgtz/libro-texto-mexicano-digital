# Protocolo de validación humana del libro de códigos 0.1

## Propósito

Validar manualmente las categorías de `docs/CODEBOOK_0_1.md` antes de cualquier clasificación automática de acciones pedagógicas o posiciones del alumno.

El principio rector es conservador: **la automatización no decide todavía qué es observar, explicar, investigar, experimentar, colaborar, etc.** Primero se construye una referencia humana trazable.

## Fase 1 — pool preregistrado de páginas

`data/samples/human_validation_page_pool.csv` contiene **100 páginas candidatas**, 25 por generación.

Distribución por generación:

- Q1 = 6 páginas;
- Q2 = 6 páginas;
- Q3 = 6 páginas;
- Q4 = 7 páginas.

La selección se hizo únicamente entre páginas posteriores al índice que produjeron texto OCR y se distribuyó regularmente por posición dentro de cada cuarto del libro. **No se inspeccionó el contenido para escoger páginas que favorecieran una hipótesis pedagógica.**

Las variables `recognized_words_technical` y `mean_word_confidence_technical` son auxiliares de control técnico. No forman parte de la codificación sustantiva.

## Fase 2 — inventario humano de tipos presentes

Para cada página candidata, un codificador humano debe abrir la URL oficial y registrar en `page_type_inventory` qué unidades funcionales están realmente presentes. Valores posibles, separados por `|`:

- `expository`
- `instruction`
- `question`
- `activity`
- `experiment`
- `project`
- `assessment`

Esta etapa es un inventario de presencia, no la codificación definitiva del fragmento.

## Fase 3 — selección del fragmento

Después del inventario de tipos, se escogerán **25 fragmentos por generación** con representación de distintas posiciones del libro y, hasta donde el corpus lo permita, diversidad de tipos funcionales.

Reglas:

1. cada fragmento debe ser una unidad funcionalmente autónoma;
2. una consigna, pregunta o actividad delimitada tiene prioridad sobre un párrafo arbitrariamente cortado;
3. un mismo fragmento puede contener más de un tipo cuando la estructura lo requiera, pero debe existir una unidad principal identificable;
4. no se elegirá o descartará un fragmento por producir un resultado analítico conveniente;
5. cualquier sustitución debe conservar `page_id`, razón y fecha.

El texto íntegro del fragmento se conserva sólo en la hoja privada/local de codificación; **no se versiona en el repositorio**.

## Fase 4 — codificación humana

Campos mínimos por fragmento:

### Tipo funcional

Uno o más de:

`expository | instruction | question | activity | experiment | project | assessment`

### Acción pedagógica solicitada

Una o más de:

`observe | describe | recall | explain | compare | classify | measure | experiment | investigate | predict | infer | discuss | solve | create | decide | act_on_environment`

### Posición pedagógica del alumno

Una o más de:

`receiver | instruction_follower | observer | experimenter | investigator | reasoner | collaborator | decision_maker | community_agent`

### Dimensiones de contenido

Usar las etiquetas de la sección D de `CODEBOOK_0_1.md` cuando sean observables.

## Regla de inferencia

Se mantiene la regla central del libro de códigos: **se codifica lo que el fragmento pide o hace lingüísticamente, no lo que el tema de la página sugiere**.

Ejemplos:

- un texto que describe un experimento no se codifica como `experiment` si el alumno sólo debe leerlo;
- una página ambiental no convierte al estudiante en `community_agent` si no se le exige proponer, decidir o actuar;
- una pregunta de recuerdo no se codifica como `reasoner` sólo porque trate un concepto científico complejo.

## Fase 5 — segunda revisión

Los 100 fragmentos finales deberán ser revisados por segunda vez antes de entrenar reglas o modelos.

En la primera iteración se registrarán:

- desacuerdos;
- categorías difíciles de distinguir;
- definiciones demasiado amplias o estrechas;
- necesidad de ejemplos positivos/negativos.

Sólo después se publicará `CODEBOOK_0_2.md`. La versión 0.1 se conserva sin sobrescribir para trazabilidad.

## Salida publicable

El repositorio puede conservar una tabla derivada con:

- `sample_id`;
- `book_id` / generación;
- `page_id`;
- posición;
- tipos codificados;
- acciones pedagógicas;
- posiciones del alumno;
- dimensiones temáticas;
- estado de revisión;
- hash del fragmento si se necesita trazabilidad.

No es necesario publicar el fragmento textual para reproducir el análisis de frecuencias y relaciones.

## Criterio para pasar a automatización

La clasificación automática sólo comienza cuando:

1. existan 25 fragmentos codificados por generación;
2. las reglas ambiguas hayan sido revisadas;
3. se haya creado `CODEBOOK_0_2.md` o se documente explícitamente que 0.1 permanece sin cambios;
4. la muestra humana se mantenga separada del conjunto usado para ajustar reglas automáticas, cuando sea técnicamente posible.
