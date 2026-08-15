# Modelo de datos mínimo — borrador 0.2

## Principio temporal

El proyecto distingue explícitamente entre **generación del catálogo** y **año bibliográfico de la edición concreta**. Una etiqueta como `1993` en el Catálogo Histórico de CONALITEG agrupa una generación de materiales y no debe copiarse automáticamente como fecha de publicación. El año de edición sólo se fija después de verificar la página legal o una fuente bibliográfica suficientemente sólida.

## Entidad: libro

Campos iniciales:

- `book_id`
- `title`
- `catalog_generation`
- `edition_year`
- `edition_year_status`
- `school_cycle`
- `grade`
- `subject_or_field`
- `publisher_or_institution`
- `edition`
- `isbn`
- `source_url`
- `source_repository`
- `access_date`
- `rights_note`
- `availability_status`
- `checksum` si existe una copia de trabajo autorizada

### `edition_year_status`

Valores de trabajo previstos:

- `verified` — año comprobado en la página legal o fuente primaria equivalente;
- `unverified` — no se dispone todavía de un año bibliográfico seguro;
- `unverified_candidate_YYYY` — existe una fecha candidata respaldada por una fuente secundaria o reproducción, pendiente de cotejo con el ejemplar oficial.

## Entidad: página

- `page_id`
- `book_id`
- `page_number_printed`
- `page_number_file`
- `page_type` — portada, legal, índice, contenido, actividad, evaluación, bibliografía, etc.
- `ocr_text`
- `ocr_quality`
- `has_image`
- `has_activity`
- `has_question`
- `has_instruction`

## Entidad: fragmento analítico

- `fragment_id`
- `page_id`
- `fragment_type`
- `text`
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
