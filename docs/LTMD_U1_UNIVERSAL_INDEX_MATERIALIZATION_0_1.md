# LTMD-U1 — materialización del Índice Universal 0.1

**Versión del corte:** `LTMD_U1_UNIVERSAL_INDEX_MATERIALIZATION_0.1`  
**Fecha:** 2026-08-30

## Resultado

La bóveda privada FTRL-U1 fue reconstruida desde sus productos preservados, sin volver a descargar páginas fuente ni ejecutar OCR nuevo. La enumeración cerró exactamente en:

- **288** bases SQLite privadas;
- **86,549** filas de página;
- **86,549** `page_id` únicos;
- **492** objetos canónicos;
- **0** duplicados idénticos entre bases;
- **0** conflictos de identidad/hash.

Las 288 bases presentan una sola variante de esquema `pages` y todas contienen los campos mínimos exigidos por el builder del Índice Universal.

## Índice privado

El corpus se materializó como una base SQLite3 privada con tabla `pages`, dimensiones indexadas y FTS5 `pages_fts`.

Estado final canónico:

- páginas `pages`: **86,549**;
- filas FTS5: **86,549**;
- objetos canónicos: **492**;
- `duplicate_page_ids`: **0**;
- `PRAGMA integrity_check`: **ok**;
- orden canónico de filas: `page_id_ascending`;
- tokenizer: `unicode61 remove_diacritics 2`;
- tamaño lógico: **209,022,976 bytes**;
- SHA-256 del SQLite privado: `aec55cc7dd83c2e1e22d26e3baf8f7ca2e35e32898827ec84e6222edd4bcf7a2`.

El archivo SQLite no se publica en GitHub.

## Preservación

La copia privada canónica se comprimió de forma determinista para preservación:

- tamaño comprimido: **83,745,081 bytes**;
- SHA-256 comprimido: `8ae9c16b7d31a500b07cbed4084cbc98da72f1630edef136a929ad76176d9c71`.

Después de archivarla privadamente se realizó una redescarga independiente. El archivo redescargado reprodujo exactamente el SHA-256 comprimido y, al descomprimirlo en flujo, reprodujo el SHA-256 del SQLite lógico. La ubicación privada no se expone en la superficie pública.

## Identidad del conjunto de entrada

Para evitar que nombres o rutas locales formen parte de la identidad del corpus, las 288 bases se representan por sus SHA-256 ordenados lexicográficamente. La huella del conjunto —los 288 SHA-256 en minúsculas unidos con `LF`, sin `LF` terminal— es:

`bbc63e8b34376d7f92e34183906df244593800180af91748927b932b721ed389`

Esta huella permite comparar reconstrucciones realizadas en directorios o equipos diferentes sin exigir nombres de archivo idénticos.

## Distribución técnica

### Por generación

| generación | páginas |
|---:|---:|
| 1960 | 3,536 |
| 1966 | 6,680 |
| 1972 | 7,020 |
| 1982 | 3,292 |
| 1988 | 5,274 |
| 1993 | 21,708 |
| 2008 | 6,538 |
| 2011 | 7,611 |
| 2014 | 13,752 |
| 2018 | 2,744 |
| 2019 | 8,394 |

### Por grado

| grado | páginas |
|---:|---:|
| 1 | 10,459 |
| 2 | 10,814 |
| 3 | 20,333 |
| 4 | 13,059 |
| 5 | 12,710 |
| 6 | 19,174 |

### Por ola operacional

| ola | páginas |
|---|---:|
| W1 | 6,516 |
| W2 | 11,945 |
| W3 | 20,765 |
| W4 | 2,414 |
| W5 | 2,653 |
| W6 | 5,258 |
| W7 | 3,261 |
| W8 | 1,490 |
| W9 | 448 |
| W10 | 11,937 |
| W11 | 19,862 |

La ola sigue siendo una dimensión operacional de LTMD; no se reinterpreta automáticamente como ontología curricular.

## Smoke tests FTS5

Se realizaron consultas corpus-wide únicamente para verificar recuperación, filtrado y comportamiento del tokenizer. Estos conteos son **señales computacionales**, no hallazgos históricos validados.

- `raramuri`: 23 páginas candidatas / 17 libros;
- `rarámuri`: 23 / 17, confirmando equivalencia diacrítica esperada;
- `democracia`: 359 / 107;
- frase `"medio ambiente"`: 427 / 206;
- `migracion`: 289 / 97;
- `familia`: 3,816 / 461;
- `discapacidad`: 95 / 38;
- `tecnologia`: 533 / 181.

En la ejecución local, todas estas consultas de conteo simple se resolvieron en milisegundos. El desempeño observado es diagnóstico del entorno de prueba, no un benchmark contractual.

## Frontera científica

La existencia de un índice full-text no cambia la categoría epistemológica de los resultados:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- una coincidencia FTS5 se clasifica como `computational_candidate`;
- `semantic_ready` permanece en **false** para esta capa corpus-wide.

## Siguiente fase

El Índice Universal elimina la necesidad de construir un ledger privado distinto para cada pregunta temática. La siguiente capa debe ser un motor genérico que reciba consultas FTS5 acotadas, aplique filtros por generación/grado/ola, calcule páginas y libros únicos y devuelva sólo agregados seguros con procedencia y advertencias epistemológicas.
