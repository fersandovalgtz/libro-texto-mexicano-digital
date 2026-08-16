#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,tempfile
from pathlib import Path
import segment_ltmd_u1_w1_1966_fragments as core
STRUCT=Path('data/catalog/ltmd_u1_w1_2008_page_structure.csv');MAN=Path('data/catalog/ltmd_u1_w1_2008_page_manifest.csv');VERSION='FRAGSEG_LTMD_U1_W1_2008_0.1';BOOKS={'LTMD-CN3-G2008','LTMD-CN4-G2008'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--book-id',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w1_2008_fragments');a=ap.parse_args()
 if a.book_id not in BOOKS:raise SystemExit('unexpected book')
 core.VERSION=VERSION
 structure=[r for r in csv.DictReader(STRUCT.open(encoding='utf-8')) if r['book_id']==a.book_id and r['primary_structure'] in core.ELIGIBLE]
 raw=[r for r in csv.DictReader(MAN.open(encoding='utf-8')) if r['book_id']==a.book_id and r['effective_asset_status'].startswith('source_jpeg')];sources={}
 for r in raw:
  x=dict(r);x['source_asset_url']=r['effective_source_asset_url'];x['asset_status']=r['effective_asset_status'];sources[r['page_id']]=x
 if not structure:raise SystemExit('no eligible pages')
 frags=[];fails=[]
 with tempfile.TemporaryDirectory(prefix='ltmd-u1-w1-2008-frag-') as td:
  temp=Path(td)
  for r in structure:
   try:z,status=core.process_page(r,sources[r['page_id']],temp)
   except Exception as e:z=[];status=f'exception:{type(e).__name__}'
   if status!='ok' or not z:fails.append((r['page_id'],r['book_id'],status,len(z)))
   frags.extend(z)
   for p in temp.iterdir():p.unlink(missing_ok=True)
 d=Path(a.output_dir);d.mkdir(parents=True,exist_ok=True);out=d/f"fragment_{a.book_id.lower()}.csv";fail=d/f"fragment_{a.book_id.lower()}_failures.csv";fields=['fragment_id','page_id','book_id','catalog_generation','grade','viewer_page','fragment_sequence','candidate_type','token_count','char_count','question_mark_count','imperative_signal_count','material_signal','project_signal','experiment_signal','assessment_signal','activity_signal','text_sha256','segmenter_version','source_structure_class','classification_certainty','uncertain_boundary']
 with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(frags)
 with fail.open('w',encoding='utf-8',newline='') as f:w=csv.writer(f);w.writerow(['page_id','book_id','status','fragment_count']);w.writerows(fails)
 fatal=[x for x in fails if x[2]!='ok'];print(f'{a.book_id}: eligible={len(structure)} fragments={len(frags)} empty={len(fails)-len(fatal)} fatal={len(fatal)}')
 if fatal:raise SystemExit(f'{len(fatal)} fatal FRAGSEG failures')
if __name__=='__main__':main()
