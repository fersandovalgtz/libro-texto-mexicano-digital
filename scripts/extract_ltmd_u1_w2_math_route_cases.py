#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

SRC=Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w2_math_route_cases.csv')
IDS={
'H2008P4MA276',
'H2018P3DMA','H2018P4DMA','H2018P5DMA','H2018P6DMA',
'H2019P3DMA','H2019P4DMA','H2019P5DMA','H2019P6DMA',
}

def main():
    with SRC.open(encoding='utf-8',newline='') as f:
        r=csv.DictReader(f); rows=[x for x in r if x.get('viewer_key') in IDS or x.get('book_id') in IDS]
        fields=r.fieldnames or []
    if not rows: raise SystemExit('no selected route cases found')
    found={x.get('viewer_key') or x.get('book_id') for x in rows}
    missing=IDS-found
    if missing: raise SystemExit(f'missing route cases: {sorted(missing)}')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f'wrote {len(rows)} rows across {len(found)} selected viewers; columns={fields}')
if __name__=='__main__': main()
