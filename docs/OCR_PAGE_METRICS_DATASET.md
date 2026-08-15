# Dataset derivado de métricas OCR por página

## Archivo

`data/derived/ocr_page_metrics.csv`

## Propósito

Conservar una capa técnica reproducible entre el manifiesto de páginas y los futuros datasets de fragmentos, **sin publicar ni versionar las transcripciones OCR**.

Cada fila corresponde a uno de los **759 JPEG fuente reales** del piloto 0.1 de *Libro de Texto Mexicano Digital*.

## Procedencia

El archivo procede del barrido OCR adaptativo integral ejecutado en GitHub Actions el **15 de agosto de 2026**:

- workflow: `Full pilot OCR metrics`;
- run ID: `31889772875`;
- commit procesado: `1c69805d32a7ed37adcb0a6ff978f9f85041556d`;
- artefacto validado: `ocr-full-pilot-metrics-adaptive`;
- artifact ID: `9248298948`;
- digest del ZIP: `sha256:40f3c395717c64cc5616bfb520a8974e28a1cb9bbe749e59257973dd046231c5`.

El artefacto fue promovido al repositorio por el workflow `Publish OCR page metrics`, run `31890335720`. Antes del commit, el workflow validó:

- 759 filas de datos;
- 757 `text_detected`;
- 2 `no_text_detected`;
- 0 `unresolved`;
- 698 páginas seleccionadas con `psm 3`;
- 7 con `psm 11`;
- 52 con `psm 6`.

## Columnas

### Identidad y procedencia

- `page_id`: identificador estable de la página en el proyecto.
- `book_id`: identificador del libro.
- `catalog_generation`: generación del Catálogo Histórico de CONALITEG.
- `viewer_page`: posición en el visor.
- `qc_slot`: posición preregistrada para control de calidad cuando corresponde.
- `asset_status`: estado del recurso; en este dataset todos son `source_jpeg` porque los cuatro `terminal_synthetic` no pasan a OCR.
- `source_bytes`: tamaño del JPEG descargado durante la ejecución.

### Ejecución OCR

- `attempts`: registro compacto de los modos probados y su número de palabras, por ejemplo `psm3:ok:0;psm11:ok:8;psm6:ok:14`.
- `selected_psm`: modo finalmente aceptado según la regla OCR 0.1.
- `recognized_words`: número de tokens detectados en la salida seleccionada o, para páginas no aceptadas, en el mejor intento técnico disponible.
- `ocr_chars`: suma de caracteres de los tokens reconocidos.

### Diagnóstico de confianza

- `mean_word_confidence`: media de la confianza interna de Tesseract para los tokens de la página.
- `median_word_confidence`: mediana de esa confianza.
- `low_confidence_word_rate`: proporción de tokens con confianza interna inferior a 60.

Estas medidas **no son CER, WER ni precisión científica**. Se utilizan para triage, comparación técnica y selección de casos que requieren inspección.

### Estado

- `ocr_class`:
  - `text_detected`: la página supera la regla de aceptación;
  - `no_text_detected`: no alcanza el umbral de texto aceptado;
  - `unresolved`: fallo técnico sin una salida interpretable.
- `ocr_status`: `ok` o `error`.
- `error`: diagnóstico técnico cuando existe.

## Regla OCR 0.1 que produjo el dataset

1. ejecutar Tesseract español con `psm 3`;
2. aceptar `psm 3` si produce al menos una palabra;
3. si produce cero o falla, ejecutar `psm 11` y `psm 6`;
4. aceptar un fallback sólo cuando produce **cinco o más palabras**;
5. si ambos fallbacks superan el umbral, elegir el de mayor número de palabras y usar confianza como desempate;
6. una salida de 1–4 tokens en fallback no convierte la página en `text_detected`;
7. no procesar filas `terminal_synthetic`.

## Lo que este dataset permite

- medir cobertura del OCR por generación;
- localizar páginas que requirieron fallback;
- estudiar la distribución técnica de confianza;
- seleccionar casos para validación humana;
- enlazar métricas con `page_id` sin distribuir el texto fuente;
- reproducir controles de calidad y perfiles técnicos.

## Lo que este dataset no permite por sí solo

- afirmar que el texto OCR es exacto;
- comparar vocabulario o semántica sin validar CER/WER;
- inferir que una generación tiene mayor complejidad pedagógica a partir de confianza OCR;
- considerar `recognized_words` como longitud textual histórica exacta;
- clasificar acciones pedagógicas o posiciones del alumno.

## Relación con la validación humana

La muestra primaria CER/WER contiene 48 páginas preregistradas antes de la evaluación adaptativa. Debe auditarse contra este dataset para comprobar qué modos OCR están representados. Si los fallbacks aparecen insuficientemente representados, se añadirá un **estrato suplementario de estrés OCR**, sin alterar ni sustituir la muestra primaria preregistrada.
