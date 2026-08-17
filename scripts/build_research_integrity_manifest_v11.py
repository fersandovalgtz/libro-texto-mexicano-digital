#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.11.

0.11 is additive over the complete 0.10 perimeter and freezes the publication-
safe bibliographic instance-candidate chain:

candidate-support 0.1
    -> narrow reprint OCR recovery 0.2
    -> bibliographic observations 0.4
    -> bibliographic instance candidates 0.3

It also freezes the policy that defines the older instance-resolution experiment
as superseded for interpretation/publication. Historical experimental files are
left in the repository but are intentionally NOT promoted to the critical
perimeter unless required by the current causal chain.
"""
from __future__ import annotations

import json
import build_research_integrity_manifest_v10 as v10

base = v10.base
base.VERSION = 'LTMD_INTEGRITY_0.11'

SCOPE = (
    'LTMD v0.11: frozen v0.10 perimeter plus a causally reproducible '
    'bibliographic instance-candidate chain (support audit -> narrow OCR '
    'recovery 0.2 -> observations 0.4 -> candidates 0.3), publication-safe '
    'candidate evidence tiers, and explicit supersession of the older '
    'instance-resolution interpretation'
)
SCOPE_ES = (
    'perímetro v0.10 congelado + cadena causal reproducible de candidatos de '
    'instancia bibliográfica (audit de soporte → recovery OCR estrecho 0.2 → '
    'observaciones 0.4 → candidatos 0.3), tiers de evidencia seguros para '
    'publicación y supersesión explícita de la interpretación antigua de '
    'instance-resolution'
)

V11_CRITICAL = [
    # Reprint OCR recovery: current causally reproducible version only.
    'data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.csv',
    'data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md',
    'scripts/recover_ltmd_u1_w7_reprint_ocr_confusions_v02.py',
    '.github/workflows/recover-ltmd-u1-w7-reprint-ocr-confusions.yml',

    # Observation producer chain required to materialize current 0.4 outputs.
    'scripts/build_ltmd_bibliographic_observations_v03.py',
    'scripts/build_ltmd_bibliographic_observations_v04.py',

    # Publication-safe bibliographic instance candidates.
    'data/catalog/ltmd_bibliographic_instance_candidates.csv',
    'data/catalog/ltmd_bibliographic_instance_candidates.md',
    'scripts/build_ltmd_bibliographic_instance_candidates_v02.py',
    'scripts/build_ltmd_bibliographic_instance_candidates_v03.py',
    '.github/workflows/build-ltmd-bibliographic-instance-candidates.yml',
    'docs/LTMD_BIBLIOGRAPHIC_INSTANCE_POLICY_0_1.md',

    # Versioned integrity builder itself.
    'scripts/build_research_integrity_manifest_v11.py',
]

for path in V11_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)


def main() -> None:
    # v10.main() materializes the complete inherited perimeter and its report;
    # VERSION already points to 0.11 and V11_CRITICAL has already been appended.
    v10.main()

    data = json.loads(base.OUT.read_text(encoding='utf-8'))
    data['scope'] = SCOPE
    base.OUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    report = base.REPORT.read_text(encoding='utf-8')
    inherited_line = f'Alcance: {v10.SCOPE_ES}.'
    new_line = f'Alcance: {SCOPE_ES}.'
    if inherited_line not in report:
        raise SystemExit(
            'LTMD_INTEGRITY_0.11 scope postprocessor could not locate v0.10 scope line'
        )
    base.REPORT.write_text(
        report.replace(inherited_line, new_line, 1),
        encoding='utf-8',
    )


if __name__ == '__main__':
    main()
