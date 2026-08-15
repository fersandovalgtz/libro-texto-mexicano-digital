# Método para construir la hipótesis OCR privada de una región CER/WER

## Problema

Cuando la referencia humana utiliza `crop_block`, existen dos maneras posibles de producir la hipótesis OCR:

1. recortar primero la imagen y ejecutar Tesseract sobre ese recorte; o
2. ejecutar el pipeline de página completa y extraer después los tokens cuyas cajas espaciales caen dentro del recorte.

El proyecto adopta la **opción 2**.

## Razón

Recortar una imagen antes de OCR puede modificar sustancialmente la segmentación de página y, por tanto, cambiar el comportamiento de Tesseract. Si el objetivo de CER/WER es validar **el pipeline OCR 0.1 que se aplica al corpus**, no debemos sustituirlo por un problema artificialmente más simple creado después de seleccionar la región humana.

## Regla operativa

Para cada página de referencia:

1. consultar `data/derived/ocr_page_metrics.csv`;
2. obtener el `selected_psm` congelado por el pipeline OCR 0.1;
3. descargar temporalmente el JPEG oficial;
4. ejecutar Tesseract sobre la **página completa** usando ese `psm` y salida TSV;
5. para `full_page`, conservar todos los tokens válidos;
6. para `crop_block`, convertir las coordenadas normalizadas del recorte a píxeles;
7. conservar los tokens cuyo **centro geométrico** cae dentro del rectángulo;
8. reconstruir el orden textual utilizando el orden TSV y los identificadores `block_num`, `par_num`, `line_num`, `word_num`;
9. guardar esa transcripción únicamente en el campo privado `ocr_region_text_private`;
10. borrar la imagen temporal;
11. calcular CER/WER sólo después de que la referencia humana haya sido revisada.

## Coordenadas

La selección utiliza:

- `crop_x0`
- `crop_y0`
- `crop_x1`
- `crop_y1`

normalizadas en `[0,1]`.

Un token pertenece al recorte cuando el centro de su bounding box cumple:

`x0_px <= center_x <= x1_px`

`y0_px <= center_y <= y1_px`

## Por qué usar el centro de la caja

La regla del centro evita decisiones ambiguas cuando una palabra toca ligeramente el borde del rectángulo. Es simple, determinista y reproducible. Si durante la validación humana se observa que esta regla corta sistemáticamente palabras de borde, el cambio deberá documentarse y versionarse antes de recalcular métricas.

## PSM congelado

No se vuelve a elegir el modo OCR mirando la referencia humana.

El `selected_psm` procede del dataset permanente:

`data/derived/ocr_page_metrics.csv`

Esto conserva la separación entre:

- selección técnica del OCR, realizada antes de CER/WER; y
- evaluación humana de exactitud, realizada después.

## Script

El procedimiento está implementado en:

`scripts/build_private_ocr_reference_hypotheses.py`

El script:

- lee un CSV privado exportado de la hoja de Google Drive;
- usa `page_id` para obtener el `selected_psm` público;
- descarga la imagen a un directorio temporal;
- ejecuta TSV de página completa;
- filtra por región cuando corresponde;
- produce un CSV **privado** que contiene `ocr_region_text_private`;
- no debe ejecutarse en un workflow público que publique el resultado como artefacto;
- no debe commitearse su salida.

## Relación con `evaluate_ocr_cer_wer.py`

El evaluador fue actualizado para aceptar directamente el esquema privado de Drive:

- `sample_id`
- `generation`
- `page_id`
- `reference_scope`
- coordenadas normalizadas
- `human_reference_text_private`
- `ocr_region_text_private`

Su salida excluye ambos textos y conserva únicamente:

- metadatos de la región;
- longitudes;
- distancias de edición;
- CER;
- WER;
- estado de evaluación.

## Seguridad de publicación

El código es público y reproducible. Los datos textuales privados no lo son.

Éste es un caso deliberado de **reproducibilidad del método sin redistribución de la expresión completa de la fuente**.
