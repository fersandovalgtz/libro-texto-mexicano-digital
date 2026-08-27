#!/usr/bin/env python3
"""Report SEMB 0.3 readiness without opening private holdout or human labels.

Validates preregistered manifests, blinding and the 2026-08-27 holdout-integrity
remediation. It deliberately does not inspect classifier A/B or historical
comparison outputs as a model-selection signal.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

SAMPLE=Path('data/validation/semb03_human_reference_sample.csv')
TEMPLATE=Path('data/validation/semb03_human_reference_annotation_template.csv')
REL=Path('data/validation/semb03_reliability_subset.csv')
CRIT=Path('data/validation/semb03_acceptance_criteria.json')
GRID=Path('data/validation/semb03_candidate_grid.json')
INTEGRITY=Path('data/validation/semb03_holdout_integrity_status.json')
COMMITMENT=Path('data/validation/semb03_private_holdout_commitment.json')
LOCK=Path('data/validation/semb03_model_lock.json')
OUT_JSON=Path('data/derived/semb03_readiness_report.json')
OUT_MD=Path('data/derived/semb03_readiness_report.md')
VERSION='SEMB03_READINESS_0.4'


def read_csv(path):
    with path.open(encoding='utf-8',newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    checks=[]
    sample=read_csv(SAMPLE);template=read_csv(TEMPLATE);rel=read_csv(REL)
    criteria=json.load(CRIT.open(encoding='utf-8'));grid=json.load(GRID.open(encoding='utf-8'))
    integrity=json.load(INTEGRITY.open(encoding='utf-8'))

    def ck(name,ok,detail):
        checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
        if not ok:
            raise AssertionError(f'{name}: {detail}')

    ck('legacy_sample_n_480',len(sample)==480,f'n={len(sample)}')
    ck('legacy_sample_unique_ids',len({r['sample_id'] for r in sample})==480,'sample_id unique')
    ck('legacy_sample_unique_fragments',len({r['fragment_id'] for r in sample})==480,'fragment_id unique')
    roles={x:sum(r['analysis_role']==x for r in sample) for x in ('development','locked_validation')}
    ck('legacy_roles_320_160',roles=={'development':320,'locked_validation':160},str(roles))
    gens={g:sum(r['catalog_generation']==g for r in sample) for g in ('1972','1988','1993','2014')}
    ck('legacy_generations_balanced',all(v==120 for v in gens.values()),str(gens))
    tfields=set(template[0]) if template else set();forbidden={'catalog_generation','analysis_role','fragment_id','page_id','candidate_type','text_sha256'}
    ck('template_blinded_fields',not(tfields&forbidden),f'forbidden_present={sorted(tfields&forbidden)}')
    ck('template_n_480',len(template)==480,f'n={len(template)}')
    ck('opaque_sample_ids',all(re.fullmatch(r'S03-[0-9A-F]{16}',r['sample_id'] or '') for r in template),'all IDs opaque')
    ck('template_matches_master',{r['sample_id'] for r in template}=={r['sample_id'] for r in sample},'same 480 IDs')
    rel_ids={r['sample_id'] for r in rel}
    ck('reliability_n_120',len(rel)==120 and len(rel_ids)==120,f'n={len(rel)}')
    ck('reliability_subset_of_master',rel_ids<={r['sample_id'] for r in sample},'all reliability IDs valid')
    ck('criteria_frozen',criteria.get('criteria_version')=='SEMB03_ACCEPTANCE_0.1' and criteria.get('frozen_before_human_reference') is True,criteria.get('criteria_version','missing'))
    ck('candidate_grid_frozen',grid.get('candidate_grid_version')=='SEMB03_CANDIDATES_0.1' and grid.get('frozen_before_human_reference') is True,grid.get('candidate_grid_version','missing'))
    ck('development_grouped_by_page',grid.get('development_cv')=={'method':'GroupKFold','n_splits':5,'group':'page_id'},str(grid.get('development_cv')))

    legacy_status=integrity.get('legacy_public_sample',{})
    replacement=integrity.get('replacement_private_holdout',{})
    ck('holdout_integrity_version',integrity.get('integrity_version')=='SEMB03_HOLDOUT_INTEGRITY_0.1',integrity.get('integrity_version','missing'))
    ck('legacy_final_holdout_invalidated',legacy_status.get('final_validation_admissibility')=='invalidated_by_prelock_public_exposure',str(legacy_status.get('final_validation_admissibility')))
    ck('replacement_holdout_contract',replacement.get('n')==160 and replacement.get('per_generation')==40 and replacement.get('source_pool_must_exclude_all_legacy_480') is True,'160 = 40/generation; legacy 480 excluded')

    prehuman={
      'uncertainty_diagnostic':'data/derived/semb02_uncertainty_diagnostic.md',
      'synthetic_stress_suite':'data/validation/semb03_synthetic_stress_cases.csv',
      'synthetic_stress_result':'data/derived/semb02_synthetic_stress_result.json',
      'sample_coverage_audit':'data/derived/semb03_sample_coverage.md',
      'sample_token_coverage':'data/derived/semb03_sample_token_coverage.csv',
      'heading_construct_audit':'data/derived/fragseg_heading_candidate_audit.md',
      'layout_proxy_audit':'data/derived/fragseg_layout_proxy_audit.md',
      'fragtype_shadow':'data/derived/fragment_manifest_fragtype03_shadow.csv',
      'short_residual_sample':'data/validation/short_residual_validation_sample.csv',
      'short_residual_blind_template':'data/validation/short_residual_annotation_template.csv',
      'acceptance_criteria':'data/validation/semb03_acceptance_criteria.json',
      'candidate_grid':'data/validation/semb03_candidate_grid.json',
      'frontmatter_bibliographic_audit':'data/derived/frontmatter_bibliographic_audit.md',
      'research_integrity_manifest':'data/derived/research_integrity_manifest.json',
      'synthetic_gate_candidate':'data/derived/semb03_gate_synthetic_development.json',
      'synthetic_label_head_candidate':'data/derived/semb03_label_heads_synthetic_development.json',
      'holdout_integrity_status':'data/validation/semb03_holdout_integrity_status.json',
    }
    prehuman_state={key:Path(value).exists() for key,value in prehuman.items()}

    later={
      'human_reference_consensus':'private/semb03_human_reference_consensus.csv',
      'development_result':'data/validation/semb03_development_result.json',
      'private_holdout_commitment':'data/validation/semb03_private_holdout_commitment.json',
      'model_lock':'data/validation/semb03_model_lock.json',
      'locked_validation_result':'data/validation/semb03_locked_validation_result.json',
      'production_manifest':'data/validation/semb03_production_manifest.json',
    }
    later_state={key:Path(value).exists() for key,value in later.items()}

    stage='WAITING_HUMAN_REFERENCE'
    if later_state['human_reference_consensus']:
        stage='HUMAN_REFERENCE_PRESENT'
    if later_state['development_result']:
        stage='DEVELOPMENT_COMPLETE'
    if later_state['model_lock']:
        stage='MODEL_LOCKED'
    if later_state['locked_validation_result']:
        stage='LOCKED_VALIDATION_COMPLETE'
    if later_state['production_manifest']:
        stage='PRODUCTION_READY'

    commitment_valid=False
    if COMMITMENT.exists():
        commitment=json.load(COMMITMENT.open(encoding='utf-8'))
        commitment_valid=(
            commitment.get('commitment_version')=='SEMB03_PRIVATE_HOLDOUT_COMMITMENT_0.1'
            and commitment.get('holdout_n')==160
            and commitment.get('per_generation')=={'1972':40,'1988':40,'1993':40,'2014':40}
            and commitment.get('legacy_sample_excluded') is True
            and commitment.get('ids_public') is False
        )
        ck('private_holdout_commitment_contract',commitment_valid,'160 committed private cases; IDs not public; legacy excluded')

    lock_gate=False
    if LOCK.exists():
        lock=json.load(LOCK.open(encoding='utf-8'))
        lock_gate=(
            commitment_valid
            and lock.get('lock_version')=='SEMB03_MODEL_LOCK_0.2'
            and lock.get('legacy_public_holdout_admissible') is False
            and lock.get('locked_validation_accessed_before_lock') is False
            and bool(lock.get('private_holdout_commitment_sha256'))
        )
        ck('private_holdout_model_lock_gate',lock_gate,'lock 0.2 bound to replacement private holdout commitment')

    complete=sum(prehuman_state.values());total=len(prehuman_state)
    safe_to_open=bool(lock_gate and not later_state['locked_validation_result'])
    report={
      'readiness_version':VERSION,
      'stage':stage,
      'infrastructure_checks':checks,
      'prehuman_modules':prehuman_state,
      'prehuman_modules_present':complete,
      'prehuman_modules_total':total,
      'later_stage_artifacts':later_state,
      'legacy_public_locked_validation_admissible':False,
      'final_holdout_protocol':'replacement_private_committed',
      'private_holdout_commitment_valid':commitment_valid,
      'human_blocker':'A genuine human reference is required before validated model development.' if stage=='WAITING_HUMAN_REFERENCE' else None,
      'safe_to_open_locked_validation':safe_to_open,
    }
    OUT_JSON.parent.mkdir(parents=True,exist_ok=True)
    json.dump(report,OUT_JSON.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)

    lines=['# Estado de preparación SEMB 0.3','',f'Versión: `{VERSION}`.','',f'**Etapa actual: `{stage}`.**',f'**Módulos prehumanos materializados: {complete}/{total}.**','',
           '**Holdout final:** reemplazo privado comprometido criptográficamente; los 160 casos públicos históricos no son admisibles como validación final.','',
           'La infraestructura se verifica sin usar salidas A/B ni resultados históricos como función de selección.','', '## Controles estructurales']
    for item in checks:
        lines.append(f"- {item['status']} — `{item['check']}`: {item['detail']}")
    lines+=['','## Módulos prehumanos']
    for key,value in prehuman_state.items():
        lines.append(f"- {'✅' if value else '⬜'} `{key}`")
    lines+=['','## Artefactos de etapas posteriores']
    for key,value in later_state.items():
        lines.append(f"- `{key}`: {'presente' if value else 'ausente'}")
    lines+=['','## Lectura',
            'Si todos los módulos prehumanos están presentes y la etapa continúa en `WAITING_HUMAN_REFERENCE`, el bloqueo restante es epistemológico y deliberado: se necesita referencia humana real para desarrollar un modelo validable. Ningún candidato sintético puede saltar directamente a producción. La validación final sólo puede abrirse cuando existe un `SEMB03_MODEL_LOCK_0.2` ligado al compromiso del holdout privado de reemplazo.']
    OUT_MD.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
