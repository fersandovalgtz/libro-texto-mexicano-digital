#!/usr/bin/env python3
"""Audit CN4/CN6 no-text OCR pages with non-semantic visual proxies.

For pages classified `no_text_detected`, reconstruct + SHA-verify the source image,
compute grayscale entropy, non-white ratio, dark-pixel ratio and simple edge density,
then delete the image. No image, OCR text or semantic visual labels are persisted.
"""
from __future__ import annotations
import csv,hashlib,math,tempfile
from pathlib import Path
from urllib.request import Request,urlopen

from PIL import Image,ImageFilter

OCR=Path('data/expansion/cn46_ocr_page_metrics.csv')
MAN=Path('data/expansion/cn46_page_manifest.csv')
OUT=Path('data/expansion/cn46_no_text_visual_proxies.csv')
REPORT=Path('data/expansion/cn46_no_text_visual_proxies.md')
VERSION='CN46_NOTEXT_VISUAL_0.1'
UA='LibroTextoMexicanoDigital/0.1 no-text visual proxy audit'

def download_verify(row,path):
    h=hashlib.sha256()
    with urlopen(Request(row['source_asset_url'],headers={'User-Agent':UA}),timeout=45) as r,path.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b:break
            h.update(b);f.write(b)
    if h.hexdigest()!=row['sha256']:raise RuntimeError('SHA mismatch')

def entropy(hist,total):
    return -sum((n/total)*math.log2(n/total) for n in hist if n)

def metrics(path):
    im=Image.open(path).convert('L');im.thumbnail((1200,1200));px=list(im.getdata());n=len(px);hist=im.histogram()
    nonwhite=sum(v<245 for v in px)/n;dark=sum(v<100 for v in px)/n
    edges=im.filter(ImageFilter.FIND_EDGES);ep=list(edges.getdata());edge=sum(v>35 for v in ep)/len(ep)
    return {'width':im.width,'height':im.height,'grayscale_entropy':f'{entropy(hist,n):.6f}','nonwhite_ratio':f'{nonwhite:.6f}','dark_pixel_ratio':f'{dark:.6f}','edge_density':f'{edge:.6f}','visual_proxy_class':'near_blank' if nonwhite<.01 and edge<.01 else ('sparse_visual' if nonwhite<.08 else 'visual_content_present')}

def main():
    no=[r for r in csv.DictReader(OCR.open(encoding='utf-8')) if r['ocr_class']=='no_text_detected'];manifest={r['page_id']:r for r in csv.DictReader(MAN.open(encoding='utf-8'))}
    if len(no)!=8:raise SystemExit(f'expected 8 no-text pages from CN46_OCR_0.1, found {len(no)}')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn46-notext-') as td:
        td=Path(td)
        for r in no:
            src=manifest[r['page_id']];img=td/f"{r['page_id']}.jpg";download_verify(src,img)
            rows.append({'audit_version':VERSION,'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':r['viewer_page'],'source_sha256_verified':1,**metrics(img)})
            img.unlink(missing_ok=True)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    counts={c:sum(r['visual_proxy_class']==c for r in rows) for c in ('near_blank','sparse_visual','visual_content_present')}
    lines=['# Auditoría visual-proxy de páginas sin texto — CN4/CN6','',f'Versión: `{VERSION}`. Páginas auditadas: **{len(rows)}**.','',f"- `near_blank`: **{counts['near_blank']}**.\n- `sparse_visual`: **{counts['sparse_visual']}**.\n- `visual_content_present`: **{counts['visual_content_present']}**.",'','## Detalle']
    for r in rows:lines.append(f"- `{r['page_id']}`: nonwhite={float(r['nonwhite_ratio']):.3f}; entropy={float(r['grayscale_entropy']):.2f}; edge={float(r['edge_density']):.3f}; `{r['visual_proxy_class']}`.")
    lines+=['','## Restricción','Estas métricas sólo distinguen densidad visual aproximada. No identifican el contenido de la imagen y no sustituyen una inspección visual cuando ésta sea necesaria para una afirmación histórica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
