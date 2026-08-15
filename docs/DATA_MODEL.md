# Modelo de datos mínimo — borrador 0.1

## Entidad: libro

Campos iniciales:

- `book_id`
- `title`
- `year`
- `school_cycle`
- `grade`
- `subject_or_field`
- `publisher_or_institution`
- `edition`
- `source_url`
- `source_repository`
- `access_date`
- `rights_note`
- `checksum` si existe una copia de trabajo autorizada

## Entidad: página

- `page_id`
- `book_id`
- `page_number_printed`
- `page_number_file`
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
