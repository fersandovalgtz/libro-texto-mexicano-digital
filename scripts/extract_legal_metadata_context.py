#!/usr/bin/env python3
"""Extract compact bibliographic context from known legal-page candidates.

The script does not persist complete OCR. It keeps only short lines containing
bibliographic markers (edición, reimpresión, ISBN, derechos, copyright, impreso)
and caps each retained line at 180 characters. Source JPEGs live only in a
temporary directory.
"""
from __future__ import annotations
import csv,re,subprocess,tempfile
from pathlib import Path
from urllib.request import Request,urlopen

UA='LibroTextoMexicanoDigital/0.1 legal metadata context'
LEGAL_PAGES={
 'LTMD-CN5-G1972':4,
 'LTMD-CN5-G1988':2,
 'LTMD-CN5-G1993':2,
 'LTMD-CN5-G2014':2,
}
KEYS=('edición','edicion','reimpresión','reimpresion','isbn','derechos','copyright','impreso','secretaría de educación pública','secretaria de educacion publica')
YEAR_RE=re.compile(r'\b(?:19[5-9]\d|20[0-2]\d)\b')
FIELDS=('book_id','catalog_generation','viewer_page','source_filename','years','edition_context','isbn_context','rights_context','ocr_status','error')

def fetch(url,target):
    req=Request(url,headers={'User-Agent':UA})
    with urlopen(req,timeout=30) as r,target.open('wb') as fh:
        raw=r.headers.get('Content-Length'); expected=int(raw) if raw and raw.isdigit() else None; total=0
        while expected is None or total<expected:
            need=65536 if expected is None else min(65536,expected-total)
            chunk=r.read(need)
            if not chunk: break
            fh.write(chunk); total+=len(chunk)

def ocr(path):
    p=subprocess.run(['tesseract',str(path),'stdout','-l','spa','--psm','3'],capture_output=True,text=True,timeout=60)
    if p.returncode: raise RuntimeError(p.stderr.strip() or f'tesseract exit {p.returncode}')
    return p.stdout

def compact(s): return re.sub(r'\s+',' ',s).strip()[:180]

def main():
    rows=list(csv.DictReader(open('data/derived/page_manifest.csv',encoding='utf-8',newline='')))
    chosen=[r for r in rows if r['book_id'] in LEGAL_PAGES and int(r['viewer_page'])==LEGAL_PAGES[r['book_id']]]
    outrows=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-legal-') as tmp:
      root=Path(tmp)
      for r in chosen:
        img=root/f"{r['page_id']}.jpg"
        try:
          fetch(r['source_asset_url'],img); text=ocr(img)
          lines=[compact(x) for x in text.splitlines() if compact(x)]
          edition=[]; isbn=[]; rights=[]
          for line in lines:
            low=line.lower()
            if ('edición' in low or 'edicion' in low or 'reimpresión' in low or 'reimpresion' in low) and line not in edition: edition.append(line)
            if 'isbn' in low and line not in isbn: isbn.append(line)
            if any(k in low for k in ('derechos','copyright','impreso','secretaría de educación pública','secretaria de educacion publica')) and line not in rights: rights.append(line)
          outrows.append({'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'viewer_page':r['viewer_page'],'source_filename':r['source_filename'],'years':'|'.join(sorted(set(YEAR_RE.findall(text)))),'edition_context':' || '.join(edition[:6]),'isbn_context':' || '.join(isbn[:4]),'rights_context':' || '.join(rights[:6]),'ocr_status':'ok','error':''})
        except Exception as e:
          outrows.append({'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'viewer_page':r['viewer_page'],'source_filename':r['source_filename'],'years':'','edition_context':'','isbn_context':'','rights_context':'','ocr_status':'error','error':f'{type(e).__name__}: {e}'})
        finally: img.unlink(missing_ok=True)
    with open('data/derived/legal_metadata_context.csv','w',encoding='utf-8',newline='') as fh:
      w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(outrows)
    for r in outrows: print(r)
if __name__=='__main__':main()
