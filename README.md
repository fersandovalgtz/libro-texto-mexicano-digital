# Libro de Texto Mexicano Digital

Infraestructura abierta de investigación para estudiar longitudinalmente los libros de texto mexicanos mediante historia de la educación, humanidades digitales, análisis computacional y ciencia abierta.

## Estado actual

**LTMD es ya una infraestructura histórico-computacional de corpus a escala sustancial dentro de la familia *Ciencias Naturales*. Las capas técnicas están reproduciblemente materializadas; la inferencia semántica histórica permanece deliberadamente bloqueada hasta completar la referencia humana de SEMB 0.3.**

El corte del **15 de agosto de 2026** contiene:

- **piloto CN5**: 759 imágenes reales y 9,594 fragmentos, con Rule A, SEMB 0.2 y análisis A/B exploratorio;
- **expansión CN4/CN6**: 1,897 posiciones declaradas, 1,888 JPEG reales y 19,067 fragmentos;
- **Ciencias Naturales Ola 2**: 19 libros, 3,177 JPEG fuente y 36,195 fragmentos;
- **64,856 ocurrencias técnicas de fragmento** en las tres capas anteriores;
- **catálogo maestro reproducible**: 542 visores históricos indexados, 542 títulos recuperados y 191 familias normalizadas de título nuclear;
- **familia estricta Ciencias Naturales**: 37 visores, de los cuales 35/37 tienen resolución completa de activos.

`corpus_ready` **no equivale** a `semantic_ready`. Las 64,856 ocurrencias tampoco equivalen a 64,856 observaciones históricas independientes: LTMD representa explícitamente reutilización, revisión, reemplazo y aliases documentales.

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

Para dependencia documental se mantienen tres vistas reversibles:

- **object view** — cada ocurrencia dentro del objeto que la contiene;
- **unique-content view** — contenido idéntico agrupado sin borrar procedencia;
- **revision view** — continuidad, sustitución y revisión entre objetos.

## Familia estricta *Ciencias Naturales*

El inventario estricto contiene **37 visores** en nueve generaciones del catálogo:

- `full_direct`: **31**;
- `full_alias_same_bytes`: **4**;
- `partial_internal_unserved`: **2**;
- `not_resolved`: **0**.

En total, **35/37 visores (94.6%)** tienen resolución completa de activos.

### 2018 → 2019: alias demostrado por bytes

Los cuatro visores 2018 de 3º, 4º, 5º y 6º no sirven sus JPEG bajo la clave 2018. La auditoría de enrutamiento encontró los activos 2019 correspondientes y comparó **652 pares**:

- SHA-256 idéntico: **652/652**;
- tamaño idéntico: **652/652**.

Las entradas 2018 se conservan como registros institucionales distintos, pero el contenido digital se modela como `catalog_entry_aliases_same_asset_bytes` y no se reprocesa como observación independiente.

### 2008: tres posiciones internas no servidas

Dos objetos 2008 conservan únicamente **tres posiciones internas** que el recurso público no sirve. Cada posición falló cinco intentos, mientras las posiciones adyacentes reprodujeron sus SHA-256 conocidos. LTMD registra el hecho como `internal_unserved_position_observed`; no lo interpreta como “página faltante del libro” sin cotejo bibliográfico externo.

## Piloto CN5

El piloto está formado por *Ciencias Naturales* de quinto grado en generaciones del catálogo **1972, 1988, 1993 y 2014**. `catalog_generation` se mantiene separada de año de edición, copyright e ISBN.

- 763 posiciones de visor;
- **759 JPEG reales**;
- 4 terminales sintéticos;
- OCR con texto detectable: **757/759**;
- PAGESTRUCT: **759 páginas**;
- FRAGSEG: **9,594 fragmentos**.

Es la única capa que actualmente llega a Rule A, SEMB 0.2, comparación A/B y una primera historia exploratoria.

## SEMB 0.2: resultado metodológico negativo

SEMB 0.2 produjo **99.49% de incertidumbre global**. En una batería sintética independiente de **105 casos**, su gate obtuvo:

- balanced accuracy: **0.526**;
- sensibilidad: **0.597**;
- especificidad: **0.455**.

El proyecto no corrigió esta limitación bajando umbrales después de observar las diferencias históricas. SEMB 0.2 se conserva como evidencia reproducible de una operacionalización insuficiente.

## SEMB 0.3: validación humana preregistrada

La infraestructura prehumana contiene **480 casos**:

- 320 `development`;
- 160 `locked_validation`;
- 120 casos reservados para doble codificación de fiabilidad;
- 312 páginas cubiertas por la muestra;
- 138 páginas representadas en validación bloqueada.

Los criterios de aceptación, arquitecturas candidatas, stage gates y reglas de apertura quedaron congelados antes de observar anotaciones humanas. La etapa actual es:

**`WAITING_HUMAN_REFERENCE`**

Las expansiones CN4/CN6 y Ola 2 no se clasifican productivamente con SEMB 0.2 ni con candidatos SEMB 0.3 para producir narrativa histórica.

## Corrección de FRAGSEG y unidades breves

La etiqueta residual `heading_candidate` del piloto resultó demasiado interpretativa. `FRAGTYPE_0.3_SHADOW` conserva límites, IDs y hashes y reinterpreta esas unidades como `short_residual_candidate`.

El universo potencial de fragmentos de ≥4 tokens pasa de **5,037 a 7,429 (+2,392; +47.5%)**, pero esos casos no se incorporan automáticamente a la inferencia. Existe una muestra ciega específica para validar la política final.

## Expansión CN4/CN6

Nueve objetos adicionales fueron auditados y procesados técnicamente.

### Procedencia y OCR

- posiciones declaradas: **1,897**;
- JPEG fuente reales: **1,888**;
- terminales sintéticos: **9**;
- SHA-256 verificados: **1,888/1,888**;
- texto detectado: **1,880/1,888 (99.58%)**;
- `no_text_detected`: 8;
- `unresolved`: 0.

### PAGESTRUCT

- `textual`: 877;
- `mixed_text_image`: 682;
- `visual_only`: 153;
- `toc_or_navigation`: 36;
- `bibliography_or_credits`: 30;
- `front_matter`: 2;
- `unknown`: 108;
- páginas elegibles para FRAGSEG: **1,559**.

### FRAGSEG

**19,067 fragmentos**, distribuidos en:

- 8,483 `short_residual_candidate`;
- 3,711 `question_candidate`;
- 3,183 `expository_candidate`;
- 2,906 `instruction_candidate`;
- 427 `activity_candidate`;
- 234 `experiment_candidate`;
- 87 `project_candidate`;
- 36 `assessment_candidate`.

Treinta y cuatro páginas conservan huecos legítimos de secuencia por 40 candidatos de cero tokens descartados; los IDs no se renumeran.

## Ciencias Naturales Ola 2

La Ola 2 incorporó exclusivamente objetos `full_direct` no procesados previamente. Excluye aliases 2018 y los dos objetos 2008 parciales.

### Activos y OCR

- **19 libros**;
- **3,177 JPEG**;
- SHA-256 verificados: **3,177/3,177**;
- texto detectado: **3,164/3,177 (99.59%)**;
- `no_text_detected`: 13;
- `unresolved`: 0.

### PAGESTRUCT

- `textual`: 1,459;
- `mixed_text_image`: 1,069;
- `visual_only`: 300;
- `toc_or_navigation`: 118;
- `bibliography_or_credits`: 80;
- `front_matter`: 1;
- `unknown`: 150;
- páginas elegibles para FRAGSEG: **2,528**.

### FRAGSEG

**36,195 fragmentos**, con 36,195 IDs únicos y cobertura de 2,528/2,528 páginas elegibles:

- 18,423 `short_residual_candidate`;
- 5,990 `question_candidate`;
- 4,897 `expository_candidate`;
- 4,720 `instruction_candidate`;
- 1,096 `activity_candidate`;
- 446 `experiment_candidate`;
- 432 `project_candidate`;
- 191 `assessment_candidate`.

Ochenta páginas conservan huecos legítimos correspondientes a 97 slots de cero tokens descartados.

## Dependencia documental

LTMD no supone independencia por `catalog_generation`.

### CN4 1972 ↔ 1988

De 214 páginas alineables, **188/214 (87.9%) son byte-idénticas** en la misma posición. Las diferencias están localizadas y el corpus se interpreta como reutilización masiva con revisión localizada, no como dos libros completamente independientes.

### Vista de contenido único CN4/CN6

Las 19,067 ocurrencias CN4/CN6 corresponden a:

- **16,155 unidades textuales únicas**;
- 1,857 unidades que aparecen más de una vez;
- 1,731 unidades que aparecen en dos o más libros;
- ratio unidades únicas / ocurrencias: **84.7%**.

La deduplicación es una vista analítica reversible; nunca elimina las ocurrencias originales ni su procedencia.

## Catálogo maestro reproducible

El snapshot institucional indexado contiene:

- **542 claves de visor**;
- **542/542 visores alcanzables**;
- **542/542 títulos recuperados**;
- **191 familias de título nuclear**;
- 8 grupos de títulos repetidos conservados como colas de auditoría.

La identidad documental se fundamenta en `book_id` + `viewer_key`; `catalog_generation` no se usa automáticamente como `edition_year`.

## Derechos y reutilización

El repositorio **no redistribuye indiscriminadamente PDF, imágenes ni OCR íntegro de las obras fuente**. Conserva identificadores, URLs de procedencia, tamaños, SHA-256, código, métricas y derivados no sustitutivos.

Cuando una etapa necesita contenido fuente, éste se reconstruye temporalmente, se verifica contra el hash persistido y se elimina después del procesamiento. Código y derivados propios se distinguen jurídicamente de los materiales fuente.

Véase [`docs/RIGHTS_AND_REUSE_0_1.md`](docs/RIGHTS_AND_REUSE_0_1.md).

## Reproducibilidad e integridad científica

El corte vigente es **`LTMD_INTEGRITY_0.5`**.

El manifiesto criptográfico conserva tamaño y SHA-256 de todos los artefactos declarados críticos. En el corte previo a la actualización visible del README verificó:

- **149/149 artefactos críticos presentes**;
- `missing_critical=[]`;
- 9 artefactos opcionales ya presentes;
- cuatro productos humanos futuros legítimamente ausentes: consenso SEMB 0.3, referencia de validación bloqueada, `model_lock` y resultado de validación bloqueada.

La actualización del README y del índice metodológico vuelve a disparar el manifiesto; el corte final debe conservar cero ausencias.

Archivos:

- [`data/derived/research_integrity_manifest.json`](data/derived/research_integrity_manifest.json)
- [`data/derived/research_integrity_manifest.md`](data/derived/research_integrity_manifest.md)

## Publicación científica

LTMD separa dos productos:

1. **artículo de método/recurso digital** — actualmente en [`docs/METHODS_ARTICLE_DRAFT_0_2.md`](docs/METHODS_ARTICLE_DRAFT_0_2.md);
2. **artículo histórico-educativo** — bloqueado hasta superar SEMB 0.3 y reconstruir la inferencia bajo unidades documentales defendibles.

Las cifras principales del manuscrito metodológico se recomputan automáticamente desde los artefactos congelados mediante [`scripts/verify_methods_article_claims.py`](scripts/verify_methods_article_claims.py) y CI.

## Documentación central

La entrada recomendada es el **[Índice maestro de método](docs/METHOD_INDEX.md)**.

Documentos clave:

- [`docs/PROJECT_STATUS_2026-08-15.md`](docs/PROJECT_STATUS_2026-08-15.md) — estado consolidado;
- [`docs/METHODS_SNAPSHOT_2026-08-15.md`](docs/METHODS_SNAPSHOT_2026-08-15.md) — instantánea metodológica escalada;
- [`docs/METHODS_ARTICLE_DRAFT_0_2.md`](docs/METHODS_ARTICLE_DRAFT_0_2.md) — manuscrito metodológico vigente;
- [`docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md`](docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md) — referencia humana;
- [`docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md`](docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md) — criterios congelados;
- [`docs/SEMB03_STAGE_GATES_0_1.md`](docs/SEMB03_STAGE_GATES_0_1.md) — gates semánticos;
- [`docs/DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md`](docs/DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md) — dependencia documental;
- [`docs/CN_WAVE2_COMPLETION_2026-08-15.md`](docs/CN_WAVE2_COMPLETION_2026-08-15.md) — cierre de Ola 2;
- [`docs/RELEASE_CHECKLIST_0_1.md`](docs/RELEASE_CHECKLIST_0_1.md) — release científica.

## Regla epistemológica del proyecto

LTMD privilegia una regla sencilla: **una cifra reproducible no es automáticamente una afirmación válida**. Cada salto —fuente, identidad documental, OCR, estructura, fragmentación, clasificación e inferencia— debe conservar evidencia suficiente para ser auditado independientemente.

Por ello el proyecto conserva también resultados negativos, aliases, posiciones no servidas, revisiones, huecos legítimos de secuencia y fallos de infraestructura: forman parte de la trazabilidad del corpus.

## Citación

Para trabajos académicos debe utilizarse la metadata versionada en [`CITATION.cff`](CITATION.cff) y, cuando se cite una release, la versión/DOI correspondiente a ese corte científico. No debe citarse una versión móvil de `main` como sustituto de una release congelada cuando exista una versión depositada.
