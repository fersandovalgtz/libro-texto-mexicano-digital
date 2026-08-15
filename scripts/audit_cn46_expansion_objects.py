#!/usr/bin/env python3
"""Audit discovered CN4/CN6 CONALITEG objects without persisting source/OCR text.

For verified viewers discovered from libros_2023.js this script:
- resolves ag_pages from public claves.json;
- probes every expected page image concurrently plus the terminal synthetic slot;
- OCRs viewer pages 1–8 ephemerally using Tesseract;
- publishes only bibliographic signals/candidates and asset availability metadata.

No page image or OCR transcript is committed.
"""
from __future__ import annotations

import csv,json,re,subprocess,tempfile,unicodedata
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen

BASE='https://historico.conaliteg.gob.mx/'
UA='LibroTextoMexicanoDigital/0.1 CN46 object audit'
DISC=Path('data/expansion/cn46_viewer_candidates.csv')
INV=Path('data/expansion/cn46_inventory_preliminary.csv')
ASSETS=Path('data/expansion/cn46_asset_audit.csv')
FRONT=Path('data/expansion/cn46_frontmatter_audit.csv')
REPORT=Path('data/expansion/cn46_object_audit_report.md')
VERSION='CN46_OBJECT_AUDIT_0.1'

def fetch_bytes(url,timeout=30):
    req=Request(url,headers={'User-Agent':UA})
    with urlopen(req,timeout=timeout) as r:return r.read()

def low(s):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())

def years_near(text,terms,window=120):
    t=low(text);found=set()
    for term in terms:
        for m in re.finditer(term,t):
            found.update(re.findall(r'\b(19[0-9]{2}|20[0-9]{2})\b',t[max(0,m.start()-window):m.end()+window]))
    return sorted(found)

def isbns(text):
    vals=[]
    for m in re.finditer(r'(?i)isbn\s*[:\-]?\s*([0-9Xx][0-9Xx\-\s]{7,24}[0-9Xx])',text):
        raw=re.sub(r'\s+',' ',m.group(1)).strip(' .,:;');digits=re.sub(r'[^0-9Xx]','',raw)
        if len(digits) in {10,13}:vals.append(raw)
    return sorted(set(vals))

def viewer_asset_url(key,viewer_page):
    idx=0 if viewer_page==1 else viewer_page
    return f'{BASE}c/{key}/{idx:03d}.jpg'

def probe(url):
    # GET one byte is more portable than HEAD across legacy servers.
    req=Request(url,headers={'User-Agent':UA,'Range':'bytes=0-0'})
    try:
        with urlopen(req,timeout=20) as r:
            status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
            r.read(1)
            return status,ctype,''
    except HTTPError as e:return e.code,e.headers.get('Content-Type','') if e.headers else '',f'HTTPError: {e.code}'
    except Exception as e:return '', '',f'{type(e).__name__}: {e}'

def run_ocr(img,outbase,psm):
    p=subprocess.run(['tesseract',str(img),str(outbase),'-l','spa','--psm',str(psm),'tsv'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if p.returncode:return ''
    fp=outbase.with_suffix('.tsv')
    if not fp.exists():return ''
    words=[]
    with fp.open(encoding='utf-8',errors='replace',newline='') as f:
        for r in csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE):
            if r.get('level')=='5' and r.get('text','').strip():words.append(r['text'].strip())
    return ' '.join(words)

def best_ocr(img,tempstem):
    best=''
    for psm in (3,6,11):
        out=tempstem.with_name(tempstem.name+f'_p{psm}')
        txt=run_ocr(img,out,psm)
        score=sum(c.isalnum() for c in txt)
        if score>sum(c.isalnum() for c in best):best=txt
    return best

def book_id(row):
    if row['viewer_key']=='H1993P6CI209':return 'LTMD-CN6-G1993-DH'
    if row['viewer_key']=='H1993P6CI210':return 'LTMD-CN6-G1993-CN'
    return f"LTMD-CN{row['grade']}-G{row['catalog_generation']}"

def title_only(viewer_title):
    return re.split(r'\s+Grado\s+[46]',viewer_title,flags=re.I)[0].strip()

def main():
    discovered=[r for r in csv.DictReader(DISC.open(encoding='utf-8')) if r['verification_status']=='verified_title']
    if len(discovered)!=9:raise SystemExit(f'expected 9 verified viewers, found {len(discovered)}')
    claves=json.loads(fetch_bytes(BASE+'claves.json').decode('utf-8-sig'))
    asset_rows=[];front_rows=[];inventory=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-cn46-') as td:
        tmp=Path(td)
        for r in discovered:
            key=r['viewer_key'];entry=claves.get(key)
            if not isinstance(entry,dict):raise SystemExit(f'missing claves.json entry: {key}')
            n=int(entry['ag_pages'])
            # Expected real slots mirror the audited pilot convention: viewer 1 => 000,
            # viewer 2..N-1 => numeric file; N is explicitly probed as terminal slot.
            pages=list(range(1,n+1))
            with ThreadPoolExecutor(max_workers=16) as ex:
                fut={ex.submit(probe,viewer_asset_url(key,p)):p for p in pages}
                local=[]
                for f in as_completed(fut):
                    p=fut[f];status,ctype,err=f.result();reachable=int(status in (200,206) and 'image' in (ctype or '').lower())
                    local.append({'audit_version':VERSION,'book_id':book_id(r),'viewer_key':key,'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'source_image_index':0 if p==1 else p,'is_terminal_declared_slot':int(p==n),'url':viewer_asset_url(key,p),'http_status':status,'content_type':ctype,'reachable_image':reachable,'error':err})
            local.sort(key=lambda x:x['viewer_page']);asset_rows+=local
            reachable=sum(x['reachable_image'] for x in local);terminal=[x for x in local if x['viewer_page']==n][0]
            # OCR front matter pages only, with no persistent text.
            local_front=[]
            for p in range(1,min(8,n)+1):
                url=viewer_asset_url(key,p);img=tmp/f'{key}_{p:03d}.jpg';stem=tmp/f'{key}_{p:03d}'
                try:
                    img.write_bytes(fetch_bytes(url));text=best_ocr(img,stem);t=low(text)
                    local_front.append({'audit_version':VERSION,'book_id':book_id(r),'viewer_key':key,'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'ocr_ok':int(bool(text.strip())),'ocr_char_count':len(text),'edition_term':int('edicion' in t),'copyright_term':int('derechos reservados' in t or 'copyright' in t or 'd. r.' in t or 'd.r.' in t),'printing_term':int('impresion' in t or 'impreso' in t or 'reimpresion' in t),'isbn_term':int('isbn' in t),'edition_year_candidates':';'.join(years_near(text,[r'primera edici[oó]n',r'segunda edici[oó]n',r'tercera edici[oó]n',r'edici[oó]n revisada',r'edici[oó]n'])),'copyright_year_candidates':';'.join(years_near(text,[r'derechos reservados',r'd\.\s*r\.',r'copyright',r'©'])),'printing_year_candidates':';'.join(years_near(text,[r'impresi[oó]n',r'impreso',r'reimpresi[oó]n'])),'isbn_candidates':';'.join(isbns(text)),'all_years_detected':';'.join(sorted(set(re.findall(r'\b(19[0-9]{2}|20[0-9]{2})\b',t))))})
                except Exception as e:
                    local_front.append({'audit_version':VERSION,'book_id':book_id(r),'viewer_key':key,'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':p,'ocr_ok':0,'ocr_char_count':0,'edition_term':'','copyright_term':'','printing_term':'','isbn_term':'','edition_year_candidates':'','copyright_year_candidates':'','printing_year_candidates':'','isbn_candidates':'','all_years_detected':''})
                for x in tmp.iterdir():
                    try:x.unlink()
                    except Exception:pass
            front_rows+=local_front
            ed=sorted({y for x in local_front for y in x['edition_year_candidates'].split(';') if y});cr=sorted({y for x in local_front for y in x['copyright_year_candidates'].split(';') if y});pr=sorted({y for x in local_front for y in x['printing_year_candidates'].split(';') if y});isb=sorted({y for x in local_front for y in x['isbn_candidates'].split(';') if y})
            inventory.append({'book_id':book_id(r),'title':title_only(r['viewer_title']),'catalog_generation':r['catalog_generation'],'grade':r['grade'],'subject_or_field':'Ciencias Naturales','viewer_key':key,'source_url':r['source_url'],'page_count':n,'source_asset_count':reachable,'terminal_slot_reachable':terminal['reachable_image'],'page_count_status':'audited' if reachable in {n-1,n} else 'anomaly','edition_year':'','edition_year_status':'unverified','edition_year_candidates':';'.join(ed),'copyright_year_candidates':';'.join(cr),'printing_year_candidates':';'.join(pr),'isbn_candidates':';'.join(isb),'selection_status':'pending_comparability_review' if (r['catalog_generation']=='1993' and r['grade']=='6') else 'candidate_core','source_repository':'CONALITEG Catálogo Histórico','access_date':'2026-08-15','rights_note':'Consulta pública; no se asume autorización para redistribuir archivos fuente, imágenes u OCR completo.'})
    INV.parent.mkdir(parents=True,exist_ok=True)
    for path,rows in ((ASSETS,asset_rows),(FRONT,front_rows),(INV,inventory)):
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    lines=['# Auditoría de objetos de expansión CN4/CN6','',f'Versión: `{VERSION}`. Se auditaron **{len(inventory)} visores** confirmados como Ciencias Naturales. No se persisten imágenes ni OCR.','', '## Inventario preliminar']
    for x in inventory:
        sig=[]
        if x['edition_year_candidates']:sig.append('edición? '+x['edition_year_candidates'])
        if x['copyright_year_candidates']:sig.append('copyright? '+x['copyright_year_candidates'])
        if x['isbn_candidates']:sig.append('ISBN? '+x['isbn_candidates'])
        lines.append(f"- `{x['book_id']}` · `{x['viewer_key']}` · {x['title']} · visor={x['page_count']} · imágenes accesibles={x['source_asset_count']} · terminal accesible={x['terminal_slot_reachable']} · {x['selection_status']}"+(f" · {'; '.join(sig)}" if sig else ''))
    lines+=['','## Regla de interpretación','Los años e ISBN extraídos por OCR son candidatos técnicos. Ninguno se convierte automáticamente en metadato bibliográfico verificado. Los dos objetos de 6º/1993 permanecen simultáneamente en el inventario hasta resolver su relación documental.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
