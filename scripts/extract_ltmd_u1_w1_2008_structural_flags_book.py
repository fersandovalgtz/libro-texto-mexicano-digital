#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,re,tempfile
from pathlib import Path
from urllib.request import Request,urlopen
from extract_ltmd_u1_w1_1966_structural_flags_book import VOCAB,norm,run_ocr
MET=Path('data/catalog/ltmd_u1_w1_2008_ocr_metrics.csv');MAN=Path('data/catalog/ltmd_u1_w1_2008_page_manifest.csv');VERSION='LTMD_U1_W1_2008_STRUCTKW_0.1';UA='LibroTextoMexicanoDigital/U1-W1 2008 structural flags'
def download(src,dest):
 h=hashlib.sha256()
 with urlopen(Request(src['effective_source_asset_url'],headers={'User-Agent':UA}),timeout=45) as r,dest.open('wb') as f:
  while True:
   b=r.read(1024*1024)
   if not b:break
   h.update(b);f.write(b)
 if h.hexdigest()!=src['sha256']:raise RuntimeError(f"SHA mismatch {src['page_id']}")
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--book-id',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w1_2008_structkw');a=ap.parse_args();met=[r for r in csv.DictReader(MET.open(encoding='utf-8')) if r['book_id']==a.book_id];man={r['page_id']:r for r in csv.DictReader(MAN.open(encoding='utf-8')) if r['book_id']==a.book_id and r['effective_asset_status'].startswith('source_jpeg')}
 if not met:raise SystemExit('no metrics');m=max(int(r['viewer_page']) for r in met);cand=[r for r in met if int(r['viewer_page'])<=16 or int(r['viewer_page'])>m-16];out=[]
 with tempfile.TemporaryDirectory(prefix='ltmd-u1-w1-2008-struct-') as td:
  td=Path(td)
  for r in cand:
   src=man[r['page_id']];img=td/f"{r['page_id']}.jpg";verified=0;text='';err=''
   try:download(src,img);verified=1;text=norm(run_ocr(img,r['selected_psm'] or 3))
   except Exception as e:err=f'{type(e).__name__}: {e}'
   scores={cat:sum(1 for pat in pats if re.search(pat,text)) for cat,pats in VOCAB.items()};p=int(r['viewer_page'])
   out.append({'scanner_version':VERSION,'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'selected_psm':r['selected_psm'],'source_sha256_verified':verified,'front_zone':int(p<=16),'end_zone':int(p>m-16),'front_matter_score':scores['front_matter'],'toc_navigation_score':scores['toc_navigation'],'bibliography_credits_score':scores['bibliography_credits'],'matched_category_count':sum(v>0 for v in scores.values()),'error':err});img.unlink(missing_ok=True)
 if any(not int(r['source_sha256_verified']) for r in out):raise SystemExit('structural provenance failure')
 d=Path(a.output_dir);d.mkdir(parents=True,exist_ok=True);p=d/f"structkw_{a.book_id.lower()}.csv"
 with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 print(f'{a.book_id}: structural candidates={len(out)} all SHA verified')
if __name__=='__main__':main()
