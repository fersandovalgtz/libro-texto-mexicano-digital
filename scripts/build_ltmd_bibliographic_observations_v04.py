#!/usr/bin/env python3
"""Build LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4.

0.4 preserves the scientific content of 0.3 while replacing its recovery
provenance with LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2, whose target
cohort is derived from the immutable pre-recovery candidate-support audit rather
than from a mutable final candidate table.
"""
from __future__ import annotations

import build_ltmd_bibliographic_observations_v03 as v03

VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4'
RECOVERY_VERSION = 'LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2'


def main() -> None:
    old_version = v03.VERSION
    old_recovery = v03.RECOVERY_VERSION
    try:
        v03.VERSION = VERSION
        v03.RECOVERY_VERSION = RECOVERY_VERSION
        v03.main()
    finally:
        v03.VERSION = old_version
        v03.RECOVERY_VERSION = old_recovery

    text = v03.REPORT.read_text(encoding='utf-8')
    text = text.replace('0.3 conserva las 93 observaciones', '0.4 conserva las 93 observaciones')
    text = text.replace('Las dos recuperaciones 0.3 preservan', 'Las dos recuperaciones 0.4 preservan')
    marker = '**No se habilita fuzzy matching general.**'
    addition = (
        marker + '\n\nLa procedencia de recovery es ahora `LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.2`, '
        'que deriva sus cinco targets desde el audit pre-recovery y elimina la dependencia circular '
        'con la tabla final de candidatos.'
    )
    if marker not in text:
        raise SystemExit('0.4 report postprocessor could not locate fuzzy-matching marker')
    v03.REPORT.write_text(text.replace(marker, addition, 1), encoding='utf-8')


if __name__ == '__main__':
    main()
