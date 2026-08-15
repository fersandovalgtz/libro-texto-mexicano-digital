# Addendum de alineación CER/WER con el pipeline real — 15 de agosto de 2026

## Estatus y precedencia

Este addendum **complementa y, donde exista conflicto, sustituye** la interpretación operativa de `docs/OCR_TRANSCRIPTION_CONVENTIONS.md` respecto de cómo obtener la hipótesis OCR de una región de validación.

Se registra antes de inspeccionar el resultado de la nueva corrida correctiva de página completa.

## Problema detectado

El primer lote de validación 1972 ejecutó Tesseract 5.3.4 directamente sobre tres **recortes** fijados para la referencia humana. Sin embargo, el pipeline OCR 0.1 utilizado para procesar los 759 activos ejecuta Tesseract sobre la **página completa**.

El reconocimiento de un recorte puede diferir del reconocimiento de la misma zona cuando el motor procesa la página completa. Un recorte puede simplificar el layout, eliminar distractores y producir una estimación de error artificialmente optimista.

Por tanto, las métricas obtenidas mediante `crop → Tesseract` se conservan como **calibración de región**, pero quedan **superseded** como estimación de exactitud del pipeline productivo.

## Regla corregida

Para validar el pipeline OCR 0.1:

1. ejecutar Tesseract sobre la **imagen fuente completa**, no sobre el recorte;
2. usar exactamente el `selected_psm` que el pipeline adaptativo asignó a esa página (`data/derived/ocr_page_metrics.csv`);
3. solicitar salida TSV para conservar cajas de palabras y orden de lectura del motor;
4. la región humana continúa fijándose por coordenadas de imagen, independientemente del OCR;
5. extraer del TSV sólo los tokens OCR cuyo **centro geométrico** `(x + width/2, y + height/2)` caiga dentro de la región fijada;
6. reconstruir la hipótesis regional respetando el orden TSV: palabras separadas por espacio y líneas OCR separadas por salto de línea;
7. aplicar después las normalizaciones ortográfica y léxica preregistradas;
8. calcular CER/WER contra la referencia humana de la misma región.

### Regla de frontera

Se usa el **centro de la caja de palabra** en vez de intersección parcial para evitar decisiones ambiguas cuando un bounding box toca marginalmente el límite del recorte.

Para una región `x0,y0,x1,y1`, se incluye una palabra si:

`x0 <= x_center < x1` y `y0 <= y_center < y1`.

No se modifica una región para capturar o excluir una palabra después de conocer el OCR.

## Páginas `full_page`

Cuando `reference_scope=full_page`, se utiliza todo el texto producido por el modo OCR seleccionado para la página, manteniendo el orden de lectura del TSV/texto del motor.

## Fallback adaptativo

La validación debe corresponder al **modo finalmente seleccionado por el pipeline**, no necesariamente `psm 3`.

Ejemplo ya conocido del corpus: la página 246 de la generación 1972 fue procesada por el fallback `psm 6`; cuando sea validada, su hipótesis de referencia será la salida de página completa de `psm 6`, no una nueva corrida de recorte con `psm 3`.

## Consecuencia para el primer lote 1972

Las métricas productivas reportadas previamente para LEGAL, TOC y Q1_1 mediante OCR directo del recorte se mantienen en la bitácora como antecedente de calibración, pero **no serán usadas en los agregados CER/WER del piloto**.

Se ejecutará una corrida correctiva con:

- Tesseract 5.3.4;
- imagen completa;
- `psm 3` para las tres páginas, pues ése es el modo seleccionado en el barrido adaptativo;
- salida TSV de página completa;
- selección regional por centro de bounding box;
- mismo SHA-256 de fuente;
- mismas regiones humanas ya congeladas.

Las métricas resultantes serán las primeras cifras técnicamente alineadas al pipeline real; aun así seguirán marcadas como provisionales hasta la segunda revisión humana independiente.

## Gobernanza

El TSV y el texto completo de página son material privado de trabajo por su capacidad de reconstruir contenido. No se versionan ni se suben legibles a GitHub. Cuando sea necesario transportarlos desde el runner, se empleará ciphertext de un solo uso; GitHub conservará públicamente únicamente metadatos técnicos y métricas no sustitutivas.

## Regla para los siguientes lotes

No se calculará ningún nuevo CER/WER del piloto con `crop → OCR`. El recorte define la **región de evaluación humana**; la hipótesis debe extraerse siempre del OCR de **página completa del pipeline productivo**.
