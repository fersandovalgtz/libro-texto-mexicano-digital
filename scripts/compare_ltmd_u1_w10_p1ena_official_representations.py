#!/usr/bin/env python3
"""Compare retained H2014P1ENA with current official CONALITEG P1ENA representations.

The historical W10 asset manifest is authoritative. Current output.json is
searched recursively only for P1ENA. Candidate asset bases are derived from
matching configuration paths; every historically served basename is fetched
and SHA-256 compared in memory. No source image is persisted. A representation
is strong only when all 168 observable historical JPEGs are byte-identical at
the same positions and the exact historical hole (114.jpg) is served.
"""
from __future__ import annotations
import csv,hashlib,json,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

VERSION='LTMD_U1_W10_P1ENA_OFFICIAL_REPRESENTATIONS_0.1'
VIEWER='H2014P1ENA';CODE='P1ENA';EXPECTED_SOURCE=168;EXPECTED_HOLES=1
OUTPUT_URL='https://libros.conaliteg.gob.mx/output.json';UA='LibroTextoMexicanoDigital/U1-W10 P1ENA comparator 0.1'
MAN=Path('data/catalog/ltmd_u1_w10_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w10_p1ena_official_representation_comparison.csv')
REPORT=Path('docs/LTMD_U1_W10_P1ENA_OFFICIAL_REPRESENTATION_COMPARISON.md')

def fetch(url,attempts=3,cap=20_000_000):
    last=''
    for attempt in range(1,attempts+1):
        try:
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
                status=int(getattr(r,'status',200) or 200);ctype=r.headers.get('Content-Type','');data=r.read(cap+1)
            if len(data)>cap:raise RuntimeError('body exceeds safety cap')
            return status,ctype,data,''
        except HTTPError as exc:
            if exc.code in {404,410}:return exc.code,'',b'',f'HTTP {exc.code}'
            last=f'HTTPError {exc.code}'
        except (URLError,TimeoutError,OSError,RuntimeError) as exc:last=f'{type(exc).__name__}: {exc}'
        if attempt<attempts:time.sleep(attempt)
    return 0,'',b'',last

def walk(obj,path=()):
    if isinstance(obj,dict):
        yield path,obj
        for k,v in obj.items():yield from walk(v,path+(str(k),))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from walk(v,path+(str(i),))

def configs(data):
    found={}
    for path,obj in walk(data):
        if not isinstance(obj,dict):continue
        ag=str(obj.get('ag_clave','')).strip();key_match=bool(path and path[-1]==CODE)
        if ag!=CODE and not key_match:continue
        try:pages=int(obj.get('ag_pages',0) or 0)
        except (TypeError,ValueError):pages=0
        prefix=list(path[:-1]) if key_match else list(path);version=''
        for p in prefix:
            if p.isdigit() and len(p) in {2,4}:version=p;break
        base=f'https://libros.conaliteg.gob.mx/{version}/c/{CODE}/' if version else f'https://libros.conaliteg.gob.mx/c/{CODE}/'
        rec={'label':version or 'root','base':base,'ag_pages':pages,'json_path':'/'.join(path)}
        prev=found.get(base)
        if prev is None or pages>prev['ag_pages']:found[base]=rec
    return sorted(found.values(),key=lambda r:r['base'])

def basename(r):return Path(urlparse(r['source_asset_url']).path).name

def compare(cfg,row):
    name=basename(row);url=cfg['base']+name;status,ctype,data,error=fetch(url);sha=hashlib.sha256(data).hexdigest() if data else '';magic=int(len(data)>=3 and data[:3]==b'\xff\xd8\xff')
    return {'comparison_version':VERSION,'viewer_key':VIEWER,'official_code':CODE,'candidate_label':cfg['label'],'candidate_base':cfg['base'],'official_ag_pages':cfg['ag_pages'],'official_json_path':cfg['json_path'],'viewer_page':row.get('viewer_page',''),'source_image_index':row.get('source_image_index',''),'historical_asset_status':row.get('asset_status',''),'historical_url':row.get('source_asset_url',''),'official_url':url,'http_status':status,'content_type':ctype,'byte_size':len(data),'jpeg_magic':magic,'historical_sha256':row.get('sha256',''),'official_sha256':sha,'sha256_match':int(bool(sha) and sha==row.get('sha256','')),'error':error}

def main():
    st,ct,body,err=fetch(OUTPUT_URL)
    if st!=200 or not body:raise SystemExit(f'official output.json unavailable: {st} {err}')
    data=json.loads(body.decode('utf-8-sig'));output_sha=hashlib.sha256(body).hexdigest()
    rows=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r.get('viewer_key')==VIEWER]
    source=[r for r in rows if r.get('asset_status')=='source_jpeg'];holes=[r for r in rows if r.get('asset_status')=='internal_unserved']
    if len(source)!=EXPECTED_SOURCE or len(holes)!=EXPECTED_HOLES:raise SystemExit(f'historical P1ENA contract mismatch source={len(source)} holes={len(holes)}')
    cfgs=configs(data);results=[];summaries=[]
    if not cfgs:summaries.append({'label':'none','base':'','ag_pages':0,'json_path':'','served':0,'matches':0,'errors':0,'hole_ok':False,'strong':False,'state':'official_config_not_found'})
    for cfg in cfgs:
        rr=[]
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs=[ex.submit(compare,cfg,r) for r in source+holes]
            for fut in as_completed(futs):rr.append(fut.result())
        rr.sort(key=lambda r:int(r['source_image_index']) if str(r['source_image_index']).isdigit() else 10**9)
        observed=[r for r in rr if r['historical_asset_status']=='source_jpeg'];hole=[r for r in rr if r['historical_asset_status']=='internal_unserved'][0]
        served=sum(r['http_status']==200 and r['jpeg_magic']==1 for r in observed);matches=sum(int(r['sha256_match']) for r in observed);errors=sum(r['http_status']==0 for r in rr);hole_ok=hole['http_status']==200 and hole['jpeg_magic']==1 and bool(hole['official_sha256']);strong=(served==EXPECTED_SOURCE and matches==EXPECTED_SOURCE and errors==0 and hole_ok)
        summaries.append({'label':cfg['label'],'base':cfg['base'],'ag_pages':cfg['ag_pages'],'json_path':cfg['json_path'],'served':served,'matches':matches,'errors':errors,'hole_ok':hole_ok,'strong':strong,'state':'strong_recovery_candidate' if strong else 'not_recoverable_by_exact_sequence'});results+=rr
    fields=['comparison_version','viewer_key','official_code','candidate_label','candidate_base','official_ag_pages','official_json_path','viewer_page','source_image_index','historical_asset_status','historical_url','official_url','http_status','content_type','byte_size','jpeg_magic','historical_sha256','official_sha256','sha256_match','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
    strong=[s for s in summaries if s['strong']];state='single_strong_recovery_candidate' if len(strong)==1 else ('ambiguous_multiple_strong_candidates' if len(strong)>1 else 'not_recoverable_by_exact_sequence')
    hole=holes[0];lines=['# LTMD-U1 W10 — comparación de representaciones oficiales P1ENA','',f'Versión: `{VERSION}`.','',f'- Visor histórico: `{VIEWER}`.',f'- Código oficial consultado: `{CODE}`.',f'- `output.json` SHA-256: `{output_sha}`.',f'- Posiciones históricas servidas: **{len(source)}**.',f'- Hueco histórico: página **{hole.get("viewer_page","")}**, índice **{hole.get("source_image_index","")}**, archivo `{basename(hole)}`.','- Imágenes persistidas: **0**.','','## Resultado','','| candidato | ag_pages | base | JPEG servidos | SHA idénticos | hueco válido | errores | estado |','|---|---:|---|---:|---:|---|---:|---|']
    for s in summaries:lines.append(f"| `{s['label']}` | {s['ag_pages']} | `{s['base'] or '—'}` | {s['served']}/{EXPECTED_SOURCE} | {s['matches']}/{EXPECTED_SOURCE} | {'sí' if s['hole_ok'] else 'no'} | {s['errors']} | `{s['state']}` |")
    lines+=['',f'**Estado global: `{state}`.**','', '## Regla','','La representación actual sólo puede recuperar `H2014P1ENA` si las 168 posiciones históricas observables coinciden byte a byte en posición y el hueco exacto `114.jpg` existe como JPEG válido. Código corto, título, ISBN, año, cardinalidad, OCR o semejanza visual no crean identidad. Un candidato fuerte requeriría todavía actualizar explícitamente procedencia, compuerta de fuente y sólo las capas downstream afectadas.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
