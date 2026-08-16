#!/usr/bin/env python3
"""Build SHA-256 page manifests for the two LTMD-U1 W1 1966 nature-study viewers.

Source bytes are streamed only for hashing and never persisted in the repository.
Every declared position is probed empirically. An internal unserved position is a
hard anomaly; an unserved final position is recorded as terminal_synthetic.
"""
from __future__ import annotations
import csv, hashlib, json, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCOPE=Path('data/catalog/ltmd_u1_w1_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w1_1966_page_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w1_1966_page_manifest_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w1_1966_page_manifest.md')
VERSION='LTMD_U1_W1_1966_PAGE_MANIFEST_0.1'
BASE='https://historico.conaliteg.gob.mx/'
UA='LibroTextoMexicanoDigital/U1-W1 1966 asset manifest'
EXPECTED={'H1966P6CI374','H1966P6CI375'}

def asset_url(key,p):
    return f'{BASE}c/{key}/{0 if p==1 else p:03d}.jpg'

def qtile(p,n):
    r=p/n
    return 'Q1' if r<=.25 else ('Q2' if r<=.5 else ('Q3' if r<=.75 else 'Q4'))

def fetch_hash(url,max_attempts=3):
    last=''
    for attempt in range(1,max_attempts+1):
        try:
            h=hashlib.sha256(); size=0
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as resp:
                status=getattr(resp,'status',None); ctype=resp.headers.get('Content-Type','')
                while True:
                    b=resp.read(1024*1024)
                    if not b: break
                    h.update(b); size+=len(b)
            if status==200 and 'image' in ctype.lower() and size>0:
                return {'reachable_image':1,'http_status':status,'content_type':ctype,'byte_size':size,'sha256':h.hexdigest(),'fetch_attempts':attempt,'error':''}
            last=f'unexpected status={status} type={ctype} size={size}'
        except HTTPError as e:
            if e.code==404:
                return {'reachable_image':0,'http_status':404,'content_type':e.headers.get('Content-Type','') if e.headers else '','byte_size':'','sha256':'','fetch_attempts':attempt,'error':'HTTP 404'}
            last=f'HTTPError {e.code}'
        except (URLError,TimeoutError,OSError) as e:
            last=f'{type(e).__name__}: {e}'
        if attempt<max_attempts: time.sleep(attempt)
    return {'reachable_image':0,'http_status':'','content_type':'','byte_size':'','sha256':'','fetch_attempts':max_attempts,'error':last}

def main():
    scope=[r for r in csv.DictReader(SCOPE.open(encoding='utf-8')) if r['execution_action']=='new_direct_ingestion']
    if {r['viewer_key'] for r in scope}!=EXPECTED:
        raise SystemExit('1966 W1 scope drift')
    with urlopen(Request(BASE+'claves.json',headers={'User-Agent':UA}),timeout=45) as resp:
        claves=json.loads(resp.read().decode('utf-8-sig'))
    books=[]
    for r in scope:
        cfg=claves.get(r['viewer_key'])
        if not isinstance(cfg,dict) or 'ag_pages' not in cfg:
            raise SystemExit(f"missing ag_pages for {r['viewer_key']}")
        b=dict(r); b['viewer_positions_declared']=int(cfg['ag_pages']); books.append(b)
    records=[]; futures={}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for b in books:
            n=int(b['viewer_positions_declared'])
            for p in range(1,n+1):
                rec={
                    'manifest_version':VERSION,
                    'page_id':f"{b['book_id']}-VP{p:03d}",
                    'book_id':b['book_id'],
                    'viewer_key':b['viewer_key'],
                    'catalog_generation':b['catalog_generation'],
                    'grade_code':b['grade_code'],
                    'title_core':b['title_core'],
                    'viewer_page':p,
                    'declared_page_count':n,
                    'source_image_index':0 if p==1 else p,
                    'source_asset_url':asset_url(b['viewer_key'],p),
                    'is_final_declared_position':int(p==n),
                    'position_ratio':f'{p/n:.6f}',
                    'position_quartile':qtile(p,n),
                }
                records.append(rec); futures[ex.submit(fetch_hash,rec['source_asset_url'])]=rec
        for i,fut in enumerate(as_completed(futures),1):
            futures[fut].update(fut.result())
            if i%100==0: print('probed',i,'/',len(futures))
    records.sort(key=lambda r:(r['viewer_key'],int(r['viewer_page'])))
    internal=[]
    for r in records:
        if int(r['reachable_image']): r['asset_status']='source_jpeg'
        elif int(r['is_final_declared_position']): r['asset_status']='terminal_synthetic'
        else: r['asset_status']='internal_unserved'; internal.append(r)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['manifest_version','page_id','book_id','viewer_key','catalog_generation','grade_code','title_core','viewer_page','declared_page_count','source_image_index','source_asset_url','is_final_declared_position','position_ratio','position_quartile','asset_status','reachable_image','http_status','content_type','byte_size','sha256','fetch_attempts','error']
    with OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(records)
    summaries=[]
    for b in sorted(books,key=lambda x:x['viewer_key']):
        rr=[r for r in records if r['viewer_key']==b['viewer_key']]
        src=[r for r in rr if r['asset_status']=='source_jpeg']; term=[r for r in rr if r['asset_status']=='terminal_synthetic']; miss=[r for r in rr if r['asset_status']=='internal_unserved']
        summaries.append({
            'manifest_version':VERSION,'book_id':b['book_id'],'viewer_key':b['viewer_key'],'catalog_generation':b['catalog_generation'],'grade_code':b['grade_code'],'title_core':b['title_core'],
            'viewer_positions':len(rr),'source_jpegs':len(src),'terminal_synthetic':len(term),'internal_unserved':len(miss),'source_bytes':sum(int(r['byte_size']) for r in src),'unique_source_hashes':len({r['sha256'] for r in src}),'asset_layer_ready':int(not miss and all(r['sha256'] for r in src))
        })
    with SUMMARY.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0])); w.writeheader(); w.writerows(summaries)
    src=[r for r in records if r['asset_status']=='source_jpeg']; term=[r for r in records if r['asset_status']=='terminal_synthetic']
    lines=['# LTMD-U1 W1 — manifiesto de activos de 1966','',f'Versión: `{VERSION}`.','',f'- Visores: **{len(books)}**.\n- Posiciones declaradas: **{len(records):,}**.\n- JPEG fuente hasheados: **{len(src):,}**.\n- Terminales sintéticos observados: **{len(term)}**.\n- Posiciones internas no servidas: **{len(internal)}**.\n- Bytes fuente recorridos: **{sum(int(r["byte_size"]) for r in src):,}**.','', '## Por objeto']
    for s in summaries:
        lines.append(f"- `{s['viewer_key']}` / `{s['book_id']}`: posiciones={s['viewer_positions']}; JPEG={s['source_jpegs']}; terminal={s['terminal_synthetic']}; internos no servidos={s['internal_unserved']}; asset-layer-ready={'sí' if int(s['asset_layer_ready']) else 'no'}.")
    lines += ['','## Regla','La auditoría prueba empíricamente cada posición declarada por `claves.json`. Sólo una ausencia en la posición final se registra como `terminal_synthetic`; cualquier ausencia interna bloquea la promoción automática a la siguiente capa. Las imágenes no se persisten.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))
    if internal: raise SystemExit(f'{len(internal)} internal unserved positions detected')

if __name__=='__main__': main()
