# Benchmark OCR — 15 de agosto de 2026

## Propósito

Medir la viabilidad inicial de OCR sobre la muestra posicional preregistrada del piloto sin conservar en GitHub imágenes fuente ni transcripciones OCR extensas.

Motor: **Tesseract, idioma español**.

## Prueba 1 — benchmark basal concurrente

Configuración inicial: `--psm 3`, 40 páginas, 10 por generación, 4 procesos concurrentes.

| Generación | Páginas | Ejecuciones terminadas | Timeouts | Páginas con texto reconocido | Páginas terminadas con 0 palabras | Confianza media en páginas con texto* |
|---|---:|---:|---:|---:|---:|---:|
| 1972 | 10 | 5 | 5 | 4 | 1 | 93.13 |
| 1988 | 10 | 3 | 7 | 3 | 0 | 93.06 |
| 1993 | 10 | 0 | 10 | 0 | 0 | — |
| 2014 | 10 | 6 | 4 | 2 | 4 | 91.73 |
| **Total** | **40** | **14** | **26** | **9** | **5** | — |

\* La confianza de Tesseract es una métrica diagnóstica interna del motor. **No equivale a precisión científica** y no sustituye CER/WER contra una referencia humana.

La primera lectura sugería que el layout podía ser el principal problema, especialmente en 1993.

## Prueba 2 — cambio de segmentación con concurrencia

Se probaron 8 páginas, dos por generación, con `psm 6 → psm 11`, timeout de 25 s por intento y 4 procesos concurrentes.

Resultado: **8/8 páginas quedaron sin resolver por timeout**. Cambiar el modo de segmentación no corrigió el problema bajo esa carga concurrente.

## Prueba 3 — control serial

Para separar el efecto del layout del efecto de la concurrencia se ejecutó una página por generación de forma **serial**, con `OMP_THREAD_LIMIT=1` y secuencia `psm 3 → 6 → 11`.

Las cuatro páginas fueron resueltas inmediatamente por el **primer intento, `psm 3`**:

| Generación | Página del visor | Palabras reconocidas | Confianza media | Confianza mediana | Palabras <60 de confianza |
|---|---:|---:|---:|---:|---:|
| 1972 | 26 | 34 | 95.89 | 96.66 | 0.00 % |
| 1988 | 16 | 30 | 91.72 | 93.67 | 0.00 % |
| 1993 | 18 | 281 | 92.88 | 96.07 | 1.78 % |
| 2014 | 16 | 246 | 90.68 | 96.10 | 6.10 % |

## Diagnóstico revisado

El principal problema observado en los benchmarks iniciales es **sobresuscripción/concurrencia de Tesseract en el runner de GitHub Actions**, no una incapacidad intrínseca del motor para leer 1993 ni una falla general del layout.

La evidencia decisiva es que la misma página de 1993 que agotó 90 s durante la corrida concurrente fue procesada correctamente en el control serial y produjo 281 palabras con confianza media de 92.88.

Por tanto:

- **Tesseract continúa como candidato fuerte a motor base del piloto**;
- no se justifica por ahora cambiar de motor únicamente por los timeouts del primer benchmark;
- tampoco se justifica una ruta OCR especial para 1993 en esta etapa;
- la siguiente optimización debe buscar el nivel seguro de concurrencia (`1` vs `2` procesos) con `OMP_THREAD_LIMIT=1`;
- `psm 3` vuelve a ser el modo basal, con fallback sólo para páginas que terminen sin texto o fallen realmente.

## Pipeline provisional

1. descargar una página a almacenamiento temporal;
2. ejecutar Tesseract `spa`, inicialmente `psm 3`;
3. limitar hilos/procesos para evitar sobresuscripción;
4. si el resultado es cero palabras o falla, aplicar fallback controlado (`psm 6`/`11` o preprocesamiento);
5. clasificar por separado `text_detected`, `no_text_detected` y `unresolved`;
6. conservar OCR íntegro sólo como extracción de trabajo;
7. publicar métricas y datos derivados;
8. medir calidad real mediante CER/WER contra transcripción humana.

## Próxima prueba

Determinar la concurrencia estable mínima/óptima sobre una muestra multipágina. Si dos procesos con `OMP_THREAD_LIMIT=1` mantienen una tasa de resolución alta, se usarán para el piloto; si reaparecen timeouts, el procesamiento se mantendrá serial.

Scripts/workflows relevantes:

- `scripts/ocr_sample_metrics.py`
- `scripts/ocr_adaptive_metrics.py`
- `.github/workflows/ocr-serial-diagnostic.yml`
- `.github/workflows/ocr-adaptive.yml`

La decisión científica sobre calidad OCR seguirá dependiendo de **CER/WER**, no de la confianza interna de Tesseract.
