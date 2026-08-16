# Índice maestro de método — LTMD

**Libro de Texto Mexicano Digital**  
Corte documental: **15 de agosto de 2026**  
Release candidate metodológica: **v0.1.0-rc.1**

Este documento organiza la documentación metodológica vigente y permite reconstruir el estado científico del proyecto desde una sola entrada. LTMD combina un piloto semántico intensivo, expansiones técnicas de _Ciencias Naturales_, un catálogo maestro reproducible, infraestructura de validación humana preregistrada y un paquete formal de release.

## 1. Estado y alcance

- `PROJECT_STATUS_2026-08-15.md` — estado consolidado.
- `METHODS_SNAPSHOT_2026-08-15.md` — instantánea metodológica.
- `CN_WAVE2_COMPLETION_2026-08-15.md` — cierre técnico de Ola 2.
- `AUTOMATED_WORK_CEILING_0_1.md` — frontera entre automatización y evidencia humana.

El corpus técnico materializa **64,856 ocurrencias de fragmento**: 9,594 del piloto CN5, 19,067 de CN4/CN6 y 36,195 de Ola 2. Esta cardinalidad describe ocurrencias técnicas, no observaciones históricas independientes.

## 2. Corpus, procedencia e identidad documental

- `PRIMARY_SOURCE_REGISTER_0_1.md`
- `CORPUS_EXPANSION_PLAN_0_1.md`
- `DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md`
- `CN6_1993_DOCUMENT_RELATION_0_1.md`

La familia estricta _Ciencias Naturales_ comprende 37 visores: 31 `full_direct`, 4 `full_alias_same_bytes`, 2 `partial_internal_unserved` y 0 `not_resolved`. Los aliases 2018→2019 están demostrados mediante 652/652 pares byte-idénticos. Los dos objetos 2008 parciales conservan tres posiciones internas no servidas por el recurso público.

## 3. Estructura y segmentación

- `CODEBOOK_0_1.md`
- `SHORT_RESIDUAL_VALIDATION_PROTOCOL_0_1.md`

Pipeline técnico común:

`catálogo → visor → identidad documental → manifiesto de página + SHA-256 → OCR temporal → PAGESTRUCT → FRAGSEG → metadatos/hashes`

Las expansiones CN4/CN6 y Ola 2 están **`corpus_ready` pero no `semantic_ready`**.

## 4. Dependencia documental y vistas analíticas

LTMD distingue `object view`, `unique-content view` y `revision view`. En CN4/CN6, 19,067 ocurrencias corresponden a 16,155 unidades textuales únicas. Reutilización, revisión y aliases se representan explícitamente para evitar inflar independencia estadística.

## 5. Validación semántica

- `SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md`
- `SEMB03_ACCEPTANCE_CRITERIA_0_1.md`
- `SEMB03_CANDIDATE_ARCHITECTURES_0_1.md`
- `SEMB03_STAGE_GATES_0_1.md`
- `HISTORICAL_ANALYSIS_PLAN_0_2.md`

SEMB 0.2 se conserva como **resultado metodológico negativo reproducible**: 99.49% de incertidumbre global. SEMB 0.3 permanece en `WAITING_HUMAN_REFERENCE`. La muestra prehumana contiene 480 casos: 320 de desarrollo, 160 de validación bloqueada y 120 destinados a doble codificación para fiabilidad.

No se permite usar la expansión del corpus para ajustar retrospectivamente el clasificador ni transformar tendencias exploratorias de SEMB 0.2 en resultados históricos confirmados.

## 6. Publicación científica

- `METHODS_ARTICLE_DRAFT_0_2.md` — manuscrito metodológico vigente.
- `ARTICLE_OUTLINE_PILOT_0_2.md`
- `PUBLICATION_STRATEGY_0_1.md`
- `FIGURE_PIPELINE_0_1.md`
- `TABLE_PILOT_OBJECTS_0_1.md`

Las cifras principales del manuscrito se recomputan mediante `scripts/verify_methods_article_claims.py` y CI. El artículo histórico permanece bloqueado hasta que SEMB 0.3 supere la referencia humana.

## 7. Release candidate y reproducibilidad

- `../VERSION` — `0.1.0-rc.1`.
- `../CHANGELOG.md`
- `RELEASE_NOTES_v0.1.0-rc.1.md`
- `RELEASE_CHECKLIST_0_1.md`
- `RELEASE_OUTPUTS_0_1.md`
- `REPRODUCIBILITY_ENVIRONMENT_0_1.md`
- `REPRODUCIBILITY_REPORT_v0.1.0-rc.1.md`
- `../data/derived/release_candidate_preflight.json`

El preflight vigente exige y ha demostrado `rc_technical_ready=true`, `publish_ready=true`, `technical_failures=[]`, `publish_blockers=[]`, integridad **166/166**, recomputación SHA-256 completa sin discrepancias y claim check del manuscrito en PASS.

`publish_ready=true` se refiere al corte metodológico/técnico; no abre ni sustituye gates humanos.

## 8. Derechos, reutilización y licencias

- `../LICENSE` — Apache License 2.0 para software propio.
- `../DATA_LICENSE.md` — CC BY 4.0 para derivados originales licenciables bajo alcance limitado.
- `RIGHTS_AND_REUSE_0_1.md`
- `RIGHTS_PUBLICATION_MATRIX_0_2.md`
- `LICENSE_DECISION_MEMO_0_1.md`
- `DRAFT_CONALITEG_RIGHTS_INQUIRY.md`

Las licencias adoptadas excluyen expresamente obras, páginas, imágenes, texto fuente, OCR sustitutivo y otros materiales de CONALITEG/SEP o terceros. La consulta institucional sigue siendo útil para usos futuros más amplios, pero no es blocker del paquete público conservador.

## 9. Contexto curricular e historiográfico

- `CURRICULAR_SOURCE_AUDIT_2026-08-15.md`
- `CURRICULAR_CONTEXT_0_2.md`

Las afirmaciones se separan por calidad de evidencia: objeto primario, norma oficial, fuente institucional retrospectiva e historiografía especializada. `catalog_generation` nunca se usa automáticamente como `edition_year`.

## 10. Integridad científica

El corte vigente es **`LTMD_INTEGRITY_0.6`**:

- `../data/derived/research_integrity_manifest.json`
- `../data/derived/research_integrity_manifest.md`

El manifiesto registra **166/166 artefactos críticos presentes** y `missing_critical=[]`. El preflight recomputa cada SHA-256 crítico contra el checkout. Los productos humanos aún ausentes corresponden legítimamente a gates futuros: consenso SEMB 0.3, referencia de validación bloqueada, `model_lock` y resultado de validación bloqueada.

## 11. Regla de lectura del repositorio

Una capa técnica reproducible no debe confundirse con una inferencia histórica validada. El orden científico es:

`procedencia → identidad/dependencia documental → OCR → estructura → segmentación → validación de constructo → clasificación → inferencia histórica`

Saltarse una frontera puede producir cifras reproducibles pero afirmaciones científicamente no defendibles. LTMD conserva deliberadamente resultados negativos, fallos de infraestructura y anomalías documentales porque forman parte de la trazabilidad del método.
