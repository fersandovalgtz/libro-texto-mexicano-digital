#!/usr/bin/env python3
"""Report SEMB 0.3 readiness without opening human or locked-validation data.

Validates core preregistered manifests/blinding and reports the state of every
pre-human evidence module. It deliberately does not inspect classifier A/B or
historical comparison outputs as a model-selection signal.
"""
from __future__ import annotations
import csv,json,re
from pathlib import Path

SAMPLE=Path('data/validation/semb03_human_reference_sample.csv')
TEMPLATE=Path('data/validation/semb03_human_reference_annotation_template.csv')
REL=Path('data/validation/semb03_reliability_subset.csv')
CRIT=Path('data/validation/semb03_acceptance_criteria.json')
OUT_JSON=Path('data/derived/semb03_readiness_report.json')
OUT_MD=Path('data/derived/semb03_readiness_report.md')
VERSION='SEMB03_READINESS_0.2'

def read_csv(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
    checks=[]
    sample=read_csv(SAMPLE);template=read_csv(TEMPLATE);rel=read_csv(REL);criteria=json.load(CRIT.open(encoding='utf-8'))
    def ck(name,ok,detail):
        checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
        if not ok:raise AssertionError(f'{name}: {detail}')

    ck('sample_n_480',len(sample)==480,f'n={len(sample)}')
    ck('sample_unique_ids',len({r['sample_id'] for r in sample})==480,'sample_id unique')
    ck('sample_unique_fragments',len({r['fragment_id'] for r in sample})==480,'fragment_id unique')
    roles={x:sum(r['analysis_role']==x for r in sample) for x in ('development','locked_validation')}
    ck('roles_320_160',roles=={'development':320,'locked_validation':160},str(roles))
    gens={g:sum(r['catalog_generation']==g for r in sample) for g in ('1972','1988','1993','2014')}
    ck('generations_balanced',all(v==120 for v in gens.values()),str(gens))
    tfields=set(template[0]) if template else set();forbidden={'catalog_generation','analysis_role','fragment_id','page_id','candidate_type','text_sha256'}
    ck('template_blinded_fields',not(tfields&forbidden),f'forbidden_present={sorted(tfields&forbidden)}')
    ck('template_n_480',len(template)==480,f'n={len(template)}')
    ck('opaque_sample_ids',all(re.fullmatch(r'S03-[0-9A-F]{16}',r['sample_id'] or '') for r in template),'all IDs opaque')
    ck('template_matches_master',{r['sample_id'] for r in template}=={r['sample_id'] for r in sample},'same 480 IDs')
    rel_ids={r['sample_id'] for r in rel}
    ck('reliability_n_120',len(rel)==120 and len(rel_ids)==120,f'n={len(rel)}')
    ck('reliability_subset_of_master',rel_ids<={r['sample_id'] for r in sample},'all reliability IDs valid')
    ck('criteria_frozen',criteria.get('criteria_version')=='SEMB03_ACCEPTANCE_0.1' and criteria.get('frozen_before_human_reference') is True,criteria.get('criteria_version','missing'))

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
      'research_integrity_manifest':'data/derived/research_integrity_manifest.json',
      'synthetic_gate_candidate':'data/derived/semb03_gate_synthetic_development.json',
      'synthetic_label_head_candidate':'data/derived/semb03_label_heads_synthetic_development.json',
    }
    prehuman_state={k:Path(v).exists() for k,v in prehuman.items()}

    later={
      'human_reference_consensus':'private/semb03_human_reference_consensus.csv',
      'development_result':'data/validation/semb03_development_result.json',
      'model_lock':'data/validation/semb03_model_lock.json',
      'locked_validation_result':'data/validation/semb03_locked_validation_result.json',
      'production_manifest':'data/validation/semb03_production_manifest.json',
    }
    later_state={k:Path(v).exists() for k,v in later.items()}
    stage='WAITING_HUMAN_REFERENCE'
    if later_state['human_reference_consensus']:stage='HUMAN_REFERENCE_PRESENT'
    if later_state['development_result']:stage='DEVELOPMENT_COMPLETE'
    if later_state['model_lock']:stage='MODEL_LOCKED'
    if later_state['locked_validation_result']:stage='LOCKED_VALIDATION_COMPLETE'
    if later_state['production_manifest']:stage='PRODUCTION_READY'
    complete=sum(prehuman_state.values());total=len(prehuman_state)
    report={'readiness_version':VERSION,'stage':stage,'infrastructure_checks':checks,'prehuman_modules':prehuman_state,
            'prehuman_modules_present':complete,'prehuman_modules_total':total,'later_stage_artifacts':later_state,
            'human_blocker':'A genuine human reference is required before validated model development.' if stage=='WAITING_HUMAN_REFERENCE' else None,
            'safe_to_open_locked_validation':bool(later_state['model_lock'])}
    OUT_JSON.parent.mkdir(parents=True,exist_ok=True);json.dump(report,OUT_JSON.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    lines=['# Estado de preparación SEMB 0.3','',f'Versión: `{VERSION}`.','',f'**Etapa actual: `{stage}`.**',f'**Módulos prehumanos materializados: {complete}/{total}.**','',
           'La infraestructura se verifica sin usar salidas A/B ni resultados históricos como función de selección.','', '## Controles estructurales']
    for c in checks:lines.append(f"- {c['status']} — `{c['check']}`: {c['detail']}")
    lines+=['','## Módulos prehumanos']
    for k,v in prehuman_state.items():lines.append(f"- {'✅' if v else '⬜'} `{k}`")
    lines+=['','## Artefactos de etapas posteriores']
    for k,v in later_state.items():lines.append(f"- `{k}`: {'presente' if v else 'ausente'}")
    lines+=['','## Lectura','Mientras la etapa sea `WAITING_HUMAN_REFERENCE`, puede completarse infraestructura, pruebas sintéticas y candidatos provisionales. Ningún candidato sintético puede saltar directamente a producción. La validación bloqueada sólo es segura después de existir `model_lock`.']
    OUT_MD.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
