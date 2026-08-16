# Preflight de release candidata LTMD

Candidata: **v0.1.0-rc.1**.

Commit observado: `18082d0067731035e72bb8689bb99d5271c6c2dd`.

RC técnicamente lista: **SÍ**.
Lista para publicación pública: **SÍ**.

Integridad: **150/150** (`LTMD_INTEGRITY_0.5`).
Verificación de cifras del artículo: **PASS**.

## Controles técnicos

- [x] `required_release_files` — missing=[]
- [x] `version_file` — VERSION='0.1.0-rc.1'
- [x] `citation_version` — expected 0.1.0-rc.1
- [x] `citation_date` — expected 2026-08-15
- [x] `no_invented_doi` — CFF explicitly defers DOI until real deposit
- [x] `integrity_0_5` — critical=150/150
- [x] `methods_claim_check` — passed=True
- [x] `direct_semantic_dependency_pinned` — sentence-transformers==5.6.1
- [x] `license_recommendation_documented` — Apache-2.0 + CC BY 4.0 recommendation recorded without applying licenses
- [x] `gitignore_private_` — requires private/
- [x] `gitignore_data_work_` — requires data/work/
- [x] `gitignore__env` — requires .env
- [x] `no_forbidden_source_or_work_files_tracked` — forbidden=[]
- [x] `semb03_human_gate_still_closed` — premature_outputs=[]

## Blockers de publicación

- Ninguno.

## Interpretación

`rc_technical_ready` significa que el corte puede auditarse como candidata metodológica. `publish_ready` exige además licencias materializadas y consistentes con la política preregistrada. El DOI no se exige antes de la publicación real: debe añadirse únicamente después de que Zenodo archive el tag correspondiente.
