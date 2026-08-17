#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.9 with the completed W3 technical perimeter.

0.9 preserves the complete 0.8 perimeter and promotes the nine W3
Español/Lengua FRAGSEG, exact-reuse, and completion outputs that 0.7/0.8 kept
optional until materialization. It also freezes this versioned builder itself.

This promotion is technical only. Exact OCR+FRAGSEG text identity and processing
aliases do not imply bibliographic, curricular, pedagogical, historical, or
semantic equivalence.
"""
from __future__ import annotations

import json
import build_research_integrity_manifest_v08 as v08

base = v08.base
base.VERSION = 'LTMD_INTEGRITY_0.9'

SCOPE = (
    'LTMD v0.9: frozen v0.8 perimeter plus completed W3 Spanish/Language '
    'FRAGSEG, exact-text reuse/document-dependence evidence, and validated '
    'technical closure; W7 source-admissible technical closure and the '
    'nonsemantic W4-W7 technical comparison remain frozen from v0.8'
)
SCOPE_ES = (
    'perímetro v0.8 congelado + W3 Español/Lengua: FRAGSEG completo, '
    'reutilización textual exacta/dependencia documental y cierre técnico '
    'validado; se conservan el cierre técnico de la cohorte W7 admisible y la '
    'comparación técnica no semántica W4↔W7 de v0.8'
)
OLD_SCOPE_ES_ASCII = (
    'CN5 piloto + expansión CN4/CN6 cerrada + Ola 2 cerrada + readiness de la '
    'familia estricta Ciencias Naturales + dependencia/contenido único + '
    'infraestructura SEMB 0.3 prehumana + artículo metodológico 0.2.'
)

W3_CLOSURE_CRITICAL = list(v08.v07.W3_PENDING_OPTIONAL)
W3_CLOSURE_CRITICAL.append('scripts/build_research_integrity_manifest_v09.py')

# Promote the formerly pending W3 products: they are now required, not optional.
for path in v08.v07.W3_PENDING_OPTIONAL:
    if path in base.OPTIONAL:
        base.OPTIONAL.remove(path)

for path in W3_CLOSURE_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)


def main() -> None:
    base.main()

    data = json.loads(base.OUT.read_text(encoding='utf-8'))
    data['scope'] = SCOPE
    base.OUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    report = base.REPORT.read_text(encoding='utf-8')
    old_line = f'Alcance: {OLD_SCOPE_ES_ASCII}'
    new_line = f'Alcance: {SCOPE_ES}.'
    if old_line not in report:
        raise SystemExit(
            'LTMD_INTEGRITY_0.9 scope postprocessor could not locate inherited scope line'
        )
    base.REPORT.write_text(
        report.replace(old_line, new_line, 1),
        encoding='utf-8',
    )


if __name__ == '__main__':
    main()
