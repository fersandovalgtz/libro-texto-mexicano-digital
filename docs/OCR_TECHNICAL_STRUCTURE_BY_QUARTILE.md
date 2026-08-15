# Perfil técnico OCR por cuartiles del libro — piloto 0.1

**Fecha:** 15 de agosto de 2026.

## Propósito

Comprobar si la dificultad OCR, el uso de fallback y la densidad técnica de texto están distribuidos uniformemente a lo largo de cada libro.

Este análisis es **puramente técnico**. No permite todavía inferir cambios pedagógicos, curriculares o de complejidad cognitiva.

Fuente:

`data/derived/ocr_structure_by_quartile.csv`

El cuartil se calcula usando `viewer_page / page_count`, la misma convención estructural utilizada en el diseño de muestreo.

## Resumen de fallbacks

| Generación | Q1 | Q2 | Q3 | Q4 | Total fallback |
|---|---:|---:|---:|---:|---:|
| 1972 | 13/64 | 10/65 | 2/65 | 8/64 | 33/258 |
| 1988 | 1/40 | 1/41 | 1/41 | 0/40 | 3/162 |
| 1993 | 0/44 | 2/45 | 2/45 | 3/44 | 7/178 |
| 2014 | 3/40 | 6/41 | 4/40 | 3/40 | 16/161 |

### Tasas aproximadas

- **1972:** Q1 20.3 %, Q2 15.4 %, Q3 3.1 %, Q4 12.5 %.
- **1988:** Q1 2.5 %, Q2 2.4 %, Q3 2.4 %, Q4 0 %.
- **1993:** Q1 0 %, Q2 4.4 %, Q3 4.4 %, Q4 6.8 %.
- **2014:** Q1 7.5 %, Q2 14.6 %, Q3 10.0 %, Q4 7.5 %.

## Hallazgo técnico 1 — 1972 no tiene dificultad uniforme

El primer cuarto de 1972 necesitó fallback en 13 de 64 páginas y el segundo cuarto en 10 de 65. El tercer cuarto, en cambio, sólo necesitó fallback en 2 de 65.

Las medias de confianza por página muestran el mismo efecto de composición:

- Q1 = 81.25
- Q2 = 84.66
- Q3 = 92.46
- Q4 = 85.30

Sin embargo, la **mediana** de confianza permanece alrededor de 94–95 en los cuatro cuartiles. Esto indica que la caída de la media está impulsada por un subconjunto de páginas muy difíciles, no por degradación uniforme de todas las páginas.

**Implicación metodológica:** no interpretar una media baja de confianza de toda la generación como mala legibilidad general. La distribución es heterogénea y sesgada por outliers/fallbacks.

## Hallazgo técnico 2 — 1988 es el volumen más estable

1988 sólo requiere tres fallbacks en 162 activos:

- uno en Q1;
- uno en Q2;
- uno en Q3;
- ninguno en Q4.

La confianza media por cuartil asciende progresivamente de 87.86 a 92.43, mientras la tasa media de tokens de baja confianza baja de 7.6 % en Q1 a 2.2 % en Q4.

Este patrón puede deberse a diseño, escaneo, densidad u otras propiedades materiales. **No debe interpretarse todavía como cambio de estilo pedagógico.**

## Hallazgo técnico 3 — 1993 presenta alta densidad textual OCR y dificultad relativamente distribuida

Mediana de palabras reconocidas por página textual:

- Q1 = 217.5
- Q2 = 235
- Q3 = 257
- Q4 = 220

Los fallbacks aparecen principalmente desde Q2 y aumentan ligeramente hacia Q4, pero la confianza media permanece bastante estable alrededor de 86.8–87.7.

La mayor densidad OCR de 1993 respecto de 1972/1988 **no equivale todavía a mayor cantidad real de texto ni complejidad conceptual**. Debe verificarse CER/WER y considerar tipografía/layout.

## Hallazgo técnico 4 — 2014 concentra fallbacks en Q2

Fallbacks:

- Q1: 3
- Q2: 6
- Q3: 4
- Q4: 3

Q2 presenta la confianza media más baja de la generación (81.42) y la tasa media más alta de palabras de baja confianza (18.4 %).

Las dos páginas que no alcanzan el umbral final están en:

- Q3: visor 102, `visual_or_marginal_text`;
- Q4: visor 157, página completamente blanca.

Por ello, el 98.76 % de cobertura textual de 2014 no representa una falla general de la generación.

## Tamaño técnico de los JPEG

El tamaño medio de archivo refuerza una diferencia material ya observada:

- 1972: aproximadamente 67–71 KB por página según cuartil;
- 1988: aproximadamente 52–65 KB;
- 1993: aproximadamente 75–86 KB;
- 2014: aproximadamente 433–557 KB.

Esto refleja diferencias de digitalización/compresión/resolución y debe considerarse al comparar comportamiento OCR.

## Regla para análisis posteriores

Toda comparación que utilice texto OCR deberá conservar al menos:

- `catalog_generation`;
- `viewer_page`;
- posición/cuatril;
- `selected_psm`;
- confianza OCR técnica;
- CER/WER de la generación/estrato cuando esté disponible.

Cuando se comparen acciones pedagógicas o vocabulario, deberá comprobarse que un supuesto efecto temporal no sea simplemente un efecto de:

- posición dentro del libro;
- tipo de página;
- modo OCR;
- calidad de digitalización;
- densidad de texto.

## Decisión

El perfil por cuartiles se incorpora como **variable de control técnico** del piloto. No se utilizará como resultado historiográfico autónomo.
