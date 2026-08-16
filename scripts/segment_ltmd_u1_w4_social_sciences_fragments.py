#!/usr/bin/env python3
"""Run the frozen W3 Spanish FRAGSEG engine on canonical W4 Social Sciences pages.

The segmentation mechanics and candidate-rule vocabulary are deliberately reused
unchanged for cross-domain technical comparability. Only input/output paths,
provenance label and version change. Candidate types remain unvalidated technical
signals under the no-human-reference operating mode.
"""
from __future__ import annotations
import sys
from pathlib import Path
import scripts.segment_ltmd_u1_w3_spanish_fragments as engine

engine.STRUCTURE = Path('data/catalog/ltmd_u1_w4_social_sciences_page_structure.csv')
engine.MANIFEST = Path('data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv')
engine.VERSION = 'FRAGSEG_LTMD_U1_W4_SOCIAL_SCIENCES_0.1'
engine.UA = 'LibroTextoMexicanoDigital/U1-W4 Social Sciences FRAGSEG 0.1'

if '--output-dir' not in sys.argv:
    sys.argv.extend(['--output-dir', 'data/work/ltmd_u1_w4_social_sciences_fragments'])

if __name__ == '__main__':
    engine.main()
