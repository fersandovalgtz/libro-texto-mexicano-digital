#!/usr/bin/env python3
"""Audit exact recovery evidence for W7 H2014P5FCA page 104.

Two bounded evidence channels are tested:
1) current official CONALITEG P5FCA representations discovered recursively in
   output.json and compared byte-for-byte against all 224 historical JPEGs;
2) Wayback CDX for the exact historical 104.jpg URL and its HTTP transport
   variant.
No source image is persisted. A current official representation is a strong
candidate only if all 224 observable historical positions match SHA-256 in the
same basename/position and the exact missing 104.jpg is served as JPEG.
"""
from __future__ import annotations
import csv,hashlib,json,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

VERSION='LTMD_U1_W7_H2014P5FCA_RECOVERY_AUDIT_0.1'
VIEWER='H2014P5FCA';CODE='P5FCA';EXPECTED_SOURCE=224;EXPECTED_HOLES=1
MAN=Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w7_h2014p5fca_recovery_audit.csv')
REPORT=Path('docs/LTMD_U1_W7_H2014P5FCA_RECOVERY_AUDIT.md')
OUTPUT_URL='https://libros.conaliteg.gob.mx/output.json'
WAYBACK='https://web.archive.org/cdx/search/cdx'
HIST_HOLE='https://historico.conaliteg.gob.mx/c/H2014P5FCA/104.jpg'
UA='LibroTextoMexicanoDigital/U1-W7 H2014P5FCA recovery audit 0.1'

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
    return {'record_type':'official_position','audit_version':VERSION,'viewer_key':VIEWER,'candidate_label':cfg['label'],'candidate_base':cfg['base'],'official_ag_pages':cfg['ag_pages'],'official_json_path':cfg['json_path'],'viewer_page':row.get('viewer_page',''),'source_image_index':row.get('source_image_index',''),'historical_asset_status':row.get('asset_status',''),'historical_url':row.get('source_asset_url',''),'probe_url':url,'http_status':status,'content_type':ctype,'byte_size':len(data),'jpeg_magic':magic,'historical_sha256':row.get('sha256',''),'observed_sha256':sha,'sha256_match':int(bool(sha) and sha==row.get('sha256','')),'query_state':'','capture_count':'','error':error}

def wayback(role,url,attempts=3):
    endpoint=WAYBACK+'?'+urlencode({'url':url,'output':'json','fl':'timestamp,original,statuscode,mimetype,digest,length','filter':'statuscode:200','collapse':'digest'},doseq=True);last=''
    for attempt in range(1,attempts+1):
        try:
            with urlopen(Request(endpoint,headers={'User-Agent':UA}),timeout=25) as r:obj=json.loads(r.read().decode('utf-8','replace'))
            captures=obj[1:] if isinstance(obj,list) and obj and isinstance(obj[0],list) else []
            return {'record_type':'wayback_query','audit_version':VERSION,'viewer_key':VIEWER,'candidate_label':role,'candidate_base':'','official_ag_pages':'','official_json_path':'','viewer_page':'104','source_image_index':'104','historical_asset_status':'internal_unserved','historical_url':HIST_HOLE,'probe_url':url,'http_status':'','content_type':'','byte_size':'','jpeg_magic':'','historical_sha256':'','observed_sha256':'','sha256_match':'','query_state':'success_capture' if captures else 'success_no_capture','capture_count':len(captures),'error':''}
        except (HTTPError,URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:
            last=f'{type(exc).__name__}: {exc}'
            if attempt<attempts:time.sleep(attempt)
    return {'record_type':'wayback_query','audit_version':VERSION,'viewer_key':VIEWER,'candidate_label':role,'candidate_base':'','official_ag_pages':'','official_json_path':'','viewer_page':'104','source_image_index':'104','historical_asset_status':'internal_unserved','historical_url':HIST_HOLE,'probe_url':url,'http_status':'','content_type':'','byte_size':'','jpeg_magic':'','historical_sha256':'','observed_sha256':'','sha256_match':'','query_state':'error','capture_count':0,'error':last}

def main():
    rows=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r.get('viewer_key')==VIEWER]
    source=[r for r in rows if r.get('asset_status')=='source_jpeg'];holes=[r for r in rows if r.get('asset_status')=='internal_unserved']
    if len(source)!=EXPECTED_SOURCE or len(holes)!=EXPECTED_HOLES:raise SystemExit(f'historical contract mismatch source={len(source)} holes={len(holes)}')
    if basename(holes[0])!='104.jpg':raise SystemExit(f'unexpected hole basename {basename(holes[0])}')
    st,ct,body,err=fetch(OUTPUT_URL)
    if st!=200 or not body:raise SystemExit(f'official output.json unavailable: {st} {err}')
    data=json.loads(body.decode('utf-8-sig'));output_sha=hashlib.sha256(body).hexdigest();cfgs=configs(data)
    out=[];summaries=[]
    if not cfgs:summaries.append({'label':'none','base':'','ag_pages':0,'served':0,'matches':0,'errors':0,'hole_ok':False,'strong':False,'state':'official_config_not_found'})
    for cfg in cfgs:
        rr=[]
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs=[ex.submit(compare,cfg,r) for r in source+holes]
            for fut in as_completed(futs):rr.append(fut.result())
        observed=[r for r in rr if r['historical_asset_status']=='source_jpeg'];hole=[r for r in rr if r['historical_asset_status']=='internal_unserved'][0]
        served=sum(r['http_status']==200 and r['jpeg_magic']==1 for r in observed);matches=sum(int(r['sha256_match']) for r in observed);errors=sum(r['http_status']==0 for r in rr);hole_ok=hole['http_status']==200 and hole['jpeg_magic']==1 and bool(hole['observed_sha256']);strong=(served==EXPECTED_SOURCE and matches==EXPECTED_SOURCE and errors==0 and hole_ok)
        summaries.append({'label':cfg['label'],'base':cfg['base'],'ag_pages':cfg['ag_pages'],'served':served,'matches':matches,'errors':errors,'hole_ok':hole_ok,'strong':strong,'state':'strong_recovery_candidate' if strong else 'not_recoverable_by_exact_sequence'});out+=rr
    wb=[]
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs=[ex.submit(wayback,'https_exact',HIST_HOLE),ex.submit(wayback,'http_transport',HIST_HOLE.replace('https://','http://',1))]
        for fut in as_completed(futs):wb.append(fut.result())
    out+=wb
    fields=['record_type','audit_version','viewer_key','candidate_label','candidate_base','official_ag_pages','official_json_path','viewer_page','source_image_index','historical_asset_status','historical_url','probe_url','http_status','content_type','byte_size','jpeg_magic','historical_sha256','observed_sha256','sha256_match','query_state','capture_count','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    strong=[s for s in summaries if s['strong']];wb_errors=sum(r['query_state']=='error' for r in wb);wb_captures=sum(int(r['capture_count']) for r in wb);wb_no=sum(r['query_state']=='success_no_capture' for r in wb)
    state='single_strong_recovery_candidate' if len(strong)==1 else ('ambiguous_multiple_strong_candidates' if len(strong)>1 else 'retention_supported_no_exact_recovery')
    lines=['# LTMD-U1 W7 — auditoría de recuperación H2014P5FCA','',f'Versión: `{VERSION}`.','',f'- Visor: `{VIEWER}`.',f'- Código oficial vigente: `{CODE}`.',f'- `output.json` SHA-256 observado: `{output_sha}`.',f'- JPEG históricos observables: **{len(source)}**.',f'- Hueco histórico exacto: **104.jpg**.','- Imágenes persistidas: **0**.','','## Representaciones oficiales','','| candidato | ag_pages | base | JPEG servidos | SHA idénticos | 104.jpg válido | errores | estado |','|---|---:|---|---:|---:|---|---:|---|']
    for s in summaries:lines.append(f"| `{s['label']}` | {s['ag_pages']} | `{s['base'] or '—'}` | {s['served']}/{EXPECTED_SOURCE} | {s['matches']}/{EXPECTED_SOURCE} | {'sí' if s['hole_ok'] else 'no'} | {s['errors']} | `{s['state']}` |")
    lines+=['','## Wayback exacto',f'- Consultas: **{len(wb)}/2**.',f'- Concluyentes sin captura: **{wb_no}**.',f'- Capturas CDX 200: **{wb_captures}**.',f'- Fallos de consulta: **{wb_errors}**.','',f'**Estado global: `{state}`.**','', '## Regla','','`H2014P5FCA` sólo puede abandonar la retención si una representación institucional/archivística demuestra correspondencia posicional suficiente. Para la representación oficial actual se exige 224/224 SHA-256 idénticos y `104.jpg` válido. La ausencia en Wayback cierra únicamente esa vía archivística exacta; un error de consulta no cuenta como ausencia. Título, clave, grado, año, cardinalidad u OCR no crean identidad.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
