#!/usr/bin/env python3
"""Build LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.3.

0.3 preserves the candidate logic and scientific outcome of 0.2 while moving
the dependency to LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4, whose OCR-recovery
provenance is causally reproducible from the pre-recovery support audit.
"""
from __future__ import annotations

import build_ltmd_bibliographic_instance_candidates_v02 as v02

VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.3'
OBS_VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4'


def main() -> None:
    old_version = v02.VERSION
    old_obs_version = v02.OBS_VERSION
    try:
        v02.VERSION = VERSION
        v02.OBS_VERSION = OBS_VERSION
        v02.main()
    finally:
        v02.VERSION = old_version
        v02.OBS_VERSION = old_obs_version

    text = v02.REPORT.read_text(encoding='utf-8')
    text = text.replace(
        '0.2 se reconstruye directamente desde `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.3`;',
        '0.3 se reconstruye directamente desde `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4`;',
    )
    marker = 'Las dos recuperaciones OCR estrechas incorporadas en Observaciones 0.3 elevan la cobertura de **9 a 11** candidatos sin cambiar la regla temporal.'
    replacement = (
        'Las dos recuperaciones OCR estrechas, ahora procedentes de la cadena causal '
        '`candidate-support 0.1 → recovery 0.2 → observations 0.4`, elevan la cobertura '
        'de **9 a 11** candidatos sin cambiar la regla temporal.'
    )
    if marker not in text:
        raise SystemExit('0.3 candidate report postprocessor could not locate recovery sentence')
    v02.REPORT.write_text(text.replace(marker, replacement, 1), encoding='utf-8')


if __name__ == '__main__':
    main()
