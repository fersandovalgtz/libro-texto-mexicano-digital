# LTMD-U1 — reutilización y similitud transversal 0.1

Versión: `LTMD_U1_REUSE_SIMILARITY_0.1`.

Esta capa consolida señales corpus-wide para evitar confundir **repetición técnica/editorial** con cambio histórico. La jerarquía es deliberadamente estricta: igualdad criptográfica de fuente, igualdad de una representación textual técnica y similitud aproximada son evidencias distintas y nunca generan aliases por sí mismas.

## Protocolo fijado antes de inspeccionar candidatos aproximados

- `exact_source_reuse`: igualdad de `source_sha256`. Prueba igualdad de los bytes fuente representados por ese hash; no identidad bibliográfica ni equivalencia curricular.
- `exact_text_representation_reuse`: igualdad de `search_text_sha256`, sólo en páginas con `ocr_char_count >= 200` y `ocr_word_count >= 30`. Las páginas vacías o de información insuficiente no cuentan como reutilización textual.
- `similarity_candidate`: shingles de 5 tokens normalizados ya materializados en `LTMD_U1_LEXICAL_POSITIONS_0.1`; mínimo 50 shingles distintos; MinHash determinista de 96 componentes; LSH 12×8; sólo pares entre objetos canónicos distintos; igualdad textual exacta excluida; verificación exacta posterior de Jaccard ≥0.80 y al menos 40 shingles compartidos.
- `near_exact_candidate`: mismo protocolo, con Jaccard ≥0.95.

Los umbrales se fijaron antes de observar candidatos concretos y no se ajustan retrospectivamente.

## Materialización U1 real

Universo: 86,549 páginas y 492 objetos canónicos. 71,274 páginas superan el filtro de información textual y 15,275 quedan excluidas de las comparaciones textuales. 65,488 páginas tienen además al menos 50 shingles distintos para la capa aproximada.

La capa exacta contiene 3,347 grupos repetidos de fuente, de los cuales 3,330 cruzan objetos canónicos; y 3,013 grupos repetidos de representación textual, de los cuales 3,001 cruzan objetos. La agregación por objetos produce 23 pares con igualdad de bytes fuente y 998 pares con alguna igualdad textual admisible.

La búsqueda aproximada generó 13,965 pares LSH distintos, no exactos y entre objetos diferentes. La verificación exacta dejó 9,146 señales: 6,152 `similarity_candidate` y 2,994 `near_exact_candidate`, distribuidas entre 3,867 pares de objetos. Estas cifras describen señales computacionales, no equivalencias semánticas.

## Privacidad y estado científico

El SQLite privado contiene hashes, membresías de grupos, páginas y pares necesarios para que Analytics pueda advertir reutilización. GitHub no publica esos valores: sólo código, protocolo, cardinalidades, hashes del artefacto y estados epistemológicos.

`text_verified=false`, `semantic_ready=false`, estado por defecto `exploratory_signal`. `similarity_candidate` nunca crea aliases y no implica identidad bibliográfica, equivalencia curricular, relación pedagógica, relación semántica ni afirmación histórica.

El artefacto privado pasó `quick_check=ok`, fue comprimido, archivado en la bóveda Analytics canónica de Drive y redescargado; el SHA-256 de la copia coincide tanto en su gzip como al descomprimir el SQLite lógico.

## Reentrada

Con esta capa cerrada, la ruta corpus-wide pasa a **verticales exploratorios**. Staging real continúa después de esa integración, no antes.
