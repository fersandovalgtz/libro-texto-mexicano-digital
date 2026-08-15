# Índice maestro de método — LTMD

**Libro de Texto Mexicano Digital**  
Corte documental: **15 de agosto de 2026**.

Este documento organiza la documentación metodológica vigente y permite reconstruir el estado científico del proyecto desde una sola entrada. LTMD ya no se describe adecuadamente como un piloto aislado: combina un piloto semántico intensivo, dos expansiones técnicas de *Ciencias Naturales*, un catálogo maestro reproducible y una infraestructura de validación humana preregistrada.

## 1. Estado y alcance

- `PROJECT_STATUS_2026-08-15.md` — estado consolidado, corpus técnico, readiness de activos, bloqueos y trabajo permitido.
- `METHODS_SNAPSHOT_2026-08-15.md` — instantánea metodológica del corte escalado.
- `CN_WAVE2_COMPLETION_2026-08-15.md` — cierre técnico de la Ola 2.
- `AUTOMATED_WORK_CEILING_0_1.md` — frontera entre trabajo automatizable y decisiones que requieren evidencia humana.

El corpus técnico materializa **64,856 ocurrencias de fragmento**: 9,594 del piloto CN5, 19,067 de CN4/CN6 y 36,195 de Ola 2. Esta cardinalidad describe ocurrencias técnicas, no 64,856 observaciones históricas independientes.

## 2. Corpus, procedencia e identidad documental

- `PRIMARY_SOURCE_REGISTER_0_1.md` — jerarquía de fuentes primarias y estado de verificación.
- `CORPUS_EXPANSION_PLAN_0_1.md` — estrategia de escalamiento.
- `DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md` — reglas para reutilización, revisión, reemplazo y deduplicación reversible.
- `CN6_1993_DOCUMENT_RELATION_0_1.md` — caso de dos objetos de sexto dentro de una misma generación de catálogo.
- `RIGHTS_AND_REUSE_0_1.md` — política de fuentes, derivados, hashes, OCR temporal y redistribución.

La familia estricta *Ciencias Naturales* comprende 37 visores: 31 `full_direct`, 4 `full_alias_same_bytes`, 2 `partial_internal_unserved` y 0 `not_resolved`. Los cuatro aliases 2018→2019 están demostrados mediante 652/652 pares de activos byte-idénticos. Los dos objetos 2008 parciales conservan tres posiciones internas no servidas por el recurso público.

## 3. Estructura y segmentación

- `CODEBOOK_0_1.md` — definiciones de variables y categorías.
- `SHORT_RESIDUAL_VALIDATION_PROTOCOL_0_1.md` — protocolo para validar la reinterpretación de unidades breves residuales.

El pipeline técnico común es:

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
- `SEMB03_STAGE_GATES_0_1.md` — puertas desde fiabilidad humana hasta model lock, validación bloqueada y producción.
- `HISTORICAL_ANALYSIS_PLAN_0_2.md` — plan histórico condicionado a validación.

SEMB 0.2 se conserva como **resultado metodológico negativo reproducible**: 99.49% de incertidumbre global; en una batería sintética independiente de 105 casos, el gate obtuvo balanced accuracy 0.526, sensibilidad 0.597 y especificidad 0.455.

SEMB 0.3 permanece en `WAITING_HUMAN_REFERENCE`. La muestra prehumana contiene 480 casos: 320 de desarrollo, 160 de validación bloqueada y 120 destinados a doble codificación para fiabilidad. No se permite usar la expansión del corpus para ajustar retrospectivamente el clasificador.

## 6. Publicación científica

- `METHODS_ARTICLE_DRAFT_0_1.md` — primera formulación del artículo metodológico.
- `METHODS_ARTICLE_DRAFT_0_2.md` — manuscrito actualizado para la infraestructura escalada.
- `ARTICLE_OUTLINE_PILOT_0_2.md` — arquitectura de artículo derivada del piloto.
- `PUBLICATION_STRATEGY_0_1.md` — separación entre artículo de método/recurso y artículo histórico.
- `FIGURE_PIPELINE_0_1.md` — pipeline de figuras reproducibles.
- `TABLE_PILOT_OBJECTS_0_1.md` — tabla documental del piloto.
- `RELEASE_CHECKLIST_0_1.md` — requisitos de una release científica estable.

Las cifras principales de `METHODS_ARTICLE_DRAFT_0_2.md` se recomputan desde los artefactos congelados mediante `scripts/verify_methods_article_claims.py` y CI. El artículo histórico permanece bloqueado hasta que SEMB 0.3 supere la referencia humana y se reconstruyan los análisis bajo el nuevo estimando documental.

## 7. Contexto curricular e historiográfico

- `CURRICULAR_SOURCE_AUDIT_2026-08-15.md` — auditoría de fuentes curriculares.
- `CURRICULAR_CONTEXT_0_2.md` — contexto curricular con niveles de evidencia.

Las afirmaciones se separan por calidad de evidencia: objeto primario, norma oficial, fuente institucional retrospectiva e historiografía especializada. `catalog_generation` nunca se usa automáticamente como `edition_year`.

## 8. Integridad científica

El corte vigente es **`LTMD_INTEGRITY_0.5`**. Sus salidas son:

- `../data/derived/research_integrity_manifest.json`
- `../data/derived/research_integrity_manifest.md`

Antes de esta actualización del índice, el manifiesto verificó **149/149 artefactos críticos**, `missing_critical=[]`. Los productos aún ausentes corresponden legítimamente a gates humanos futuros: consenso SEMB 0.3, referencia de validación bloqueada, `model_lock` y resultado de validación bloqueada.

Al formar este índice parte de la documentación metodológica central, el manifiesto siguiente debe incorporarlo al conjunto crítico y conservar cero ausencias.

## 9. Regla de lectura del repositorio

Una capa técnica reproducible no debe confundirse con una inferencia histórica validada. El orden científico que gobierna LTMD es:

`procedencia → identidad/dependencia documental → OCR → estructura → segmentación → validación de constructo → clasificación → inferencia histórica`

Saltarse una de esas fronteras puede producir cifras reproducibles pero afirmaciones científicamente no defendibles. El proyecto conserva deliberadamente los resultados negativos, los fallos de infraestructura y las anomalías documentales porque también forman parte de la trazabilidad del método.
