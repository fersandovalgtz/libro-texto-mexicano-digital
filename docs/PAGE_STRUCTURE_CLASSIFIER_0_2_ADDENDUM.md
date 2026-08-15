# Addendum PAGESTRUCT 0.2 — control de end matter denso

Fecha: 2026-08-15

## Motivo de la revisión

`PAGESTRUCT_0.1` permitió segmentar 641 páginas elegibles y produjo 9,818 fragmentos sin fallos. La auditoría derivada `FRAGAUDIT_0.1` detectó una densidad máxima de 113 fragmentos en una página de 2014. Sin inspeccionar manualmente el contenido fuente, la revisión de métricas públicas mostró dos páginas consecutivas de la zona final de 2014 (vp155 y vp156) con 1,065 y 1,139 palabras OCR, confianza media 80.16 y 81.04, clasificadas por la regla genérica `OCR_TEXT_RICH`.

El patrón demuestra una limitación general de 0.1: un documento de end matter extremadamente denso puede cumplir el umbral de texto fuerte aunque no deba entrar automáticamente al corpus pedagógico body-only.

## Cambios preregistrados de 0.2

### 1. Vocabulario específico de créditos de producción/imagen

Se amplía exclusivamente la familia `bibliography_credits` con expresiones específicas:

- `créditos iconográficos`
- `créditos fotográficos`
- `créditos de imágenes`
- `fuentes de las imágenes`
- `fuentes de imagen`
- `imagen de portada`
- `fotografía de portada`
- `ilustración de portada`
- `agradecimientos`
- `colofón`

No se añaden términos genéricos aislados como `fotografía`, `imagen` o `ilustración`, porque aparecen legítimamente en texto pedagógico.

### 2. Regla conservadora `END_ZONE_DENSE_UNCERTAIN`

Si, después de evaluar los overrides semánticos de keywords y el ruido visual, una página:

- pertenece a las últimas 16 páginas fuente de su libro;
- contiene `recognized_words >= 800`;
- tiene `mean_word_confidence < 85`;
- no ha sido resuelta por keywords estructurales;

entonces se clasifica `unknown`, certeza `medium`, en lugar de `textual`.

La regla **no infiere** que la página sea bibliografía/créditos. Sólo impide que un patrón extremo de end matter sea tratado como body text sin evidencia suficiente.

## Versiones

- scanner de keywords: `STRUCTKW_0.2`
- clasificador: `PAGESTRUCT_0.2`

## Consecuencia sobre FRAGSEG

`FRAGSEG_0.1` permanece como corrida histórica reproducible construida sobre PAGESTRUCT 0.1. Si PAGESTRUCT 0.2 cambia el conjunto de páginas elegibles, la segmentación debe regenerarse bajo una nueva versión (`FRAGSEG_0.2`) y los resultados 0.1 quedan superseded para el análisis principal, sin eliminarse del historial metodológico.

## Criterios de aceptación de PAGESTRUCT 0.2

- 759 páginas clasificadas;
- controles visual-only conocidos preservados;
- `unknown <= 10 %`;
- versión correcta en todas las filas;
- reporte explícito de páginas afectadas por `END_ZONE_DENSE_UNCERTAIN`;
- comparación documentada 0.1 → 0.2 antes de ejecutar nueva segmentación.
