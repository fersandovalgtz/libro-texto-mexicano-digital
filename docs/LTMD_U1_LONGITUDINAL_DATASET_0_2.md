# LTMD-U1 — dataset longitudinal atlas-ready 0.2

**Estado:** derivado público-seguro y exploratorio; no es liberación semántica ni aplicación institucional desplegada. **Issue:** [#171](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/171). **Revisión:** [PR #179](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/pull/179).

## Propósito y ejecución

Se prolonga la vista longitudinal 0.1 sin abrir otro repositorio. El constructor reconcilia los cinco archivos agregados de `data/analytics` contra `ltmd_analytics_indigenous_manifest_0_1.json`. Comprueba SHA-256 de contenido, esquemas cerrados, unicidad de claves, cardinalidades, totales de generaciones y estratos, denominadores y estados epistemológicos. Acepta sólo la normalización de saltos de línea LF→CRLF exigida por los hashes canónicos originales.

```sh
python scripts/build_ltmd_u1_longitudinal_dataset.py \
  --output /tmp/ltmd_u1_longitudinal_atlas_dataset.json
python -m pytest -q tests/test_build_ltmd_u1_longitudinal_dataset.py
```

El workflow `.github/workflows/test-ltmd-analytics.yml` ejecuta ambas acciones contra archivos **reales** bajo CI y publica un artefacto descargable temporal. No se accede a SQLite, OCR, PDF o JPEG originales.

## Universo y cobertura

- Corpus registrado: **86,549** páginas técnicas en **11** generaciones: 1960, 1966, 1972, 1982, 1988, 1993, 2008, 2011, 2014, 2018 y 2019.
- Estudio temático: **1,151** observaciones de páginas candidatas automatizadas, que no constituyen validación de contenido.
- Dimensiones existentes cruzadas: **140** estratos no vacíos generación × grado × ola; **387** celdas de una lengua detectada × generación × grado × ola; **45** celdas de término explícito × generación.
- Agrupaciones analíticas: `1960_1966`, `1972_1988`, `1993`, `2008_2011`, `2014_2019`. Son **conjuntos de cortes disponibles**; no implican presencia ni continuidad de todos los años intermedios.
- Los 11 dominios `W1`–`W11` son divisiones **operativas** conforme a `data/catalog/ltmd_u1_coverage.md`. No se interpretan automáticamente como asignaturas de un plan de estudios.

## Contrato de salida (JSON)

| Sección | Grano | Variables centrales y límites |
| --- | --- | --- |
| `scope` | release | Conteos y cardinalidades reconciliadas; marca `generation_grade_wave_corpus_denominators_public=false` |
| `cohorts[]` | conjunto de generaciones observadas | `observed_generations`, `corpus_pages`, `candidate_pages`, `explicit_general_pages`, `named_language_contextual_pages`, `candidate_pages_per_1000`; `distinct_candidate_books_across_generations=null` |
| `generations[]` | generación editorial | Conteos, `candidate_books_within_generation`, `candidate_pages_per_1000`, `epistemic_state` |
| `strata[]` | generación × grado × ola | `operational_domain`, páginas candidatas, explícitas y contextuales, libros *dentro del estrato*; `corpus_pages_same_stratum=null`; `candidate_pages_per_1000=null` |
| `language_matrix[]` | lengua × generación × grado × ola | páginas y libros candidatos *dentro de esa celda*, más `denominator_state=private_manifest_required` |
| `explicit_terms[]` | término × generación | páginas y libros candidatos por término y generación, no sumables entre términos para obtener páginas únicas |
| `provenance` | release | Versión, SHA-256 del **manifiesto público**, hashes SHA-256 canónicos de **tablas públicas** y hash de cobertura |
| `scientific_state` | release | `human_validation_complete=false`, `semantic_ready=false`, `not_visually_validated` |

**Denominadores:** la tasa de generación o cohorte es `candidate_pages / corpus_pages × 1000` únicamente sobre páginas indexadas del **mismo** corte. Los denominadores exactos de generación × grado × ola existen en el Corpus Analytics Manifest completo, **conservado privado**. No están publicados como tabla accesible y por eso las tasas por estrato/lengua quedan nulas. El valor `null` significa **no calculable con los agregados actuales**, no ausencia de referencias ni valor cero.

**Libros:** dentro de una generación, estrato o celda los totales son únicos según el agregado original; no se deben sumar totales de libros entre generaciones, estratos o lenguas para inferir libros únicos. Los grupos de lenguas, los términos y las etiquetas explícita/contextual pueden superponerse; su suma no representa la unión de páginas.

## Exclusiones y gobernanza

El constructor no emite identificadores de página, claves de visor/libro, rutas privadas, hashes OCR, texto, fragmentos, URLs de objetos ni libros fuente. Rechaza columnas inesperadas; nunca promueve señales automáticas a semántica validada. El uso y la eventual publicación permanecen subordinados a [#2](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/issues/2) y a los documentos `DATA_LICENSE.md`, `PROVENANCE.md` y `GOVERNANCE.md`.

## Qué falta para cerrar #171

El presente corte avanza la construcción **atlas-ready**, pero queda pendiente ejecutar auditoría y revisión de la integración completa de las dimensiones privadas, aportar tasas estratificadas sólo con denominadores válidos y autorizados, evaluar comparabilidad de familias editoriales, revisar el PR y confirmar el contrato final de interfaz. El gate de despliegue de API con índice privado sigue separado y no se abre por el éxito de una prueba de datos agregados.

**Criterio de conclusión:** generación reproducible + integración del universo/denominadores autorizados + comprobación de derechos + revisión técnica y científica; no simplemente obtener una gráfica bonita.
