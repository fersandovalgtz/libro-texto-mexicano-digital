# Política de orden de lectura en validación OCR

**Fecha:** 15 de agosto de 2026  
**Motivo:** primer caso explícito detectado en `LTMD-CER-1988-Q1_1` (visor 16).

## Problema

La exactitud OCR no se limita a reconocer caracteres o palabras. En páginas con imágenes, columnas, cajas o bloques separados, Tesseract puede reconocer correctamente tokens individuales pero emitirlos en un **orden de lectura incorrecto**.

En la página 16 de la generación 1988, una frase situada en la parte superior es segmentada por Tesseract en más de un bloque. La secuencia TSV/texto productiva no conserva el orden lingüístico visible de la fuente. Este error eleva CER/WER aunque una parte importante de los tokens sea reconocible individualmente.

## Regla para pipeline OCR 0.1

1. CER/WER debe evaluar la salida que realmente produce el pipeline 0.1.
2. La extracción regional conserva el orden de Tesseract definido por `page_num, block_num, par_num, line_num, word_num`.
3. **No se reordenan tokens retrospectivamente** después de observar una página con CER/WER alto.
4. No se usa la referencia humana para decidir un orden que minimice la distancia de edición.
5. Un fallo de lectura/segmentación espacial cuenta como error del pipeline, no como excepción que deba borrarse.

## Posible pipeline 0.2

Puede explorarse después una ruta específica de reconstrucción geométrica del orden de lectura, por ejemplo:

- clustering por bandas horizontales;
- ordenamiento por coordenadas `top/left` dentro de bandas;
- detección de columnas/cajas;
- modelos de layout/document understanding.

Pero cualquier método de este tipo deberá:

1. definirse como una **nueva versión** del pipeline;
2. fijar sus reglas antes de evaluar el conjunto completo;
3. recalcular la muestra CER/WER correspondiente;
4. compararse contra OCR 0.1 sin sustituir silenciosamente los resultados originales.

## Reporte

Las páginas cuyo principal problema sea el orden de lectura se etiquetarán en notas técnicas como `reading_order_failure`. Cuando el número de casos lo justifique, se añadirá una variable derivada estructurada para cuantificar su frecuencia por generación/layout.

## Gobernanza

La evidencia textual que permite diagnosticar el orden incorrecto permanece en Drive privado. GitHub puede registrar page_id, tipo de fallo, métricas y regla metodológica, pero no la transcripción/OCR extenso.
