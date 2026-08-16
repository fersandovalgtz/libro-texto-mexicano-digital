#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.8 with the W7 provenance/routing perimeter.

0.8 preserves the complete 0.7 perimeter and extends it only with the frozen
LTMD-U1 W7 Civics/Ethics source, architecture, declared inventory, asset
provenance, provenance validation, and unresolved-viewer routing evidence.

W7 OCR and semantic derivatives are deliberately excluded: five viewer routes
remain unresolved and the W7 operating rule keeps productive OCR closed until
that source-routing boundary is reconciled with evidence.
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

    # Evidence for the five unresolved viewer routes.
    'data/catalog/ltmd_u1_w7_routing_diagnostics.json',
    'data/catalog/ltmd_u1_w7_routing_diagnostics.md',
    'data/catalog/ltmd_u1_w7_viewer_route_contract.json',
    'data/catalog/ltmd_u1_w7_viewer_route_contract.md',

    # Executable provenance/routing controls.
    'scripts/validate_ltmd_u1_w7_provenance.py',
    'scripts/diagnose_ltmd_u1_w7_routing.py',
    'scripts/extract_ltmd_u1_w7_viewer_route_contract.py',
    '.github/workflows/validate-ltmd-u1-w7-provenance.yml',
    '.github/workflows/diagnose-ltmd-u1-w7-routing.yml',
    '.github/workflows/extract-ltmd-u1-w7-viewer-route-contract.yml',

    # This wrapper is itself frozen by 0.8.
    'scripts/build_research_integrity_manifest_v08.py',
]

for path in W7_PROVENANCE_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)

if __name__ == '__main__':
    base.main()
