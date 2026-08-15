# Auditoría de páginas sin texto basal — 15 de agosto de 2026

## Problema

El barrido integral con Tesseract español y `psm 3` produjo texto en 698 de los 759 JPEG del piloto. Las 61 páginas restantes fueron clasificadas inicialmente como `no_text_detected`.

No se asumió que esas 61 páginas fueran errores OCR. Podían ser:

- páginas gráficas;
- páginas casi vacías;
- separadores;
- páginas con layout incompatible con `psm 3`;
- falsos negativos del modo basal.

## Procedimiento

Se creó `data/derived/no_text_page_register.csv` con las 61 páginas exactas derivadas del artefacto integral de OCR.

`scripts/audit_no_text_pages.py` procesó cada página sin conservar transcripciones:

1. descarga temporal del JPEG;
2. métricas visuales: dimensiones, media y desviación de gris, entropía, proporción de píxeles oscuros, proporción de píxeles muy oscuros y señal de bordes;
3. reintento OCR con `psm 11` y `psm 6`;
4. conservación únicamente de conteos y confianza interna;
5. clasificación técnica conservadora.

Configuración:

- Tesseract 5.3.4;
- modelo español del paquete `tesseract-ocr-spa`;
- `OMP_THREAD_LIMIT=1`;
- dos procesos concurrentes;
- timeout 45 s por modo;
- Pillow para métricas de imagen.

## Resultado

| Generación | Sin texto con `psm 3` | Recuperadas por fallback | Compleja sin recuperación | Baja señal sin recuperación |
|---|---:|---:|---:|---:|
| 1972 | 33 | 33 | 0 | 0 |
| 1988 | 3 | 3 | 0 | 0 |
| 1993 | 7 | 7 | 0 | 0 |
| 2014 | 18 | 16 | 1 | 1 |
| **Total** | **61** | **59** | **1** | **1** |

Los fallbacks recuperaron **4,779 palabras detectadas** en las 59 páginas recuperadas. Este conteo es sólo una señal técnica; no se interpreta como texto validado.

## Consecuencia para la cobertura

- cobertura basal `psm 3`: 698 / 759 = **91.96 %**;
- páginas adicionales recuperadas por fallback: 59;
- páginas que producen texto detectable en al menos una configuración: **757 / 759 = 99.74 %**.

Por tanto, la gran mayoría de las páginas inicialmente vacías eran **falsos negativos del modo de segmentación basal**, no activos inutilizables.

## Dos páginas restantes

### 2014, visor 157

Métricas:

- 969 × 1276 px;
- media de gris = 255.0;
- desviación estándar = 0.0;
- entropía = 0;
- píxeles oscuros = 0;
- `psm 11` = 0 palabras;
- `psm 6` = 0 palabras.

La imagen es computacionalmente **completamente blanca**. Se considera página fuente válida pero sin contenido textual/visual significativo, no fallo OCR.

### 2014, visor 102

Métricas:

- 969 × 1276 px;
- media de gris = 236.277;
- desviación = 23.804;
- entropía = 4.6739;
- proporción de píxeles oscuros = 0.031779;
- `psm 11` = 0 palabras;
- `psm 6` = 2 palabras con confianza media 29.53.

La página contiene señal visual real, pero ningún OCR estándar produce texto robusto. Antes de considerarla predominantemente gráfica se ejecuta una prueba adicional con autocontraste, ampliación, nitidez, umbral de Otsu y `psm 3/6/11`. Esa prueba conserva únicamente métricas.

## Decisión provisional

El pipeline masivo no debe utilizar un único modo OCR. La estrategia provisional pasa a ser:

1. `psm 3` como modo basal;
2. si produce cero palabras, fallback `psm 11` y/o `psm 6`;
3. páginas que permanezcan en cero se someten a diagnóstico visual/preprocesamiento;
4. una página blanca o visual no se cuenta como fallo de extracción textual;
5. CER/WER humano sigue siendo la prueba de exactitud; esta auditoría sólo establece **cobertura de detección**.

## Implicación metodológica

Este resultado evita una conclusión equivocada que habría sido plausible con el primer barrido: que 1972 y 2014 tenían una proporción sustancialmente mayor de páginas intrínsecamente no textuales. En realidad, buena parte de esa diferencia provenía del comportamiento de `psm 3` frente a determinados layouts. Cualquier comparación histórica sobre densidad textual o proporción de páginas visuales deberá utilizar la salida corregida y no el benchmark basal.
