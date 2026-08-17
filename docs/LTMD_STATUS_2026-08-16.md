# Libro de Texto Mexicano Digital — estado científico y técnico

Corte: **16 de agosto de 2026**.

## Regla epistemológica vigente

El proyecto opera temporalmente **sin referencia humana disponible**. Esto no bloquea la expansión técnica del corpus. Continúan procedencia, auditoría de activos, OCR técnico, PAGESTRUCT, FRAGSEG, metadatos, reutilización textual exacta, dependencia documental, integridad y documentación reproducible.

Permanecen no validados o estacionados CER/WER contra referencia humana, confiabilidad intercodificador, consenso humano, validación SEMB03 y cualquier afirmación histórica primaria que dependa de categorías semánticas automáticas no validadas. Véase `docs/NO_HUMAN_REFERENCE_OPERATING_MODE_0_1.md`.

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

El visor oficial construye la ruta `./c/{ag_clave}/{ag_page}.jpg` con numeración a tres dígitos. El probe mínimo de conformidad produjo **12/12 HTTP 404** en cuatro visores 2018 y **12/12 HTTP 200** en los controles 2019 del mismo grado. Esto descarta, para el muestreo, un error general de fórmula de LTMD y documenta un subárbol oficial 2018 no servido en esa ruta; **no demuestra inexistencia de las obras ni autoriza sustituirlas por 2019**. `H2014P5FCA` permanece retenido por un hueco interno aislado.

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

## Comparación técnica W4 ↔ W7

El comparador no semántico `LTMD_U1_W4_W7_TECHNICAL_COMPARISON_0.1` fue publicado con éxito. Entre sus descriptores:

- Páginas PAGESTRUCT elegibles: **83.60% W4** vs **84.18% W7**.
- Fragmentos por página elegible: **10.595 W4** vs **12.186 W7**.
- `mixed_text_image`: **24.90% W4** vs **37.07% W7**.
- Unidades exactas repetidas: **14.11% W4** vs **24.06% W7**.
- Unidades exactas presentes en ≥2 generaciones: **13.71% W4** vs **22.58% W7**.

Estas diferencias son descriptivas de dos conjuntos con dominios, generaciones e inventarios distintos. Sirven para formular hipótesis y auditar el comportamiento del pipeline; no justifican atribuciones causales a reformas, asignaturas o periodos sin diseño posterior y validación humana. Véase `docs/LTMD_U1_W4_W7_TECHNICAL_COMPARISON.md`.

## Integridad científica

`LTMD_INTEGRITY_0.9` preserva el perímetro 0.8 y promueve a críticos los nueve productos W3 que habían permanecido opcionales hasta materializarse: manifiesto y resumen FRAGSEG, auditoría de huecos de secuencia, reporte FRAGSEG, unidades textuales exactas, proyección identidad-contenido, solapamiento exacto entre visores, reporte de reuso exacto y cierre técnico W3. El propio constructor 0.9 forma parte del perímetro. Cada artefacto crítico conserva tamaño y SHA-256; la desaparición de cualquiera hace fallar el workflow de integridad.

## Orquestación y recuperación

Las cadenas costosas separan fuente, OCR, PAGESTRUCT y FRAGSEG. W7 fue migrado a una orquestación explícita: cada etapa downstream se lanza mediante `workflow_dispatch` con el gate `pipeline=true`. Esto evita depender de pushes del bot, elimina cascadas implícitas de `workflow_run` y evita su límite de profundidad. Los workflows de procesamiento no se autoejecutan por modificaciones de su propio YAML.

Los recoveries reutilizan artifacts válidos y recomputan únicamente visores faltantes cuando esa infraestructura existe. Un cambio descriptivo o de documentación no debe volver a lanzar OCR masivo.

## Prioridades inmediatas

1. Validar y congelar `LTMD_INTEGRITY_0.9` con el cierre W3 ya incorporado al perímetro crítico.
2. Investigar las cinco retenciones de fuente W7 mediante evidencia documental o descubrimiento de fuente, sin aliases heurísticos: el hueco `H2014P5FCA` y los cuatro subárboles 2018.
3. Diseñar, sólo si aporta valor científico, un comparador técnico W3↔W4↔W7 estrictamente descriptivo y no semántico.
4. Mantener sincronizados el tablero maestro, los reportes de cierre y el manifiesto de integridad después de cada cambio de perímetro.
5. Incorporar W3, W7 y la comparación W4↔W7 al artículo metodológico como evidencia técnica/descriptiva, manteniendo separada cualquier validación humana/semántica futura.

## Principio de publicación

La ausencia temporal de referencia humana cambia el **nivel de inferencia admisible**, no el estándar de ingeniería científica. Toda expansión mantiene provenance verificable, cardinalidades comprobables, aliases no destructivos, huecos explícitos, separación entre objeto y contenido y límites epistemológicos visibles.
