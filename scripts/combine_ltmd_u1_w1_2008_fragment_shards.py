#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path
STRUCT=Path('data/catalog/ltmd_u1_w1_2008_page_structure.csv');OUT=Path('data/catalog/ltmd_u1_w1_2008_fragment_manifest.csv');SUMMARY=Path('data/catalog/ltmd_u1_w1_2008_fragment_manifest_summary.csv');GAPS=Path('data/catalog/ltmd_u1_w1_2008_fragment_sequence_gaps.csv');REPORT=Path('data/catalog/ltmd_u1_w1_2008_fragment_manifest.md');VERSION='FRAGSEG_LTMD_U1_W1_2008_0.1';ELIGIBLE={'textual','mixed_text_image'};BOOKS={'LTMD-CN3-G2008','LTMD-CN4-G2008'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w1_2008_fragments');a=ap.parse_args();structure=list(csv.DictReader(STRUCT.open(encoding='utf-8')));eligible={(r['book_id'],r['page_id']) for r in structure if r['primary_structure'] in ELIGIBLE};files=sorted(p for p in Path(a.input_dir).glob('fragment_*.csv') if not p.name.endswith('_failures.csv'));fails=sorted(Path(a.input_dir).glob('fragment_*_failures.csv'))
 if len(files)!=2 or len(fails)!=2:raise SystemExit(f'shard count mismatch {len(files)}/{len(fails)}')
 rows=[];empty=[]
 for p in files:rows+=list(csv.DictReader(p.open(encoding='utf-8')))
 for p in fails:
  for r in csv.DictReader(p.open(encoding='utf-8')):
   if r['status']!='ok':raise SystemExit(f'fatal persisted {r}')
   empty.append((r['book_id'],r['page_id']))
 if {r['book_id'] for r in rows}!=BOOKS or any(r['segmenter_version']!=VERSION for r in rows):raise SystemExit('book/version mismatch')
 ids=[r['fragment_id'] for r in rows]
 if len(ids)!=len(set(ids)):raise SystemExit('duplicate IDs')
 coverage={(r['book_id'],r['page_id']) for r in rows}|set(empty)
 if coverage!=eligible:raise SystemExit(f'eligible coverage mismatch missing={len(eligible-coverage)} extra={len(coverage-eligible)}')
 by=defaultdict(list)
 for r in rows:by[(r['book_id'],r['page_id'])].append(int(r['fragment_sequence']))
 gaps=[]
 for (b,p),vals in sorted(by.items()):
  sv=sorted(vals)
  if any(v<=0 for v in sv) or len(sv)!=len(set(sv)):raise SystemExit(f'invalid sequence {b} {p}')
  miss=[x for x in range(1,max(sv)+1) if x not in set(sv)] if sv else []
  if miss:gaps.append({'book_id':b,'page_id':p,'observed_fragment_count':len(sv),'max_sequence':max(sv),'missing_sequence_slots':' '.join(map(str,miss)),'missing_slot_count':len(miss)})
 rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page']),int(r['fragment_sequence'])));OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 if gaps:
  with GAPS.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaps[0]));w.writeheader();w.writerows(gaps)
 else:GAPS.write_text('book_id,page_id,observed_fragment_count,max_sequence,missing_sequence_slots,missing_slot_count\n',encoding='utf-8')
 types=sorted({r['candidate_type'] for r in rows});counts=defaultdict(Counter);pages=defaultdict(set)
 for r in rows:counts[r['book_id']][r['candidate_type']]+=1;counts['ALL'][r['candidate_type']]+=1;pages[r['book_id']].add(r['page_id']);pages['ALL'].add(r['page_id'])
 sums=[]
 for b in sorted(BOOKS)+['ALL']:
  c=counts[b];z={'segmenter_version':VERSION,'book_id':b,'fragment_count':sum(c.values()),'segmented_page_count':len(pages[b])};z.update({t:c[t] for t in types});sums.append(z)
 with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(sums[0]));w.writeheader();w.writerows(sums)
 allr=sums[-1];slots=sum(int(r['missing_slot_count']) for r in gaps);lines=['# FRAGSEG — LTMD-U1 W1 2008','',f'Versión: `{VERSION}`.','',f'- Páginas elegibles: **{len(eligible)}**.\n- Páginas con fragmentos: **{allr["segmented_page_count"]}**.\n- Páginas elegibles sin fragmentos: **{len(empty)}**.\n- Fragmentos: **{allr["fragment_count"]}**.\n- IDs únicos: **{len(set(ids))}**.\n- Páginas con huecos de secuencia: **{len(gaps)}**; slots omitidos: **{slots}**.','', 'El texto completo no se persiste; los tres activos recuperados conservan procedencia en el manifiesto reconciliado. Esta capa es técnica, no semántica.'];REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
