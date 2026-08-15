# Política para páginas visuales sin texto en la muestra CER/WER

**Fecha:** 15 de agosto de 2026  
**Momento:** fijada al inspeccionar la fuente de `LTMD-CER-1972-Q4_2` (visor 246) y **antes de inspeccionar la hipótesis OCR regional de esa página**.

## Problema

La muestra CER/WER fue preregistrada por posición y no debe sustituirse retrospectivamente. Una página seleccionada puede resultar predominantemente o totalmente visual.

En la página 246 de la generación 1972, la región de contenido visual no contiene texto lingüístico visible. El único texto de la página es el folio, que no forma parte del contenido sustantivo y se excluye mediante región.

Una referencia humana vacía tiene denominador cero. Por tanto, CER/WER no es una métrica definida ni informativa para esa unidad.

## Regla

Cuando una página preregistrada sea visualmente **sin texto lingüístico dentro de la región de evaluación**:

1. **no se sustituye la página**;
2. se conserva su `page_id`, generación, posición y procedencia;
3. se fija la región visual antes de inspeccionar el OCR regional;
4. la referencia humana se registra como vacía y la unidad se clasifica `visual_only`;
5. no se calcula CER/WER para esa página y no se introduce un cero artificial;
6. la página queda fuera del denominador del agregado CER/WER textual, pero permanece explícitamente en el reporte de composición de la muestra;
7. el OCR de la región se evalúa mediante **falsos positivos**:
   - `spurious_ocr_words`: número de tokens OCR no vacíos dentro de la región visual;
   - `spurious_ocr_chars`: caracteres OCR reconstruidos dentro de la región;
   - `visual_false_positive = 1` si el pipeline produce cualquier token lingüístico en una región cuya referencia es vacía;
8. el modo OCR evaluado debe seguir siendo el `selected_psm` real del pipeline adaptativo;
9. el texto OCR espurio permanece privado; públicamente sólo se conservan conteos/métricas.

## Segunda revisión

La clasificación `visual_only` debe recibir segunda revisión humana independiente, igual que una transcripción textual. Hasta entonces se reporta como `visual_only_provisional`.

La revisión confirma:
- que la región no contiene texto lingüístico pequeño o integrado en la imagen;
- que el folio/encabezado excluido realmente queda fuera de la región;
- que no se omitió accidentalmente una leyenda pertinente.

## Agregados

Para cada generación se reportará:

- `sample_pages_total`;
- `textual_reference_pages`;
- `visual_only_pages`;
- CER/WER sólo sobre `textual_reference_pages` revisadas;
- falsos positivos OCR de las páginas `visual_only` por separado.

Así, la muestra corporal de una generación puede conservar sus 10 posiciones originales aunque el denominador CER/WER textual sea menor que 10.

## Caso inicial

`LTMD-CER-1972-Q4_2`, visor 246:

- modo de producción seleccionado previamente por el pipeline: `psm 6`;
- región visual fijada: `(45,55)-(625,950)` px sobre fuente 670×993;
- región normalizada aprox.: `(0.067164,0.055388)-(0.932836,0.956697)`;
- folio 246 queda fuera de la región;
- clasificación humana inicial: `visual_only_provisional`.

El número de tokens OCR espurios **no se registra en este documento todavía**, porque esta política se congela antes de inspeccionar la hipótesis OCR regional.
