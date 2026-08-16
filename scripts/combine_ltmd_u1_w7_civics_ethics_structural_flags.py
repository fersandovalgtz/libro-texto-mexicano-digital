#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from pathlib import Path
METRICS=Path('data/catalog/ltmd_u1_w7_civics_ethics_ocr_metrics.csv');OUT=Path('data/catalog/ltmd_u1_w7_civics_ethics_structural_keyword_flags.csv');VERSION='LTMD_U1_W7_CIVICS_ETHICS_STRUCTKW_0.1';EXPECTED=25;EXPECTED_PAGES=3261

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w7_civics_ethics_structkw');a=ap.parse_args();metrics=list(csv.DictReader(METRICS.open(encoding='utf-8',newline='')));by={}
 if len(metrics)!=EXPECTED_PAGES:raise SystemExit(f'expected {EXPECTED_PAGES} W7 OCR rows, got {len(metrics)}')
 for r in metrics:by.setdefault(r['viewer_key'],[]).append(r)
 if len(by)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} W7 OCR viewers, got {len(by)}')
 expected=set()
 for k,rr in by.items():
  m=max(int(r['viewer_page']) for r in rr);expected|={(k,r['page_id']) for r in rr if int(r['viewer_page'])<=16 or int(r['viewer_page'])>m-16}
 files=sorted(Path(a.input_dir).rglob('structkw_*.csv'))
 if len(files)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} structural shards, got {len(files)}')
 rows=[];seen=[]
 for p in files:
  rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
  if not rr:raise SystemExit(f'empty structural shard {p}')
  ks={r['viewer_key'] for r in rr};vs={r['scanner_version'] for r in rr}
  if len(ks)!=1 or vs!={VERSION}:raise SystemExit(f'invalid structural shard {p}')
  seen+=list(ks);rows+=rr
 if set(seen)!=set(by) or len(seen)!=EXPECTED:raise SystemExit('W7 structural viewer coverage mismatch')
 keys={(r['viewer_key'],r['page_id']) for r in rows}
 if len(keys)!=len(rows) or keys!=expected:raise SystemExit(f'W7 structural page coverage mismatch missing={len(expected-keys)} extra={len(keys-expected)}')
 if any(r['source_sha256_verified']!='1' for r in rows):raise SystemExit('W7 structural SHA failure')
 rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page'])))
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(f'wrote {len(rows)} W7 structural rows for {EXPECTED} canonical viewers')
if __name__=='__main__':main()
