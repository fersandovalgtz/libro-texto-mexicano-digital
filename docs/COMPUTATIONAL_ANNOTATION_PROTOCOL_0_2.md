# Protocolo de anotación computacional 0.2

Fecha: 2026-08-15

## Decisión rectora

El proyecto **Libro de Texto Mexicano Digital** no dependerá de segunda revisión humana, doble codificación humana ni adjudicación humana para avanzar desde el piloto hacia el análisis longitudinal.

La decisión sustituye, hacia adelante, las partes del protocolo 0.1 que exigían revisión humana independiente antes de automatizar. `CODEBOOK_0_1.md` se conserva sin reescribir como preregistro histórico y para trazabilidad de cómo se definieron las categorías antes del análisis masivo.

## Consecuencia para CER/WER

Las 48 posiciones primarias ya trabajadas siguen siendo útiles como **muestra diagnóstica de referencia de operador**. Sin una segunda revisión independiente, no se presentarán como un gold standard humano definitivo.

Las métricas deben denominarse de forma explícita:

- `operator_reference_cer_lexical`
- `operator_reference_wer_lexical`
- `operator_reference_cer_orthographic`
- `operator_reference_wer_orthographic`

Las páginas `visual_only` permanecen fuera del denominador CER/WER textual y se analizan como control de falsos positivos de OCR.

## Sustituto de la validación humana

La robustez se evaluará por **triangulación computacional reproducible**, no por consenso de revisores humanos.

Para cada fragmento o página se conservarán, cuando aplique:

1. resultado del método principal;
2. resultado de al menos un método computacional alternativo;
3. acuerdo/desacuerdo entre métodos;
4. score o evidencia que sustentó la asignación;
5. versión exacta del código/modelo/reglas;
6. procedencia `book_id → page_id → fragment_id`;
7. bandera de ambigüedad cuando los métodos discrepen o la evidencia sea insuficiente.

El desacuerdo computacional **no se resuelve manualmente**. Se conserva como dato y puede producir una categoría `uncertain` o una distribución de etiquetas.

## Pipeline analítico 0.2

### Capa 1 — clasificación página

Asignar automáticamente una clase estructural mínima:

- `textual`
- `mixed_text_image`
- `visual_only`
- `front_matter`
- `toc_or_navigation`
- `bibliography_or_credits`
- `unknown`

La clasificación combinará métricas OCR, densidad de texto, estructura espacial y señales léxicas. Los casos de fotografía con ruido OCR no se tratarán como texto sólo porque Tesseract produzca tokens.

### Capa 2 — segmentación funcional

Segmentar las páginas textuales o mixtas en fragmentos funcionales conservando orden y trazabilidad.

Unidad objetivo:

> consigna, pregunta, enunciado expositivo o bloque de actividad funcionalmente autónomo.

Cada fragmento tendrá al menos:

- `fragment_id`
- `book_id`
- `page_id`
- `catalog_generation`
- `fragment_order`
- `fragment_type_candidate`
- `text_length_chars`
- `text_length_tokens`
- `source_method`
- `segmentation_version`
- `confidence_or_stability`

El texto completo de trabajo podrá permanecer en la capa privada; el repositorio público sólo deberá contener derivados compatibles con la política jurídica vigente.

### Capa 3 — codificación pedagógica computacional

Aplicar el esquema conceptual preregistrado en `CODEBOOK_0_1.md` mediante un clasificador multietiqueta computacional.

Familias iniciales:

- tipo de fragmento;
- acción pedagógica solicitada;
- posición pedagógica del alumno;
- dimensiones sustantivas del contenido;
- variables estructurales adicionales.

La clasificación debe ser conservadora: si la evidencia lingüística no alcanza un umbral definido, se asigna `uncertain` en lugar de inferir por el tema de la página.

### Capa 4 — triangulación

Se compararán al menos dos estrategias:

**A. Reglas/rasgos transparentes**

- verbos imperativos e interrogativos;
- patrones de materiales/procedimientos;
- marcadores de trabajo individual/equipo/comunidad;
- patrones de explicación, comparación, medición, predicción, investigación, decisión, etc.;
- señales de encabezados de actividad, proyecto y evaluación.

**B. Clasificación semántica computacional**

Un modelo de clasificación o método semántico independiente de las reglas. Su salida debe almacenarse separada de A.

El producto analítico principal puede utilizar:

- consenso A+B;
- etiqueta principal + bandera de desacuerdo;
- distribución por método;
- análisis de sensibilidad excluyendo casos inciertos.

No se ocultarán desacuerdos mediante adjudicación manual.

## Control de estabilidad

Antes de interpretar diferencias históricas se ejecutarán controles como:

- estabilidad al variar umbrales razonables;
- estabilidad por longitud del fragmento;
- estabilidad por generación;
- sensibilidad a páginas con layout complejo;
- comparación `body-only` frente a corpus completo;
- comparación incluyendo/excluyendo fragmentos `uncertain`;
- tasa de acuerdo entre métodos por categoría;
- matrices de confusión entre métodos sin asumir que uno sea gold standard.

## Regla para resultados científicos

Las afirmaciones longitudinales deben apoyarse en patrones que sean **robustos a más de una especificación computacional**.

Ejemplo de criterio:

> una diferencia entre generaciones se considera robusta si mantiene dirección y magnitud sustantiva bajo el método A, el método B y un análisis de consenso, y no depende únicamente de fragmentos clasificados como inciertos.

## Próximo producto técnico

Construir el primer dataset de fragmentos para las cuatro generaciones:

`book → page → fragment → tipo → acciones → posición del alumno → contenido → estabilidad → procedencia`

Ése será el insumo para la primera comparación histórica 1972–1988–1993/1998–2014.
