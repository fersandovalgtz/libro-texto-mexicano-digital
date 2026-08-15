# Validación OCR provisional — muestra primaria 1988

Fecha: 15 de agosto de 2026  
Estado: **provisional; pendiente de revisión humana independiente**

## Alcance

Se completaron técnicamente las 12 posiciones preregistradas de la muestra primaria del libro de **Ciencias Naturales, quinto grado, generación de catálogo 1988**.

Este documento no publica transcripciones de referencia ni OCR extenso. La capa textual permanece en Drive privado. Las métricas derivadas se encuentran en `data/derived/ocr_validation_1988_provisional.csv`.

## Método

- Tesseract 5.3.4, español.
- OCR sobre página completa.
- `selected_psm=3` en las 12 posiciones de esta generación.
- Región de evaluación fijada independientemente.
- Hipótesis regional reconstruida desde TSV mediante centro geométrico de las cajas de palabra.
- Orden de lectura conservado tal como lo entrega Tesseract; no hay reordenamiento post hoc en pipeline 0.1.
- CER/WER léxico como familia principal; CER/WER ortográfico como control editorial.
- Referencias actuales: borradores visuales aún pendientes de revisión humana independiente.

## Corrección de infraestructura durante el cierre

La página 155 reveló que un token OCR puede empezar con una comilla doble literal. El parser TSV anterior utilizaba quoting CSV por defecto, lo que podía absorber filas posteriores ante una comilla no balanceada. Se corrigió `scripts/extract_region_from_tsv.py` para leer Tesseract TSV con `quoting=csv.QUOTE_NONE` y se añadió una prueba de regresión.

La auditoría de las 24 hipótesis privadas persistidas de 1972–1988 encontró una sola hipótesis con comilla doble: vp155, el caso ya corregido. Los TSV de algunos lotes anteriores ya habían sido eliminados conforme a la política de retención mínima, por lo que este control retroactivo se documenta como auditoría de las hipótesis persistidas, no como reinspección de todos los TSV históricos.

## Resultados provisionales

Las 12 posiciones son textuales y tienen métricas calculadas.

Promedios macro por página:
- CER léxico: **0.074785**
- WER léxico: **0.121609**
- CER ortográfico: **0.081964**
- WER ortográfico: **0.140160**

Medianas:
- CER léxico: **0.007945**
- WER léxico: **0.042455**

Estas medias están fuertemente influidas por dos casos adversos de layout; por ello no deben interpretarse sin distribución.

### Sólo cuerpo del libro — 10 posiciones posicionales

- media macro CER léxico: **0.033196**
- media macro WER léxico: **0.065931**
- mediana CER léxico: **0.006960**
- mediana WER léxico: **0.036700**

## Casos adversos principales

### Índice — vp003

- CER léxico: **0.558242**
- WER léxico: **0.750000**

La estructura de lista, numeración, líderes y ruido gráfico degrada fuertemente el reconocimiento y la secuencia.

### Primera posición corporal — vp016

- CER léxico: **0.251534**
- WER léxico: **0.344828**

El principal problema no es sólo reconocimiento de caracteres: Tesseract divide la frase superior en bloques y los emite en un orden de lectura incorrecto. Este caso motivó la regla de no reordenar geométricamente después de observar resultados; cualquier reordenador futuro deberá evaluarse como pipeline 0.2.

### vp155

- CER léxico: **0.022648**
- WER léxico: **0.047872**

Además de errores OCR reales, esta página sirvió para descubrir el bug de parsing de comillas en TSV. Las métricas aquí reportadas ya corresponden al parser corregido.

## Lectura técnica provisional

El desempeño es **heterogéneo por layout**. La mediana es baja, mientras el promedio aumenta por unos pocos casos difíciles. Las páginas corporales de texto lineal suelen situarse en rangos bajos de CER/WER; índices y bloques con orden espacial complejo son los principales riesgos.

No se concluye todavía que la generación sea apta o no apta para análisis léxico fino. Esa decisión requiere completar la revisión humana independiente y comparar las cuatro generaciones con el mismo protocolo.

## Estado del piloto

- 1972: 12/12 posiciones técnicamente procesadas.
- 1988: 12/12 posiciones técnicamente procesadas.
- total: **24/48 = 50 %** de la muestra primaria técnicamente trabajada.

La siguiente generación a procesar es **1993**.