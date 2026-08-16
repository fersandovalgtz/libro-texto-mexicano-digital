#!/usr/bin/env python3
"""Run the frozen W3 FRAGSEG engine on canonical W6 Geography/Atlas pages.

The segmentation engine itself is unchanged. W6 canonical source provenance uses
`source_kind` rather than the older `asset_status`; this wrapper builds a
short-lived compatibility view that maps every already-reconciled canonical
source row to `asset_status=source_jpeg`. URLs, SHA-256 values, sizes and page
identities remain exactly those of the W6 canonical manifest, including the two
cryptographically recovered H2008P4GE273 pages.
"""
from __future__ import annotations
import csv
import importlib.util
import sys
import tempfile
from pathlib import Path

ENGINE_PATH=Path(__file__).with_name('segment_ltmd_u1_w3_spanish_fragments.py')
spec=importlib.util.spec_from_file_location('ltmd_w3_fragseg_engine',ENGINE_PATH)
if spec is None or spec.loader is None:raise SystemExit(f'cannot load frozen W3 FRAGSEG engine from {ENGINE_PATH}')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)

SOURCE=Path('data/catalog/ltmd_u1_w6_geography_atlas_canonical_page_manifest.csv')
rows=list(csv.DictReader(SOURCE.open(encoding='utf-8',newline='')))
if len(rows)!=5258 or len({r['viewer_key'] for r in rows})!=37:raise SystemExit('W6 FRAGSEG compatibility manifest cardinality mismatch')
if any(not r.get('source_asset_url') or not r.get('sha256') or not r.get('byte_size') for r in rows):raise SystemExit('W6 FRAGSEG compatibility manifest has incomplete source provenance')

compat=Path(tempfile.mkstemp(prefix='ltmd-w6-fragseg-manifest-',suffix='.csv')[1])
fields=list(rows[0].keys())+(['asset_status'] if 'asset_status' not in rows[0] else [])
with compat.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for r in rows:
        q=dict(r);q['asset_status']='source_jpeg';w.writerow(q)

engine.STRUCTURE=Path('data/catalog/ltmd_u1_w6_geography_atlas_page_structure.csv')
engine.MANIFEST=compat
engine.VERSION='FRAGSEG_LTMD_U1_W6_GEOGRAPHY_ATLAS_0.1'
engine.UA='LibroTextoMexicanoDigital/U1-W6 Geography Atlas FRAGSEG 0.1'
if '--output-dir' not in sys.argv:sys.argv.extend(['--output-dir','data/work/ltmd_u1_w6_geography_atlas_fragments'])

if __name__=='__main__':
    try:engine.main()
    finally:compat.unlink(missing_ok=True)
