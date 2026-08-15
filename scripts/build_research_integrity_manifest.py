#!/usr/bin/env python3
"""Build a cryptographic integrity manifest for critical LTMD research artifacts."""
from __future__ import annotations
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path

OUT=Path('data/derived/research_integrity_manifest.json')
REPORT=Path('data/derived/research_integrity_manifest.md')
VERSION='LTMD_INTEGRITY_0.3'

# Required artifacts define the frozen methodological state or the reproducible
# corpus/model infrastructure. A missing critical artifact makes the manifest fail.
CRITICAL=[
 'README.md',
 'data/book_inventory.csv',
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
 'data/validation/semb03_candidate_grid.json',
 'data/validation/semb03_synthetic_stress_cases.csv',
 'data/validation/short_residual_validation_sample.csv',
 'data/validation/short_residual_annotation_template.csv',
 'docs/CODEBOOK_0_1.md',
 'docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md',
 'docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md',
 'docs/SEMB03_CANDIDATE_ARCHITECTURES_0_1.md',
 'docs/SEMB03_STAGE_GATES_0_1.md',
 'docs/SHORT_RESIDUAL_VALIDATION_PROTOCOL_0_1.md',
 'docs/HISTORICAL_ANALYSIS_PLAN_0_2.md',
 'docs/METHODS_SNAPSHOT_2026-08-15.md',
 'docs/AUTOMATED_WORK_CEILING_0_1.md',
 'docs/CURRICULAR_SOURCE_AUDIT_2026-08-15.md',
 'docs/PRIMARY_SOURCE_REGISTER_0_1.md',
 'docs/CURRICULAR_CONTEXT_0_2.md',
 'docs/ARTICLE_OUTLINE_PILOT_0_2.md',
 'docs/PUBLICATION_STRATEGY_0_1.md',
 'docs/CORPUS_EXPANSION_PLAN_0_1.md',
 'scripts/segment_fragments.py',
 'scripts/semantic_classifier_B02_core.py',
 'scripts/classify_fragments_B02.py',
 'scripts/sample_semb03_human_reference.py',
 'scripts/validate_semb03_annotations.py',
 'scripts/evaluate_semb03_human_reliability.py',
 'scripts/build_semb03_consensus_draft.py',
 'scripts/check_semb03_readiness.py',
 'scripts/lock_semb03_model.py',
 'scripts/evaluate_semb03_locked_validation.py',
 'scripts/build_semb03_synthetic_stress.py',
 'scripts/evaluate_semb02_synthetic_stress.py',
 'scripts/develop_semb03_gate_synthetic.py',
 'scripts/develop_semb03_label_heads_synthetic.py',
 'scripts/audit_fragseg_layout_proxy.py',
 'scripts/audit_semb03_sample_coverage.py',
 'scripts/build_fragtype03_shadow.py',
 'scripts/sample_short_residual_validation.py',
 'scripts/audit_frontmatter_bibliography.py',
 'scripts/selftest_semb03_infrastructure.py',
 'scripts/probe_catalog_search_architecture.py'
]

# Derived diagnostics are reproducible and important, but may appear only after
# their workflow has run. Presence and hash are recorded when available.
OPTIONAL=[
 'data/derived/semb02_synthetic_stress_result.json',
 'data/derived/semb03_sample_coverage.csv',
 'data/derived/semb03_sample_token_coverage.csv',
 'data/derived/fragseg_layout_proxy_summary.csv',
 'data/derived/frontmatter_bibliographic_audit.csv',
 'data/derived/semb03_gate_synthetic_development.json',
 'data/derived/semb03_label_heads_synthetic_development.json',
 'data/derived/semb03_readiness_report.json',
 'data/derived/catalog_search_architecture_probe.json'
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
    lines=['# Manifiesto de integridad científica LTMD','',f'Versión: `{VERSION}`.','',f'Commit observado: `{manifest["git_head"]}`.','',f'Archivos críticos verificados: **{len(CRITICAL)}**. Artefactos derivados adicionales presentes: **{manifest["optional_present_count"]}**.','',
           'Cada entrada conserva tamaño y SHA-256. Una modificación legítima produce una nueva huella auditable; una desaparición de un artefacto crítico hace fallar el workflow.','',
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
