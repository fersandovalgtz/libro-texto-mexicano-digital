# Estado de preparación SEMB 0.3

Versión: `SEMB03_READINESS_0.4`.

**Etapa actual: `WAITING_HUMAN_REFERENCE`.**
**Módulos prehumanos materializados: 17/17.**

**Holdout final:** reemplazo privado comprometido criptográficamente; los 160 casos públicos históricos no son admisibles como validación final.

La infraestructura se verifica sin usar salidas A/B ni resultados históricos como función de selección.

## Controles estructurales
- PASS — `legacy_sample_n_480`: n=480
- PASS — `legacy_sample_unique_ids`: sample_id unique
- PASS — `legacy_sample_unique_fragments`: fragment_id unique
- PASS — `legacy_roles_320_160`: {'development': 320, 'locked_validation': 160}
- PASS — `legacy_generations_balanced`: {'1972': 120, '1988': 120, '1993': 120, '2014': 120}
- PASS — `template_blinded_fields`: forbidden_present=[]
- PASS — `template_n_480`: n=480
- PASS — `opaque_sample_ids`: all IDs opaque
- PASS — `template_matches_master`: same 480 IDs
- PASS — `reliability_n_120`: n=120
- PASS — `reliability_subset_of_master`: all reliability IDs valid
- PASS — `criteria_frozen`: SEMB03_ACCEPTANCE_0.1
- PASS — `candidate_grid_frozen`: SEMB03_CANDIDATES_0.1
- PASS — `development_grouped_by_page`: {'method': 'GroupKFold', 'n_splits': 5, 'group': 'page_id'}
- PASS — `holdout_integrity_version`: SEMB03_HOLDOUT_INTEGRITY_0.1
- PASS — `legacy_final_holdout_invalidated`: invalidated_by_prelock_public_exposure
- PASS — `replacement_holdout_contract`: 160 = 40/generation; legacy 480 excluded

## Módulos prehumanos
- ✅ `uncertainty_diagnostic`
- ✅ `synthetic_stress_suite`
- ✅ `synthetic_stress_result`
- ✅ `sample_coverage_audit`
- ✅ `sample_token_coverage`
- ✅ `heading_construct_audit`
- ✅ `layout_proxy_audit`
- ✅ `fragtype_shadow`
- ✅ `short_residual_sample`
- ✅ `short_residual_blind_template`
- ✅ `acceptance_criteria`
- ✅ `candidate_grid`
- ✅ `frontmatter_bibliographic_audit`
- ✅ `research_integrity_manifest`
- ✅ `synthetic_gate_candidate`
- ✅ `synthetic_label_head_candidate`
- ✅ `holdout_integrity_status`

## Artefactos de etapas posteriores
- `human_reference_consensus`: ausente
- `development_result`: ausente
- `private_holdout_commitment`: ausente
- `model_lock`: ausente
- `locked_validation_result`: ausente
- `production_manifest`: ausente

## Lectura
Si todos los módulos prehumanos están presentes y la etapa continúa en `WAITING_HUMAN_REFERENCE`, el bloqueo restante es epistemológico y deliberado: se necesita referencia humana real para desarrollar un modelo validable. Ningún candidato sintético puede saltar directamente a producción. La validación final sólo puede abrirse cuando existe un `SEMB03_MODEL_LOCK_0.2` ligado al compromiso del holdout privado de reemplazo.
