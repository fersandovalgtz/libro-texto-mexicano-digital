#!/usr/bin/env python3
"""Build a provenance + SHA-256 page manifest for the CN4/CN6 expansion corpus.

Images are streamed from the public CONALITEG viewer, hashed in memory/chunks,
and discarded. No source image is written to the repository. The output keeps one
row per declared viewer position so each terminal synthetic slot remains explicit.
"""
from __future__ import annotations

import csv,hashlib,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

INV=Path('data/expansion/cn46_inventory_preliminary.csv')
OUT=Path('data/expansion/cn46_page_manifest.csv')
SUMMARY=Path('data/expansion/cn46_page_manifest_summary.csv')
REPORT=Path('data/expansion/cn46_page_manifest_report.md')
VERSION='CN46_PAGE_MANIFEST_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN46 page manifest hash audit'

FIELDS=(
    'manifest_version','page_id','book_id','catalog_generation','grade','viewer_key',
    'viewer_page','source_image_index','source_filename','source_asset_url',
    'asset_status','http_status','content_type','byte_size','sha256','fetch_attempts',
    'position_ratio','position_quartile','page_type_status','error'
)

def qtile(page,n):
    r=page/n
    if r<=.25:return 'Q1'
    if r<=.5:return 'Q2'
    if r<=.75:return 'Q3'
    return 'Q4'

def source_url(key,p):
    idx=0 if p==1 else p
    return f'https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg'

def fetch_hash(url,max_attempts=3):
    last=''
    for attempt in range(1,max_attempts+1):
        try:
            req=Request(url,headers={'User-Agent':UA})
            with urlopen(req,timeout=45) as r:
                status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
                h=hashlib.sha256();size=0
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    h.update(b);size+=len(b)
                if status==200 and 'image' in ctype.lower() and size>0:
                    return {'http_status':status,'content_type':ctype,'byte_size':size,'sha256':h.hexdigest(),'fetch_attempts':attempt,'error':''}
                last=f'unexpected response status={status} type={ctype} size={size}'
        except (HTTPError,URLError,TimeoutError,OSError) as e:
            last=f'{type(e).__name__}: {e}'
        if attempt<max_attempts:time.sleep(attempt)
    return {'http_status':'','content_type':'','byte_size':'','sha256':'','fetch_attempts':max_attempts,'error':last}

def main():
    books=list(csv.DictReader(INV.open(encoding='utf-8',newline='')))
    if len(books)!=9:raise SystemExit(f'expected 9 audited expansion objects, found {len(books)}')
    rows=[];jobs={}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for b in books:
            n=int(b['page_count']);assets=int(b['source_asset_count'])
            if assets!=n-1:raise SystemExit(f"{b['book_id']}: expected exactly one terminal synthetic slot, got pages={n} assets={assets}")
            for p in range(1,n+1):
                terminal=(p==n)
                idx='' if terminal else (0 if p==1 else p)
                filename='' if terminal else f'{int(idx):03d}.jpg'
                url='' if terminal else source_url(b['viewer_key'],p)
                row={
                    'manifest_version':VERSION,
                    'page_id':f"{b['book_id']}-VP{p:03d}",
                    'book_id':b['book_id'],'catalog_generation':b['catalog_generation'],'grade':b['grade'],'viewer_key':b['viewer_key'],
                    'viewer_page':p,'source_image_index':idx,'source_filename':filename,'source_asset_url':url,
                    'asset_status':'terminal_synthetic' if terminal else 'source_jpeg',
                    'http_status':'','content_type':'','byte_size':'','sha256':'','fetch_attempts':'',
                    'position_ratio':f'{p/n:.6f}','position_quartile':qtile(p,n),
                    'page_type_status':'terminal_synthetic' if terminal else 'unclassified','error':''
                }
                rows.append(row)
                if not terminal:jobs[ex.submit(fetch_hash,url)]=row
        for fut in as_completed(jobs):
            row=jobs[fut]
            try:row.update(fut.result())
            except Exception as e:row.update({'error':f'{type(e).__name__}: {e}','fetch_attempts':3})
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    failures=[r for r in rows if r['asset_status']=='source_jpeg' and not r['sha256']]
    source=[r for r in rows if r['asset_status']=='source_jpeg'];terminal=[r for r in rows if r['asset_status']=='terminal_synthetic']
    if len(rows)!=1888 or len(source)!=1879 or len(terminal)!=9:
        raise SystemExit(f'invariant failure viewer={len(rows)} source={len(source)} terminal={len(terminal)}')
    if failures:raise SystemExit(f'{len(failures)} source assets could not be hashed; refusing incomplete manifest')
    if len({r['page_id'] for r in rows})!=len(rows):raise SystemExit('duplicate page_id')
    if len({r['sha256'] for r in source})!=len(source):
        # Duplicate bytes are not necessarily invalid, but must be explicit rather than hidden.
        duplicate_hashes=len(source)-len({r['sha256'] for r in source})
    else:duplicate_hashes=0
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    summary=[]
    for b in books:
        rr=[r for r in rows if r['book_id']==b['book_id']];ss=[r for r in rr if r['asset_status']=='source_jpeg']
        summary.append({'manifest_version':VERSION,'book_id':b['book_id'],'catalog_generation':b['catalog_generation'],'grade':b['grade'],'viewer_key':b['viewer_key'],'viewer_positions':len(rr),'source_jpegs':len(ss),'terminal_synthetic':sum(r['asset_status']=='terminal_synthetic' for r in rr),'total_source_bytes':sum(int(r['byte_size']) for r in ss),'unique_source_hashes':len({r['sha256'] for r in ss})})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    total_bytes=sum(int(r['byte_size']) for r in source)
    lines=['# Manifiesto de páginas — expansión CN4/CN6','',f'Versión: `{VERSION}`.','',f'- Posiciones de visor: **{len(rows):,}**.\n- JPEG fuente verificados y hasheados: **{len(source):,}**.\n- Posiciones terminales sintéticas: **{len(terminal)}**.\n- Bytes fuente recorridos para SHA-256: **{total_bytes:,}**.\n- Hashes repetidos entre páginas: **{duplicate_hashes}**.','', '## Por objeto']
    for s in summary:lines.append(f"- `{s['book_id']}`: visor={s['viewer_positions']}; JPEG={s['source_jpegs']}; bytes={int(s['total_source_bytes']):,}; hashes únicos={s['unique_source_hashes']}.")
    lines+=['','## Regla de procedencia','El manifiesto conserva URL, tamaño y SHA-256 de cada activo, pero no redistribuye el JPEG. Una etapa posterior debe reconstruir temporalmente el activo y comprobar el hash antes de producir OCR o derivados.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
