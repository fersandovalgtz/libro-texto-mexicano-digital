# LTMD-U1 — motor de consulta corpus-wide 0.1

Versión: **LTMD_U1_CORPUS_QUERY_ENGINE_0.1**

## Propósito

Esta capa convierte el Índice Universal privado LTMD-U1 en un motor de recuperación transversal. A diferencia de los primeros verticales temáticos, no requiere un ledger específico para cada pregunta: recibe una expresión FTS5, aplica filtros sobre el mismo universo de 86,549 páginas y devuelve exclusivamente agregados.

El motor **no devuelve** OCR, `search_text`, snippets, `page_id`, URL fuente, hashes de página/OCR ni rutas privadas.

## Entrada

- Índice Universal privado `LTMD_U1_UNIVERSAL_INDEX_0.1`.
- Expresión FTS5 mediante `--query`.
- Filtros repetibles:
  - `--generation`
  - `--grade-code`
  - `--wave`
- Desglose opcional:
  - `--group-by generation`
  - `--group-by grade_code`
  - `--group-by wave`
- Verificación criptográfica opcional del índice mediante `--expected-index-sha256`.

Ejemplo privado:

```bash
python scripts/query_u1_universal_index.py \
  --index /ruta/privada/ltmd_u1_universal_index_0_1.sqlite \
  --expected-index-sha256 aec55cc7dd83c2e1e22d26e3baf8f7ca2e35e32898827ec84e6222edd4bcf7a2 \
  --query '"medio ambiente"' \
  --generation 2014 \
  --grade-code 6 \
  --group-by wave
```

## Denominadores exactos

El Índice Universal contiene el universo de páginas, no sólo los hits. Por ello, para cualquier combinación admitida de generación, grado y ola, el motor calcula:

- `corpus_pages_in_scope`;
- `corpus_books_in_scope`;
- `candidate_pages`;
- `candidate_books`;
- `candidate_pages_per_1000`.

La tasa utiliza exactamente el mismo conjunto de filtros en numerador y denominador. Esto elimina la limitación del primer motor temático, que sólo disponía de denominadores por generación.

Cuando se solicita `group_by`, cada grupo recalcula su propio denominador dentro del universo filtrado.

## Consulta FTS5

`--query` acepta sintaxis FTS5. La expresión se pasa como parámetro enlazado a SQLite; los filtros también son parametrizados. Un error de sintaxis FTS5 se devuelve como error genérico `invalid FTS5 query expression`, sin propagar detalles internos de SQLite.

El tokenizer heredado del Índice Universal es `unicode61 remove_diacritics 2`. Por tanto, búsquedas como `raramuri` y `rarámuri` recuperan el mismo término normalizado cuando el resto de la expresión es equivalente.

## Contrato de salida

La respuesta JSON utiliza `schemas/ltmd_u1_corpus_query_response.schema.json` y sólo expone:

- consulta suministrada;
- filtros normalizados;
- métricas agregadas;
- breakdown agregado opcional;
- versión del motor e índice;
- SHA-256 del índice sólo cuando fue verificado explícitamente;
- advertencias epistemológicas.

No se emiten identificadores ni contenido que permita reconstruir las páginas fuente.

## Estado epistemológico

Toda respuesta 0.1 conserva:

```text
result_state = exploratory_signal
human_validation_complete = false
```

Las reglas obligatorias son:

- `ocr_available != text_verified`;
- `search_hit != historical_claim`;
- `zero_hits != demonstrated_absence`;
- `computational_candidate != semantic_ready`.

Una búsqueda puede priorizar investigación o alimentar una visualización; no sustituye validación humana del constructo.

## Privacidad

El índice universal y su OCR derivado permanecen privados. El motor está diseñado para ejecutarse server-side/local-only. El output no contiene:

- texto OCR;
- snippets;
- `page_id`;
- `canonical_viewer_key`;
- URL fuente;
- hashes de páginas;
- paths del filesystem.

El conteo de libros se calcula internamente mediante `COUNT(DISTINCT canonical_viewer_key)` pero ese identificador no se devuelve.

## Próximo paso

Tras validar este motor contra el índice canónico real, LTMD Analytics debe generalizar su contrato HTTP para consumirlo. Antes del staging se fijará además el **Corpus Analytics Manifest 0.1**, con denominadores y dimensiones auditables del universo utilizado por producto.
