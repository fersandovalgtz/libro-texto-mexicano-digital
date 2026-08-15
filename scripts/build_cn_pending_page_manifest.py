#!/usr/bin/env python3
"""Build complete SHA-256 page manifest for the 25 unaudited strict CN viewers.

Every declared viewer position is probed using the catalog's observed file mapping.
Reachable image bytes are streamed and hashed; unavailable final positions are
recorded as terminal synthetic. Any unavailable internal position is a hard anomaly
that blocks `corpus_ready`. Source images are never committed.
"""
from __future__ import annotations
import csv,hashlib,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

INV=Path('data/catalog/ciencias_naturales_technical_inventory.csv')
OUT=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
SUMMARY=Path('data/catalog/ciencias_naturales_pending_page_manifest_summary.csv')
REPORT=Path('data/catalog/ciencias_naturales_pending_page_manifest.md')
VERSION='CN_PENDING_PAGE_MANIFEST_0.1'
UA='LibroTextoMexicanoDigital/0.1 full CN pending page manifest'
BASE='https://historico.conaliteg.gob.mx/'

def url(key,p):return f'{BASE}c/{key}/{0 if p==1 else p:03d}.jpg'
def qtile(p,n):
    r=p/n
    return 'Q1' if r<=.25 else ('Q2' if r<=.5 else ('Q3' if r<=.75 else 'Q4'))
def fetch_hash(u,max_attempts=3):
    last=''
    for attempt in range(1,max_attempts+1):
        try:
            h=hashlib.sha256();size=0
            with urlopen(Request(u,headers={'User-Agent':UA}),timeout=45) as r:
                status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    h.update(b);size+=len(b)
            if status==200 and 'image' in ctype.lower() and size>0:return {'reachable_image':1,'http_status':status,'content_type':ctype,'byte_size':size,'sha256':h.hexdigest(),'fetch_attempts':attempt,'error':''}
            last=f'unexpected status={status} type={ctype} size={size}'
        except HTTPError as e:
            if e.code==404:return {'reachable_image':0,'http_status':404,'content_type':e.headers.get('Content-Type','') if e.headers else '','byte_size':'','sha256':'','fetch_attempts':attempt,'error':'HTTP 404'}
            last=f'HTTPError {e.code}'
        except (URLError,TimeoutError,OSError) as e:last=f'{type(e).__name__}: {e}'
        if attempt<max_attempts:time.sleep(attempt)
    return {'reachable_image':0,'http_status':'','content_type':'','byte_size':'','sha256':'','fetch_attempts':max_attempts,'error':last}

def main():
    books=[r for r in csv.DictReader(INV.open(encoding='utf-8')) if r['current_corpus_status']=='catalog_only']
    if len(books)!=25:raise SystemExit(f'expected 25 pending books, found {len(books)}')
    declared=sum(int(b['viewer_positions_declared']) for b in books)
    if declared!=4207:raise SystemExit(f'pending declared-position total drifted: {declared}')
    rows=[];futs={}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for b in books:
            n=int(b['viewer_positions_declared'])
            for p in range(1,n+1):
                row={'manifest_version':VERSION,'page_id':f"{b['book_id']}-VP{p:03d}",'book_id':b['book_id'],'viewer_key':b['viewer_key'],'catalog_generation':b['catalog_generation'],'grade':b['grade'],'viewer_page':p,'declared_page_count':n,'source_image_index':0 if p==1 else p,'source_asset_url':url(b['viewer_key'],p),'is_final_declared_position':int(p==n),'position_ratio':f'{p/n:.6f}','position_quartile':qtile(p,n)}
                rows.append(row);futs[ex.submit(fetch_hash,row['source_asset_url'])]=row
        done=0
        for fut in as_completed(futs):
            futs[fut].update(fut.result());done+=1
            if done%500==0:print('hashed/probed',done,'/',len(futs))
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    anomalies=[]
    for r in rows:
        if int(r['reachable_image']):r['asset_status']='source_jpeg'
        elif int(r['is_final_declared_position']):r['asset_status']='terminal_synthetic'
        else:r['asset_status']='internal_missing';anomalies.append(r)
    if anomalies:
        # Persist diagnostic so failure is inspectable, then stop before corpus_ready claim.
        print('INTERNAL MISSING',[(r['book_id'],r['viewer_page'],r['error']) for r in anomalies[:20]])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['manifest_version','page_id','book_id','viewer_key','catalog_generation','grade','viewer_page','declared_page_count','source_image_index','source_asset_url','is_final_declared_position','position_ratio','position_quartile','asset_status','reachable_image','http_status','content_type','byte_size','sha256','fetch_attempts','error']
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    summary=[]
    for b in books:
        rr=[r for r in rows if r['book_id']==b['book_id']];src=[r for r in rr if r['asset_status']=='source_jpeg'];term=[r for r in rr if r['asset_status']=='terminal_synthetic'];miss=[r for r in rr if r['asset_status']=='internal_missing']
        summary.append({'manifest_version':VERSION,'book_id':b['book_id'],'viewer_key':b['viewer_key'],'catalog_generation':b['catalog_generation'],'grade':b['grade'],'viewer_positions':len(rr),'source_jpegs':len(src),'terminal_synthetic':len(term),'internal_missing':len(miss),'total_source_bytes':sum(int(r['byte_size']) for r in src),'unique_source_hashes':len({r['sha256'] for r in src}),'corpus_ready_asset_layer':int(not miss and all(r['sha256'] for r in src))})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    src=[r for r in rows if r['asset_status']=='source_jpeg'];term=[r for r in rows if r['asset_status']=='terminal_synthetic'];miss=[r for r in rows if r['asset_status']=='internal_missing'];dup=len(src)-len({r['sha256'] for r in src})
    lines=['# Manifiesto de páginas — 25 objetos pendientes de Ciencias Naturales','',f'Versión: `{VERSION}`.','',f'- Posiciones declaradas: **{len(rows):,}**.\n- JPEG fuente verificados y hasheados: **{len(src):,}**.\n- Finales declarados sin imagen / terminal sintético: **{len(term)}**.\n- Huecos internos: **{len(miss)}**.\n- Bytes fuente recorridos: **{sum(int(r["byte_size"]) for r in src):,}**.\n- Hashes repetidos dentro de esta ola: **{dup}**.','', '## Por objeto']
    for s in summary:lines.append(f"- `{s['book_id']}`: posiciones={s['viewer_positions']}; JPEG={s['source_jpegs']}; terminal={s['terminal_synthetic']}; internos ausentes={s['internal_missing']}; corpus-ready-activos={'sí' if int(s['corpus_ready_asset_layer']) else 'no'}.")
    lines+=['','## Regla','Cada posición se prueba de forma empírica. Sólo una ausencia en la posición final puede clasificarse como terminal sintético; una ausencia interna bloquea la auditoría y debe investigarse.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))
    if miss:raise SystemExit(f'{len(miss)} internal missing positions detected; asset layer not fully corpus-ready')

if __name__=='__main__':main()
