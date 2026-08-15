#!/usr/bin/env python3
"""Extract front/end structural keyword flags for one CN Wave 2 book."""
from __future__ import annotations
import argparse,csv,hashlib,re,subprocess,tempfile,unicodedata
from pathlib import Path
from urllib.request import Request,urlopen

METRICS=Path('data/expansion/cn_wave2_ocr_page_metrics.csv')
MAN=Path('data/expansion/cn_wave2_page_manifest.csv')
VERSION='CN_WAVE2_STRUCTKW_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN Wave2 structural flags'
VOCAB={
 'front_matter':[r'\bpresentacion\b',r'\bprologo\b',r'\bintroduccion\b',r'\bconoce tu libro\b',r'\bal alumno\b',r'\bal maestro\b',r'\bmensaje\b'],
 'toc_navigation':[r'\bindice\b',r'\bcontenido(?:s)?\b',r'\bpagina(?:s)?\b',r'\bbloque(?:s)?\b',r'\btema(?:s)?\b',r'\bleccion(?:es)?\b'],
 'bibliography_credits':[r'\bbibliografia\b',r'\breferencias\b',r'\bfuentes consultadas\b',r'\bpara saber mas\b',r'\bisbn\b',r'\bderechos reservados\b',r'\bprimera edicion\b',r'\bsegunda edicion\b',r'\btercera edicion\b',r'\bcoordinacion\b',r'\bsecretaria de educacion publica\b',r'\bimpreso en mexico\b',r'\bcreditos iconograficos\b',r'\bcreditos fotograficos\b',r'\bcreditos de imagenes\b',r'\bfuentes de (?:las )?imagenes\b',r'\bfuentes de imagen\b',r'\bimagen de portada\b',r'\bfotografia de portada\b',r'\bilustracion de portada\b',r'\bagradecimientos\b',r'\bcolofon\b']}

def norm(s):
    s=unicodedata.normalize('NFKD',s);s=''.join(ch for ch in s if not unicodedata.combining(ch));return re.sub(r'\s+',' ',s.casefold())

def download_verify(row,target):
    h=hashlib.sha256()
    with urlopen(Request(row['source_asset_url'],headers={'User-Agent':UA}),timeout=45) as r,target.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b:break
            h.update(b);f.write(b)
    if h.hexdigest()!=row['sha256']:raise RuntimeError(f"SHA mismatch {row['page_id']}")

def run_ocr(img,psm):
    cp=subprocess.run(['tesseract',str(img),'stdout','-l','spa','--psm',str(psm or 3)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,timeout=90,check=False)
    return cp.stdout if cp.returncode==0 else ''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--book-id',required=True);ap.add_argument('--output-dir',default='data/work/cn_wave2_structkw');args=ap.parse_args()
    metrics=[r for r in csv.DictReader(METRICS.open(encoding='utf-8')) if r['book_id']==args.book_id]
    if not metrics:raise SystemExit(f'no consolidated Wave2 OCR rows for {args.book_id}')
    manifest={r['page_id']:r for r in csv.DictReader(MAN.open(encoding='utf-8')) if r['book_id']==args.book_id}
    max_page=max(int(r['viewer_page']) for r in metrics);candidates=[r for r in metrics if int(r['viewer_page'])<=16 or int(r['viewer_page'])>max_page-16]
    out=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn-wave2-struct-') as td:
        td=Path(td)
        for r in candidates:
            src=manifest[r['page_id']];img=td/f"{r['page_id']}.jpg";text='';verified=0;err=''
            try:
                download_verify(src,img);verified=1;text=norm(run_ocr(img,r['selected_psm'] or 3))
            except Exception as e:err=f'{type(e).__name__}: {e}'
            scores={cat:sum(1 for pat in pats if re.search(pat,text)) for cat,pats in VOCAB.items()};p=int(r['viewer_page'])
            out.append({'scanner_version':VERSION,'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'selected_psm':r['selected_psm'],'source_sha256_verified':verified,'front_zone':int(p<=16),'end_zone':int(p>max_page-16),'front_matter_score':scores['front_matter'],'toc_navigation_score':scores['toc_navigation'],'bibliography_credits_score':scores['bibliography_credits'],'matched_category_count':sum(v>0 for v in scores.values()),'error':err})
            img.unlink(missing_ok=True)
    if any(not int(r['source_sha256_verified']) for r in out):raise SystemExit(f'{args.book_id}: structural source verification failure')
    d=Path(args.output_dir);d.mkdir(parents=True,exist_ok=True);slug=args.book_id.lower().replace('ltmd-','');p=d/f'structkw_{slug}.csv'
    with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    print(f'{args.book_id}: structural candidates={len(out)} all SHA verified; out={p}')

if __name__=='__main__':main()
