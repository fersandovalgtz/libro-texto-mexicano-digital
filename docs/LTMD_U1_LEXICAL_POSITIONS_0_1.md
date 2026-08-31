# LTMD-U1 — posiciones léxicas y estadística unigram 0.1

Versión de artefacto privado: **LTMD_U1_LEXICAL_POSITIONS_0.1**  
Constructor público: **LTMD_U1_LEXICAL_POSITIONS_BUILDER_0.1**

## Propósito

Esta capa convierte el FTS5 del Índice Universal LTMD-U1 en una única materialización privada reutilizable para análisis léxico. El objetivo es evitar múltiples barridos incompatibles o redundantes sobre el OCR: la misma normalización FTS5 alimenta frecuencia, dispersión y los futuros n-gramas/coocurrencias.

El tokenizer es exactamente `unicode61 remove_diacritics 2`, heredado del Índice Universal. No se introduce una tokenización paralela.

## Estructura privada

El SQLite generado contiene:

- `terms`: vocabulario normalizado, frecuencia de páginas y ocurrencias;
- `objects`: mapa interno de objetos canónicos a identificadores enteros;
- `pages`: dimensiones técnicas mínimas por fila del índice;
- `token_positions`: `term_id`, fila de página y posición del token;
- `term_pages`: relación única término-página;
- `term_stats`: frecuencia global y dispersión por objetos/generaciones/grados/olas.

El vocabulario y las posiciones son **privados**. No son un dataset público.

## Un solo barrido FTS5

`fts5vocab(..., 'instance')` se recorre una sola vez para materializar `token_positions`. Después se crean índices por `(page_rowid, token_offset)` y `(term_id, page_rowid)`. Los productos posteriores deben consultar esta materialización en vez de volver a tokenizar OCR o ejecutar barridos independientes de FTS5.

Esto permite construir n-gramas y ventanas de coocurrencia conservando la misma secuencia de tokens que usa el buscador.

## Corte canónico 0.1

La materialización real sobre `LTMD_U1_UNIVERSAL_INDEX_0.1` produjo:

- 86,549 páginas;
- 492 objetos canónicos;
- 239,259 términos FTS5 distintos;
- 13,265,844 instancias de token;
- 7,848,708 relaciones término-página;
- 239,259 filas de estadística global.

El SQLite privado pasó `quick_check = ok`.

## Privacidad

No deben publicarse por defecto:

- vocabulario completo;
- términos raros;
- posiciones de tokens;
- identificadores de página u objeto;
- texto OCR o snippets;
- URLs de fuente.

La capa pública se limita a cardinalidades, hashes, políticas, agregados suficientemente dispersos y, en fases posteriores, rankings/coocurrencias que superen umbrales de publicación explícitos.

## Frontera epistemológica

Frecuencia de tokens OCR no equivale a significado histórico. Se mantienen:

- `ocr_available != text_verified`;
- `frequency != semantic meaning`;
- `search_hit != historical_claim`;
- `computational_candidate != semantic_ready`.

El estado por defecto sigue siendo `exploratory_signal`.

## Reentrada siguiente

Sobre esta única materialización deben construirse, en orden:

1. estadísticas por dimensión con denominadores exactos;
2. bigramas/trigramas agregados con supresión de secuencias raras;
3. coocurrencias por ventana con métricas de frecuencia y dispersión;
4. contrato público de publicación/supresión;
5. sólo después, consumo desde LTMD Analytics.
