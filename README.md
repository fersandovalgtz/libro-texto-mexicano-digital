# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante historia de la educación, humanidades digitales, análisis computacional y ciencia abierta.

## Estado actual

**LTMD adopta como objetivo de su primera gran fase la cobertura integral del universo histórico disponible en el snapshot U1 del Catálogo Histórico de CONALITEG: 542 visores. Ciencias Naturales funciona como banco de pruebas e inicio del corpus, no como límite del proyecto.**

Corte documental: **15 de agosto de 2026**.

El corpus técnico materializado hasta ahora contiene:

- **piloto CN5**: 759 imágenes reales y **9,594 fragmentos**;
- **expansión CN4/CN6**: 1,897 posiciones declaradas, 1,888 JPEG reales y **19,067 fragmentos**;
- **Ciencias Naturales Ola 2**: 19 libros, 3,177 JPEG fuente y **36,195 fragmentos**;
- **64,856 ocurrencias técnicas de fragmento** en total;
- catálogo maestro reproducible: **542 visores**, 542 títulos recuperados y 191 familias normalizadas de título nuclear.

`corpus_ready` **no equivale** a `semantic_ready`. Las 64,856 ocurrencias tampoco equivalen a 64,856 observaciones históricas independientes: LTMD representa explícitamente reutilización, revisión, reemplazo, aliases y dependencia documental.

## Objetivo maestro LTMD-U1: 542/542

El universo operativo **LTMD-U1** está fijado en **542 visores únicos**. El tablero ejecutable actual reporta:

- catálogo censado: **542/542 (100.00%)**;
- títulos normalizados: **542/542 (100.00%)** en 191 familias;
- activos completamente resueltos con evidencia: **36/542 (6.64%)**, más 2 resoluciones parciales documentadas;
- FRAGSEG directamente materializado: **32/542 (5.90%)**;
- cobertura FRAGSEG efectiva, incluyendo cuatro aliases byte-idénticos ya representados: **36/542 (6.64%)**;
- relaciones documentales registradas: **12/542 (2.21%)**;
- cobertura semántica humana validada: **0/542**, porque SEMB 0.3 continúa en `WAITING_HUMAN_REFERENCE`.

La meta U1 es alcanzar **542/542 visores técnicamente representados**, mediante procesamiento directo o alias criptográficamente verificado, conservando siempre identidad documental y excepciones. Este objetivo no autoriza a extrapolar el clasificador semántico de Ciencias Naturales a otras áreas sin validación humana propia.

El programa completo está en **[`docs/LTMD_U1_MASTER_PLAN_0_1.md`](docs/LTMD_U1_MASTER_PLAN_0_1.md)** y el tablero vivo en **[`data/catalog/ltmd_u1_coverage.md`](data/catalog/ltmd_u1_coverage.md)**. La cola integral está en `data/catalog/ltmd_u1_wave_queue.csv`.

La primera ola pendiente, **U1-W1**, contiene sólo cuatro visores de Ciencias Naturales/Estudio de la Naturaleza. Después siguen Matemáticas, Español/Lengua, Ciencias Sociales, Historia, Geografía/Atlas, Cívica/Ética, Artes, Educación Física, materiales integrados y títulos que requieren revisión operacional.

## Release publicada

La primera release candidate metodológica pública es **[`v0.1.0-rc.1`](https://github.com/fersandovalgtz/libro-texto-mexicano-digital/releases/tag/v0.1.0-rc.1)**.

Antes de crear el tag, el preflight reproducible demostró:

- `rc_technical_ready=true`;
- `publish_ready=true`;
- `technical_failures=[]`;
- `publish_blockers=[]`;
- `LTMD_INTEGRITY_0.6`: **166/166 artefactos críticos**;
- SHA-256 de los 166 artefactos críticos recomputados contra el checkout: **PASS**, cero discrepancias;
- verificación de cifras del artículo metodológico: **PASS**;
- fuentes/working files prohibidos rastreados: **0**;
- gate humano SEMB 0.3: **cerrado correctamente**.

El tag `v0.1.0-rc.1` congela el commit de release verificado; `main` puede continuar evolucionando después de ese corte. El programa U1 se desarrolla en `main` después de esa release y no modifica retroactivamente el tag.

**El DOI de Zenodo está pendiente hasta que exista un registro real del depósito.** LTMD no anticipa ni inventa identificadores persistentes.

Documentos del paquete:

- [`VERSION`](VERSION)
- [`CHANGELOG.md`](CHANGELOG.md)
- [`LICENSE`](LICENSE) — software propio, Apache License 2.0
- [`DATA_LICENSE.md`](DATA_LICENSE.md) — derivados originales licenciables, CC BY 4.0
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

Para dependencia documental se mantienen vistas reversibles: **object view**, **unique-content view** y **revision view**.

## Familia estricta _Ciencias Naturales_

El inventario estricto contiene **37 visores** en nueve generaciones del catálogo: 31 `full_direct`, 4 `full_alias_same_bytes`, 2 `partial_internal_unserved` y 0 `not_resolved`.

Los cuatro visores 2018 de 3º, 4º, 5º y 6º se relacionan con activos 2019 mediante **652/652 pares byte-idénticos**. Dos objetos 2008 conservan tres posiciones internas no servidas; LTMD las registra como hecho técnico sin convertirlas en “página faltante” sin comprobación bibliográfica externa.

La taxonomía operativa U1 identifica además materiales afines como *Estudio de la Naturaleza*. Por eso el dominio operacional `ciencias_naturales` contiene 40 visores, de los cuales 36 están cubiertos efectivamente y cuatro forman U1-W1.

## Piloto CN5

El piloto utiliza _Ciencias Naturales_ de quinto grado en generaciones del catálogo 1972, 1988, 1993 y 2014. `catalog_generation` se mantiene separada de año de edición, copyright e ISBN.

- 763 posiciones de visor;
- 759 JPEG reales;
- OCR con texto detectable: 757/759;
- PAGESTRUCT: 759 páginas;
- FRAGSEG: **9,594 fragmentos**.

Es la única capa que actualmente llega a Rule A, SEMB 0.2, comparación A/B y una primera historia exploratoria.

## SEMB 0.2: resultado metodológico negativo

SEMB 0.2 produjo **99.49% de incertidumbre global**. LTMD no bajó umbrales retrospectivamente para maximizar diferencias históricas. Se conserva como **resultado negativo/diagnóstico reproducible**, no como clasificador válido para expandir inferencias históricas.

## SEMB 0.3: referencia humana preregistrada

La infraestructura prehumana contiene **480 casos**: 320 `development`, 160 `locked_validation` y 120 reservados para doble codificación de fiabilidad. Los criterios de aceptación, arquitecturas candidatas y stage gates quedaron congelados antes de observar anotaciones humanas.

Etapa actual: **`WAITING_HUMAN_REFERENCE`**.

Las expansiones técnicas y el programa U1 no se clasifican productivamente con SEMB 0.2 ni con candidatos SEMB 0.3 para producir narrativa histórica.

## Unidades breves y FRAGTYPE 0.3

`FRAGTYPE_0.3_SHADOW` conserva límites, IDs y hashes y reinterpreta la etiqueta residual `heading_candidate` como `short_residual_candidate`. Esos casos no se incorporan automáticamente a inferencia; existe una muestra ciega específica para validar su política final.

## Expansiones técnicas

CN4/CN6 contiene 1,888 JPEG reales y **19,067 fragmentos**; la vista de contenido único conserva **16,155 unidades textuales únicas**. Ola 2 contiene 19 libros, 3,177 JPEG y **36,195 fragmentos**. Ambas capas están `corpus_ready`, no `semantic_ready`.

## Dependencia documental

LTMD no supone independencia por `catalog_generation`. En CN4 1972↔1988, 188/214 páginas alineables (87.9%) son byte-idénticas en la misma posición. Las relaciones documentales, reutilizaciones y revisiones forman parte del estimando y de la trazabilidad.

## Catálogo maestro reproducible

El snapshot institucional indexado contiene 542 claves de visor, 542/542 visores alcanzables, 542/542 títulos recuperados y 191 familias de título nuclear. La identidad documental se fundamenta en `book_id` + `viewer_key`; `catalog_generation` no se usa automáticamente como `edition_year`.

## Derechos, licencias y reutilización

El **software original de LTMD** se distribuye bajo **Apache License 2.0**, conforme a [`LICENSE`](LICENSE).

Los **datos derivados originales de LTMD** sobre los cuales el licenciante posea o controle los derechos necesarios se ofrecen bajo **CC BY 4.0**, conforme a [`DATA_LICENSE.md`](DATA_LICENSE.md).

Estas licencias **no se aplican** a libros, PDF, JPEG, páginas, portadas, ilustraciones, texto fuente, OCR sustitutivo, marcas ni otros materiales de CONALITEG/SEP o terceros. Cuando una etapa necesita contenido fuente, éste se reconstruye temporalmente, se verifica contra el hash persistido y se elimina después del procesamiento.

Véanse [`docs/RIGHTS_AND_REUSE_0_1.md`](docs/RIGHTS_AND_REUSE_0_1.md), [`docs/RIGHTS_PUBLICATION_MATRIX_0_2.md`](docs/RIGHTS_PUBLICATION_MATRIX_0_2.md) y [`docs/LICENSE_DECISION_MEMO_0_1.md`](docs/LICENSE_DECISION_MEMO_0_1.md).

## Reproducibilidad e integridad científica

El corte de release utiliza **`LTMD_INTEGRITY_0.6`**, con **166/166 artefactos críticos presentes**, `missing_critical=[]` y recomputación SHA-256 completa en PASS. El desarrollo posterior de U1 en `main` se versionará en cortes de integridad posteriores y no altera ese tag.

El entorno de referencia es Ubuntu 24.04. `requirements-release.txt` fija la dependencia Python directa de SEMB 0.2 (`sentence-transformers==5.6.1`). Python patch-level y el lock transitivo de wheels permanecen documentados como parcialmente congelados.

## Publicación científica

LTMD separa dos productos:

1. **artículo de método/recurso digital** — [`docs/METHODS_ARTICLE_DRAFT_0_2.md`](docs/METHODS_ARTICLE_DRAFT_0_2.md);
2. **artículo histórico-educativo** — bloqueado hasta superar SEMB 0.3 y reconstruir la inferencia bajo unidades documentales defendibles.

La publicación de `v0.1.0-rc.1` se refiere a **publicabilidad del corte metodológico/técnico**, no a validación de SEMB 0.3 ni a confirmación de tendencias históricas exploratorias.

## Documentación central

La entrada recomendada es el **[Índice maestro de método](docs/METHOD_INDEX.md)**. Para la expansión integral, consulte el **[Plan Maestro LTMD-U1](docs/LTMD_U1_MASTER_PLAN_0_1.md)**.

## Regla epistemológica

LTMD privilegia una regla sencilla: **una cifra reproducible no es automáticamente una afirmación válida**. Cada salto —fuente, identidad documental, OCR, estructura, fragmentación, clasificación e inferencia— debe conservar evidencia suficiente para ser auditado independientemente.

## Citación

Mientras no exista un DOI versionado real, use la metadata de [`CITATION.cff`](CITATION.cff), el tag `v0.1.0-rc.1` y la GitHub Release correspondiente. Cuando Zenodo archive la release, deberá utilizarse el DOI versionado real de ese corte científico.
