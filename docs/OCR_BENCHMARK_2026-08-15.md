# Benchmark OCR basal — 15 de agosto de 2026

## Propósito

Medir la viabilidad inicial de OCR sobre la muestra posicional preregistrada del piloto sin conservar en GitHub imágenes fuente ni transcripciones OCR extensas.

Motor basal: **Tesseract, idioma español, `--psm 3`**.

Muestra: 40 páginas, 10 por generación, seleccionadas antes de observar el resultado OCR.

## Resultado basal

| Generación | Páginas | Ejecuciones terminadas | Timeouts | Páginas con texto reconocido | Páginas terminadas con 0 palabras | Confianza media en páginas con texto* |
|---|---:|---:|---:|---:|---:|---:|
| 1972 | 10 | 5 | 5 | 4 | 1 | 93.13 |
| 1988 | 10 | 3 | 7 | 3 | 0 | 93.06 |
| 1993 | 10 | 0 | 10 | 0 | 0 | — |
| 2014 | 10 | 6 | 4 | 2 | 4 | 91.73 |
| **Total** | **40** | **14** | **26** | **9** | **5** | — |

\* La confianza de Tesseract es una métrica diagnóstica interna del motor. **No equivale a precisión científica** y no sustituye CER/WER contra una referencia humana.

## Lectura técnica

El resultado no permite concluir que las páginas sean ilegibles. De hecho, cuando `psm 3` termina sobre páginas con texto, las confianzas medias son altas (~91–96 % en los casos observados). El problema dominante es la robustez de la segmentación automática del layout: 26/40 páginas agotan el timeout de 90 segundos.

La generación 1993 es el caso crítico: 10/10 páginas de la muestra basal agotaron el timeout con `psm 3`. Por tanto, escalar directamente este modo a las 763 páginas sería metodológicamente y operacionalmente incorrecto.

En 2014 aparecen dos fenómenos distintos: timeouts y páginas que terminan correctamente pero con cero palabras. Estas últimas pueden corresponder a páginas predominantemente visuales, diseños que requieren otra segmentación o falsos negativos OCR. Deben mantenerse como categoría separada.

## Decisión

No se descarta Tesseract. Se reemplaza el enfoque monolítico por un pipeline adaptativo:

1. `psm 6` como primer intento breve;
2. `psm 11` como fallback para texto disperso;
3. timeout corto por intento;
4. distinguir `text_detected`, `no_text_detected` y `unresolved`;
5. medir calidad real con CER/WER sobre una muestra manual;
6. si 1993 continúa fallando, crear una segunda ruta OCR específica para esa generación.

Script adaptativo: `scripts/ocr_adaptive_metrics.py`.

Workflow: `.github/workflows/ocr-adaptive.yml`.

## Criterio provisional para conservar Tesseract como motor base

La prueba adaptativa deberá reducir sustancialmente los fallos respecto de `psm 3`. Como regla operativa provisional, se buscará una tasa de páginas no resueltas inferior a 10–15 % en la muestra de control. El umbral es una decisión interna del piloto, no un estándar general de OCR.

La decisión definitiva se tomará después de medir CER/WER y no únicamente a partir de confianza del motor o tiempo de ejecución.
