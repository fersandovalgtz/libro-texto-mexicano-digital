# Perfil OCR integral del piloto 0.1 — 15 de agosto de 2026

## Alcance

Se recorrieron las cuatro series de **Ciencias Naturales, quinto grado** del Catálogo Histórico de CONALITEG incluidas en el piloto: generaciones 1972, 1988, 1993 y 2014.

Las imágenes se descargaron únicamente a almacenamiento temporal de GitHub Actions y no se conservaron. Los artefactos generados contienen métricas por página, no transcripciones OCR completas.

## Corrección de arquitectura

`claves.json` declara **763 páginas de visor**, pero la auditoría integral mostró que en cada uno de los cuatro libros la última página declarada es una **página terminal sintética sin JPEG**.

| Generación | Páginas de visor | JPEG fuente | Terminal sintética |
|---|---:|---:|---:|
| 1972 | 259 | 258 | 1 |
| 1988 | 163 | 162 | 1 |
| 1993 | 179 | 178 | 1 |
| 2014 | 162 | 161 | 1 |
| **Total** | **763** | **759** | **4** |

La distinción queda modelada mediante `page_count`, `source_asset_count` y `asset_status`. Los `terminal_synthetic` se conservan en el manifiesto estructural pero se excluyen de OCR.

## Etapa A — barrido basal `psm 3`

Configuración: Tesseract español, `OMP_THREAD_LIMIT=1`, dos procesos concurrentes, `psm 3`.

| Generación | JPEG | Con texto | Sin texto basal | % texto basal | Palabras técnicas | Confianza media interna* |
|---|---:|---:|---:|---:|---:|---:|
| 1972 | 258 | 225 | 33 | 87.21 % | 38,502 | 93.91 |
| 1988 | 162 | 159 | 3 | 98.15 % | 22,181 | 91.18 |
| 1993 | 178 | 171 | 7 | 96.07 % | 38,725 | 89.17 |
| 2014 | 161 | 143 | 18 | 88.82 % | 31,041 | 90.53 |
| **Total** | **759** | **698** | **61** | **91.96 %** | **130,449** | — |

El resultado basal superaba ya el umbral técnico preregistrado de 90 %, pero no se aceptó como cobertura definitiva.

## Etapa B — auditoría de las 61 páginas sin texto basal

Cada una de las 61 páginas se reintentó con `psm 11` y `psm 6`, además de medir su complejidad visual. No se conservaron transcripciones.

Resultado:

- 59 de 61 fueron recuperadas por segmentación alternativa;
- 1972: 33/33 recuperadas;
- 1988: 3/3;
- 1993: 7/7;
- 2014: 16/18;
- 2014 visor 157 es una imagen completamente blanca;
- 2014 visor 102 contiene señal visual pero sólo produce recuperación OCR marginal y de muy baja confianza.

Este resultado demostró que la mayoría de los `no_text_detected` basales eran **falsos negativos de segmentación**, no páginas intrínsecamente no textuales.

## Etapa C — barrido adaptativo integral definitivo

Se reejecutaron **los 759 JPEG desde cero** con la regla OCR 0.1:

1. `psm 3` como modo basal;
2. si produce ≥1 palabra, se acepta;
3. si produce cero o falla, ejecutar `psm 11` y `psm 6`;
4. un fallback sólo se acepta si produce ≥5 palabras;
5. si ambos superan el umbral, se selecciona el de mayor número de palabras; la confianza desempata;
6. 1–4 tokens de fallback no convierten la página en `text_detected`.

Configuración de ejecución:

- GitHub Actions Ubuntu 24.04;
- Python 3.12.13;
- Tesseract 5.3.4;
- modelo `tesseract-ocr-spa`;
- `OMP_THREAD_LIMIT=1`;
- dos procesos concurrentes;
- timeout 60 s;
- run reproducible: workflow `Full pilot OCR metrics`, corrida 2 del 15 de agosto de 2026.

### Resultado definitivo de cobertura

| Generación | JPEG | Texto aceptado | Sin texto | `psm 3` | `psm 11` | `psm 6` | Cobertura |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1972 | 258 | 258 | 0 | 225 | 5 | 28 | 100.00 % |
| 1988 | 162 | 162 | 0 | 159 | 0 | 3 | 100.00 % |
| 1993 | 178 | 178 | 0 | 171 | 1 | 6 | 100.00 % |
| 2014 | 161 | 159 | 2 | 143 | 1 | 15 | 98.76 % |
| **Total** | **759** | **757** | **2** | **698** | **7** | **52** | **99.74 %** |

No hubo ningún activo JPEG `unresolved`.

El pipeline detectó **135,228 palabras aceptadas como texto**. Además existen dos tokens marginales de la página 2014 visor 102 que se conservan en métricas técnicas pero **no se aceptan como extracción textual**, por lo que `recognized_words_all_metrics` es 135,230 y `accepted_text_words` es 135,228.

## Confianza interna después de incorporar páginas difíciles

Confianza media interna por página textual en el barrido adaptativo:

- 1972: 85.94
- 1988: 90.14
- 1993: 87.08
- 2014: 84.69

Estas medias son **más bajas que en el barrido basal**, especialmente en 1972 y 2014, porque el corpus adaptativo incorpora las páginas difíciles que `psm 3` dejaba fuera. La disminución no significa que el OCR haya empeorado: es un efecto de composición de la muestra.

\* En todas las etapas, la confianza de Tesseract es únicamente una métrica diagnóstica interna. **No equivale a precisión científica**.

## Las dos páginas no textuales finales

### 2014, visor 157

Imagen 969 × 1276 totalmente blanca: media de gris 255, desviación 0, entropía 0, cero píxeles oscuros. Se clasifica como página blanca fuente, no como fallo OCR.

### 2014, visor 102

La página contiene señal visual. Modos estándar no producen texto robusto. Una prueba adicional con autocontraste, ampliación 2×, nitidez y Otsu llegó como máximo a 14 tokens, pero con confianza media 37.48 y 71.43 % de tokens por debajo de confianza 60. Se mantiene como **`visual_or_marginal_text`**, no como texto procesable.

## Qué queda demostrado y qué no

### Demostrado técnicamente

- los cuatro libros pueden enumerarse reproduciblemente;
- existen 759 JPEG fuente válidos;
- 757/759 tienen texto detectable bajo la regla OCR 0.1;
- ninguna generación requiere, por ahora, otro motor OCR para alcanzar cobertura;
- la estrategia adaptativa corrige prácticamente todos los falsos negativos de `psm 3`.

### Todavía no demostrado

- que las transcripciones sean suficientemente exactas para análisis léxico fino;
- que la confianza de Tesseract represente CER/WER;
- que los fragmentos puedan segmentarse automáticamente con validez pedagógica;
- que las categorías del libro de códigos puedan automatizarse sin error sistemático.

## Siguiente prueba científica: CER/WER humano

La infraestructura OCR queda técnicamente cerrada para el piloto. La siguiente validación es de **exactitud**, no de cobertura.

Muestra preregistrada: 48 páginas, cuatro grupos de 12 (página legal, índice y 10 posiciones por libro). Se construirá referencia humana y se calcularán CER/WER. Las transcripciones de referencia y el OCR íntegro permanecerán fuera del repositorio público; se versionarán únicamente métricas derivadas.

## Validación del libro de códigos

En paralelo existe un pool preregistrado de 100 páginas, 25 por generación. La codificación pedagógica definitiva sólo comenzará tras revisión humana. Notion contiene una base específica de validación con los 100 candidatos y campos para tipos funcionales, acciones pedagógicas, posiciones del alumno, dimensiones, notas y segunda revisión.

## Archivos derivados relevantes

- `data/derived/ocr_full_pilot_baseline_summary.csv` — conserva el barrido basal `psm 3` para trazabilidad;
- `data/derived/ocr_full_pilot_summary.csv` — resumen adaptativo definitivo;
- `data/derived/no_text_page_register.csv` — 61 falsos negativos/casos basales auditados;
- `data/derived/no_text_page_audit_summary.csv` — resultado resumido de la auditoría;
- `docs/NO_TEXT_PAGE_AUDIT_2026-08-15.md` — interpretación de la fase de fallback.

## Decisión de fase

La **viabilidad de acceso + cobertura OCR** del piloto 0.1 se considera demostrada. No se justifica seguir optimizando cobertura antes de medir exactitud humana. El frente activo pasa a:

1. CER/WER humano;
2. validación manual del libro de códigos;
3. segmentación página → fragmento;
4. primer dataset analítico e interpretación histórica.
