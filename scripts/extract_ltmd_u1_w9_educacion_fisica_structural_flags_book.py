#!/usr/bin/env python3
"""Run the frozen W8 structural-zone scanner on canonical LTMD-U1 W9 Educación Física pages.

The keyword vocabulary, source verification and bounded first/last-page scan are
reused unchanged for cross-domain technical comparability. Only W9 paths,
provenance labels and scope invariants differ.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

ENGINE_PATH=Path(__file__).with_name('extract_ltmd_u1_w8_artes_structural_flags_book.py')
spec=importlib.util.spec_from_file_location('ltmd_w8_structural_flags_engine',ENGINE_PATH)
if spec is None or spec.loader is None:
    raise SystemExit(f'cannot load frozen structural-flags engine from {ENGINE_PATH}')
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

engine.METRICS=Path('data/catalog/ltmd_u1_w9_educacion_fisica_ocr_metrics.csv')
engine.MAN=Path('data/catalog/ltmd_u1_w9_canonical_page_manifest.csv')
engine.VERSION='LTMD_U1_W9_EDUCACION_FISICA_STRUCTKW_0.1'
engine.UA='LibroTextoMexicanoDigital/U1-W9 Educacion Fisica structural flags 0.1'
engine.EXPECTED_CANONICAL=4
engine.EXPECTED_PAGES=448

if '--output-dir' not in sys.argv:
    sys.argv.extend(['--output-dir','data/work/ltmd_u1_w9_educacion_fisica_structkw'])

if __name__=='__main__':
    engine.main()
