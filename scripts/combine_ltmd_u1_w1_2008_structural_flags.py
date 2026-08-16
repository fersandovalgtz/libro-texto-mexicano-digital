#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from pathlib import Path
MET=Path('data/catalog/ltmd_u1_w1_2008_ocr_metrics.csv');OUT=Path('data/catalog/ltmd_u1_w1_2008_structural_keyword_flags.csv');VERSION='LTMD_U1_W1_2008_STRUCTKW_0.1';BOOKS={'LTMD-CN3-G2008','LTMD-CN4-G2008'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w1_2008_structkw');a=ap.parse_args();met=list(csv.DictReader(MET.open(encoding='utf-8')));by={}
 for r in met:by.setdefault(r['book_id'],[]).append(r)
 expected=set()
 for b,rr in by.items():
  m=max(int(r['viewer_page']) for r in rr);expected|={(b,r['page_id']) for r in rr if int(r['viewer_page'])<=16 or int(r['viewer_page'])>m-16}
 files=sorted(Path(a.input_dir).glob('structkw_*.csv'));rows=[]
 if len(files)!=2:raise SystemExit(f'expected 2 shards got {len(files)}')
 for p in files:rows+=list(csv.DictReader(p.open(encoding='utf-8')))
 keys={(r['book_id'],r['page_id']) for r in rows}
 if {r['book_id'] for r in rows}!=BOOKS or keys!=expected or len(keys)!=len(rows):raise SystemExit('structural coverage mismatch')
 if any(r['scanner_version']!=VERSION or r['source_sha256_verified']!='1' for r in rows):raise SystemExit('structural version/SHA failure')
 rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])));OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(f'wrote {len(rows)} W1 2008 structural rows')
if __name__=='__main__':main()
