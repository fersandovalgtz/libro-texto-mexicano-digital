# Modelo de datos mínimo — borrador 0.3

## Principio temporal

El proyecto distingue explícitamente entre **generación del catálogo**, **año bibliográfico de la edición concreta** y **año de derechos/copyright**. Una etiqueta como `1993` en el Catálogo Histórico de CONALITEG agrupa una generación de materiales y no debe copiarse automáticamente como fecha de publicación. Del mismo modo, una línea `Derechos reservados SEP, 1977` demuestra un año de derechos, pero no necesariamente una edición publicada en 1977 si la página no lo declara así.

El año de edición sólo se fija como `verified` cuando la página legal o una fuente primaria equivalente lo vincula explícitamente con una edición.

## Entidad: libro

Campos iniciales:

- `book_id`
- `title`
- `catalog_generation`
- `edition_year`
- `edition_year_status`
- `edition`
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

### `edition_year_status`

Valores de trabajo previstos:

- `verified` — año y edición vinculados explícitamente en la página legal o fuente primaria equivalente;
- `unverified` — no se dispone todavía de un año bibliográfico seguro;
- `unverified_candidate_YYYY` — existe una fecha candidata respaldada por evidencia parcial o secundaria, pendiente de verificación suficiente.

### Regla de evidencia bibliográfica

Se registran por separado:

- **edición**: p. ej. `Primera edición`;
- **año de edición**: p. ej. `1998` cuando la fuente dice `Primera edición, 1998`;
- **copyright_year**: p. ej. `1977` cuando la fuente sólo dice `Derechos reservados SEP, 1977`;
- **generación del catálogo**: clasificación histórica de CONALITEG que puede ser distinta de cualquiera de las anteriores.

Esta separación evita fabricar cronologías a partir de etiquetas administrativas.

## Entidad: página

- `page_id`
- `book_id`
- `viewer_page`
- `source_image_index`
- `page_number_printed`
- `page_type` — portada, legal, índice, contenido, actividad, evaluación, bibliografía, etc.
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

Este esquema es deliberadamente mínimo. Ningún campo se considera definitivo hasta probarlo con el corpus piloto.
