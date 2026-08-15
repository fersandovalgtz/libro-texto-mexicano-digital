# Perfil OCR integral del piloto 0.1 — 15 de agosto de 2026

## Alcance

Se recorrieron las cuatro series de **Ciencias Naturales, quinto grado** del Catálogo Histórico de CONALITEG incluidas en el piloto: generaciones 1972, 1988, 1993 y 2014.

La corrida se realizó con Tesseract en español, `psm 3`, `OMP_THREAD_LIMIT=1` y dos procesos concurrentes. Las imágenes se descargaron únicamente a almacenamiento temporal del runner y no se conservaron. El artefacto de salida contiene métricas por página, no transcripciones.

## Corrección de arquitectura

`claves.json` declara **763 páginas de visor**, pero la auditoría integral mostró que en cada uno de los cuatro libros la última página declarada es una **página terminal sintética sin JPEG**. Por tanto:

| Generación | Páginas declaradas por el visor | JPEG accesibles | Terminal sintética |
|---|---:|---:|---:|
| 1972 | 259 | 258 | 1 |
| 1988 | 163 | 162 | 1 |
| 1993 | 179 | 178 | 1 |
| 2014 | 162 | 161 | 1 |
| **Total** | **763** | **759** | **4** |

Esta distinción queda modelada mediante `page_count` (estructura del visor), `source_asset_count` (activos JPEG) y `asset_status` en el manifiesto. Las páginas terminales ya no deben enviarse a OCR.

## Resultado del barrido sobre los 759 activos

| Generación | JPEG | Páginas con texto | Sin texto detectado | % con texto | Palabras reconocidas | Mediana palabras/pág. textual | Confianza media interna* |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1972 | 258 | 225 | 33 | 87.21 % | 38,502 | 176 | 93.91 |
| 1988 | 162 | 159 | 3 | 98.15 % | 22,181 | 141 | 91.18 |
| 1993 | 178 | 171 | 7 | 96.07 % | 38,725 | 236 | 89.17 |
| 2014 | 161 | 143 | 18 | 88.82 % | 31,041 | 203 | 90.53 |
| **Total** | **759** | **698** | **61** | **91.96 %** | **130,449** | — | — |

\* La confianza interna de Tesseract se usa sólo para triage técnico. **No equivale a precisión científica** y no sustituye CER/WER contra transcripción humana.

## Lecturas preliminares

1. El criterio técnico del piloto de lograr texto procesable en al menos 90 % de las páginas se supera globalmente: **698 de 759 activos (91.96 %) contienen texto detectado**. La interpretación final debe excluir páginas cuyo diseño sea deliberadamente visual, portadas o separadores.
2. **1988** es el volumen más homogéneamente textual: sólo tres páginas válidas quedaron con cero palabras detectadas.
3. **1993** tiene la menor confianza interna media (89.17) y la mayor tasa media de palabras de baja confianza, pero a la vez la mayor densidad textual: mediana de 236 palabras por página textual. Esto hace especialmente importante medir CER/WER en esa generación.
4. **1972 y 2014** contienen proporciones mayores de páginas sin texto detectado. Esto puede reflejar recursos visuales, separadores, diagramas o páginas con texto que el OCR no detectó. Estas páginas deben revisarse como una categoría de diseño y no tratarse automáticamente como fallos.
5. El número de palabras reconocidas **no debe interpretarse todavía como longitud textual real** entre generaciones. Depende del OCR, la maquetación, páginas visuales y estructura editorial.

## Decisión técnica

Tesseract continúa como motor base del piloto. La siguiente validación ya no es de infraestructura sino de **exactitud textual**:

- muestra preregistrada: 48 páginas (legal + índice + 10 posiciones por libro);
- transcripción humana de referencia: 80–150 palabras por página cuando sea posible;
- métricas: CER y WER;
- segunda revisión humana antes de calcular los errores;
- las páginas no se sustituyen retrospectivamente por haber producido OCR difícil.

## Próximo dataset derivado

El siguiente barrido procesará el OCR **en memoria**, descartará inmediatamente la transcripción y conservará sólo señales no sustitutivas del texto fuente, por ejemplo:

- número de signos de interrogación / preguntas candidatas;
- encabezados o marcadores de actividad;
- ocurrencias candidatas de acciones pedagógicas del libro de códigos;
- densidad de instrucciones;
- longitud y estructura de página;
- posición longitudinal.

Estas señales serán indicadores heurísticos para seleccionar y segmentar fragmentos; **no se considerarán codificación pedagógica definitiva** hasta validarlas manualmente.
