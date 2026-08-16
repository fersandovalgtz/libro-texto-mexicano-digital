# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante historia de la educación, humanidades digitales, análisis computacional y ciencia abierta.

## Estado actual

**LTMD es una infraestructura histórico-computacional de corpus a escala sustancial dentro de la familia _Ciencias Naturales_. Las capas técnicas están reproduciblemente materializadas; la inferencia semántica histórica permanece deliberadamente bloqueada hasta completar la referencia humana de SEMB 0.3.**

Corte documental: **15 de agosto de 2026**.

El corpus técnico materializado contiene:

- **piloto CN5**: 759 imágenes reales y **9,594 fragmentos**;
- **expansión CN4/CN6**: 1,897 posiciones declaradas, 1,888 JPEG reales y **19,067 fragmentos**;
- **Ciencias Naturales Ola 2**: 19 libros, 3,177 JPEG fuente y **36,195 fragmentos**;
- **64,856 ocurrencias técnicas de fragmento** en total;
- catálogo maestro reproducible: **542 visores**, 542 títulos recuperados y 191 familias normalizadas de título nuclear;
- familia estricta _Ciencias Naturales_: **37 visores**, con **35/37** completamente resueltos a nivel de activos.

`corpus_ready` **no equivale** a `semantic_ready`. Las 64,856 ocurrencias tampoco equivalen a 64,856 observaciones históricas independientes: LTMD representa explícitamente reutilización, revisión, reemplazo, aliases y dependencia documental.

## Release candidate vigente

La candidata metodológica actual es **`v0.1.0-rc.1`**.

El preflight automatizado reporta:

- `rc_technical_ready=true`;
- `technical_failures=[]`;
- `LTMD_INTEGRITY_0.5`: **150/150 artefactos críticos**;
- verificación de cifras del artículo metodológico: **PASS**;
- fuentes/working files prohibidos rastreados: **0**;
- gate humano SEMB 0.3: **cerrado correctamente**;
- `publish_ready=false` únicamente por dos blockers: licencia del código propio y licencia/política de derivados originales LTMD.

**No existe todavía un DOI de esta candidata.** El DOI se incorporará sólo después de que una release real sea archivada por Zenodo; LTMD no anticipa ni inventa identificadores persistentes.

Documentos de la candidata:

- [`VERSION`](VERSION)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`docs/RELEASE_NOTES_v0.1.0-rc.1.md`](docs/RELEASE_NOTES_v0.1.0-rc.1.md)
- [`docs/REPRODUCIBILITY_ENVIRONMENT_0_1.md`](docs/REPRODUCIBILITY_ENVIRONMENT_0_1.md)
- [`docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md`](docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md)
- [`docs/RELEASE_OUTPUTS_0_1.md`](docs/RELEASE_OUTPUTS_0_1.md)
- [`data/derived/release_candidate_preflight.json`](data/derived/release_candidate_preflight.json)
- [`docs/RELEASE_CHECKLIST_0_1.md`](docs/RELEASE_CHECKLIST_0_1.md)

## Pregunta general

¿Cómo se transforman, a través del tiempo, el currículo, el lenguaje pedagógico, las actividades escolares, los valores, las representaciones sociales y los recursos visuales presentes en los libros de texto mexicanos?

## Arquitectura científica

```text
catálogo institucional
        ↓
identidad documental / viewer_key / book_id
        ↓
resolución de activos + SHA-256
        ↓
OCR temporal
        ↓
PAGESTRUCT
        ↓
FRAGSEG
        ↓
metadatos y hashes
        ↓
validación humana de constructo
        ↓
clasificación validada
        ↓
análisis histórico
```

Para dependencia documental se mantienen vistas reversibles:

- **object view** — cada ocurrencia dentro del objeto que la contiene;
- **unique-content view** — contenido idéntico agrupado sin borrar procedencia;
- **revision view** — continuidad, sustitución y revisión entre objetos.

## Familia estricta _Ciencias Naturales_

El inventario contiene **37 visores** en nueve generaciones del catálogo:

- `full_direct`: 31;
- `full_alias_same_bytes`: 4;
- `partial_internal_unserved`: 2;
- `not_resolved`: 0.

### Alias 2018 → 2019

Los cuatro visores 2018 de 3º, 4º, 5º y 6º no sirven sus JPEG bajo la clave 2018. La auditoría localizó los activos 2019 correspondientes y comparó **652 pares**: 652/652 tienen SHA-256 y tamaño idénticos. Las entradas de catálogo se conservan, pero no se reprocesan como observaciones independientes.

### 2008

Dos objetos 2008 conservan sólo **tres posiciones internas** que el recurso público no sirve. LTMD registra `internal_unserved_position_observed`; no convierte ese hecho técnico en “página faltante del libro” sin comprobación bibliográfica externa.

## Piloto CN5

El piloto utiliza _Ciencias Naturales_ de quinto grado en generaciones del catálogo 1972, 1988, 1993 y 2014. `catalog_generation` se mantiene separada de año de edición, copyright e ISBN.

- 763 posiciones de visor;
- 759 JPEG reales;
- 4 terminales sintéticos;
- OCR con texto detectable: 757/759;
- PAGESTRUCT: 759 páginas;
- FRAGSEG: **9,594 fragmentos**.

Es la única capa que actualmente llega a Rule A, SEMB 0.2, comparación A/B y una primera historia exploratoria.

## SEMB 0.2: resultado metodológico negativo

SEMB 0.2 produjo **99.49% de incertidumbre global**. Una batería sintética independiente de 105 casos confirmó una operacionalización insuficiente del gate. LTMD no bajó los umbrales retrospectivamente para maximizar diferencias históricas.

SEMB 0.2 se conserva como **resultado negativo/diagnóstico reproducible**, no como clasificador válido para expandir inferencias históricas.

## SEMB 0.3: referencia humana preregistrada

La infraestructura prehumana contiene **480 casos**:

- 320 `development`;
- 160 `locked_validation`;
- 120 casos reservados para doble codificación de fiabilidad.

Los criterios de aceptación, arquitecturas candidatas, stage gates y reglas de apertura quedaron congelados antes de observar anotaciones humanas. La etapa actual es:

**`WAITING_HUMAN_REFERENCE`**

Las expansiones CN4/CN6 y Ola 2 no se clasifican productivamente con SEMB 0.2 ni con candidatos SEMB 0.3 para producir narrativa histórica.

## Unidades breves y FRAGTYPE 0.3

La etiqueta residual `heading_candidate` del piloto resultó demasiado interpretativa. `FRAGTYPE_0.3_SHADOW` conserva límites, IDs y hashes y reinterpreta esas unidades como `short_residual_candidate`.

El universo potencial de fragmentos de ≥4 tokens pasa de 5,037 a 7,429 (+2,392; +47.5%), pero esos casos no se incorporan automáticamente a inferencia: existe una muestra ciega específica para validar su política final.

## Expansión CN4/CN6

Nueve objetos adicionales fueron auditados y procesados técnicamente.

- posiciones declaradas: 1,897;
- JPEG fuente reales: **1,888**;
- SHA-256 verificados: 1,888/1,888;
- texto detectado: 1,880/1,888 (99.58%);
- páginas elegibles para FRAGSEG: 1,559;
- FRAGSEG: **19,067 fragmentos**.

La vista de contenido único conserva **16,155 unidades textuales únicas** entre esas 19,067 ocurrencias. La deduplicación es reversible y nunca elimina la procedencia original.

## Ciencias Naturales Ola 2

La Ola 2 incorporó exclusivamente objetos `full_direct` no procesados previamente; excluye aliases 2018 y los dos objetos 2008 parciales.

- **19 libros**;
- 3,177 JPEG;
- SHA-256 verificados: 3,177/3,177;
- texto detectado: 3,164/3,177 (99.59%);
- `unresolved`: 0;
- páginas elegibles: 2,528;
- FRAGSEG: **36,195 fragmentos**, con 36,195 IDs únicos.

Esta capa está `corpus_ready`, no `semantic_ready`.

## Dependencia documental

LTMD no supone independencia por `catalog_generation`.

En CN4 1972↔1988, 188/214 páginas alineables (87.9%) son byte-idénticas en la misma posición, acompañadas por revisión localizada. El proyecto modela esa continuidad en lugar de contar automáticamente ambos objetos como observaciones independientes.

En CN6 bajo generación 1993 se conservan dos objetos documentales distintos, incluido _Ciencias Naturales y desarrollo humano_. Las relaciones se modelan mediante `book_id`, `viewer_key`, `edition_year`, `document_role` y clusters de dependencia.

## Catálogo maestro reproducible

El snapshot institucional indexado contiene:

- 542 claves de visor;
- 542/542 visores alcanzables;
- 542/542 títulos recuperados;
- 191 familias de título nuclear;
- 8 grupos de títulos repetidos conservados como colas de auditoría.

La identidad documental se fundamenta en `book_id` + `viewer_key`; `catalog_generation` no se usa automáticamente como `edition_year`.

## Derechos y reutilización

LTMD **no redistribuye indiscriminadamente PDF, imágenes ni OCR íntegro de las obras fuente**. Conserva identificadores, URLs de procedencia, tamaños, SHA-256, código, métricas y derivados no sustitutivos.

Cuando una etapa necesita contenido fuente, éste se reconstruye temporalmente, se verifica contra el hash persistido y se elimina después del procesamiento.

La candidata `v0.1.0-rc.1` mantiene deliberadamente pendientes dos decisiones de licencia:

1. licencia del código propio;
2. licencia/política de los datos derivados originales.

No se interpretará una futura licencia LTMD como relicenciamiento de materiales fuente de CONALITEG/SEP o de terceros.

Véanse:

- [`docs/RIGHTS_AND_REUSE_0_1.md`](docs/RIGHTS_AND_REUSE_0_1.md)
- [`docs/RELEASE_OUTPUTS_0_1.md`](docs/RELEASE_OUTPUTS_0_1.md)

## Reproducibilidad e integridad científica

El corte vigente es **`LTMD_INTEGRITY_0.5`**, con **150/150 artefactos críticos presentes** y `missing_critical=[]` en el corte validado de la candidata.

El entorno de referencia de release es Ubuntu 24.04. `requirements-release.txt` fija la dependencia Python directa de SEMB 0.2 (`sentence-transformers==5.6.1`) y la revisión exacta del modelo se mantiene en el workflow congelado. La reproducción de procedimiento/artefactos es alta; Python patch-level y el lock transitivo de wheels todavía están documentados como parcialmente congelados.

Archivos:

- [`data/derived/research_integrity_manifest.json`](data/derived/research_integrity_manifest.json)
- [`data/derived/research_integrity_manifest.md`](data/derived/research_integrity_manifest.md)
- [`data/derived/release_candidate_preflight.json`](data/derived/release_candidate_preflight.json)
- [`docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md`](docs/REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md)

## Publicación científica

LTMD separa dos productos:

1. **artículo de método/recurso digital** — [`docs/METHODS_ARTICLE_DRAFT_0_2.md`](docs/METHODS_ARTICLE_DRAFT_0_2.md);
2. **artículo histórico-educativo** — bloqueado hasta superar SEMB 0.3 y reconstruir la inferencia bajo unidades documentales defendibles.

Las cifras centrales del manuscrito metodológico se recomputan automáticamente desde los artefactos congelados mediante CI. La candidata de release no transforma las tendencias exploratorias de SEMB 0.2 en resultados históricos confirmados.

## Documentación central

La entrada recomendada es el **[Índice maestro de método](docs/METHOD_INDEX.md)**.

Documentos clave:

- [`docs/PROJECT_STATUS_2026-08-15.md`](docs/PROJECT_STATUS_2026-08-15.md)
- [`docs/METHODS_SNAPSHOT_2026-08-15.md`](docs/METHODS_SNAPSHOT_2026-08-15.md)
- [`docs/METHODS_ARTICLE_DRAFT_0_2.md`](docs/METHODS_ARTICLE_DRAFT_0_2.md)
- [`docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md`](docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md)
- [`docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md`](docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md)
- [`docs/SEMB03_STAGE_GATES_0_1.md`](docs/SEMB03_STAGE_GATES_0_1.md)
- [`docs/DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md`](docs/DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md)
- [`docs/CN_WAVE2_COMPLETION_2026-08-15.md`](docs/CN_WAVE2_COMPLETION_2026-08-15.md)
- [`docs/RELEASE_CHECKLIST_0_1.md`](docs/RELEASE_CHECKLIST_0_1.md)

## Regla epistemológica

LTMD privilegia una regla sencilla: **una cifra reproducible no es automáticamente una afirmación válida**. Cada salto —fuente, identidad documental, OCR, estructura, fragmentación, clasificación e inferencia— debe conservar evidencia suficiente para ser auditado independientemente.

Por ello el proyecto conserva también resultados negativos, aliases, posiciones no servidas, revisiones, huecos legítimos de secuencia y fallos de infraestructura: forman parte de la trazabilidad del corpus.

## Citación

Mientras no exista un DOI versionado real, use la metadata de [`CITATION.cff`](CITATION.cff) y la versión de candidata correspondiente. La referencia provisional de `v0.1.0-rc.1` está documentada en las release notes.

Cuando exista una release archivada en Zenodo, deberá citarse el DOI versionado de ese corte científico. No debe citarse una versión móvil de `main` como sustituto de una release congelada cuando exista una versión depositada.
