#!/usr/bin/env python3
"""Audit current official CONALITEG representations for retained W11 EAM viewers.

The historical W11 nonstandard asset manifest is authoritative. Current
CONALITEG output.json is searched recursively only for P1EAM/P2EAM entries.
Candidate asset bases are derived from the JSON path in which each matching
configuration occurs; no title/year/cardinality heuristic creates identity.
Every historically served JPEG basename is fetched and hashed in memory. A
current representation can become a strong recovery candidate only when every
observable historical position is byte-identical and every historical hole is
served as a valid JPEG. Source images are never persisted.
"""
from __future__ import annotations
import csv,hashlib,json,time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

VERSION='LTMD_U1_W11_EAM_OFFICIAL_REPRESENTATIONS_0.1'
OUTPUT_URL='https://libros.conaliteg.gob.mx/output.json'
UA='LibroTextoMexicanoDigital/U1-W11 EAM official comparator 0.1'
MAN=Path('data/catalog/ltmd_u1_w11_nonstandard_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w11_eam_official_representation_comparison.csv')
REPORT=Path('docs/LTMD_U1_W11_EAM_OFFICIAL_REPRESENTATION_COMPARISON.md')
TARGETS={
 'H2014P1EAM':{'code':'P1EAM','expected_source':48,'expected_holes':1},
 'H2014P2EAM':{'code':'P2EAM','expected_source':17,'expected_holes':2},
}

def fetch(url,attempts=3,cap=12_000_000):
    last=''
    for attempt in range(1,attempts+1):
        try:
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
                status=int(getattr(r,'status',200) or 200);ctype=r.headers.get('Content-Type','');data=r.read(cap+1)
            if len(data)>cap:raise RuntimeError(f'body exceeds {cap} byte cap')
            return status,ctype,data,''
        except HTTPError as exc:
            if exc.code in {404,410}:return exc.code,'',b'',f'HTTP {exc.code}'
            last=f'HTTPError {exc.code}'
        except (URLError,TimeoutError,OSError,RuntimeError) as exc:last=f'{type(exc).__name__}: {exc}'
        if attempt<attempts:time.sleep(attempt)
    return 0,'',b'',last

def basename(row):return Path(urlparse(row['source_asset_url']).path).name

def walk(obj,path=()):
    if isinstance(obj,dict):
        yield path,obj
        for k,v in obj.items():yield from walk(v,path+(str(k),))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from walk(v,path+(str(i),))

def candidate_configs(data,code):
    found={}
    for path,obj in walk(data):
        if not isinstance(obj,dict):continue
        ag=str(obj.get('ag_clave','')).strip()
        key_match=bool(path and path[-1]==code)
        if ag!=code and not key_match:continue
        pages=obj.get('ag_pages','')
        try:pages_i=int(pages)
        except (TypeError,ValueError):pages_i=0
        prefix=list(path[:-1]) if key_match else list(path)
        # output.json uses prefixes such as '.', '20', '2021', '2022'.
        clean=[p for p in prefix if p not in {'','.','./'} and not p.isdigit() is False]
        # Keep a numeric top-level version prefix only; nested non-version keys do
        # not become URL guesses.
        version=''
        for p in prefix:
            if p.isdigit() and len(p) in {2,4}:version=p;break
        base=(f'https://libros.conaliteg.gob.mx/{version}/c/{code}/' if version else f'https://libros.conaliteg.gob.mx/c/{code}/')
        label=version or 'root'
        found[(label,base,pages_i,'/'.join(path))]={'label':label,'base':base,'ag_pages':pages_i,'json_path':'/'.join(path)}
    return sorted(found.values(),key=lambda r:(r['label'],r['json_path']))

def compare_one(viewer,code,cfg,row):
    name=basename(row);url=cfg['base']+name;status,ctype,data,error=fetch(url)
    sha=hashlib.sha256(data).hexdigest() if data else '';magic=int(len(data)>=3 and data[:3]==b'\xff\xd8\xff')
    return {'comparison_version':VERSION,'viewer_key':viewer,'official_code':code,'candidate_label':cfg['label'],'candidate_base':cfg['base'],'official_ag_pages':cfg['ag_pages'],'official_json_path':cfg['json_path'],'viewer_page':row.get('viewer_page',''),'source_image_index':row.get('source_image_index',''),'historical_asset_status':row.get('asset_status',''),'historical_url':row.get('source_asset_url',''),'official_url':url,'http_status':status,'content_type':ctype,'byte_size':len(data),'jpeg_magic':magic,'historical_sha256':row.get('sha256',''),'official_sha256':sha,'sha256_match':int(bool(sha) and sha==row.get('sha256','')),'error':error}

def main():
    status,ctype,body,error=fetch(OUTPUT_URL,cap=20_000_000)
    if status!=200 or not body:raise SystemExit(f'cannot fetch official output.json: status={status} {error}')
    try:data=json.loads(body.decode('utf-8-sig'))
    except Exception as exc:raise SystemExit(f'invalid official output.json: {exc}')
    output_sha=hashlib.sha256(body).hexdigest()
    manifest=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    rows_out=[];summaries=[]
    for viewer,spec in TARGETS.items():
        rows=[r for r in manifest if r.get('viewer_key')==viewer]
        source=[r for r in rows if r.get('asset_status')=='source_jpeg'];holes=[r for r in rows if r.get('asset_status')=='internal_unserved']
        if len(source)!=spec['expected_source'] or len(holes)!=spec['expected_holes']:
            raise SystemExit(f'{viewer} historical contract mismatch source={len(source)} holes={len(holes)}')
        cfgs=candidate_configs(data,spec['code'])
        if not cfgs:
            summaries.append({'viewer':viewer,'code':spec['code'],'label':'none','base':'','ag_pages':0,'json_path':'','served':0,'matches':0,'errors':0,'holes_valid':0,'holes_total':len(holes),'strong':False,'state':'official_config_not_found'})
            continue
        # De-duplicate equivalent bases while retaining a representative path and
        # the maximum official cardinality observed for that base.
        bybase={}
        for c in cfgs:
            prev=bybase.get(c['base'])
            if prev is None or c['ag_pages']>prev['ag_pages']:bybase[c['base']]=c
        for cfg in sorted(bybase.values(),key=lambda c:c['base']):
            rr=[]
            with ThreadPoolExecutor(max_workers=4) as ex:
                futs=[ex.submit(compare_one,viewer,spec['code'],cfg,r) for r in source+holes]
                for fut in as_completed(futs):rr.append(fut.result())
            rr.sort(key=lambda r:(int(r['source_image_index']) if str(r['source_image_index']).isdigit() else 10**9,r['official_url']))
            observed=[r for r in rr if r['historical_asset_status']=='source_jpeg'];hole_rows=[r for r in rr if r['historical_asset_status']=='internal_unserved']
            served=sum(r['http_status']==200 and r['jpeg_magic']==1 for r in observed);matches=sum(int(r['sha256_match']) for r in observed);errors=sum(r['http_status']==0 for r in rr);holes_valid=sum(r['http_status']==200 and r['jpeg_magic']==1 and bool(r['official_sha256']) for r in hole_rows)
            strong=(served==len(source) and matches==len(source) and errors==0 and holes_valid==len(holes))
            state='strong_recovery_candidate' if strong else 'not_recoverable_by_exact_sequence'
            summaries.append({'viewer':viewer,'code':spec['code'],'label':cfg['label'],'base':cfg['base'],'ag_pages':cfg['ag_pages'],'json_path':cfg['json_path'],'served':served,'matches':matches,'errors':errors,'holes_valid':holes_valid,'holes_total':len(holes),'strong':strong,'state':state})
            rows_out.extend(rr)
    fields=['comparison_version','viewer_key','official_code','candidate_label','candidate_base','official_ag_pages','official_json_path','viewer_page','source_image_index','historical_asset_status','historical_url','official_url','http_status','content_type','byte_size','jpeg_magic','historical_sha256','official_sha256','sha256_match','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows_out)
    lines=['# LTMD-U1 W11 — comparación de representaciones oficiales EAM','',f'Versión: `{VERSION}`.','',f'- `output.json` oficial: `{OUTPUT_URL}`.',f'- SHA-256 del `output.json` observado: `{output_sha}`.','- Imágenes persistidas: **0**.','','## Resultado','','| visor | código | candidato | ag_pages | JPEG históricos servidos | SHA idénticos | huecos válidos | errores | estado |','|---|---|---|---:|---:|---:|---:|---:|---|']
    for s in summaries:
        exp=TARGETS[s['viewer']]['expected_source'];lines.append(f"| `{s['viewer']}` | `{s['code']}` | `{s['label']}` | {s['ag_pages']} | {s['served']}/{exp} | {s['matches']}/{exp} | {s['holes_valid']}/{s['holes_total']} | {s['errors']} | `{s['state']}` |")
    strong=[s for s in summaries if s['strong']]
    lines+=['',f'- Candidatos fuertes totales: **{len(strong)}**.','', '## Regla','','Una representación oficial sólo puede recuperar un visor retenido cuando todas las posiciones históricas observables coinciden byte a byte en la misma posición y todos los huecos exactos están servidos como JPEG válidos. La coincidencia de código corto, título, grado, cardinalidad o generación no basta. Un candidato fuerte no modifica automáticamente la compuerta W11: requiere actualización explícita de procedencia y recomputación de las capas afectadas.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
