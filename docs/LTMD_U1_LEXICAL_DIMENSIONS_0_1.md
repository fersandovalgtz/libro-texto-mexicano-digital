# LTMD-U1 — dimensiones léxicas 0.1

Versión de artefacto privado: **LTMD_U1_LEXICAL_DIMENSIONS_0.1**  
Constructor público: **LTMD_U1_LEXICAL_DIMENSIONS_BUILDER_0.1**

## Propósito

Esta capa deriva estadísticas léxicas por generación, grado y ola a partir de `LTMD_U1_LEXICAL_POSITIONS_0.1`. No vuelve a leer OCR, no vuelve a consultar FTS5 y no introduce otra tokenización.

La separación en un SQLite privado propio mantiene inmutable el artefacto de posiciones léxicas y permite versionar de forma independiente los derivados dimensionales.

## Contrato

El artefacto contiene:

- `term_page_stats`: frecuencia de cada término por página;
- `term_dimension_stats`: frecuencia, páginas y objetos para cada término dentro de cada valor de generación, grado u ola;
- `dimension_denominators`: páginas y objetos del mismo universo para cada valor dimensional;
- `meta`: versión, cardinalidades y estado científico.

Las tasas posteriores deben usar el numerador y el denominador del mismo valor dimensional. No se admiten denominadores globales para filtros parciales.

## Corte canónico 0.1

Materializado desde `LTMD_U1_LEXICAL_POSITIONS_0.1`:

- 7,848,708 filas término–página;
- 1,517,473 filas término–dimensión;
  - 598,484 por generación;
  - 437,827 por grado;
  - 481,162 por ola;
- 28 denominadores dimensionales:
  - 11 generaciones;
  - 6 grados;
  - 11 olas.

Los denominadores reproducen exactamente el universo de 86,549 páginas del Corpus Analytics Manifest 0.1.

El SQLite privado pesa 158,904,320 bytes y tiene SHA-256 `018d2bf6520fc8e1cda5aa34c0dfedb39ae9320a07d95e0fe193c17423eeb99b`. La copia gzip local pesa 50,842,335 bytes y tiene SHA-256 `475941720453781b0ff44c1689a32cc60a976aa95184caf1abd400dfe28e27c8`. El artefacto pasó `quick_check = ok`.

## Privacidad

El artefacto es privado. GitHub no publica:

- términos ni vocabulario;
- identificadores de página u objeto;
- matrices término×dimensión completas;
- OCR o snippets;
- rutas privadas.

La superficie pública sólo fija constructor, tests, contrato, cardinalidades y hashes.

## Estado científico

Toda frecuencia sigue siendo una señal computacional:

- `text_verified = false`;
- `semantic_ready = false`;
- `result_state = exploratory_signal`.

La ola (`wave`) continúa siendo una taxonomía operacional, no una ontología curricular.

## Reentrada

Con los denominadores dimensionales ya cerrados, el siguiente bloque es:

1. bigramas y trigramas derivados de `token_positions` con límites de página;
2. supresión de secuencias raras antes de cualquier publicación;
3. coocurrencias por ventana con frecuencia y dispersión por páginas/objetos;
4. contrato público de publicación/supresión.

No se vuelve a tokenizar OCR ni a barrer FTS5.
