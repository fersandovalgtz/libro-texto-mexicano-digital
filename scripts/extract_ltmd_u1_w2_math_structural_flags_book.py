#!/usr/bin/env python3
"""Extract conservative front/end structural keyword flags for one W2 Math viewer."""
from __future__ import annotations
import argparse,csv,hashlib,re,subprocess,tempfile,unicodedata
from pathlib import Path
from urllib.request import Request,urlopen

METRICS=Path('data/catalog/ltmd_u1_w2_math_ocr_metrics.csv')
MAN=Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv')
VERSION='LTMD_U1_W2_MATH_STRUCTKW_0.1'
UA='LibroTextoMexicanoDigital/U1-W2 Mathematics structural flags'
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
            if not b: break
            h.update(b);f.write(b)
    if h.hexdigest()!=row['sha256']: raise RuntimeError(f"SHA mismatch {row['viewer_key']} page {row['viewer_page']}")

def run_ocr(img,psm):
    cp=subprocess.run(['tesseract',str(img),'stdout','-l','spa','--psm',str(psm or 3)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,timeout=90,check=False)
    return cp.stdout if cp.returncode==0 else ''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--viewer-key',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w2_math_structkw');args=ap.parse_args()
    metrics=[r for r in csv.DictReader(METRICS.open(encoding='utf-8')) if r['viewer_key']==args.viewer_key]
    if not metrics: raise SystemExit(f'no W2 OCR rows for {args.viewer_key}')
    manifest={(r['viewer_key'],int(r['viewer_page'])):r for r in csv.DictReader(MAN.open(encoding='utf-8')) if r['asset_status']=='source_jpeg'}
    max_page=max(int(r['viewer_page']) for r in metrics);candidates=[r for r in metrics if int(r['viewer_page'])<=16 or int(r['viewer_page'])>max_page-16]
    out=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w2-math-struct-') as td:
        td=Path(td)
        for r in candidates:
            src=manifest[(args.viewer_key,int(r['viewer_page']))];img=td/f"{r['page_id']}.jpg";text='';verified=0;err=''
            try: download_verify(src,img);verified=1;text=norm(run_ocr(img,r['selected_psm'] or 3))
            except Exception as e: err=f'{type(e).__name__}: {e}'
            scores={cat:sum(1 for pat in pats if re.search(pat,text)) for cat,pats in VOCAB.items()};p=int(r['viewer_page'])
            out.append({'scanner_version':VERSION,'page_id':r['page_id'],'viewer_key':r['viewer_key'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'selected_psm':r['selected_psm'],'source_sha256_verified':verified,'front_zone':int(p<=16),'end_zone':int(p>max_page-16),'front_matter_score':scores['front_matter'],'toc_navigation_score':scores['toc_navigation'],'bibliography_credits_score':scores['bibliography_credits'],'matched_category_count':sum(v>0 for v in scores.values()),'error':err})
            img.unlink(missing_ok=True)
    if any(not int(r['source_sha256_verified']) for r in out): raise SystemExit(f'{args.viewer_key}: structural source verification failure')
    d=Path(args.output_dir);d.mkdir(parents=True,exist_ok=True);p=d/f'structkw_{args.viewer_key.lower()}.csv'
    with p.open('w',encoding='utf-8',newline='') as f: w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    print(f'{args.viewer_key}: structural candidates={len(out)} all SHA verified; out={p}')
if __name__=='__main__': main()
