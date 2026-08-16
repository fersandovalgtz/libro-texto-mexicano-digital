#!/usr/bin/env python3
"""Freeze the exact LTMD-U1 W2 Mathematics scope from the live U1 queue."""
from __future__ import annotations
import csv
from pathlib import Path

IN=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_w2_scope.csv')
VERSION='LTMD_U1_W2_SCOPE_0.1'
EXPECTED=64

def main():
    rows=[r for r in csv.DictReader(IN.open(encoding='utf-8')) if r['wave_label']=='U1-W2-matematicas' and r['queue_status']=='queued']
    if len(rows)!=EXPECTED:raise SystemExit(f'W2 scope drift: expected {EXPECTED}, got {len(rows)}')
    if len({r['viewer_key'] for r in rows})!=EXPECTED:raise SystemExit('duplicate W2 viewer_key')
    out=[]
    for r in sorted(rows,key=lambda x:(int(x['catalog_generation']),int(x['grade_code']),x['viewer_key'])):
        out.append({'scope_version':VERSION,'viewer_key':r['viewer_key'],'book_id':f"U1-{r['viewer_key']}",'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'asset_status_at_freeze':r['asset_status'],'execution_action':'architecture_then_direct_ingestion','source_url':r['source_url']})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    print(f'{VERSION}: frozen {len(out)} Mathematics viewers')

if __name__=='__main__':main()
