#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from pathlib import Path
METRICS=Path('data/catalog/ltmd_u1_w2_math_ocr_metrics.csv')
OUT=Path('data/catalog/ltmd_u1_w2_math_structural_keyword_flags.csv')
VERSION='LTMD_U1_W2_MATH_STRUCTKW_0.2'
EXPECTED=57

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w2_math_structkw');a=ap.parse_args()
    metrics=list(csv.DictReader(METRICS.open(encoding='utf-8')));by={}
    for r in metrics: by.setdefault(r['viewer_key'],[]).append(r)
    if len(by)!=EXPECTED: raise SystemExit(f'expected {EXPECTED} canonical OCR viewers, found {len(by)}')
    expected=set()
    for key,rr in by.items():
        m=max(int(r['viewer_page']) for r in rr)
        expected|={(key,r['page_id']) for r in rr if int(r['viewer_page'])<=16 or int(r['viewer_page'])>m-16}
    files=sorted(Path(a.input_dir).rglob('structkw_*.csv'))
    if len(files)!=EXPECTED: raise SystemExit(f'expected {EXPECTED} structkw shards, got {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr: raise SystemExit(f'empty shard {p}')
        keys={r['viewer_key'] for r in rr};versions={r['scanner_version'] for r in rr}
        if len(keys)!=1 or versions!={VERSION}: raise SystemExit(f'invalid shard {p}')
        seen+=list(keys);rows+=rr
    if set(seen)!=set(by) or len(seen)!=EXPECTED: raise SystemExit('structural canonical viewer coverage mismatch')
    keys={(r['viewer_key'],r['page_id']) for r in rows}
    if len(keys)!=len(rows): raise SystemExit('duplicate structural page keys')
    if keys!=expected: raise SystemExit(f'structural coverage mismatch missing={len(expected-keys)} extra={len(keys-expected)}')
    if any(r['source_sha256_verified']!='1' for r in rows): raise SystemExit('structural SHA failure')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'wrote {len(rows)} W2 Mathematics structural rows for {EXPECTED} canonical viewers; all effective SHA verified')
if __name__=='__main__':main()
