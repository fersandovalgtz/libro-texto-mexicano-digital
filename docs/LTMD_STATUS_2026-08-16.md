# Libro de Texto Mexicano Digital — estado científico y técnico

Corte: **16 de agosto de 2026**.

## Regla epistemológica vigente

El proyecto opera temporalmente **sin referencia humana disponible**. Esto no bloquea la expansión técnica del corpus. Continúan procedencia, auditoría de activos, OCR técnico, PAGESTRUCT, FRAGSEG, metadatos, reutilización textual exacta, dependencia documental, integridad y documentación reproducible.

Permanecen no validados o estacionados CER/WER contra referencia humana, confiabilidad intercodificador, consenso humano, validación SEMB03 y cualquier afirmación histórica primaria que dependa de categorías semánticas automáticas no validadas. Véase `docs/NO_HUMAN_REFERENCE_OPERATING_MODE_0_1.md`.

## Semántica temporal y capa bibliográfica

`catalog_generation` se interpreta como **etiqueta institucional de cohorte/navegación** y no como fecha bibliográfica automática. `H2014P5FCA` constituye evidencia falsadora directa del supuesto `catalog_generation == publication_year`: su página legal institucional, verificada contra SHA-256 y tamaño, declara **Primera edición 2014** y **Tercera reimpresión 2017 (ciclo escolar 2017–2018)**.

Esta separación quedó incorporada al modelo de datos, a la gobernanza y al plan histórico `HISTORICAL_ANALYSIS_PLAN_0.3`: cualquier análisis longitudinal debe declarar si usa `catalog_generation`, `edition_year`, `reprint_year`, `school_cycle`, `copyright_year` u otra temporalidad primaria, y no puede intercambiarlas implícitamente.

### Fingerprint bibliográfico W7 admitido

El run **31994479276** (`success`) ejecutó `LTMD_U1_W7_ADMITTED_BIBLIOGRAPHIC_FINGERPRINTS_0.1` sobre los **25/25 visores W7 fuente-admitidos**. La ventana se limitó a páginas lógicas 1–12: **300/300 páginas** fueron descargadas temporalmente, verificadas contra SHA-256 + tamaño del manifiesto fuente y sometidas a OCR técnico. No se persistieron imágenes ni OCR completo.

El fingerprint conserva candidatos de edición, reimpresión, ciclo escolar e ISBN sin resolver automáticamente cuál declaración histórica corresponde a la edición vigente del ejemplar.

### Auditoría multímodo/checksum

El run **31995336575** (`success`) auditó **107 candidatos estructurados**. Resultado:

- candidatos `strong_multipsm`: **91**;
- visores con ≥1 candidato fuerte: **25/25**;
- `single_psm`: **10**;
- `cross_line_or_unretained_only`: **3**;
- ISBN rechazados por checksum ISBN-13: **3**.

La regla exige la misma declaración en ≥2 modos PSM sobre la misma página SHA-verificada; un ISBN requiere además checksum válido. El hallazgo de ISBN multímodo pero inválidos demuestra que acuerdo OCR no equivale por sí solo a corrección bibliográfica.

### Observaciones bibliográficas 0.2

El run **31995431165** (`success`) publicó `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.2`:

- observaciones semánticas materializadas: **93**;
- objetos con ≥1 observación: **26**;
- filas normalizadas de evidencia página/SHA: **95**;
- W7 admitidos cubiertos: **25/25**;
- `H2014P5FCA` conserva sus cuatro observaciones específicas pese a estar retenido del OCR productivo por el hueco de fuente.

La capa distingue explícitamente `edition_history_statement`, `reprint_history_statement`, `school_cycle_statement` e `isbn_statement` de una futura resolución de `edition_year` o “edición vigente”. Las declaraciones históricas observadas no se convierten automáticamente en una fecha canónica del visor. `human_validated=0` permanece visible.

Véanse `docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md`, `docs/DATA_MODEL.md`, `docs/DATA_GOVERNANCE.md`, `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`, `data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.md`, `data/catalog/ltmd_u1_w7_bibliographic_candidate_support.md` y `data/catalog/ltmd_bibliographic_observations.md`.

## Ciencias Naturales y W2 Matemáticas

El piloto y las expansiones de Ciencias Naturales permanecen como base metodológica. W2 Matemáticas está técnicamente cerrado con **64 visores**, **60/64** identidades con activos resueltos, **57** objetos canónicos, **3** aliases byte-idénticos, **11,945** páginas OCR SHA-verificadas, **10,145** páginas elegibles y **135,727** fragmentos técnicos. Las cuatro excepciones DMA 2018 permanecen explícitas y no se imputan.

## LTMD-U1 W3 — Español/Lengua — cerrado técnicamente

### Fuente y topología

- Identidades institucionales cubiertas: **130/130**.
- Objetos canónicos de procesamiento: **114**.
- Aliases de provenance: **16** = **8 byte-exactos + 8 de ruta 2018→2019**.
- Páginas fuente canónicas autorizadas: **20,765**.
- Huecos internos persistentes: **8**, conservados sin renumeración.
- Identidades bloqueadas por fuente: **0**.

Los ocho aliases de ruta 2018→2019 son relaciones explícitas de procesamiento/provenance. No constituyen por sí mismos afirmaciones de identidad histórica, bibliográfica, curricular, pedagógica o semántica.

### OCR 0.1 — cerrado

Run fuente: **GitHub Actions 31960694824**, conclusión `success`.

- Canónicos procesados: **114/114**.
- Páginas procesadas: **20,765**.
- SHA-256 verificados: **20,765/20,765**.
- Texto detectado: **20,588/20,765 (99.15%)**.
- `no_text_detected`: **177**.
- `unresolved`: **0**.

El primer render del reporte OCR mostró por error `ruta 2018→2019: 0` debido a un literal abreviado en el contador descriptivo. El estado canónico real es `paired_route_alias_2018_to_2019`; el combinador fue corregido y exige la invariante **8 + 8 = 16**. La corrección no cambia páginas, hashes, OCR ni provenance.

### PAGESTRUCT 0.1 — cerrado

- Páginas clasificadas: **20,765**.
- `textual`: **8,309**.
- `mixed_text_image`: **9,028**.
- `visual_only`: **1,498**.
- `front_matter`: **34**.
- `toc_or_navigation`: **409**.
- `bibliography_or_credits`: **411**.
- `unknown`: **1,076**.
- Páginas elegibles para FRAGSEG: **17,337**.

### FRAGSEG 0.1 — cerrado

Run principal: **GitHub Actions 31968601780**, conclusión `success`.

- Páginas elegibles con ≥1 fragmento: **17,337/17,337**.
- Páginas elegibles sin fragmentos: **0**.
- Fragmentos técnicos: **222,490**.
- IDs de fragmento únicos: **222,490**.
- Páginas con huecos legítimos de secuencia: **653**.
- Slots omitidos: **832**.

Tipos candidatos: 127,366 `short_residual_candidate`, 31,149 `expository_candidate`, 30,694 `instruction_candidate`, 26,322 `question_candidate`, 4,205 `activity_candidate`, 1,354 `project_candidate`, 795 `experiment_candidate` y 605 `assessment_candidate`.

### Reutilización textual exacta y dependencia documental — cerrada

Run principal: **GitHub Actions 31970661872**, conclusión `success`.

- Unidades textuales exactas únicas: **147,375**.
- Unidades repetidas en ≥2 ocurrencias canónicas: **40,956**.
- Unidades presentes en ≥2 visores canónicos: **40,118**.
- Unidades representadas en ≥2 generaciones de catálogo: **50,144**.
- Pares de visores canónicos con ≥1 unidad exacta compartida: **6,387**.

La igualdad de `text_sha256` documenta igualdad dentro de la representación OCR+FRAGSEG fijada. No demuestra por sí sola identidad bibliográfica ni equivalencia curricular, pedagógica, histórica o semántica.

Cierre validado: `docs/LTMD_U1_W3_COMPLETION.md`. El cierre es **técnico**, no una validación semántica; `SEMB03` permanece en `WAITING_HUMAN_REFERENCE`.

## LTMD-U1 W4 — Ciencias Sociales — cerrado técnicamente

### Fuente y topología

- Visores: **14/14**.
- Arquitectura dinámica estándar: **14/14**.
- Posiciones declaradas: **2,428**.
- JPEG servidos y hasheados: **2,414**.
- Terminales sintéticos: **14**.
- Huecos internos: **0**.
- Objetos `full_direct_source`: **14**.
- Pares de libros completos byte-idénticos: **0**.
- Páginas canónicas autorizadas: **2,414**.

El objeto 2008 *Exploración de la naturaleza y la sociedad* se conserva en W4 por la clasificación operacional congelada; esto no afirma equivalencia curricular o semántica con *Ciencias Sociales*.

### OCR 0.1

- SHA-256 verificados: **2,414/2,414**.
- Texto detectado: **2,397/2,414 (99.30%)**.
- `no_text_detected`: **17**.
- `unresolved`: **0**.

### PAGESTRUCT 0.1

- `textual`: **1,417**.
- `mixed_text_image`: **601**.
- `visual_only`: **179**.
- `front_matter`: **1**.
- `toc_or_navigation`: **33**.
- `bibliography_or_credits`: **34**.
- `unknown`: **149**.
- Páginas elegibles para FRAGSEG: **2,018**.

### FRAGSEG 0.1

- Páginas elegibles con ≥1 fragmento: **2,018/2,018**.
- Fragmentos técnicos: **21,380**.
- IDs únicos: **21,380**.
- Páginas con huecos legítimos de secuencia: **42**.
- Slots omitidos: **46**.

Tipos candidatos: 10,859 `short_residual_candidate`, 5,450 `expository_candidate`, 3,145 `instruction_candidate`, 1,707 `question_candidate`, 136 `activity_candidate`, 69 `experiment_candidate`, 9 `project_candidate` y 5 `assessment_candidate`.

### Reutilización textual exacta

- Unidades exactas únicas: **17,735**.
- Unidades repetidas en ≥2 ocurrencias: **2,503**.
- Unidades presentes en ≥2 visores: **2,454**.
- Unidades presentes en ≥2 generaciones: **2,431**.
- Pares de visores con ≥1 unidad exacta compartida: **85**.

El par `H1982P4CI384` ↔ `H1988P4CI120` comparte **994** unidades exactas (Jaccard **0.359884**). Esta es evidencia de reutilización textual exacta dentro de la representación OCR+FRAGSEG; no demuestra identidad bibliográfica ni equivalencia curricular, pedagógica o semántica.

Cierre: `docs/LTMD_U1_W4_COMPLETION.md`.

## LTMD-U1 W7 — Formación Cívica y Ética — cohorte admisible cerrada técnicamente

### Fuente, routing y admisibilidad

- Identidades históricas preservadas: **30/30**.
- Identidades fuente admitidas y canónicos de procesamiento: **25**.
- Identidades retenidas por fuente: **5**.
- Imputaciones o aliases para identidades retenidas: **0**.
- Páginas fuente canónicas autorizadas: **3,261**.
- Terminales sintéticos excluidos: **25**.
- Pares de libros completos byte-idénticos entre los 25 admitidos: **0**.

El visor oficial construye la ruta `./c/{ag_clave}/{ag_page}.jpg` con numeración a tres dígitos. El probe mínimo de conformidad produjo **12/12 HTTP 404** en cuatro visores 2018 y **12/12 HTTP 200** en los controles 2019 del mismo grado. Esto descarta, para el muestreo, un error general de fórmula de LTMD y documenta un subárbol oficial 2018 no servido en esa ruta; **no demuestra inexistencia de las obras ni autoriza sustituirlas por 2019**.

`H2014P5FCA` está retenido por un único hueco interno: **página lógica 104 / `104.jpg`**, con **224/225** JPEG institucionales servidos. La comparación SHA-256 contra otros libros W7 de quinto dio **0 coincidencias byte-exactas** con `H2019P5FCA` en las 224 posiciones comparables; no existe base para un alias de recuperación.

### Investigación de las cinco fuentes retenidas — 0.3

El snapshot `LTMD_U1_W7_WITHHELD_VIEWER_PRESENCE_0.1` (run **31994842361**, `success`) verificó sin solicitar JPEG de páginas que las **5/5 identidades retenidas** siguen presentes en `claves.json` y como visores HTML HTTP 200. Las cardinalidades gate/live coinciden exactamente:

- `H2014P5FCA`: 225/225;
- `H2018P3FCA`: 114/114;
- `H2018P4FCA`: 130/130;
- `H2018P5FCA`: 226/226;
- `H2018P6FCA`: 210/210.

Esto refuerza el diagnóstico correcto para 2018: **objeto/configuración y visor institucional presentes; activos de página no servidos bajo la ruta oficial observada**.

La huella bibliográfica específica de `H2014P5FCA`, extraída de las páginas lógicas 1–12 después de verificar **12/12 SHA-256 y tamaños**, identifica en su página legal:

- **Primera edición, 2014**;
- **Tercera reimpresión, 2017**;
- ciclo escolar **2017–2018**.

El ISBN no se leyó con fiabilidad suficiente y no se imputa desde fuentes secundarias.

Dos vías archivísticas quedaron no concluyentes por infraestructura: Wayback CDX devolvió HTTP 503/timeouts y el probe Common Crawl 2017–2020 obtuvo **0/8 consultas de índice válidas por objetivo**. Esos ceros no se interpretan como ausencia histórica.

Se evaluó además un espejo externo del ciclo 2017–2018 como posible fuente de una reconstrucción derivada. Tres runs (`31990532400`, `31990634303`, `31990733990`) terminaron antes de publicar evidencia porque el HTML servido a GitHub Actions no permitió autoverificar reproduciblemente la página candidata. No se aceptó ninguna imagen externa; el workflow quedó `workflow_dispatch` manual-only para evitar reintentos y no rebajar el gate.

La investigación está formalizada en `docs/LTMD_U1_W7_WITHHELD_SOURCE_RESEARCH_0_3.md` y `docs/LTMD_U1_W7_WITHHELD_SOURCE_ACCEPTANCE_CRITERIA.md`. La issue **#5**, `Resolver fuentes W7 retenidas sin aliases heurísticos`, conserva los criterios de cierre verificables.

Estado de este corte: **25/30 admitidas; 5/30 retenidas; 0 aliases nuevos; 0 reconstrucciones externas aceptadas**.

### OCR 0.1 — cerrado

Run principal: **GitHub Actions 31980270998**, conclusión `success`.

- Canónicos procesados: **25/25**.
- Páginas procesadas: **3,261**.
- SHA-256 verificados: **3,261/3,261**.
- Texto detectado: **3,255/3,261 (99.82%)**.
- `no_text_detected`: **6**.
- `unresolved`: **0**.

### PAGESTRUCT 0.1 — cerrado

Run principal: **GitHub Actions 31980974560**, conclusión `success`.

- Páginas clasificadas: **3,261**.
- `textual`: **1,536**.
- `mixed_text_image`: **1,209**.
- `visual_only`: **145**.
- `front_matter`: **4**.
- `toc_or_navigation`: **153**.
- `bibliography_or_credits`: **105**.
- `unknown`: **109**.
- Páginas elegibles para FRAGSEG: **2,745**.

### FRAGSEG 0.1 — cerrado

Run principal: **GitHub Actions 31981223566**, conclusión `success`.

- Páginas elegibles con ≥1 fragmento: **2,745/2,745**.
- Páginas elegibles sin fragmentos: **0**.
- Fragmentos técnicos: **33,451**.
- IDs únicos: **33,451**.
- Páginas con huecos legítimos de secuencia: **83**.
- Slots omitidos: **108**.

Tipos candidatos: 17,459 `short_residual_candidate`, 5,455 `expository_candidate`, 5,185 `instruction_candidate`, 3,870 `question_candidate`, 903 `activity_candidate`, 283 `assessment_candidate`, 155 `experiment_candidate` y 141 `project_candidate`.

### Reutilización textual exacta — cerrada

Run principal: **GitHub Actions 31981755624**, conclusión `success`.

- Unidades exactas únicas: **22,651**.
- Unidades repetidas en ≥2 ocurrencias: **5,449**.
- Unidades presentes en ≥2 visores: **5,313**.
- Unidades presentes en ≥2 generaciones: **5,115**.
- Pares de visores con ≥1 unidad exacta compartida: **300**.

Los pares 2014↔2019 del mismo grado concentran el mayor reuso observado; por ejemplo, `H2014P6FCA` ↔ `H2019P6FCA` comparte **1,555** unidades exactas (Jaccard **0.502911**). Esta evidencia documenta continuidad textual exacta dentro de la representación técnica; no demuestra por sí sola equivalencia curricular, editorial o pedagógica.

Cierre validado: `docs/LTMD_U1_W7_COMPLETION.md` (run **31981780547**, `success`). El cierre aplica sólo a la cohorte con fuente admisible; **W7 no se declara históricamente completo**.

## Comparaciones técnicas no semánticas

### W4 ↔ W7

El comparador `LTMD_U1_W4_W7_TECHNICAL_COMPARISON_0.1` permanece congelado. Entre sus descriptores:

- páginas PAGESTRUCT elegibles: **83.60% W4** vs **84.18% W7**;
- fragmentos por página elegible: **10.595 W4** vs **12.186 W7**;
- `mixed_text_image`: **24.90% W4** vs **37.07% W7**;
- unidades exactas repetidas: **14.11% W4** vs **24.06% W7**;
- unidades exactas presentes en ≥2 generaciones: **13.71% W4** vs **22.58% W7**.

### W3 ↔ W4 ↔ W7

El run **31994732022** (`success`) publicó `LTMD_U1_W3_W4_W7_TECHNICAL_COMPARISON_0.2`. El primer intento falló antes de publicar porque W3 conserva un schema de reuso exacto distinto; la versión 0.2 normaliza explícitamente `canonical_occurrence_count`, `canonical_viewer_count` y `represented_catalog_generation_count` sin modificar los productos W3 cerrados.

Descriptores de escala:

- objetos canónicos: **114 W3 / 14 W4 / 25 W7**;
- páginas: **20,765 / 2,414 / 3,261**;
- páginas elegibles: **17,337 (83.49%) / 2,018 (83.60%) / 2,745 (84.18%)**;
- fragmentos: **222,490 / 21,380 / 33,451**;
- fragmentos por página elegible: **12.833 / 10.595 / 12.186**;
- unidades exactas únicas: **147,375 / 17,735 / 22,651**;
- unidades exactas repetidas: **27.79% / 14.11% / 24.06%**;
- unidades en ≥2 visores: **27.22% / 13.84% / 23.46%**;
- unidades en ≥2 generaciones de catálogo: **34.02% / 13.71% / 22.58%**.

Estas diferencias caracterizan representaciones computacionales de cohortes con dominios, inventarios y coberturas históricas distintos. **No justifican inferencias de calidad educativa, complejidad pedagógica, reforma curricular ni cambio histórico.** Véase `docs/LTMD_U1_W3_W4_W7_TECHNICAL_COMPARISON.md`.

## Integridad científica

`LTMD_INTEGRITY_0.10` es el perímetro científico vigente. Preserva 0.9 y congela adicionalmente:

- semántica `catalog_generation` vs tiempo bibliográfico;
- `DATA_MODEL`, `DATA_GOVERNANCE` y `HISTORICAL_ANALYSIS_PLAN_0.3`;
- fingerprint específico `H2014P5FCA`;
- fingerprint W7 admitido 300/300;
- auditoría multímodo/checksum;
- observaciones bibliográficas 0.2 y su tabla normalizada de evidencia;
- snapshot y criterios de aceptación de las cinco fuentes W7 retenidas;
- comparador técnico W3↔W4↔W7;
- constructor versionado 0.10.

El run **31995509011** concluyó `success`. El manifiesto publicado declara:

- archivos críticos: **392**;
- críticos presentes: **392/392**;
- `missing_critical=[]`;
- opcionales presentes: **9**.

Los fallos de infraestructura de Wayback/Common Crawl y el espejo externo no verificado **no** se promueven al perímetro científico como resultados sustantivos.

## Orquestación y recuperación

Las cadenas costosas separan fuente, OCR, PAGESTRUCT y FRAGSEG. W7 fue migrado a una orquestación explícita: cada etapa downstream se lanza mediante `workflow_dispatch` con el gate `pipeline=true`. Esto evita depender de pushes del bot, elimina cascadas implícitas de `workflow_run` y evita su límite de profundidad. Los workflows de procesamiento no se autoejecutan por modificaciones de su propio YAML.

Los recoveries reutilizan artifacts válidos y recomputan únicamente visores faltantes cuando esa infraestructura existe. Un cambio descriptivo o de documentación no debe volver a lanzar OCR masivo. Los probes externos que no puedan autoverificarse reproduciblemente deben quedar manuales, no auto-reintentarse.

## Prioridades inmediatas

1. Para `H2014P5FCA`, buscar una fuente reproducible de la **tercera reimpresión 2017 / ciclo 2017–2018** y demostrar la correspondencia de la página 104 sin convertir una copia externa en `source_jpeg` institucional.
2. Para los cuatro `H2018...`, priorizar routing histórico, relocalización o huellas bibliográficas documentales; mantener la retención si no aparece evidencia suficiente y evitar aliases 2019 heurísticos.
3. Sobre las **93 observaciones bibliográficas**, diseñar una capa posterior de resolución de ejemplar que determine —sólo cuando la evidencia lo permita— qué declaración corresponde a la edición/reimpresión efectiva del objeto; no seleccionar simplemente el ordinal o año máximo.
4. Extender gradualmente la extracción bibliográfica a W3/W4/W2 usando el mismo contrato página + SHA + soporte, antes de formular cronologías editoriales amplias.
5. Incorporar W3, W7, la separación temporal, la capa bibliográfica y el comparador W3↔W4↔W7 al artículo metodológico como evidencia técnica/descriptiva, manteniendo separada cualquier validación humana/semántica futura.

## Principio de publicación

La ausencia temporal de referencia humana cambia el **nivel de inferencia admisible**, no el estándar de ingeniería científica. Toda expansión mantiene provenance verificable, cardinalidades comprobables, aliases no destructivos, huecos explícitos, separación entre objeto y contenido y límites epistemológicos visibles.
