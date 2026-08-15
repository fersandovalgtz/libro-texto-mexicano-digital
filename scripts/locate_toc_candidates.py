#!/usr/bin/env python3
"""Locate table-of-contents candidates in the early pages of pilot books.

Source images and OCR text are temporary. The output keeps only page-level
scores and short keyword-bearing lines (max 180 chars) so it does not publish
full transcriptions.
"""
from __future__ import annotations
import argparse,csv,re,subprocess,tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request,urlopen

UA='LibroTextoMexicanoDigital/0.1 TOC locator'
TERMS=('índice','indice','contenido','contenidos','unidad','bloque','tema','lección','leccion','capítulo','capitulo')
FIELDS=('book_id','catalog_generation','viewer_page','source_filename','toc_score','cue_lines','ocr_word_count','ocr_status','error')

def fetch(url,target):
    req=Request(url,headers={'User-Agent':UA})
    with urlopen(req,timeout=30) as r,target.open('wb') as fh:
        raw=r.headers.get('Content-Length'); expected=int(raw) if raw and raw.isdigit() else None; total=0
        while expected is None or total<expected:
            need=65536 if expected is None else min(65536,expected-total)
            b=r.read(need)
            if not b: break
            fh.write(b); total+=len(b)

def compact(s): return re.sub(r'\s+',' ',s).strip()[:180]

def process(row,root):
    img=root/f"{row['page_id']}.jpg"
    try:
        fetch(row['source_asset_url'],img)
        p=subprocess.run(['tesseract',str(img),'stdout','-l','spa','--psm','3'],capture_output=True,text=True,timeout=60)
        if p.returncode: raise RuntimeError(p.stderr.strip() or f'tesseract exit {p.returncode}')
        text=p.stdout or ''; low=text.lower(); score=sum(low.count(t) for t in TERMS)
        cues=[]
        for line in text.splitlines():
            c=compact(line); l=c.lower()
            if c and any(t in l for t in TERMS) and c not in cues: cues.append(c)
        return {'book_id':row['book_id'],'catalog_generation':row['catalog_generation'],'viewer_page':row['viewer_page'],'source_filename':row['source_filename'],'toc_score':score,'cue_lines':' || '.join(cues[:8]),'ocr_word_count':len(text.split()),'ocr_status':'ok','error':''}
    except Exception as e:
        return {'book_id':row['book_id'],'catalog_generation':row['catalog_generation'],'viewer_page':row['viewer_page'],'source_filename':row['source_filename'],'toc_score':'','cue_lines':'','ocr_word_count':'','ocr_status':'error','error':f'{type(e).__name__}: {e}'}
    finally: img.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--manifest',default='data/derived/page_manifest.csv'); ap.add_argument('--output',default='data/derived/toc_candidates.csv'); ap.add_argument('--pages',type=int,default=20); ap.add_argument('--books',default='LTMD-CN5-G1972,LTMD-CN5-G1988'); ap.add_argument('--workers',type=int,default=2); args=ap.parse_args()
    books={x.strip() for x in args.books.split(',') if x.strip()}
    with Path(args.manifest).open(encoding='utf-8',newline='') as fh:
        rows=[r for r in csv.DictReader(fh) if r['book_id'] in books and int(r['viewer_page'])<=args.pages]
    with tempfile.TemporaryDirectory(prefix='ltmd-toc-') as tmp:
        root=Path(tmp)
        with ThreadPoolExecutor(max_workers=args.workers) as pool: outrows=list(pool.map(lambda r:process(r,root),rows))
    with Path(args.output).open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(outrows)
    for r in outrows:
        if str(r['toc_score']).isdigit() and int(r['toc_score'])>0: print(r)
if __name__=='__main__': main()
