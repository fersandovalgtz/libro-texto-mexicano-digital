# Validación OCR provisional — muestra primaria 1972

Fecha: 15 de agosto de 2026  
Estado: **provisional; pendiente de revisión humana independiente**

## Alcance

Este documento resume la capa técnica de validación CER/WER de las 12 páginas preregistradas para el ejemplar de **Ciencias Naturales, quinto grado, generación de catálogo 1972**.

No contiene transcripciones de referencia ni OCR extenso. El material textual de trabajo se mantiene en una capa privada. Las métricas públicas están en:

`data/derived/ocr_cer_wer_1972_provisional.csv`

## Integridad de la referencia

Las referencias actuales son **borradores visuales asistidos por IA**. No deben presentarse como referencias humanas finales. La cadena científica fijada para el proyecto es:

`imagen fuente → borrador visual → revisión humana independiente → referencia congelada → CER/WER final`

Por esta razón, todas las cifras aquí reportadas son **diagnósticos técnicos provisionales**.

## Alineación con el pipeline real

La evaluación no utiliza `crop → OCR` como métrica final. Para cada región evaluable:

1. se ejecuta Tesseract sobre la **página completa**;
2. se obtiene TSV con cajas de palabras;
3. la región de referencia se fija antes de conocer CER/WER;
4. se seleccionan palabras cuyo centro geométrico cae dentro del rectángulo preregistrado;
5. se reconstruye la hipótesis en orden TSV;
6. se calculan métricas léxicas y ortográficas.

Véase `docs/OCR_REFERENCE_ALIGNMENT_PROTOCOL.md`.

## Configuración OCR

- Tesseract 5.3.4
- idioma: español
- `psm 3`
- OCR de página completa
- texto/TSV de trabajo transportado cifrado y no versionado públicamente

## Resultado de la muestra

De las 12 páginas preregistradas:

- **11** contienen una región lingüísticamente evaluable;
- **1** (`VP246`) es una página ilustrada sin texto lingüísticamente relevante y queda `excluded_justified`, sin sustitución;
- **7 de 11** regiones evaluables tienen `WER_lexical = 0`;
- mediana de WER léxico: **0**;
- media macro de WER léxico: **0.050243**;
- media macro de CER léxico: **0.027746**;
- máximo WER léxico: **0.365079**, correspondiente al índice;
- máximo CER léxico: **0.234711**, también correspondiente al índice.

Estas medias son promedios simples por región, no tasas agrupadas por caracteres/palabras.

Como diagnóstico secundario únicamente, si se retira el índice —sin modificar la muestra oficial— la media macro de WER de las otras diez regiones evaluables es **0.018759** y la media macro de CER es **0.007050**. Este cálculo no debe sustituir la estimación principal.

## Patrón técnico observado

Los resultados sugieren una heterogeneidad marcada por **tipo de layout**:

- texto corrido, preguntas y consignas: generalmente exactos o casi exactos;
- metadatos con nombres propios: error moderado;
- índices/listas complejas y diagramas con cajas: errores sustancialmente mayores.

Por ello, en etapas posteriores no conviene describir la calidad OCR de un libro mediante una sola media sin acompañarla de distribución, tipo de página y casos adversos.

## Casos adversos principales

### Índice — VP007

- CER léxico: 0.234711
- WER léxico: 0.365079

La combinación de numeración, líderes, alineación visual y lista vertical degrada fuertemente el orden/reconocimiento.

### Diagrama del sistema nervioso — VP215

- CER léxico: 0.035176
- WER léxico: 0.094737

El layout de cajas y líneas de llamada produce sustituciones, omisiones y pequeños errores léxicos aun cuando la imagen es legible.

### Página ilustrada — VP246

Tesseract 5.3.4 produjo **0 tokens de palabra** en la página completa. La observación se conserva en la muestra, pero CER/WER no se define porque no existe texto lingüístico de referencia.

## Procedencia de las corridas

- legal, índice y Q1_1: `31893239228`
- Q1_2, Q2_1 y Q2_2: `31893410279`
- Q2_3, Q3_1 y Q3_2: `31893764533`
- Q3_3, Q4_1 y diagnóstico Q4_2: `31894060892`

Los hashes SHA-256 de cada fuente se encuentran en el CSV derivado público.

## Próximo paso

Repetir el mismo protocolo técnico con las 12 páginas primarias de la generación **1988**. En paralelo, la revisión humana independiente deberá convertir los borradores visuales en referencias congeladas para producir las métricas científicas finales de las 48 páginas primarias.