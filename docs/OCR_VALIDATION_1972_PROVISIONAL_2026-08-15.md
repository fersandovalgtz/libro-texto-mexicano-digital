# Validación OCR provisional — muestra primaria 1972

**Fecha:** 15 de agosto de 2026  
**Estado:** 12/12 posiciones técnicamente procesadas y alineadas al pipeline; **pendiente de revisión humana independiente**.

## Alcance

Este documento resume la capa técnica de validación CER/WER de las 12 páginas preregistradas para el ejemplar de **Ciencias Naturales, quinto grado, generación de catálogo 1972**.

No contiene transcripciones de referencia ni OCR extenso. El material textual de trabajo se mantiene en Google Drive privado. Las métricas públicas canónicas están en:

`data/derived/ocr_cer_wer_1972_provisional.csv`

## Integridad de la referencia

Las referencias actuales son **borradores visuales asistidos por IA**, no referencias humanas finales. La cadena científica del proyecto es:

`imagen fuente → borrador visual → revisión humana independiente → referencia congelada → CER/WER final`

Por esta razón, todas las cifras de este documento son **diagnósticos técnicos provisionales**.

## Alineación con el pipeline real

La evaluación reproduce el procesamiento productivo:

1. Tesseract se ejecuta sobre la **página completa**;
2. se usa exactamente el `selected_psm` del barrido adaptativo;
3. se obtiene TSV completo con cajas de palabras;
4. la región de referencia se fija visualmente sin usar CER/WER para optimizarla;
5. se seleccionan palabras cuyo centro geométrico cae dentro de la región;
6. se reconstruye la hipótesis en orden TSV;
7. se calculan métricas léxicas y ortográficas.

El procedimiento está documentado en `docs/OCR_REGION_ALIGNMENT_ADDENDUM_2026-08-15.md` y `scripts/extract_region_from_tsv.py`.

Las primeras pruebas `crop → OCR` fueron identificadas como metodológicamente no equivalentes al pipeline real y quedaron **superseded** para los agregados.

## Configuración OCR

- Tesseract 5.3.4;
- idioma español;
- `OMP_THREAD_LIMIT=1` en la infraestructura productiva;
- `selected_psm` específico por página;
- páginas 4–215 de esta muestra: `psm 3`;
- página 246: `psm 6`, porque el pipeline adaptativo produjo cero palabras con `psm 3` y eligió el fallback con mayor conteo;
- TXT/TSV e imágenes de trabajo transportados sólo dentro de bundles cifrados transitorios y nunca versionados legiblemente en GitHub.

## Composición final de la muestra 1972

- **12/12** posiciones preregistradas conservadas, sin sustitución;
- **11** posiciones con referencia textual evaluable;
- **1** posición `visual_only` (`VP246`), mantenida en la muestra pero fuera del denominador CER/WER;
- front matter textual: 2 páginas (legal + índice);
- cuerpo textual: 9 páginas;
- cuerpo visual-only: 1 página.

## Resultados página a página — provisionales

| rol | visor | clase | PSM | CER lex | WER lex | CER ort | WER ort |
|---|---:|---|---:|---:|---:|---:|---:|
| legal | 4 | textual | 3 | 0.033694 | 0.083333 | 0.034803 | 0.084746 |
| toc | 7 | textual | 3 | 0.234711 | 0.365079 | 0.284579 | 0.444444 |
| q1_1 | 26 | textual | 3 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q1_2 | 52 | textual | 3 | 0.000000 | 0.000000 | 0.002041 | 0.013699 |
| q2_1 | 85 | textual | 3 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q2_2 | 109 | textual | 3 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q2_3 | 124 | textual | 3 | 0.000000 | 0.000000 | 0.001148 | 0.006623 |
| q3_1 | 150 | textual | 3 | 0.001626 | 0.009524 | 0.003210 | 0.019048 |
| q3_2 | 174 | textual | 3 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3_3 | 189 | textual | 3 | 0.000000 | 0.000000 | 0.002584 | 0.028571 |
| q4_1 | 215 | textual | 3 | 0.035176 | 0.094737 | 0.036244 | 0.105263 |
| q4_2 | 246 | visual_only | 6 | — | — | — | — |

`lex` = normalización léxica, criterio principal para viabilidad analítica.  
`ort` = normalización ortográfica, control secundario.

## Agregados descriptivos provisionales

Los siguientes son **macro-promedios simples por página**, no CER/WER micro agrupado por caracteres/palabras. Se publican como diagnóstico provisional; después de la revisión humana podrán recalcularse los agregados finales a partir de conteos de edición.

| estrato | n textual | CER lex macro | WER lex macro | CER ort macro | WER ort macro |
|---|---:|---:|---:|---:|---:|
| front matter | 2 | 0.134203 | 0.224206 | 0.159691 | 0.264595 |
| cuerpo | 9 | **0.004089** | **0.011585** | 0.005025 | 0.019245 |
| total textual | 11 | 0.027746 | 0.050243 | 0.033146 | 0.063854 |

Mediana corporal provisional:
- CER léxico = **0**;
- WER léxico = **0**.

De las 9 regiones corporales textuales, **7 presentan CER léxico=0 y WER léxico=0** en el borrador de referencia actual.

Las dos regiones corporales textuales no exactas son:
- VP150: error léxico muy pequeño (CER 0.001626; WER 0.009524);
- VP215: diagrama anatómico con cajas de texto (CER 0.035176; WER 0.094737).

## Front matter

La diferencia entre cuerpo y front matter es marcada:

- página legal: CER léxico 0.033694, WER 0.083333;
- índice: CER léxico 0.234711, WER 0.365079.

El índice combina numeración, lista vertical y layout complejo. Por diseño, estos resultados no se ocultan ni se eliminan, pero tampoco se utilizan por sí solos para juzgar la viabilidad de la codificación pedagógica del cuerpo del libro.

## Página visual-only VP246

La fuente de VP246 es una ilustración sin texto lingüístico visible dentro de la región de evaluación. El único folio queda fuera del recorte. La política correspondiente está preregistrada en `docs/OCR_VISUAL_ONLY_POLICY.md`.

CER/WER no se define porque la referencia es vacía; no se asigna CER=0 ni se sustituye la página.

El pipeline adaptativo había seleccionado **`psm 6`**. Sobre la región visual sin texto humano, ese fallback produjo:

- **112 palabras léxicas espurias**;
- **323 caracteres léxicos espurios**;
- **121 cajas TSV de palabra**;
- `visual_false_positive = 1`.

Este caso demuestra de forma particularmente clara que **cobertura OCR ≠ exactitud**. El barrido técnico puede marcar una página como `text_detected` aunque el texto reconocido sea ruido generado por elementos gráficos.

## Lectura técnica provisional

La tipografía/prosa corporal de 1972 parece altamente procesable bajo el pipeline actual. Sin embargo, el desempeño depende fuertemente del tipo de layout:

- prosa, preguntas e instrucciones lineales: generalmente exactas o casi exactas;
- cajas/diagramas: error mayor;
- índices/listas complejas: error alto;
- páginas visual-only: riesgo de falsos positivos severos bajo fallback.

Por tanto, el siguiente pipeline analítico no debe depender sólo de `recognized_words > 0`. Necesitará distinguir clases de página y conservar control humano para layouts complejos.

## Procedencia de corridas canónicas

- legal, índice y Q1_1: `31893239228`;
- Q1_2, Q2_1 y Q2_2: `31893410279`;
- Q2_3, Q3_1 y Q3_2: `31893764533`;
- Q3_3, Q4_1 y Q4_2: `31894086256`.

Los SHA-256 de las fuentes, regiones y métricas están versionados en `data/derived/ocr_cer_wer_1972_provisional.csv`.

## Gobernanza y trazabilidad

- referencias e hipótesis OCR: Google Drive privado;
- métricas, estados y narrativa metodológica: Notion;
- métricas, hashes, protocolos y código: GitHub;
- imágenes/TXT/TSV: copias temporales dentro de bundle cifrado cuando se requiere transporte;
- workflows transitorios, claves privadas y plaintext destruidos después de sincronización.

## Condición para cerrar científicamente 1972

La capa técnica de las 12 posiciones queda completa. **No se considera validación científica final** hasta que una segunda revisión humana independiente:

1. verifique las 11 referencias textuales;
2. confirme la clasificación visual-only de VP246 y la exclusión del folio;
3. adjudique cualquier discrepancia de transcripción;
4. congele la referencia;
5. permita recalcular las métricas y agregados definitivos.

Una vez cumplido esto, 1972 puede funcionar como primera generación de referencia para comparar 1988, 1993/1998 y 2014.
