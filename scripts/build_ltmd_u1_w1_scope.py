#!/usr/bin/env python3
"""Freeze the exact LTMD-U1 W1 execution scope from the live U1 queue."""
from __future__ import annotations
import csv
from pathlib import Path

IN=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_w1_scope.csv')
VERSION='LTMD_U1_W1_SCOPE_0.1'
EXPECTED={
'H1966P6CI374':('U1-H1966P6CI374','new_direct_ingestion'),
'H1966P6CI375':('U1-H1966P6CI375','new_direct_ingestion'),
'H2008P3CI263':('U1-H2008P3CI263','recover_or_document_partial'),
'H2008P4CI268':('U1-H2008P4CI268','recover_or_document_partial'),
}

def main():
    rows=[r for r in csv.DictReader(IN.open(encoding='utf-8')) if r['wave_label']=='U1-W1-ciencias_naturales' and r['queue_status']=='queued']
    got={r['viewer_key'] for r in rows}
    if got!=set(EXPECTED):
        raise SystemExit(f'W1 scope drift: got={sorted(got)} expected={sorted(EXPECTED)}')
    out=[]
    for r in sorted(rows,key=lambda x:x['viewer_key']):
        book_id,action=EXPECTED[r['viewer_key']]
        out.append({
            'scope_version':VERSION,
            'viewer_key':r['viewer_key'],
            'book_id':book_id,
            'catalog_generation':r['catalog_generation'],
            'grade_code':r['grade_code'],
            'title_core':r['title_core'],
            'asset_status_at_freeze':r['asset_status'],
            'execution_action':action,
            'source_url':r['source_url'],
        })
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    print(f'{VERSION}: frozen viewers={len(out)} keys={sorted(got)}')

if __name__=='__main__':main()
