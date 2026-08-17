#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.12.

0.12 is additive over 0.11 and freezes two W7 bibliographic-readiness products:
* the 30-identity source-vs-chronology coverage matrix;
* the bounded pages-13..20 probe for the 12 source-admitted objects that lack a
  strong school-cycle observation in Observations 0.4.

The bounded probe is scientific evidence whether positive or negative. Its
criticality does not imply that a cycle must be found; it freezes the target
derivation, source verification, OCR window and observed result.
"""
from __future__ import annotations

import json
import build_research_integrity_manifest_v11 as v11

base = v11.base
base.VERSION = 'LTMD_INTEGRITY_0.12'

SCOPE = (
    'LTMD v0.12: frozen v0.11 perimeter plus the 30-identity W7 '
    'source-versus-bibliographic-readiness matrix and a bounded, source-verified '
    'logical-pages-13..20 school-cycle probe for the 12 admitted W7 objects '
    'without a strong cycle observation'
)
SCOPE_ES = (
    'perímetro v0.11 congelado + matriz W7 de 30 identidades que separa '
    'readiness de fuente y cronología bibliográfica + probe acotado, verificado '
    'contra fuente, de páginas lógicas 13–20 para los 12 objetos admitidos sin '
    'observación fuerte de ciclo escolar'
)

V12_CRITICAL = [
    # W7 30-identity readiness matrix.
    'data/derived/ltmd_u1_w7_bibliographic_coverage.csv',
    'docs/LTMD_U1_W7_BIBLIOGRAPHIC_COVERAGE.md',
    'scripts/build_ltmd_u1_w7_bibliographic_coverage_matrix.py',
    '.github/workflows/build-ltmd-u1-w7-bibliographic-coverage.yml',

    # Bounded follow-up probe for the 12 no-cycle admitted objects.
    'data/catalog/ltmd_u1_w7_missing_cycle_window_13_20.csv',
    'data/catalog/ltmd_u1_w7_missing_cycle_window_13_20.md',
    'scripts/probe_ltmd_u1_w7_missing_cycle_window_13_20.py',
    '.github/workflows/probe-ltmd-u1-w7-missing-cycle-window-13-20.yml',

    # Versioned integrity builder itself.
    'scripts/build_research_integrity_manifest_v12.py',
]

for path in V12_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)


def main() -> None:
    v11.main()

    data = json.loads(base.OUT.read_text(encoding='utf-8'))
    data['scope'] = SCOPE
    base.OUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    report = base.REPORT.read_text(encoding='utf-8')
    inherited_line = f'Alcance: {v11.SCOPE_ES}.'
    new_line = f'Alcance: {SCOPE_ES}.'
    if inherited_line not in report:
        raise SystemExit(
            'LTMD_INTEGRITY_0.12 scope postprocessor could not locate v0.11 scope line'
        )
    base.REPORT.write_text(
        report.replace(inherited_line, new_line, 1),
        encoding='utf-8',
    )


if __name__ == '__main__':
    main()
