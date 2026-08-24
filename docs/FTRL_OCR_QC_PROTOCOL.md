# Protocolo de control de calidad OCR para FTRL

Versión operativa: 0.1

## Propósito

Este protocolo define cómo identificar, ordenar y auditar páginas problemáticas de la Full-Text Research Layer (FTRL) sin publicar el texto OCR reconstruido. La cola de control de calidad es diagnóstica: una bandera de baja confianza no prueba que el texto sea incorrecto, y una página sin banderas no equivale a transcripción verificada.

## Implementación

La referencia ejecutable es `scripts/build_ftrl_qc_queue.py`. Recibe un corpus JSONL FTRL local y genera dos productos sin texto:

- una cola de páginas con identificadores, hashes, métricas, banderas y prioridad;
- un resumen agregado con conteos de banderas y distribución de confianza por generación, grado y objeto canónico.

Los outputs deben permanecer bajo `local/` por defecto, aun cuando estén diseñados para no contener `ocr_text_raw` ni `search_text`.

## Umbrales preregistrados iniciales

Los valores por defecto son deliberadamente conservadores y deben registrarse si se modifican:

- confianza crítica: `< 70`;
- confianza de revisión: `>= 70` y `< 80`;
- texto muy corto: más de cero y menos de 100 caracteres;
- texto de búsqueda vacío: revisión prioritaria;
- confianza ausente: revisión prioritaria;
- cero caracteres o cero palabras OCR: revisión prioritaria.

Estos umbrales sirven para triage técnico y no constituyen una métrica universal de exactitud OCR.

## Priorización

La cola asigna mayor prioridad a páginas sin texto recuperable, seguidas por ausencia de confianza, confianza crítica, confianza de revisión y textos excepcionalmente cortos. La puntuación sólo determina orden de inspección; no debe interpretarse como probabilidad de error.

## Reglas de auditoría

Toda página utilizada para sostener una afirmación historiográfica debe verificarse contra el activo fuente independientemente de su confianza OCR. Las páginas marcadas como `zero_search_text`, `zero_ocr_chars`, `zero_ocr_words` o `missing_confidence` deben revisarse antes de interpretar ausencias léxicas. Las páginas con baja confianza deben considerarse candidatas a re-OCR, cambio de segmentación o inspección visual.

## Separación entre texto y evidencia pública

La cola y el resumen excluyen deliberadamente:

- `ocr_text_raw`;
- `search_text`;
- snippets;
- imágenes fuente.

Conservan hashes SHA-256, identificadores de página y métricas suficientes para vincular cada diagnóstico con la corrida exacta sin redistribuir el contenido textual.

## Criterio para W5 Historia

Después de una corrida integral válida de W5, la cola QC debe generarse sobre el corpus completo y revisarse antes de presentar resultados de las consultas preregistradas. El piloto de diez páginas ya demostró dos casos de interés: una página sin texto recuperado y una página con confianza marcadamente inferior al resto; la corrida completa permitirá determinar si son excepciones aisladas o parte de patrones sistemáticos.
