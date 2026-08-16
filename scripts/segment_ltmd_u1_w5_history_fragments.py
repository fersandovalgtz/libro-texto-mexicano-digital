#!/usr/bin/env python3
"""Run the frozen W3 FRAGSEG engine on canonical W5 History pages."""
from __future__ import annotations
import sys
from pathlib import Path
import scripts.segment_ltmd_u1_w3_spanish_fragments as engine

engine.STRUCTURE = Path('data/catalog/ltmd_u1_w5_history_page_structure.csv')
engine.MANIFEST = Path('data/catalog/ltmd_u1_w5_history_canonical_page_manifest.csv')
engine.VERSION = 'FRAGSEG_LTMD_U1_W5_HISTORY_0.1'
engine.UA = 'LibroTextoMexicanoDigital/U1-W5 History FRAGSEG 0.1'

if '--output-dir' not in sys.argv:
    sys.argv.extend(['--output-dir', 'data/work/ltmd_u1_w5_history_fragments'])

if __name__ == '__main__':
    engine.main()
