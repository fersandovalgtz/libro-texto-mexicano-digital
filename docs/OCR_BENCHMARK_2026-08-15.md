# Benchmark OCR — 15 de agosto de 2026

## Propósito

Medir la viabilidad de OCR sobre el piloto sin conservar en GitHub imágenes fuente ni transcripciones OCR extensas.

Motor: **Tesseract, idioma español**.

> La confianza interna de Tesseract es una métrica diagnóstica del motor. **No equivale a precisión científica** y no sustituye CER/WER contra una referencia humana.

## Prueba 1 — benchmark basal concurrente

Configuración inicial: `--psm 3`, 40 páginas preregistradas, 10 por generación, 4 procesos concurrentes.

| Generación | Páginas | Ejecuciones terminadas | Timeouts | Texto reconocido | 0 palabras | Confianza media en páginas con texto |
|---|---:|---:|---:|---:|---:|---:|
| 1972 | 10 | 5 | 5 | 4 | 1 | 93.13 |
| 1988 | 10 | 3 | 7 | 3 | 0 | 93.06 |
| 1993 | 10 | 0 | 10 | 0 | 0 | — |
| 2014 | 10 | 6 | 4 | 2 | 4 | 91.73 |
| **Total** | **40** | **14** | **26** | **9** | **5** | — |

La primera lectura sugería un posible problema de layout, especialmente en 1993.

## Prueba 2 — cambio de segmentación con concurrencia

Se probaron 8 páginas con `psm 6 → psm 11`, timeout de 25 s y 4 procesos concurrentes.

Resultado: **8/8 quedaron sin resolver por timeout**. Cambiar segmentación no corrigió el problema bajo esa carga.

## Prueba 3 — control serial

Se ejecutó una página por generación de forma serial, con `OMP_THREAD_LIMIT=1` y secuencia `psm 3 → 6 → 11`.

Las cuatro fueron resueltas por el primer intento, `psm 3`:

| Generación | Página visor | Palabras | Confianza media | Mediana | Palabras <60 |
|---|---:|---:|---:|---:|---:|
| 1972 | 26 | 34 | 95.89 | 96.66 | 0.00 % |
| 1988 | 16 | 30 | 91.72 | 93.67 | 0.00 % |
| 1993 | 18 | 281 | 92.88 | 96.07 | 1.78 % |
| 2014 | 16 | 246 | 90.68 | 96.10 | 6.10 % |

Esto aisló el problema principal: **sobresuscripción de CPU/concurrencia**, no incapacidad del motor ni fallo intrínseco de 1993.

## Prueba 4 — dos procesos controlados

Configuración: `OMP_THREAD_LIMIT=1`, dos procesos, `psm 3`, ocho páginas (dos por generación).

Resultado: **8/8 resueltas, 0 timeouts, 0 unresolved**. Siete páginas produjeron texto y una terminó correctamente con cero palabras, clasificada como `no_text_detected`.

Ejemplos relevantes:

- 1993, página 18: 281 palabras, confianza media 92.88;
- 1993, página 170: 111 palabras, confianza media 87.58;
- 2014, página 154: 232 palabras, confianza media 91.19.

Se adopta por tanto **dos procesos + `OMP_THREAD_LIMIT=1`** como configuración operativa del piloto.

## Prueba 5 — benchmark estable de las 40 páginas preregistradas

Configuración definitiva provisional: Tesseract `spa`, `psm 3`, dos procesos, `OMP_THREAD_LIMIT=1`, timeout 60 s.

Resultado: **40/40 páginas resueltas; 0 timeouts; 0 unresolved**.

| Generación | Páginas | Con texto | Sin texto detectado | Unresolved | Confianza media en páginas textuales | Palabras reconocidas |
|---|---:|---:|---:|---:|---:|---:|
| 1972 | 10 | 9 | 1 | 0 | 94.27 | 1,270 |
| 1988 | 10 | 10 | 0 | 0 | 92.25 | 1,311 |
| 1993 | 10 | 10 | 0 | 0 | 87.09 | 2,283 |
| 2014 | 10 | 6 | 4 | 0 | 91.39 | 1,399 |
| **Total** | **40** | **35** | **5** | **0** | — | **6,263** |

Las cinco páginas sin texto detectado no son fallos de ejecución: Tesseract terminó normalmente con cero palabras. Una corresponde a 1972 y cuatro a 2014. Deberán revisarse posteriormente como páginas predominantemente visuales o como falsos negativos de segmentación.

## Diagnóstico y decisión

- **Tesseract queda adoptado como motor base provisional del piloto.**
- `psm 3` queda como modo basal.
- La configuración operativa es dos procesos con `OMP_THREAD_LIMIT=1`.
- No se justifica un motor separado para 1993 en esta fase.
- 1993 muestra confianza interna menor y mayor proporción de palabras de baja confianza; debe recibir atención especial en CER/WER.
- Las páginas con cero palabras se mantienen separadas de los fallos técnicos.
- La calidad científica real se decidirá mediante CER/WER sobre una referencia humana.

## Pipeline provisional

1. descargar una página a almacenamiento temporal;
2. ejecutar Tesseract `spa`, `psm 3`, con concurrencia controlada;
3. clasificar `text_detected`, `no_text_detected` o `unresolved`;
4. aplicar fallback sólo a cero-texto/fallos que lo justifiquen;
5. conservar OCR íntegro únicamente como extracción de trabajo;
6. publicar métricas y datos derivados;
7. medir CER/WER contra transcripción humana;
8. escalar después a segmentación página → fragmento → actividad/consigna.

## Siguiente escalamiento

Se ejecutará el mismo pipeline sobre las **763 páginas del piloto** para producir únicamente métricas OCR por página y estadísticas agregadas por generación. Ningún texto OCR completo ni imagen fuente será publicado como artefacto.

Scripts/workflows relevantes:

- `scripts/ocr_sample_metrics.py`
- `scripts/ocr_adaptive_metrics.py`
- `.github/workflows/ocr-serial-diagnostic.yml`
- `.github/workflows/ocr-two-worker-diagnostic.yml`
- `.github/workflows/ocr-qc-final.yml`
- `.github/workflows/ocr-full-pilot-metrics.yml`
