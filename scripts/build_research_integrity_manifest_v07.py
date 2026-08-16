#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.7 for the no-human-reference expansion cut.

0.7 preserves the frozen 0.6 release perimeter and extends it with the W3
Español/Lengua source+OCR+PAGESTRUCT state, the fully closed W4 Ciencias
Sociales technical wave, the explicit no-human-reference operating boundary,
and recovery/orchestration code. W3 FRAGSEG/exact-reuse/completion outputs stay
optional until they are actually materialized and pass their own invariants.
"""
from __future__ import annotations

import build_research_integrity_manifest_v06 as v06

base = v06.base
base.VERSION = 'LTMD_INTEGRITY_0.7'

EXPANSION_CRITICAL = [
    # Epistemic/status boundary.
    'docs/NO_HUMAN_REFERENCE_OPERATING_MODE_0_1.md',
    'docs/LTMD_STATUS_2026-08-16.md',

    # W3 source/topology and closed technical layers.
    'data/catalog/ltmd_u1_w3_scope.csv',
    'data/catalog/ltmd_u1_w3_scope.md',
    'data/catalog/ltmd_u1_w3_viewer_architecture.csv',
    'data/catalog/ltmd_u1_w3_viewer_architecture.md',
    'data/catalog/ltmd_u1_w3_declared_inventory.csv',
    'data/catalog/ltmd_u1_w3_declared_inventory_summary.csv',
    'data/catalog/ltmd_u1_w3_declared_inventory.md',
    'data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv',
    'data/catalog/ltmd_u1_w3_spanish_processing_inventory.md',
    'data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv',
    'data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.md',
    'data/catalog/ltmd_u1_w3_spanish_canonical_gap_manifest.csv',
    'data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv',
    'data/catalog/ltmd_u1_w3_spanish_ocr_summary.csv',
    'data/catalog/ltmd_u1_w3_spanish_ocr.md',
    'data/catalog/ltmd_u1_w3_spanish_page_structure.csv',
    'data/catalog/ltmd_u1_w3_spanish_page_structure_summary.csv',
    'data/catalog/ltmd_u1_w3_spanish_page_structure.md',
    'scripts/build_ltmd_u1_w3_spanish_scope.py',
    'scripts/audit_ltmd_u1_w3_spanish_architecture.py',
    'scripts/build_ltmd_u1_w3_spanish_declared_inventory.py',
    'scripts/build_ltmd_u1_w3_spanish_processing_inventory.py',
    'scripts/build_ltmd_u1_w3_spanish_canonical_page_manifest.py',
    'scripts/ocr_ltmd_u1_w3_spanish_book.py',
    'scripts/combine_ltmd_u1_w3_spanish_ocr.py',
    'scripts/extract_ltmd_u1_w3_spanish_structural_flags_book.py',
    'scripts/combine_ltmd_u1_w3_spanish_structural_flags.py',
    'scripts/classify_ltmd_u1_w3_spanish_page_structure.py',
    'scripts/segment_ltmd_u1_w3_spanish_fragments.py',
    'scripts/combine_ltmd_u1_w3_spanish_fragment_shards.py',
    'scripts/analyze_ltmd_u1_w3_spanish_exact_reuse.py',
    'scripts/build_ltmd_u1_w3_completion_report.py',
    '.github/workflows/build-ltmd-u1-w3-spanish-ocr.yml',
    '.github/workflows/recover-ltmd-u1-w3-spanish-ocr.yml',
    '.github/workflows/build-ltmd-u1-w3-spanish-pagestruct.yml',
    '.github/workflows/recover-ltmd-u1-w3-spanish-pagestruct.yml',
    '.github/workflows/build-ltmd-u1-w3-spanish-fragseg.yml',
    '.github/workflows/recover-ltmd-u1-w3-spanish-fragseg.yml',
    '.github/workflows/analyze-ltmd-u1-w3-spanish-exact-reuse.yml',
    '.github/workflows/recover-ltmd-u1-w3-spanish-exact-reuse.yml',
    '.github/workflows/build-ltmd-u1-w3-completion-report.yml',

    # W4 fully closed technical wave.
    'docs/LTMD_U1_W4_COMPLETION.md',
    'data/catalog/ltmd_u1_w4_scope.csv',
    'data/catalog/ltmd_u1_w4_scope.md',
    'data/catalog/ltmd_u1_w4_viewer_architecture.csv',
    'data/catalog/ltmd_u1_w4_viewer_architecture.md',
    'data/catalog/ltmd_u1_w4_declared_inventory.csv',
    'data/catalog/ltmd_u1_w4_declared_inventory_summary.csv',
    'data/catalog/ltmd_u1_w4_declared_inventory.md',
    'data/catalog/ltmd_u1_w4_social_sciences_asset_manifest.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_asset_summary.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_asset_audit.md',
    'data/catalog/ltmd_u1_w4_social_sciences_asset_relationships.md',
    'data/catalog/ltmd_u1_w4_social_sciences_processing_topology.md',
    'data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_ocr_metrics.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_ocr_summary.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_ocr.md',
    'data/catalog/ltmd_u1_w4_social_sciences_page_structure.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_page_structure_summary.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_page_structure.md',
    'data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest_summary.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_fragment_sequence_gaps.csv',
    'data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest.md',
    'data/catalog/ltmd_u1_w4_social_sciences_exact_reuse.md',
    'scripts/build_ltmd_u1_w4_social_sciences_scope.py',
    'scripts/audit_ltmd_u1_w4_social_sciences_architecture.py',
    'scripts/build_ltmd_u1_w4_social_sciences_declared_inventory.py',
    'scripts/audit_ltmd_u1_w4_social_sciences_assets_book.py',
    'scripts/combine_ltmd_u1_w4_social_sciences_asset_shards.py',
    'scripts/analyze_ltmd_u1_w4_social_sciences_asset_relationships.py',
    'scripts/build_ltmd_u1_w4_social_sciences_processing_topology.py',
    'scripts/ocr_ltmd_u1_w4_social_sciences_book.py',
    'scripts/combine_ltmd_u1_w4_social_sciences_ocr.py',
    'scripts/extract_ltmd_u1_w4_social_sciences_structural_flags_book.py',
    'scripts/combine_ltmd_u1_w4_social_sciences_structural_flags.py',
    'scripts/classify_ltmd_u1_w4_social_sciences_page_structure.py',
    'scripts/segment_ltmd_u1_w4_social_sciences_fragments.py',
    'scripts/combine_ltmd_u1_w4_social_sciences_fragment_shards.py',
    'scripts/analyze_ltmd_u1_w4_social_sciences_exact_reuse.py',
    'scripts/build_ltmd_u1_w4_completion_report.py',
    '.github/workflows/audit-ltmd-u1-w4-social-sciences-architecture.yml',
    '.github/workflows/build-ltmd-u1-w4-social-sciences-declared-inventory.yml',
    '.github/workflows/audit-ltmd-u1-w4-social-sciences-assets.yml',
    '.github/workflows/analyze-ltmd-u1-w4-social-sciences-asset-relationships.yml',
    '.github/workflows/build-ltmd-u1-w4-social-sciences-processing-topology.yml',
    '.github/workflows/build-ltmd-u1-w4-social-sciences-ocr.yml',
    '.github/workflows/recover-ltmd-u1-w4-social-sciences-ocr.yml',
    '.github/workflows/build-ltmd-u1-w4-social-sciences-pagestruct.yml',
    '.github/workflows/recover-ltmd-u1-w4-social-sciences-pagestruct.yml',
    '.github/workflows/build-ltmd-u1-w4-social-sciences-fragseg.yml',
    '.github/workflows/recover-ltmd-u1-w4-social-sciences-fragseg.yml',
    '.github/workflows/analyze-ltmd-u1-w4-social-sciences-exact-reuse.yml',
    '.github/workflows/build-ltmd-u1-w4-completion-report.yml',

    # This wrapper itself becomes part of the frozen integrity perimeter.
    'scripts/build_research_integrity_manifest_v07.py',
]

W3_PENDING_OPTIONAL = [
    'data/catalog/ltmd_u1_w3_spanish_fragment_manifest.csv',
    'data/catalog/ltmd_u1_w3_spanish_fragment_manifest_summary.csv',
    'data/catalog/ltmd_u1_w3_spanish_fragment_sequence_gaps.csv',
    'data/catalog/ltmd_u1_w3_spanish_fragment_manifest.md',
    'data/catalog/ltmd_u1_w3_spanish_exact_content_units.csv',
    'data/catalog/ltmd_u1_w3_spanish_identity_content_projection.csv',
    'data/catalog/ltmd_u1_w3_spanish_exact_viewer_overlap.csv',
    'data/catalog/ltmd_u1_w3_spanish_exact_reuse.md',
    'docs/LTMD_U1_W3_COMPLETION.md',
]

for path in EXPANSION_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)

for path in W3_PENDING_OPTIONAL:
    if path not in base.CRITICAL and path not in base.OPTIONAL:
        base.OPTIONAL.append(path)

if __name__ == '__main__':
    base.main()
