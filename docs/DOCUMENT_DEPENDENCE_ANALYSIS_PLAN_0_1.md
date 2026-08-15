# Plan de análisis de dependencia documental — LTMD 0.1

Fecha de congelación: 2026-08-15

## Problema

La expansión CN4/CN6 demostró dos formas distintas de dependencia que invalidan una lectura ingenua de `catalog_generation` como observación temporal independiente:

1. **reutilización masiva entre generaciones**: CN4/1972 y CN4/1988 comparten 188 de 214 páginas alineadas byte-idénticas (87.9%);
2. **sucesión de objetos dentro de la misma generación**: CN6 bajo `catalog_generation=1993` contiene un volumen temprano de *Ciencias Naturales* y su reemplazo de *Ciencias Naturales y desarrollo humano*, primera edición 1999.

Este plan se fija antes de aplicar cualquier clasificador semántico a la expansión.

## Unidad temporal/documental mínima

Los análisis futuros no usarán únicamente `catalog_generation`. Cada observación deberá conservar como mínimo:

- `book_id`;
- `viewer_key`;
- `catalog_generation`;
- `edition_year` y estatus de verificación;
- `document_role` cuando exista relación de sucesión;
- `page_id`;
- `source_sha256` o `text_sha256` según el nivel analizado;
- `document_cluster_id` cuando exista dependencia demostrada.

## Tipos de relación

### A. `exact_page_reuse`

Dos páginas de objetos distintos tienen el mismo SHA-256 de activo fuente. Prueba identidad binaria del recurso recuperado.

**Regla:** no contar esas páginas como dos evidencias independientes de cambio o continuidad textual. Para estadísticas de contenido se reportará tanto prevalencia por objeto como prevalencia sobre contenido único/deduplicado cuando la pregunta lo requiera.

### B. `near_text_reuse`

Las imágenes difieren, pero OCR normalizado muestra similitud muy alta predefinida (diagnóstico actual ≥0.95).

**Regla:** tratar como posible remaquetación/reescaneo; conservar ambos objetos, pero incluir análisis de sensibilidad que colapse dichas unidades a contenido equivalente.

### C. `localized_revision`

Un par de libros presenta reutilización masiva junto con un subconjunto localizado de páginas material/textualmente distintas.

**Regla:** describir el cambio a dos niveles:

- **base heredada** — páginas reutilizadas;
- **zona revisada** — páginas diferentes.

No atribuir la prevalencia global del libro revisado íntegramente a innovación de la fecha posterior.

### D. `replacement_within_generation`

Dos objetos de igual grado/asignatura y `catalog_generation` tienen evidencia histórica/bibliográfica de sucesión.

**Regla:** ambos permanecen en el corpus con `document_role` distinto. No promediar automáticamente dentro de la generación; reportar edición/rol y, sólo para resúmenes agregados, definir previamente una política de ponderación.

### E. `parallel_variant`

Dos objetos aparentemente coetáneos sin evidencia suficiente de sucesión o equivalencia.

**Regla:** conservar ambos y marcar `relation_status=unresolved`; no elegir uno silenciosamente.

## Clusters iniciales

### `DOCcluster-CN4-continuity-72-88`

Miembros:

- `LTMD-CN4-G1972`
- `LTMD-CN4-G1988`

Relación: `localized_revision` con base de 188 páginas byte-idénticas y 26 páginas cambiadas.

### `DOCcluster-CN6-reform-1990s`

Miembros:

- `LTMD-CN6-G1993-CN`
- `LTMD-CN6-G1993-DH`

Relación: `replacement_within_generation`; objeto temprano históricamente asociado con primera edición 1994 y reemplazo con primera edición 1999.

## Inferencia longitudinal

Cuando exista clasificación semántica validada, se deberán producir al menos tres vistas:

1. **object view**: cada libro como objeto editorial completo;
2. **unique-content view**: páginas/fragmentos byte/textualmente duplicados no aportan peso duplicado;
3. **revision view**: compara específicamente unidades heredadas versus unidades revisadas en relaciones `localized_revision`.

Una transición se considerará históricamente más convincente si su dirección se mantiene en las vistas pertinentes y no depende exclusivamente de duplicación de contenido.

## Dependencia estadística

Los intervalos de incertidumbre no deberán asumir independencia de fragmentos:

- fragmentos anidados en página;
- páginas anidadas en libro;
- libros relacionados por reutilización o sucesión.

Para el piloto/expansión pequeña, se priorizarán bootstrap o permutaciones agrupadas por la unidad documental relevante en lugar de errores estándar iid.

## Uso de `catalog_generation`

`catalog_generation` se conserva porque documenta la organización del Catálogo Histórico y puede ser históricamente informativa. Sin embargo:

> **no se utilizará como sustituto automático de `edition_year`, ni como identificador de una versión documental única.**

## Regla contra deduplicación destructiva

La detección de duplicados **no elimina** páginas/libros del archivo lógico. La procedencia de cada aparición se conserva. La deduplicación es una vista analítica reversible, nunca una operación que borra la historia editorial.

## Estado

`DOCUMENT_DEPENDENCE_PLAN_0.1 = FROZEN_PRE_SEMANTIC_EXPANSION`
