#!/usr/bin/env python3
"""Extract structural keyword flags for CN4/CN6 expansion, grouped by book_id.

Only front/end zones are reconstructed. Each JPEG is SHA-256 verified against the
expansion page manifest before OCR. Source images and OCR text are temporary;
only small category scores are persisted.
"""
from __future__ import annotations
import csv,hashlib,re,subprocess,tempfile,unicodedata
from pathlib import Path
from urllib.request import Request,urlopen

METRICS=Path('data/expansion/cn46_ocr_page_metrics.csv')
MAN=Path('data/expansion/cn46_page_manifest.csv')
OUT=Path('data/expansion/cn46_structural_keyword_flags.csv')
VERSION='CN46_STRUCTKW_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN46 structural flags'

VOCAB={
 'front_matter':[r'\bpresentacion\b',r'\bprologo\b',r'\bintroduccion\b',r'\bconoce tu libro\b',r'\bal alumno\b',r'\bal maestro\b',r'\bmensaje\b'],
 'toc_navigation':[r'\bindice\b',r'\bcontenido(?:s)?\b',r'\bpagina(?:s)?\b',r'\bbloque(?:s)?\b',r'\btema(?:s)?\b',r'\bleccion(?:es)?\b'],
 'bibliography_credits':[r'\bbibliografia\b',r'\breferencias\b',r'\bfuentes consultadas\b',r'\bpara saber mas\b',r'\bisbn\b',r'\bderechos reservados\b',r'\bprimera edicion\b',r'\bsegunda edicion\b',r'\btercera edicion\b',r'\bcoordinacion\b',r'\bsecretaria de educacion publica\b',r'\bimpreso en mexico\b',r'\bcreditos iconograficos\b',r'\bcreditos fotograficos\b',r'\bcreditos de imagenes\b',r'\bfuentes de (?:las )?imagenes\b',r'\bfuentes de imagen\b',r'\bimagen de portada\b',r'\bfotografia de portada\b',r'\bilustracion de portada\b',r'\bagradecimientos\b',r'\bcolofon\b']
}

def norm(s):
    s=unicodedata.normalize('NFKD',s);s=''.join(ch for ch in s if not unicodedata.combining(ch));s=s.casefold();return re.sub(r'\s+',' ',s)

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
    metrics=list(csv.DictReader(METRICS.open(encoding='utf-8')));manifest={r['page_id']:r for r in csv.DictReader(MAN.open(encoding='utf-8'))}
    if len(metrics)!=1888:raise SystemExit(f'expected 1888 OCR rows, found {len(metrics)}')
    bybook={}
    for r in metrics:bybook.setdefault(r['book_id'],[]).append(r)
    candidates=[]
    for bid,group in bybook.items():
        max_page=max(int(r['viewer_page']) for r in group)
        for r in group:
            p=int(r['viewer_page'])
            if p<=16 or p>max_page-16:candidates.append((r,max_page))
    out=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn46-structure-') as td:
        td=Path(td)
        for r,max_page in candidates:
            src=manifest[r['page_id']];img=td/f"{r['page_id']}.jpg";text='';verified=0;err=''
            try:
                download_verify(src,img);verified=1;text=norm(run_ocr(img,r['selected_psm'] or 3))
            except Exception as e:err=f'{type(e).__name__}: {e}'
            scores={cat:sum(1 for pat in pats if re.search(pat,text)) for cat,pats in VOCAB.items()}
            p=int(r['viewer_page'])
            out.append({'scanner_version':VERSION,'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'selected_psm':r['selected_psm'],'source_sha256_verified':verified,'front_zone':int(p<=16),'end_zone':int(p>max_page-16),'front_matter_score':scores['front_matter'],'toc_navigation_score':scores['toc_navigation'],'bibliography_credits_score':scores['bibliography_credits'],'matched_category_count':sum(v>0 for v in scores.values()),'error':err})
            img.unlink(missing_ok=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=list(out[0])
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    bad=sum(not int(r['source_sha256_verified']) for r in out)
    print(f'wrote {len(out)} structural candidate rows; hash failures={bad}')
    if bad:raise SystemExit('structural source verification failure')

if __name__=='__main__':main()
