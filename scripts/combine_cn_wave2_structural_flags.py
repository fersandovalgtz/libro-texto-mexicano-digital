#!/usr/bin/env python3
"""Combine per-book structural-keyword shards for CN Wave 2."""
from __future__ import annotations
import argparse,csv
from pathlib import Path

QUEUE=Path('data/expansion/cn_wave2_ingestion_queue.csv')
METRICS=Path('data/expansion/cn_wave2_ocr_page_metrics.csv')
OUT=Path('data/expansion/cn_wave2_structural_keyword_flags.csv')
VERSION='CN_WAVE2_STRUCTKW_0.1'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/cn_wave2_structkw');args=ap.parse_args()
    queue=list(csv.DictReader(QUEUE.open(encoding='utf-8')));books={r['book_id'] for r in queue}
    metrics=list(csv.DictReader(METRICS.open(encoding='utf-8')));bybook={}
    for r in metrics:bybook.setdefault(r['book_id'],[]).append(r)
    expected=set()
    for bid,rr in bybook.items():
        m=max(int(r['viewer_page']) for r in rr)
        expected|={(bid,r['page_id']) for r in rr if int(r['viewer_page'])<=16 or int(r['viewer_page'])>m-16}
    files=sorted(Path(args.input_dir).rglob('structkw_*.csv'))
    if len(files)!=19:raise SystemExit(f'expected 19 structkw shards, got {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty shard {p}')
        b={r['book_id'] for r in rr};v={r['scanner_version'] for r in rr}
        if len(b)!=1 or len(v)!=1 or next(iter(v))!=VERSION:raise SystemExit(f'invalid shard {p}')
        seen+=list(b);rows+=rr
    if set(seen)!=books or len(seen)!=19:raise SystemExit(f'book coverage mismatch {seen}')
    keys={(r['book_id'],r['page_id']) for r in rows}
    if len(keys)!=len(rows):raise SystemExit('duplicate structural page keys')
    if keys!=expected:raise SystemExit(f'structural coverage mismatch missing={len(expected-keys)} extra={len(keys-expected)}')
    if any(str(r['source_sha256_verified'])!='1' for r in rows):raise SystemExit('structural SHA failure')
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f'wrote {len(rows)} Wave2 structural rows; all SHA verified')

if __name__=='__main__':main()
