#!/usr/bin/env python3
"""Build a cryptographic integrity manifest for critical LTMD research artifacts."""
from __future__ import annotations
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path

OUT=Path('data/derived/research_integrity_manifest.json')
REPORT=Path('data/derived/research_integrity_manifest.md')
VERSION='LTMD_INTEGRITY_0.1'
CRITICAL=[
 'README.md',
 'data/derived/page_structure.csv',
 'data/derived/fragment_manifest.csv',
 'data/derived/fragment_manifest_fragtype03_shadow.csv',
 'data/derived/semantic_B02_development_result.json',
 'data/derived/semantic_B02_validation_result.json',
 'data/derived/fragment_labels_B_summary.csv',
 'data/derived/semb02_uncertainty_diagnostic.md',
 'data/derived/fragseg_heading_candidate_audit.md',
 'data/validation/semb03_human_reference_sample.csv',
 'data/validation/semb03_human_reference_annotation_template.csv',
 'data/validation/semb03_reliability_subset.csv',
 'data/validation/semb03_acceptance_criteria.json',
 'docs/CODEBOOK_0_1.md',
 'docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md',
 'docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md',
 'docs/SEMB03_STAGE_GATES_0_1.md',
 'docs/SHORT_RESIDUAL_VALIDATION_PROTOCOL_0_1.md',
 'docs/HISTORICAL_ANALYSIS_PLAN_0_2.md',
 'scripts/segment_fragments.py',
 'scripts/semantic_classifier_B02_core.py',
 'scripts/classify_fragments_B02.py',
 'scripts/sample_semb03_human_reference.py',
 'scripts/check_semb03_readiness.py',
 'scripts/lock_semb03_model.py',
 'scripts/evaluate_semb03_locked_validation.py'
]
OPTIONAL=[
 'data/derived/semb02_synthetic_stress_result.json',
 'data/validation/semb03_synthetic_stress_cases.csv',
 'data/derived/semb03_sample_coverage.csv',
 'data/derived/fragseg_layout_proxy_summary.csv',
 'data/validation/short_residual_validation_sample.csv',
 'data/validation/short_residual_annotation_template.csv'
]

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def head():
    try:return subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    except Exception:return None

def main():
    files=[];missing=[]
    for name in CRITICAL:
        p=Path(name)
        if not p.exists():missing.append(name);continue
        files.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p),'required':True})
    if missing:raise SystemExit('missing critical artifacts: '+', '.join(missing))
    for name in OPTIONAL:
        p=Path(name)
        if p.exists():files.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p),'required':False})
    manifest={'integrity_version':VERSION,'generated_utc':datetime.now(timezone.utc).isoformat(),'git_head':head(),'critical_count':len(CRITICAL),'optional_present_count':sum(not x['required'] for x in files),'files':files}
    OUT.parent.mkdir(parents=True,exist_ok=True);json.dump(manifest,OUT.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    lines=['# Manifiesto de integridad científica LTMD','',f'Versión: `{VERSION}`.','',f'Commit observado: `{manifest["git_head"]}`.','',f'Archivos críticos verificados: **{len(CRITICAL)}**. Artefactos opcionales presentes: **{manifest["optional_present_count"]}**.','',
           'Cada entrada conserva tamaño y SHA-256. El propósito es detectar cambios posteriores en corpus congelado, protocolos, criterios y código crítico. El manifiesto no impide cambios legítimos: obliga a que una modificación produzca una nueva huella auditable.','',
           '## Archivos críticos']
    for x in files:
        if x['required']:lines.append(f"- `{x['path']}` — {x['bytes']} bytes — `{x['sha256']}`")
    if any(not x['required'] for x in files):
        lines+=['','## Artefactos derivados adicionales presentes']
        for x in files:
            if not x['required']:lines.append(f"- `{x['path']}` — `{x['sha256']}`")
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('critical',len(CRITICAL),'optional_present',manifest['optional_present_count'])

if __name__=='__main__':main()
