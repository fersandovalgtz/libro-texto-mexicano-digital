# Protocolo suplementario de validación de unidades breves residuales

Versión: `SHORT_RESIDUAL_VALIDATION_0.1`

## Problema

FRAGSEG 0.2 llamó `heading_candidate` a toda unidad residual de ≤12 tokens y ≤100 caracteres que no activó señales funcionales previas. Como esa regla no usa tipografía ni geometría, la etiqueta no demuestra que la unidad sea un encabezado real. Además, SEMB 0.2 omitió automáticamente todas esas unidades.

La capa shadow `FRAGTYPE_0.3_SHADOW` demuestra que 2,392 unidades de ese grupo tienen al menos cuatro tokens y podrían ser candidatas a análisis semántico. Antes de incorporarlas a SEMB 0.3 se requiere validación suplementaria independiente.

## Muestra

Se congelan 160 fragmentos: 40 por generación, seleccionados únicamente entre antiguos `heading_candidate` con ≥4 tokens mediante hash determinista. Se asignan 100 a desarrollo de la política de elegibilidad (25 por generación) y 60 a validación bloqueada (15 por generación).

## Cegamiento

El anotador sólo recibe un ID opaco. No conoce generación, rol development/locked, etiquetas A/B ni resultados históricos. A diferencia de la referencia semántica principal, esta tarea idealmente debe observar **el fragmento y su contexto visual de página**, porque la pregunta `is_typographic_heading` es tipográfica y no puede resolverse sólo con OCR.

## Variables

- `is_typographic_heading`: 1/0/u.
- `is_semantic_unit`: 1 si la unidad expresa contenido o una consigna interpretable de manera autónoma; 0 si es ruido/fragmento no interpretable; u si es ambiguo.
- `actionable`: 1/0/u.
- `functional_class`: `heading`, `expository`, `instruction`, `question`, `label_caption`, `other`.
- `confidence`: 1–3.
- `note`: observación de ambigüedad.

## Decisión de elegibilidad

La política de inclusión para SEMB 0.3 se desarrollará sólo con los 100 casos de desarrollo y se congelará antes de abrir los 60 bloqueados. La pregunta principal no es si FRAGSEG 0.2 'acertó' el nombre, sino si una regla reproducible puede separar unidades semánticamente analizables de verdaderos encabezados/etiquetas/ruido sin depender de la generación histórica.

## Prohibición

No se podrá decidir incluir o excluir estas unidades en función de que aumenten, reduzcan o aclaren las diferencias entre 1972, 1988, 1993 y 2014.
