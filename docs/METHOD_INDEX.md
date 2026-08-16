# Índice maestro de método — LTMD

**Libro de Texto Mexicano Digital**  
Corte documental: **15 de agosto de 2026**  
Release candidate metodológica: **v0.1.0-rc.1**

Este documento organiza la documentación metodológica vigente y permite reconstruir el estado científico del proyecto desde una sola entrada. LTMD combina un piloto semántico intensivo, dos expansiones técnicas de *Ciencias Naturales*, un catálogo maestro reproducible, una infraestructura de validación humana preregistrada y un paquete formal de release candidate.

## 1. Estado y alcance

- `PROJECT_STATUS_2026-08-15.md` — estado consolidado, corpus técnico, readiness de activos, bloqueos y trabajo permitido.
- `METHODS_SNAPSHOT_2026-08-15.md` — instantánea metodológica del corte escalado.
- `CN_WAVE2_COMPLETION_2026-08-15.md` — cierre técnico de Ola 2.
- `AUTOMATED_WORK_CEILING_0_1.md` — frontera entre trabajo automatizable y decisiones que requieren evidencia humana.

El corpus técnico materializa **64,856 ocurrencias de fragmento**: 9,594 del piloto CN5, 19,067 de CN4/CN6 y 36,195 de Ola 2. Esta cardinalidad describe ocurrencias técnicas, no 64,856 observaciones históricas independientes.

## 2. Corpus, procedencia e identidad documental

- `PRIMARY_SOURCE_REGISTER_0_1.md` — jerarquía de fuentes primarias y estado de verificación.
- `CORPUS_EXPANSION_PLAN_0_1.md` — estrategia de escalamiento.
- `DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md` — reglas para reutilización, revisión, reemplazo y deduplicación reversible.
- `CN6_1993_DOCUMENT_RELATION_0_1.md` — dos objetos de sexto dentro de una misma generación de catálogo.

La familia estricta *Ciencias Naturales* comprende 37 visores: 31 `full_direct`, 4 `full_alias_same_bytes`, 2 `partial_internal_unserved` y 0 `not_resolved`. Los aliases 2018→2019 están demostrados mediante 652/652 pares de activos byte-idénticos. Los dos objetos 2008 parciales conservan tres posiciones internas no servidas por el recurso público.

## 3. Estructura y segmentación

- `CODEBOOK_0_1.md` — definiciones de variables y categorías.
- `SHORT_RESIDUAL_VALIDATION_PROTOCOL_0_1.md` — validación de la reinterpretación de unidades breves residuales.

Pipeline técnico común:

`catálogo → visor → identidad documental → manifiesto de página + SHA-256 → OCR temporal → PAGESTRUCT → FRAGSEG → metadatos/hashes`

Las expansiones CN4/CN6 y Ola 2 están **`corpus_ready` pero no `semantic_ready`**.

## 4. Dependencia documental y vistas analíticas

LTMD distingue al menos tres vistas:

- `object view` — conserva cada ocurrencia dentro de su objeto documental;
- `unique-content view` — agrupa contenido idéntico sin borrar procedencia;
- `revision view` — representa continuidad, sustitución y revisión entre objetos.

En CN4/CN6, 19,067 ocurrencias corresponden a 16,155 unidades textuales únicas. La reutilización CN4 1972↔1988 y la identidad de activos 2018↔2019 demuestran que el tamaño bruto del corpus no puede interpretarse como tamaño efectivo de evidencia independiente.

## 5. Validación semántica

- `SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md` — protocolo ciego de anotación humana.
- `SEMB03_ACCEPTANCE_CRITERIA_0_1.md` — criterios preregistrados de aceptación.
- `SEMB03_CANDIDATE_ARCHITECTURES_0_1.md` — espacio cerrado de arquitecturas candidatas.
- `SEMB03_STAGE_GATES_0_1.md` — gates desde fiabilidad humana hasta model lock, validación bloqueada y producción.
- `HISTORICAL_ANALYSIS_PLAN_0_2.md` — plan histórico condicionado a validación.

SEMB 0.2 se conserva como **resultado metodológico negativo reproducible**: 99.49% de incertidumbre global. SEMB 0.3 permanece en `WAITING_HUMAN_REFERENCE`. La muestra prehumana contiene 480 casos: 320 de desarrollo, 160 de validación bloqueada y 120 destinados a doble codificación para fiabilidad.

No se permite usar la expansión del corpus para ajustar retrospectivamente el clasificador ni transformar las tendencias exploratorias de SEMB 0.2 en resultados históricos confirmados.

## 6. Publicación científica

- `METHODS_ARTICLE_DRAFT_0_2.md` — manuscrito metodológico vigente de la infraestructura escalada.
- `ARTICLE_OUTLINE_PILOT_0_2.md` — arquitectura de artículo derivada del piloto.
- `PUBLICATION_STRATEGY_0_1.md` — separación artículo de método/recurso y artículo histórico.
- `FIGURE_PIPELINE_0_1.md` — pipeline de figuras reproducibles.
- `TABLE_PILOT_OBJECTS_0_1.md` — tabla documental del piloto.

Las cifras principales de `METHODS_ARTICLE_DRAFT_0_2.md` se recomputan desde los artefactos congelados mediante `scripts/verify_methods_article_claims.py` y CI. El artículo histórico permanece bloqueado hasta que SEMB 0.3 supere la referencia humana.

## 7. Release candidate y reproducibilidad

- `../VERSION` — `0.1.0-rc.1`.
- `../CHANGELOG.md` — historial de la candidata.
- `RELEASE_NOTES_v0.1.0-rc.1.md` — alcance y exclusiones del corte.
- `RELEASE_CHECKLIST_0_1.md` — checklist vivo de promoción a release pública.
- `RELEASE_OUTPUTS_0_1.md` — outputs públicos por workflow y exclusiones.
- `REPRODUCIBILITY_ENVIRONMENT_0_1.md` — runtime, dependencias y límites del congelamiento.
- `REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md` — dictamen reproducible de la candidata.
- `../data/derived/release_candidate_preflight.json` — resultado ejecutable de preflight.

El preflight vigente registra `rc_technical_ready=true`, `technical_failures=[]`, integridad 150/150 y claim check del manuscrito en PASS. `publish_ready=false` se mantiene por dos blockers jurídicos/documentales: licencia del código y licencia/política de derivados originales.

## 8. Derechos, reutilización y licencias

- `RIGHTS_AND_REUSE_0_1.md` — separación de fuentes, código y derivados.
- `RIGHTS_PUBLICATION_MATRIX_0_2.md` — semáforo vigente para el corpus escalado.
- `LICENSE_DECISION_MEMO_0_1.md` — recomendación fundamentada de licencia; **no aplica todavía una licencia**.
- `DRAFT_CONALITEG_RIGHTS_INQUIRY.md` — borrador para aclaración institucional.

La recomendación pre-release es Apache-2.0 para código propio y CC BY 4.0 para derivados originales en la medida en que existan derechos licenciables, con exclusión expresa de obras, páginas, imágenes, texto fuente y otros materiales de CONALITEG/SEP o terceros. La decisión no se considera aplicada hasta materializar `LICENSE`/`DATA_LICENSE.md` y obtener `publish_ready=true`.

## 9. Contexto curricular e historiográfico

- `CURRICULAR_SOURCE_AUDIT_2026-08-15.md` — auditoría de fuentes curriculares.
- `CURRICULAR_CONTEXT_0_2.md` — contexto curricular con niveles de evidencia.

Las afirmaciones se separan por calidad de evidencia: objeto primario, norma oficial, fuente institucional retrospectiva e historiografía especializada. `catalog_generation` nunca se usa automáticamente como `edition_year`.

## 10. Integridad científica

El corte vigente es **`LTMD_INTEGRITY_0.5`**. Sus salidas son:

- `../data/derived/research_integrity_manifest.json`
- `../data/derived/research_integrity_manifest.md`

El manifiesto validado del corte registra **150/150 artefactos críticos presentes** y `missing_critical=[]`. Los productos humanos aún ausentes corresponden legítimamente a gates futuros: consenso SEMB 0.3, referencia de validación bloqueada, `model_lock` y resultado de validación bloqueada.

## 11. Regla de lectura del repositorio

Una capa técnica reproducible no debe confundirse con una inferencia histórica validada. El orden científico que gobierna LTMD es:

`procedencia → identidad/dependencia documental → OCR → estructura → segmentación → validación de constructo → clasificación → inferencia histórica`

Saltarse una de esas fronteras puede producir cifras reproducibles pero afirmaciones científicamente no defendibles. El proyecto conserva deliberadamente resultados negativos, fallos de infraestructura y anomalías documentales porque forman parte de la trazabilidad del método.
