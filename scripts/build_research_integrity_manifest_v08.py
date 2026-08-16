#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.8 with the W7 source-to-processing perimeter.

0.8 preserves the complete 0.7 perimeter and extends it with LTMD-U1 W7
Civics/Ethics source scope, page-level provenance, viewer routing reconstruction,
2018 route-conformance evidence, source-admissibility decisions, complete-asset
relationship analysis, reconciled processing topology, and executable OCR
controls for the admitted cohort.

The historical scope remains 30 catalog identities. Exactly 25 source-admitted,
non-byte-identical objects are authorized as independent OCR canonicals; five
identities remain withheld because their official source assets are incomplete or
unserved. OCR result artifacts are not frozen here until the complete matrix is
materialized and passes its own coverage/provenance invariants.
"""
from __future__ import annotations

import build_research_integrity_manifest_v07 as v07

base = v07.base
base.VERSION = 'LTMD_INTEGRITY_0.8'

W7_PROVENANCE_CRITICAL = [
    # Frozen W7 source scope and viewer architecture.
    'data/catalog/ltmd_u1_w7_scope.csv',
    'data/catalog/ltmd_u1_w7_scope.md',
    'data/catalog/ltmd_u1_w7_viewer_architecture.csv',
    'data/catalog/ltmd_u1_w7_viewer_architecture.md',

    # Declared source inventory.
    'data/catalog/ltmd_u1_w7_declared_inventory.csv',
    'data/catalog/ltmd_u1_w7_declared_inventory_summary.csv',
    'data/catalog/ltmd_u1_w7_declared_inventory.md',

    # Page-level asset provenance and audit state.
    'data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_asset_summary.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_asset_audit.md',
    'data/validation/ltmd_u1_w7_provenance_validation.md',

    # Evidence that resolves the viewer routing chain.
    'data/catalog/ltmd_u1_w7_routing_diagnostics.json',
    'data/catalog/ltmd_u1_w7_routing_diagnostics.md',
    'data/catalog/ltmd_u1_w7_viewer_route_contract.json',
    'data/catalog/ltmd_u1_w7_viewer_route_contract.md',
    'data/catalog/ltmd_u1_w7_addpage_contract.json',
    'data/catalog/ltmd_u1_w7_addpage_contract.md',
    'data/catalog/ltmd_u1_w7_dynamic_dependencies.json',
    'data/catalog/ltmd_u1_w7_dynamic_dependencies.md',
    'data/catalog/ltmd_u1_w7_image_route_contract.json',
    'data/catalog/ltmd_u1_w7_image_route_contract.md',
    'data/catalog/ltmd_u1_w7_2018_route_conformance.csv',
    'data/catalog/ltmd_u1_w7_2018_route_conformance.md',

    # Explicit source gate and exact admitted-cohort relationships.
    'data/catalog/ltmd_u1_w7_source_admissibility.csv',
    'data/catalog/ltmd_u1_w7_source_admissibility.md',
    'data/catalog/ltmd_u1_w7_admitted_asset_fingerprints.csv',
    'data/catalog/ltmd_u1_w7_exact_asset_relationships.csv',
    'data/catalog/ltmd_u1_w7_admitted_asset_relationships.md',

    # Reconciled 30-identity / 25-canonical processing topology.
    'data/catalog/ltmd_u1_w7_processing_inventory.csv',
    'data/catalog/ltmd_u1_w7_canonical_page_manifest.csv',
    'data/catalog/ltmd_u1_w7_processing_topology.md',

    # Executable provenance/routing controls.
    'scripts/validate_ltmd_u1_w7_provenance.py',
    'scripts/diagnose_ltmd_u1_w7_routing.py',
    'scripts/extract_ltmd_u1_w7_viewer_route_contract.py',
    'scripts/inspect_ltmd_u1_w7_addpage_contract.py',
    'scripts/inspect_ltmd_u1_w7_dynamic_dependencies.py',
    'scripts/extract_ltmd_u1_w7_image_route_contract.py',
    'scripts/probe_ltmd_u1_w7_2018_route_conformance.py',
    'scripts/build_ltmd_u1_w7_source_admissibility.py',
    'scripts/analyze_ltmd_u1_w7_admitted_asset_relationships.py',
    'scripts/build_ltmd_u1_w7_processing_topology.py',
    'scripts/ocr_ltmd_u1_w7_civics_ethics_book.py',
    'scripts/combine_ltmd_u1_w7_civics_ethics_ocr.py',
    '.github/workflows/validate-ltmd-u1-w7-provenance.yml',
    '.github/workflows/diagnose-ltmd-u1-w7-routing.yml',
    '.github/workflows/extract-ltmd-u1-w7-viewer-route-contract.yml',
    '.github/workflows/inspect-ltmd-u1-w7-addpage-contract.yml',
    '.github/workflows/inspect-ltmd-u1-w7-dynamic-dependencies.yml',
    '.github/workflows/extract-ltmd-u1-w7-image-route-contract.yml',
    '.github/workflows/probe-ltmd-u1-w7-2018-route-conformance.yml',
    '.github/workflows/build-ltmd-u1-w7-source-admissibility.yml',
    '.github/workflows/analyze-ltmd-u1-w7-admitted-asset-relationships.yml',
    '.github/workflows/build-ltmd-u1-w7-processing-topology.yml',
    '.github/workflows/build-ltmd-u1-w7-civics-ethics-ocr.yml',

    # This wrapper is itself frozen by 0.8.
    'scripts/build_research_integrity_manifest_v08.py',
]

for path in W7_PROVENANCE_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)

if __name__ == '__main__':
    base.main()
