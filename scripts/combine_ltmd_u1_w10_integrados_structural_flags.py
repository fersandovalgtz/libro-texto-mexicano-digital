#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from pathlib import Path
METRICS=Path('data/catalog/ltmd_u1_w10_integrados_ocr_metrics.csv');OUT=Path('data/catalog/ltmd_u1_w10_integrados_structural_keyword_flags.csv');VERSION='LTMD_U1_W10_INTEGRADOS_STRUCTKW_0.1'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w10_integrados_structkw');a=ap.parse_args();metrics=list(csv.DictReader(METRICS.open(encoding='utf-8',newline='')));by={}
    if not metrics or len({r['page_id'] for r in metrics})!=len(metrics):raise SystemExit('invalid W10 OCR metrics')
    for r in metrics:by.setdefault(r['viewer_key'],[]).append(r)
    expected=set()
    for k,rr in by.items():
        m=max(int(r['viewer_page']) for r in rr);expected|={(k,r['page_id']) for r in rr if int(r['viewer_page'])<=16 or int(r['viewer_page'])>m-16}
    files=sorted(Path(a.input_dir).rglob('structkw_*.csv'))
    if len(files)!=len(by):raise SystemExit(f'expected {len(by)} structural shards, got {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
        if not rr:raise SystemExit(f'empty structural shard {p}')
        ks={r['viewer_key'] for r in rr};vs={r['scanner_version'] for r in rr}
        if len(ks)!=1 or vs!={VERSION}:raise SystemExit(f'invalid W10 structural shard {p}')
        seen+=list(ks);rows+=rr
    if set(seen)!=set(by) or len(seen)!=len(by) or len(seen)!=len(set(seen)):raise SystemExit('W10 structural viewer coverage mismatch')
    keys={(r['viewer_key'],r['page_id']) for r in rows}
    if len(keys)!=len(rows) or keys!=expected:raise SystemExit(f'W10 structural page coverage mismatch missing={len(expected-keys)} extra={len(keys-expected)}')
    if any(r['source_sha256_verified']!='1' for r in rows):raise SystemExit('W10 structural SHA failure')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'wrote {len(rows)} W10 structural rows for {len(by)} canonical viewers')
if __name__=='__main__':main()
