# Modelo de datos mínimo — borrador 0.4

## Principio temporal

El proyecto distingue explícitamente entre **generación del catálogo**, **año bibliográfico de la edición concreta**, **año de reimpresión**, **ciclo escolar** y **año de derechos/copyright**. Una etiqueta como `1993` o `2014` en el Catálogo Histórico de CONALITEG es una clasificación institucional de cohorte/navegación y no debe copiarse automáticamente como fecha de publicación.

La evidencia empírica del propio corpus obliga a esta separación. El visor `H2014P5FCA`, etiquetado por CONALITEG como `catalog_generation=2014`, contiene una página legal institucional SHA-verificada que declara `Primera edición, 2014` y `Tercera reimpresión, 2017 (ciclo escolar 2017-2018)`. Por tanto, `catalog_generation == publication_year` es una inferencia inválida como regla general.

Del mismo modo, una línea `Derechos reservados SEP, 1977` demuestra un año de derechos, pero no necesariamente una edición publicada en 1977 si la página no lo declara así.

El año de edición sólo se fija como `verified` cuando la página legal o una fuente primaria equivalente lo vincula explícitamente con una edición. La ausencia de evidencia no se completa por proximidad de cohorte, título, grado, cardinalidad o continuidad textual.

Véase `docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md`.

## Entidad: libro

Campos iniciales:

- `book_id`
- `title`
- `catalog_generation`
- `catalog_generation_source`
- `edition_year`
- `edition_year_status`
- `edition`
- `reprint_statement`
- `reprint_year`
- `copyright_year`
- `isbn`
- `legal_viewer_page`
- `toc_viewer_page_start`
- `school_cycle`
- `grade`
- `subject_or_field`
- `publisher_or_institution`
- `source_url`
- `source_repository`
- `access_date`
- `rights_note`
- `availability_status`
- `checksum` si existe una copia de trabajo autorizada

### Semántica de `catalog_generation`

`catalog_generation` conserva literalmente la cohorte/generación con la que el catálogo institucional organiza el visor. Debe permanecer trazable a la fuente de catálogo y **no se utiliza como sustituto de `edition_year`, `reprint_year`, `school_cycle` o `copyright_year`**.

Un análisis longitudinal puede agrupar por `catalog_generation` si la pregunta de investigación se refiere explícitamente a las cohortes del catálogo. Si pretende estudiar cronología editorial, reformas, circulación de ediciones o cambios históricos, debe usar campos bibliográficos observados y documentar la cobertura faltante.

### `edition_year_status`

Valores de trabajo previstos:

- `verified` — año y edición vinculados explícitamente en la página legal o fuente primaria equivalente;
- `unverified` — no se dispone todavía de un año bibliográfico seguro;
- `unverified_candidate_YYYY` — existe una fecha candidata respaldada por evidencia parcial o secundaria, pendiente de verificación suficiente.

### Regla de evidencia bibliográfica

Se registran por separado:

- **edición**: p. ej. `Primera edición`;
- **año de edición**: p. ej. `1998` cuando la fuente dice `Primera edición, 1998`;
- **reimpresión**: p. ej. `Tercera reimpresión`;
- **año de reimpresión**: p. ej. `2017` cuando la fuente lo declara;
- **ciclo escolar**: p. ej. `2017-2018` cuando está impreso en el objeto;
- **copyright_year**: p. ej. `1977` cuando la fuente sólo dice `Derechos reservados SEP, 1977`;
- **generación del catálogo**: clasificación institucional que puede ser distinta de cualquiera de las anteriores.

Esta separación evita fabricar cronologías a partir de etiquetas administrativas.

## Entidad: observación bibliográfica

Las fechas y declaraciones bibliográficas verificables se modelan además en una capa normalizada de observaciones atómicas. La implementación reproducible vigente se materializa en `data/catalog/ltmd_bibliographic_observations.csv`.

Campos mínimos:

- `observation_version`
- `book_id` / `viewer_key`
- `catalog_generation`
- `field`
- `value`
- `evidence_kind`
- `evidence_viewer_page`
- `evidence_source_sha256`
- `extraction_method`
- `human_validated`
- `notes`

### Contrato de una observación

Una observación sólo puede promocionarse a esta capa cuando:

1. la página fuente está identificada inequívocamente;
2. su byte stream corresponde a la huella criptográfica congelada en el manifiesto de procedencia;
3. existe una regla explícita y reproducible que liga el texto observado con el campo y valor;
4. se conserva si la transcripción fue obtenida por OCR técnico o revisada por una persona;
5. la observación no deriva únicamente de `catalog_generation` ni de otra fecha cercana.

`human_validated=0` significa que el valor procede de extracción técnica todavía no revisada manualmente; no borra la procedencia de la página ni convierte el OCR en referencia humana.

## Entidad: página

- `page_id`
- `book_id`
- `viewer_page`
- `source_image_index`
- `page_number_printed`
- `page_type` — portada, legal, índice, contenido, actividad, evaluación, bibliografía, etc.
- `source_sha256`
- `source_byte_size`
- `source_status`
- `ocr_text` — extracción intermedia de trabajo; no se publica íntegra mientras su redistribución no esté aclarada
- `ocr_quality`
- `has_image`
- `has_activity`
- `has_question`
- `has_instruction`

## Entidad: fragmento analítico

- `fragment_id`
- `page_id`
- `fragment_type`
- `text` — material de trabajo sujeto a la política de derechos
- `topic`
- `pedagogical_action`
- `actor_teacher`
- `actor_student`
- `place_reference`
- `person_reference`
- `social_representation`
- `review_status`

## Variables longitudinales candidatas

- vocabulario y conceptos dominantes;
- consignas y tipos de actividad;
- formas de evaluación;
- papel asignado al alumno y al docente;
- ciudadanía y nación;
- género y familia;
- pueblos indígenas e interculturalidad;
- discapacidad e inclusión;
- ciencia y tecnología;
- trabajo y vida cotidiana;
- medio ambiente;
- representación visual.

## Regla para análisis longitudinales

Todo análisis que use una variable temporal debe declarar cuál de estas dimensiones está empleando: `catalog_generation`, `edition_year`, `reprint_year`, `school_cycle` o `copyright_year`. No se permite cambiar de una a otra de manera implícita. Si la cobertura bibliográfica es incompleta, la ausencia forma parte del resultado y no se imputa automáticamente.

Este esquema sigue siendo extensible, pero la separación entre **cohorte de catálogo** y **tiempo bibliográfico observado** queda congelada como regla de integridad del modelo.
