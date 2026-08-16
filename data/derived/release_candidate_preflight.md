# Preflight de release candidata LTMD

Candidata: **v0.1.0-rc.1**.

Commit observado: `cd3e5e6d2cb14210637da00b85e7a2db6935f0c9`.

RC técnicamente lista: **SÍ**.
Lista para publicación pública: **SÍ**.

Integridad: **166/166** (`LTMD_INTEGRITY_0.6`).
SHA-256 críticos recomputados: **PASS**.
Verificación de cifras del artículo: **PASS**.

## Controles técnicos

- [x] `required_release_files` — missing=[]
- [x] `version_file` — VERSION='0.1.0-rc.1'
- [x] `citation_version` — expected 0.1.0-rc.1
- [x] `citation_date` — expected 2026-08-15
- [x] `no_invented_doi` — CFF explicitly defers DOI until real deposit
- [x] `integrity_0_6_metadata` — version=LTMD_INTEGRITY_0.6 critical=166/166
- [x] `integrity_0_6_sha256_recomputed` — mismatches=[]
- [x] `methods_claim_check` — passed=True
- [x] `direct_semantic_dependency_pinned` — sentence-transformers==5.6.1
- [x] `license_policy_documented` — Apache-2.0 + CC BY 4.0 policy documented
- [x] `gitignore_private_` — requires private/
- [x] `gitignore_data_work_` — requires data/work/
- [x] `gitignore__env` — requires .env
- [x] `no_forbidden_source_or_work_files_tracked` — forbidden=[]
- [x] `semb03_human_gate_still_closed` — premature_outputs=[]

## Blockers de publicación

- Ninguno.

## Interpretación

`rc_technical_ready` significa que el corte puede auditarse como candidata metodológica y que las huellas críticas fueron recomputadas contra el checkout actual. `publish_ready` exige además licencias materializadas y consistentes con la política documentada. El DOI no se exige antes de la publicación real: debe añadirse únicamente después de que Zenodo archive el tag correspondiente.
