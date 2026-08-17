#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.8 with the completed W7 admitted-cohort perimeter.

0.8 preserves the complete 0.7 perimeter and extends it with LTMD-U1 W7
Civics/Ethics source scope, page-level provenance, resolved routing, 2018
source-conformance evidence, source-admissibility decisions, reconciled
processing topology, completed OCR/PAGESTRUCT/FRAGSEG/exact-reuse evidence, and
the validated technical-closure report for the source-admitted cohort.
"""
from __future__ import annotations

import json
import build_research_integrity_manifest_v07 as v07

base = v07.base
base.VERSION = 'LTMD_INTEGRITY_0.8'

SCOPE = ('LTMD v0.8: frozen v0.7 perimeter plus W7 Civics/Ethics historical scope, '
         'page-level source provenance, resolved viewer routing, 2018 source-conformance '
         'evidence, 30-identity/25-canonical source-admissible processing topology, '
         'completed SHA-verified OCR, PAGESTRUCT, FRAGSEG, exact-text reuse, and admitted-cohort technical closure')
SCOPE_ES = ('perímetro v0.7 congelado + W7 Cívica/Ética: alcance histórico, provenance de página, '
            'routing del visor resuelto, evidencia de conformidad de fuente 2018, topología de '
            '30 identidades/25 canónicos admisibles, OCR/PAGESTRUCT/FRAGSEG/reuso exacto completos '
            'y cierre técnico validado de la cohorte admisible')
OLD_SCOPE_ES_ASCII = ('CN5 piloto + expansión CN4/CN6 cerrada + Ola 2 cerrada + readiness de la familia '
                      'estricta Ciencias Naturales + dependencia/contenido único + infraestructura SEMB 0.3 '
                      'prehumana + artículo metodológico 0.2.')

W7_PROVENANCE_CRITICAL = [
    'data/catalog/ltmd_u1_w7_scope.csv',
    'data/catalog/ltmd_u1_w7_scope.md',
    'data/catalog/ltmd_u1_w7_viewer_architecture.csv',
    'data/catalog/ltmd_u1_w7_viewer_architecture.md',
    'data/catalog/ltmd_u1_w7_declared_inventory.csv',
    'data/catalog/ltmd_u1_w7_declared_inventory_summary.csv',
    'data/catalog/ltmd_u1_w7_declared_inventory.md',
    'data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_asset_summary.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_asset_audit.md',
    'data/validation/ltmd_u1_w7_provenance_validation.md',
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
    'data/catalog/ltmd_u1_w7_source_admissibility.csv',
    'data/catalog/ltmd_u1_w7_source_admissibility.md',
    'data/catalog/ltmd_u1_w7_admitted_asset_fingerprints.csv',
    'data/catalog/ltmd_u1_w7_exact_asset_relationships.csv',
    'data/catalog/ltmd_u1_w7_admitted_asset_relationships.md',
    'data/catalog/ltmd_u1_w7_processing_inventory.csv',
    'data/catalog/ltmd_u1_w7_canonical_page_manifest.csv',
    'data/catalog/ltmd_u1_w7_processing_topology.md',
    'data/catalog/ltmd_u1_w7_civics_ethics_ocr_metrics.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_ocr_summary.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_ocr.md',
    'data/catalog/ltmd_u1_w7_civics_ethics_structural_keyword_flags.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_page_structure.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_page_structure_summary.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_page_structure.md',
    'data/catalog/ltmd_u1_w7_civics_ethics_fragment_manifest.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_fragment_manifest_summary.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_fragment_sequence_gaps.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_fragment_manifest.md',
    'data/catalog/ltmd_u1_w7_civics_ethics_exact_content_units.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_exact_viewer_overlap.csv',
    'data/catalog/ltmd_u1_w7_civics_ethics_exact_reuse.md',
    'docs/LTMD_U1_W7_COMPLETION.md',
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
    'scripts/extract_ltmd_u1_w7_civics_ethics_structural_flags_book.py',
    'scripts/combine_ltmd_u1_w7_civics_ethics_structural_flags.py',
    'scripts/classify_ltmd_u1_w7_civics_ethics_page_structure.py',
    'scripts/segment_ltmd_u1_w7_civics_ethics_fragments.py',
    'scripts/combine_ltmd_u1_w7_civics_ethics_fragment_shards.py',
    'scripts/analyze_ltmd_u1_w7_civics_ethics_exact_reuse.py',
    'scripts/build_ltmd_u1_w7_completion_report.py',
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
    '.github/workflows/build-ltmd-u1-w7-civics-ethics-pagestruct.yml',
    '.github/workflows/build-ltmd-u1-w7-civics-ethics-fragseg.yml',
    '.github/workflows/analyze-ltmd-u1-w7-civics-ethics-exact-reuse.yml',
    '.github/workflows/build-ltmd-u1-w7-completion-report.yml',
    'scripts/build_research_integrity_manifest_v08.py',
]

for path in W7_PROVENANCE_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)


def main():
    base.main()
    data = json.loads(base.OUT.read_text(encoding='utf-8'))
    data['scope'] = SCOPE
    base.OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = base.REPORT.read_text(encoding='utf-8')
    old_line = f'Alcance: {OLD_SCOPE_ES_ASCII}'
    new_line = f'Alcance: {SCOPE_ES}.'
    if old_line not in report:
        raise SystemExit('LTMD_INTEGRITY_0.8 scope postprocessor could not locate inherited scope line')
    base.REPORT.write_text(report.replace(old_line, new_line, 1), encoding='utf-8')


if __name__ == '__main__':
    main()
