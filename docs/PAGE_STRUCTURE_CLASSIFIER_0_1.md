# Clasificador estructural de páginas 0.1

## Propósito

Construir una capa estructural reproducible para los 759 JPEG fuente del piloto de Ciencias Naturales, quinto grado, sin revisión humana y sin publicar OCR extenso. La salida sirve como filtro previo a la segmentación `página → fragmento` y evita tratar como texto analítico páginas visuales sobre las que el OCR adaptativo puede producir falsos positivos.

## Entradas

- `data/derived/ocr_page_metrics.csv`: 759 activos fuente con métricas OCR técnicas.
- Señales estructurales efímeras obtenidas únicamente en las primeras 16 y últimas 16 páginas de cada generación.
- Tabla fija de códigos de fuente CONALITEG por generación.

## Principio de minimización de texto

El escáner estructural descarga temporalmente los JPEG candidatos, ejecuta Tesseract con el `selected_psm` ya fijado por el pipeline OCR 0.1 y normaliza el OCR sólo en memoria. Busca un vocabulario estructural preregistrado y escribe únicamente puntuaciones categóricas; no escribe ni versiona la transcripción OCR. Los JPEG y el texto temporal se eliminan al terminar cada ejecución.

## Vocabulario estructural 0.1

Tres familias:

- `front_matter`: presentación, prólogo, introducción, conoce tu libro, al alumno, al maestro, mensaje.
- `toc_navigation`: índice, contenido(s), página(s), bloque(s), tema(s), lección(es).
- `bibliography_credits`: bibliografía, referencias, fuentes consultadas, para saber más, ISBN, derechos reservados, declaraciones de edición, coordinación, Secretaría de Educación Pública, impreso en México.

La posición inicial/final nunca basta por sí sola para asignar una clase estructural semántica.

## Clases primarias

- `textual`
- `mixed_text_image`
- `visual_only`
- `front_matter`
- `toc_or_navigation`
- `bibliography_or_credits`
- `unknown`

## Reglas OCR generales

### Ruido visual fuerte

Se considera evidencia fuerte de `visual_only` cuando ocurre al menos una de las siguientes condiciones:

1. `ocr_class == no_text_detected`;
2. el modo seleccionado es fallback (`psm 6` o `psm 11`), la confianza media es menor de 50 y la tasa de palabras de baja confianza es ≥0.65;
3. hay ≤3 palabras y confianza media <50.

Esta regla se diseñó para capturar casos ya observados donde fotografías producen gran cantidad de tokens espurios bajo fallback.

### Texto fuerte

`recognized_words >= 120`, confianza media ≥75 y tasa de baja confianza ≤0.25 → `textual`, salvo que exista evidencia estructural de front matter/navegación/bibliografía.

### Texto moderado

`recognized_words >= 20`, confianza media ≥60 y tasa de baja confianza ≤0.40 → `mixed_text_image`, salvo override estructural.

### Texto escaso de alta confianza

4 o más palabras, confianza ≥75 y baja confianza ≤0.30 → `mixed_text_image` con certeza baja. No se fuerza a `textual`.

### Incertidumbre conservadora

Todo caso restante → `unknown`.

## Overrides estructurales

Se aplican sólo con evidencia OCR de keywords:

1. `bibliography_or_credits`: score ≥2, o score ≥1 en zona inicial/final con confianza ≥55.
2. `toc_or_navigation`: score ≥2, o score ≥1 en zona inicial con confianza ≥65.
3. `front_matter`: score ≥1 en zona inicial con confianza ≥55.

El orden anterior evita que una página legal sea absorbida genéricamente por `front_matter`.

## Salidas

### `data/derived/structural_keyword_flags.csv`

Una fila por página candidata de borde. Contiene scores y zonas, nunca texto fuente.

### `data/derived/page_structure.csv`

Una fila por cada uno de los 759 activos fuente con:

- identificadores y generación;
- métricas OCR seleccionadas;
- scores estructurales cuando aplican;
- `primary_structure`;
- `classification_certainty`;
- `classification_rule`;
- `evidence_flags`;
- versión del clasificador.

### `data/derived/page_structure_summary.csv`

Conteos por generación y clase.

## Controles obligatorios antes de congelar 0.1

1. exactamente 759 filas;
2. ninguna clase fuera del vocabulario permitido;
3. inspeccionar el porcentaje `unknown`;
4. verificar que los visual-only conocidos del control CER/WER no sean clasificados como texto fuerte;
5. si `unknown` es excesivo o los controles conocidos fallan, no congelar 0.1: revisar reglas o añadir métricas visuales derivadas.

## Limitaciones

Este clasificador no pretende describir exhaustivamente el diseño gráfico. `mixed_text_image` significa evidencia OCR moderada/escasa compatible con una página mixta, no una segmentación visual pixel-perfect. Las categorías son una capa operacional para decidir qué páginas pasan a segmentación textual y cuáles requieren tratamiento especial.
