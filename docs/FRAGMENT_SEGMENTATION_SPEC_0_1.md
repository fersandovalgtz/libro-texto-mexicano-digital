# Especificación de segmentación automática página → fragmento 0.1

## Objetivo

Transformar el corpus piloto desde la unidad página a unidades funcionales trazables (`fragment_id`) adecuadas para clasificación pedagógica computacional, sin revisión humana y sin publicar texto extenso de los libros.

## Dependencia

Esta fase sólo se ejecuta después de disponer de `data/derived/page_structure.csv` congelado. La clasificación estructural decide qué páginas son elegibles para análisis textual primario.

## Elegibilidad

### Segmentación primaria

Pasan a segmentación pedagógica:

- `textual`
- `mixed_text_image`

### Conservación sin segmentación pedagógica primaria

Se conservan en el inventario pero no entran al análisis body-only inicial:

- `visual_only`
- `front_matter`
- `toc_or_navigation`
- `bibliography_or_credits`
- `unknown`

Una fase posterior podrá procesar selectivamente `front_matter` o `unknown`, pero nunca se mezclará silenciosamente con body text.

## Entrada textual

Para cada página elegible se ejecutará Tesseract 5.3.4 en español con el `selected_psm` ya congelado por OCR adaptativo 0.1. El OCR completo se tratará como material de trabajo privado/efímero; GitHub sólo recibirá derivados no sustitutivos.

El TSV se leerá con `delimiter='\t'` y `quoting=csv.QUOTE_NONE` conforme a la decisión vigente sobre tokens con comillas.

## Reconstrucción mínima

1. conservar orden nativo del TSV;
2. agrupar palabras por `(block_num, par_num, line_num)`;
3. reconstruir líneas sin reordenamiento geométrico post hoc;
4. formar unidades candidatas mediante límites de bloque/párrafo y señales lingüísticas;
5. no unir automáticamente contenido de bloques separados si la distancia/orden indica componentes funcionales distintos.

## Señales de frontera de fragmento

Se considera frontera fuerte cuando ocurre alguno de estos eventos:

- cambio de bloque OCR;
- encabezado corto aislado;
- marcador de actividad/proyecto/experimento/evaluación;
- inicio de viñeta o paso numerado;
- interrogación que constituye una consigna autónoma;
- secuencia imperativa nueva después de cierre de oración;
- cambio claro entre texto expositivo y consigna;
- separación vertical excepcional dentro del mismo bloque cuando pueda derivarse del TSV.

Se considera frontera débil:

- cambio de párrafo OCR;
- línea corta seguida de bloque largo;
- transición entre pregunta y respuesta/explicación;
- lista de materiales seguida de procedimiento.

## Tipos estructurales candidatos de fragmento

La segmentación puede emitir, como rasgo preliminar y no como clasificación pedagógica final:

- `expository_candidate`
- `instruction_candidate`
- `question_candidate`
- `activity_candidate`
- `experiment_candidate`
- `project_candidate`
- `assessment_candidate`
- `heading_candidate`
- `other_candidate`

Estos rasgos se basan en señales lingüísticas explícitas y no sustituyen a los clasificadores A/B de la etapa posterior.

## Identificador

Formato recomendado:

`{page_id}-F{secuencia:03d}`

Ejemplo: `LTMD-CN5-G2014-VP109-F004`.

El identificador es determinista para una versión concreta del segmentador. Si cambia el algoritmo de segmentación y cambian fronteras, se incrementa la versión y se regeneran IDs; no se reutilizan IDs para fragmentos semánticamente distintos.

## Dataset público derivado

`data/derived/fragment_manifest.csv` contendrá como mínimo:

- `fragment_id`
- `page_id`
- `book_id`
- `catalog_generation`
- `viewer_page`
- `fragment_sequence`
- `candidate_type`
- `token_count`
- `char_count`
- `question_mark_count`
- `imperative_signal_count`
- `material_signal`
- `project_signal`
- `experiment_signal`
- `text_sha256`
- `segmenter_version`
- `source_structure_class`
- `uncertain_boundary`

No contendrá el texto completo del fragmento.

## Capa privada

Cuando sea necesario conservar texto para la clasificación semántica B, se generará una tabla privada con `fragment_id + fragment_text`. Debe permanecer fuera del repositorio público. Si se produce en CI, se transportará cifrada; si se persiste, se depositará en Drive privado.

## Controles automáticos

- unicidad de `fragment_id`;
- cada fragmento refiere exactamente a un `page_id` existente;
- ninguna página `visual_only` produce fragmentos pedagógicos;
- ningún fragmento tiene conteo negativo/cero salvo categorías explícitas de encabezado si se decide conservarlas;
- suma de fragmentos por generación y distribución de tamaños;
- detectar fragmentos extremos (>500 tokens) como posibles fallos de frontera;
- detectar páginas elegibles con cero fragmentos como fallo/`uncertain`;
- producir reporte de sensibilidad variando umbrales de unión/división.

## Política de incertidumbre

No se corregirán manualmente fronteras. Los casos ambiguos se etiquetarán `uncertain_boundary=1` y podrán excluirse del análisis principal o incorporarse en análisis de sensibilidad.
