#!/usr/bin/env python3
"""Run the frozen W3 Spanish FRAGSEG engine on canonical W11 pages.

Segmentation mechanics and candidate-rule vocabulary are reused unchanged for
cross-wave technical comparability. W11 remains semantically unvalidated.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
ENGINE_PATH=Path(__file__).with_name('segment_ltmd_u1_w3_spanish_fragments.py')
spec=importlib.util.spec_from_file_location('ltmd_w3_fragseg_engine',ENGINE_PATH)
if spec is None or spec.loader is None:raise SystemExit(f'cannot load frozen W3 FRAGSEG engine from {ENGINE_PATH}')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
engine.STRUCTURE=Path('data/catalog/ltmd_u1_w11_page_structure.csv')
engine.MANIFEST=Path('data/catalog/ltmd_u1_w11_canonical_page_manifest.csv')
engine.VERSION='FRAGSEG_LTMD_U1_W11_0.1'
engine.UA='LibroTextoMexicanoDigital/U1-W11 FRAGSEG 0.1'
if '--output-dir' not in sys.argv:sys.argv.extend(['--output-dir','data/work/ltmd_u1_w11_fragments'])
if __name__=='__main__':engine.main()
