#!/usr/bin/env python3
"""Build a cryptographic integrity manifest for critical LTMD research artifacts.

LTMD_INTEGRITY_0.5 freezes the scaled Ciencias Naturales technical corpus cut:
CN5 pilot + CN4/CN6 expansion + Wave 2, together with family asset-readiness,
document-dependence evidence, the methods manuscript, and the prehuman SEMB 0.3
infrastructure. Future human-reference/model outputs remain optional until their
stage gates are legitimately crossed.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('data/derived/research_integrity_manifest.json')
REPORT = Path('data/derived/research_integrity_manifest.md')
VERSION = 'LTMD_INTEGRITY_0.5'

CRITICAL = [
    # Repository/release identity
    'README.md',
    'CITATION.cff',
    'data/book_inventory.csv',

    # CN5 pilot frozen technical + semantic-diagnostic layers
    'data/derived/page_structure.csv',
    'data/derived/fragment_manifest.csv',
    'data/derived/fragment_manifest_fragtype03_shadow.csv',
    'data/derived/semantic_B02_development_result.json',
    'data/derived/semantic_B02_validation_result.json',
    'data/derived/fragment_labels_B_summary.csv',
    'data/derived/semb02_uncertainty_diagnostic.md',
    'data/derived/fragseg_heading_candidate_audit.md',
    'data/derived/semb02_synthetic_stress_result.json',
    'data/derived/methods_article_claim_check.json',

    # SEMB 0.3 preregistered prehuman infrastructure
    'data/validation/semb03_human_reference_sample.csv',
    'data/validation/semb03_human_reference_annotation_template.csv',
    'data/validation/semb03_reliability_subset.csv',
    'data/validation/semb03_acceptance_criteria.json',
    'data/validation/semb03_candidate_grid.json',
    'data/validation/semb03_synthetic_stress_cases.csv',
    'data/validation/short_residual_validation_sample.csv',
    'data/validation/short_residual_annotation_template.csv',

    # Methodological contracts and state documentation
    'docs/CODEBOOK_0_1.md',
    'docs/SEMB03_HUMAN_ANNOTATION_PROTOCOL_0_1.md',
    'docs/SEMB03_ACCEPTANCE_CRITERIA_0_1.md',
    'docs/SEMB03_CANDIDATE_ARCHITECTURES_0_1.md',
    'docs/SEMB03_STAGE_GATES_0_1.md',
    'docs/SHORT_RESIDUAL_VALIDATION_PROTOCOL_0_1.md',
    'docs/HISTORICAL_ANALYSIS_PLAN_0_2.md',
    'docs/METHODS_SNAPSHOT_2026-08-15.md',
    'docs/PROJECT_STATUS_2026-08-15.md',
    'docs/AUTOMATED_WORK_CEILING_0_1.md',
    'docs/CURRICULAR_SOURCE_AUDIT_2026-08-15.md',
    'docs/PRIMARY_SOURCE_REGISTER_0_1.md',
    'docs/CURRICULAR_CONTEXT_0_2.md',
    'docs/ARTICLE_OUTLINE_PILOT_0_2.md',
    'docs/METHODS_ARTICLE_DRAFT_0_1.md',
    'docs/METHODS_ARTICLE_DRAFT_0_2.md',
    'docs/PUBLICATION_STRATEGY_0_1.md',
    'docs/CORPUS_EXPANSION_PLAN_0_1.md',
    'docs/RELEASE_CHECKLIST_0_1.md',
    'docs/FIGURE_PIPELINE_0_1.md',
    'docs/TABLE_PILOT_OBJECTS_0_1.md',
    'docs/RIGHTS_AND_REUSE_0_1.md',
    'docs/CN6_1993_DOCUMENT_RELATION_0_1.md',
    'docs/DOCUMENT_DEPENDENCE_ANALYSIS_PLAN_0_1.md',
    'docs/CN_WAVE2_COMPLETION_2026-08-15.md',

    # Public catalog snapshot and normalized index
    'data/catalog/conaliteg_historical_viewer_keys.csv',
    'data/catalog/conaliteg_historical_catalog_snapshot.csv',
    'data/catalog/conaliteg_historical_title_inventory.csv',
    'data/catalog/conaliteg_title_cores.csv',
    'data/catalog/conaliteg_title_core_summary.csv',
    'data/catalog/conaliteg_duplicate_title_groups.csv',

    # Strict Ciencias Naturales family: identity/readiness/anomalies
    'data/catalog/ciencias_naturales_family_inventory.csv',
    'data/catalog/ciencias_naturales_family_asset_readiness.csv',
    'data/catalog/ciencias_naturales_family_asset_readiness.md',
    'data/catalog/cn2018_2019_asset_identity.csv',
    'data/catalog/cn2018_2019_asset_identity.md',
    'data/catalog/cn_catalog_alias_relationships.csv',
    'data/catalog/cn2008_internal_unserved_audit.csv',
    'data/catalog/cn2008_internal_unserved_audit.md',

    # CN4/CN6 object/provenance/technical layers — closed through FRAGSEG
    'data/expansion/cn46_viewer_candidates.csv',
    'data/expansion/cn46_inventory_preliminary.csv',
    'data/expansion/cn46_page_manifest.csv',
    'data/expansion/cn46_page_manifest_summary.csv',
    'data/expansion/cn46_ocr_page_metrics.csv',
    'data/expansion/cn46_ocr_summary.csv',
    'data/expansion/cn46_page_structure.csv',
    'data/expansion/cn46_page_structure_summary.csv',
    'data/expansion/cn46_fragment_manifest.csv',
    'data/expansion/cn46_fragment_manifest_summary.csv',
    'data/expansion/cn46_fragment_sequence_gaps.csv',
    'data/expansion/cn46_fragment_manifest_report.md',
    'data/expansion/document_relationships_0_1.csv',
    'data/expansion/document_clusters_0_1.csv',
    'data/expansion/cn6_1993_document_relation.csv',
    'data/expansion/cn4_1972_1988_page_differences.csv',
    'data/expansion/cn4_1972_1988_changed_page_similarity.csv',

    # Ciencias Naturales Wave 2 — frozen queue through FRAGSEG
    'data/expansion/cn_wave2_ingestion_queue.csv',
    'data/expansion/cn_wave2_ingestion_queue.md',
    'data/expansion/cn_wave2_page_manifest.csv',
    'data/expansion/cn_wave2_ocr_page_metrics.csv',
    'data/expansion/cn_wave2_ocr_summary.csv',
    'data/expansion/cn_wave2_ocr_report.md',
    'data/expansion/cn_wave2_page_structure.csv',
    'data/expansion/cn_wave2_page_structure_summary.csv',
    'data/expansion/cn_wave2_page_structure_report.md',
    'data/expansion/cn_wave2_fragment_manifest.csv',
    'data/expansion/cn_wave2_fragment_manifest_summary.csv',
    'data/expansion/cn_wave2_fragment_sequence_gaps.csv',
    'data/expansion/cn_wave2_fragment_manifest_report.md',

    # Core pilot/validation code
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

    # Catalog/CN4-CN6 expansion code
    'scripts/probe_catalog_search_architecture.py',
    'scripts/snapshot_conaliteg_catalog_keys.py',
    'scripts/audit_conaliteg_catalog_titles.py',
    'scripts/normalize_conaliteg_catalog_titles.py',
    'scripts/analyze_catalog_title_duplicates.py',
    'scripts/build_ciencias_naturales_family_inventory.py',
    'scripts/discover_cn46_viewers.py',
    'scripts/audit_cn46_expansion_objects.py',
    'scripts/extract_cn46_bibliographic_sequences.py',
    'scripts/audit_cn6_1993_legal_pages.py',
    'scripts/build_cn46_page_manifest.py',
    'scripts/analyze_cn46_exact_page_overlap.py',
    'scripts/analyze_cn4_1972_1988_differences.py',
    'scripts/audit_cn4_1972_1988_changed_page_similarity.py',
    'scripts/ocr_cn46_expansion_metrics.py',
    'scripts/audit_cn46_no_text_pages.py',
    'scripts/extract_cn46_structural_keyword_flags.py',
    'scripts/classify_cn46_page_structure.py',
    'scripts/segment_cn46_fragments.py',
    'scripts/combine_cn46_fragment_shards.py',

    # Current article verification and Wave 2 segmentation code
    'scripts/verify_methods_article_claims.py',
    'scripts/segment_cn_wave2_fragments.py',
    'scripts/combine_cn_wave2_fragment_shards.py',

    # Workflows that define the newly frozen family/Wave2 chain
    '.github/workflows/build-cn-family-asset-readiness.yml',
    '.github/workflows/audit-cn2018-2019-asset-identity.yml',
    '.github/workflows/audit-cn2008-internal-unserved.yml',
    '.github/workflows/build-cn-wave2-ingestion.yml',
    '.github/workflows/ocr-cn-wave2.yml',
    '.github/workflows/page-structure-cn-wave2.yml',
    '.github/workflows/recover-page-structure-cn-wave2.yml',
    '.github/workflows/fragment-cn-wave2.yml',
    '.github/workflows/verify-methods-article-claims.yml',
]

# Future/human-dependent outputs are intentionally not critical at this cut.
OPTIONAL = [
    'data/derived/semb03_sample_coverage.csv',
    'data/derived/semb03_sample_token_coverage.csv',
    'data/derived/fragseg_layout_proxy_summary.csv',
    'data/derived/frontmatter_bibliographic_audit.csv',
    'data/derived/semb03_gate_synthetic_development.json',
    'data/derived/semb03_label_heads_synthetic_development.json',
    'data/derived/semb03_readiness_report.json',
    'data/derived/catalog_search_architecture_probe.json',
    'data/expansion/cn46_exact_page_overlap.csv',
    'data/expansion/cn46_no_text_visual_proxies.csv',
    # These become expected only after legitimate human-reference gates.
    'data/validation/semb03_human_reference_consensus.csv',
    'data/validation/semb03_locked_validation_reference.csv',
    'data/derived/semb03_model_lock.json',
    'data/derived/semb03_locked_validation_result.json',
]


def sha(path: str) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def head() -> str | None:
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except Exception:
        return None


def main() -> None:
    files = []
    missing = []

    for name in CRITICAL:
        p = Path(name)
        if not p.exists():
            missing.append(name)
            continue
        files.append({
            'path': name,
            'bytes': p.stat().st_size,
            'sha256': sha(name),
            'required': True,
        })

    optional_present = []
    optional_missing = []
    for name in OPTIONAL:
        p = Path(name)
        if p.exists():
            files.append({
                'path': name,
                'bytes': p.stat().st_size,
                'sha256': sha(name),
                'required': False,
            })
            optional_present.append(name)
        else:
            optional_missing.append(name)

    manifest = {
        'integrity_version': VERSION,
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'git_head': head(),
        'scope': 'CN5 pilot + closed CN4/CN6 expansion + closed Ciencias Naturales Wave 2 + strict-family asset readiness + prehuman SEMB 0.3 infrastructure + methods article 0.2',
        'critical_count': len(CRITICAL),
        'critical_present_count': len(CRITICAL) - len(missing),
        'missing_critical': missing,
        'optional_present_count': len(optional_present),
        'optional_missing': optional_missing,
        'files': files,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write('\n')

    lines = [
        '# Manifiesto de integridad científica LTMD',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'Commit observado: `{manifest["git_head"]}`.',
        '',
        'Alcance: CN5 piloto + expansión CN4/CN6 cerrada + Ola 2 cerrada + readiness de la familia estricta Ciencias Naturales + infraestructura SEMB 0.3 prehumana + artículo metodológico 0.2.',
        '',
        f'Archivos críticos presentes: **{manifest["critical_present_count"]}/{manifest["critical_count"]}**.',
        f'Artefactos opcionales presentes: **{manifest["optional_present_count"]}**.',
        '',
        'Cada entrada conserva tamaño y SHA-256. Una modificación legítima produce una nueva huella auditable; la desaparición de un artefacto crítico hace fallar el workflow.',
        '',
    ]

    if missing:
        lines += ['## Artefactos críticos ausentes', '']
        for name in missing:
            lines.append(f'- `{name}`')
        lines.append('')

    lines += ['## Archivos críticos', '']
    for item in files:
        if item['required']:
            lines.append(f"- `{item['path']}` — {item['bytes']} bytes — `{item['sha256']}`")

    if optional_present:
        lines += ['', '## Artefactos derivados adicionales presentes', '']
        for item in files:
            if not item['required']:
                lines.append(f"- `{item['path']}` — `{item['sha256']}`")

    if optional_missing:
        lines += ['', '## Artefactos opcionales aún ausentes', '']
        for name in optional_missing:
            lines.append(f'- `{name}`')

    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('integrity_version', VERSION)
    print('critical_present', manifest['critical_present_count'], 'of', manifest['critical_count'])
    print('optional_present', manifest['optional_present_count'])
    if missing:
        raise SystemExit('missing critical artifacts: ' + ', '.join(missing))


if __name__ == '__main__':
    main()
