#!/usr/bin/env python3
"""Combine structural-keyword shards for the two LTMD-U1 W1 1966 books."""
from __future__ import annotations
import argparse,csv
from pathlib import Path

METRICS=Path('data/catalog/ltmd_u1_w1_1966_ocr_metrics.csv')
OUT=Path('data/catalog/ltmd_u1_w1_1966_structural_keyword_flags.csv')
VERSION='LTMD_U1_W1_1966_STRUCTKW_0.1'
EXPECTED_BOOKS={'U1-H1966P6CI374','U1-H1966P6CI375'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w1_1966_structkw');args=ap.parse_args()
    metrics=list(csv.DictReader(METRICS.open(encoding='utf-8')));bybook={}
    for r in metrics:bybook.setdefault(r['book_id'],[]).append(r)
    if set(bybook)!=EXPECTED_BOOKS:raise SystemExit(f'metrics book mismatch {set(bybook)}')
    expected=set()
    for bid,rr in bybook.items():
        m=max(int(r['viewer_page']) for r in rr);expected|={(bid,r['page_id']) for r in rr if int(r['viewer_page'])<=16 or int(r['viewer_page'])>m-16}
    files=sorted(Path(args.input_dir).rglob('structkw_*.csv'))
    if len(files)!=2:raise SystemExit(f'expected 2 structkw shards, got {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty shard {p}')
        books={r['book_id'] for r in rr};versions={r['scanner_version'] for r in rr}
        if len(books)!=1 or versions!={VERSION}:raise SystemExit(f'invalid shard {p}')
        seen+=list(books);rows+=rr
    if set(seen)!=EXPECTED_BOOKS or len(seen)!=2:raise SystemExit(f'book coverage mismatch {seen}')
    keys={(r['book_id'],r['page_id']) for r in rows}
    if len(keys)!=len(rows):raise SystemExit('duplicate structural page keys')
    if keys!=expected:raise SystemExit(f'structural coverage mismatch missing={len(expected-keys)} extra={len(keys-expected)}')
    if any(str(r['source_sha256_verified'])!='1' for r in rows):raise SystemExit('structural SHA failure')
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'wrote {len(rows)} W1 1966 structural rows; all SHA verified')

if __name__=='__main__':main()
