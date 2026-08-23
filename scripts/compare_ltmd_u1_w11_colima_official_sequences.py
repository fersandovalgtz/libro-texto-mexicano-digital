#!/usr/bin/env python3
"""Compare H2014P3COL against bounded official CONALITEG P3COL representations.

Historical W11 manifest positions/hashes are authoritative. Candidate current
representations are derived only from official CONALITEG configuration/routes.
Every historically served basename is requested and hashed in memory; no image
is persisted. A candidate is strong only if all 160 observable historical JPEGs
are byte-identical position-by-position and the isolated missing basename is
served as a valid JPEG.
"""
from __future__ import annotations
import csv,hashlib,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

VERSION='LTMD_U1_W11_COLIMA_OFFICIAL_SEQUENCES_0.1'
UA='LibroTextoMexicanoDigital/U1-W11 Colima cryptographic comparator 0.1'
VIEWER='H2014P3COL';OFFICIAL_CODE='P3COL'
MAN=Path('data/catalog/ltmd_u1_w11_standard_asset_manifest.csv')
CONFIG=Path('data/catalog/ltmd_u1_conaliteg_output_config.csv')
OUT=Path('data/catalog/ltmd_u1_w11_colima_official_sequence_comparison.csv')
REPORT=Path('docs/LTMD_U1_W11_COLIMA_OFFICIAL_SEQUENCE_COMPARISON.md')
EXPECTED_SOURCE=160;EXPECTED_HOLES=1
CANDIDATES=[
 ('root','https://libros.conaliteg.gob.mx/c/P3COL/'),
 ('2022','https://libros.conaliteg.gob.mx/2022/c/P3COL/'),
 ('2021','https://libros.conaliteg.gob.mx/2021/c/P3COL/'),
 ('20','https://libros.conaliteg.gob.mx/20/c/P3COL/'),
]

def fetch(url,attempts=3):
    last=''
    for attempt in range(1,attempts+1):
        try:
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
                status=int(getattr(r,'status',200) or 200);ctype=r.headers.get('Content-Type','');data=r.read(8_000_001)
            if len(data)>8_000_000:raise RuntimeError('asset exceeds 8 MB safety cap')
            return status,ctype,data,''
        except HTTPError as exc:
            if exc.code in {404,410}:return exc.code,'',b'',f'HTTP {exc.code}'
            last=f'HTTPError {exc.code}'
        except (URLError,TimeoutError,OSError,RuntimeError) as exc:last=f'{type(exc).__name__}: {exc}'
        if attempt<attempts:time.sleep(attempt)
    return 0,'',b'',last

def basename(row):return Path(urlparse(row['source_asset_url']).path).name

def compare(candidate_label,base,row):
    name=basename(row);url=base+name;status,ctype,data,error=fetch(url)
    sha=hashlib.sha256(data).hexdigest() if data else ''
    magic=int(len(data)>=3 and data[:3]==b'\xff\xd8\xff')
    return {'comparison_version':VERSION,'viewer_key':VIEWER,'official_code':OFFICIAL_CODE,'candidate_label':candidate_label,'candidate_base':base,'viewer_page':row.get('viewer_page',''),'source_image_index':row.get('source_image_index',''),'asset_status_historical':row.get('asset_status',''),'historical_url':row.get('source_asset_url',''),'official_url':url,'http_status':status,'content_type':ctype,'byte_size':len(data),'jpeg_magic':magic,'historical_sha256':row.get('sha256',''),'official_sha256':sha,'sha256_match':int(bool(sha) and sha==row.get('sha256','')),'error':error}

def main():
    rows=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r.get('viewer_key')==VIEWER]
    source=[r for r in rows if r.get('asset_status')=='source_jpeg'];holes=[r for r in rows if r.get('asset_status')=='internal_unserved']
    if len(source)!=EXPECTED_SOURCE or len(holes)!=EXPECTED_HOLES:raise SystemExit(f'historical Colima contract mismatch source={len(source)} holes={len(holes)}')
    cfg=[r for r in csv.DictReader(CONFIG.open(encoding='utf-8',newline='')) if r.get('target_code')==OFFICIAL_CODE]
    pages=sorted({int(r['value']) for r in cfg if r.get('field')=='ag_pages' and r.get('value','').isdigit()})
    if not pages:raise SystemExit('official P3COL config has no ag_pages')
    hole=holes[0];results=[];summaries=[]
    for label,base in CANDIDATES:
        rr=[]
        with ThreadPoolExecutor(max_workers=4) as ex:
            futs={ex.submit(compare,label,base,r):r for r in source}
            for fut in as_completed(futs):rr.append(fut.result())
        candidate=compare(label,base,hole);candidate['asset_status_historical']='internal_unserved';rr.append(candidate)
        rr.sort(key=lambda r:(int(r['source_image_index']) if str(r['source_image_index']).isdigit() else 10**9,r['official_url']))
        observed=[r for r in rr if r['asset_status_historical']=='source_jpeg']
        served=sum(r['http_status']==200 and r['jpeg_magic']==1 for r in observed)
        matches=sum(int(r['sha256_match']) for r in observed)
        errors=sum(r['http_status']==0 for r in observed)
        hole_ok=candidate['http_status']==200 and candidate['jpeg_magic']==1 and bool(candidate['official_sha256'])
        strong=(served==EXPECTED_SOURCE and matches==EXPECTED_SOURCE and errors==0 and hole_ok)
        summaries.append({'label':label,'base':base,'served':served,'matches':matches,'errors':errors,'hole_ok':hole_ok,'hole_sha':candidate['official_sha256'],'strong':strong})
        results.extend(rr)
    fields=['comparison_version','viewer_key','official_code','candidate_label','candidate_base','viewer_page','source_image_index','asset_status_historical','historical_url','official_url','http_status','content_type','byte_size','jpeg_magic','historical_sha256','official_sha256','sha256_match','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
    strong=[s for s in summaries if s['strong']]
    state='single_strong_recovery_candidate' if len(strong)==1 else ('ambiguous_multiple_strong_candidates' if len(strong)>1 else 'not_recoverable_by_exact_sequence')
    lines=['# LTMD-U1 W11 — comparación criptográfica Colima histórico ↔ representaciones oficiales','',f'Versión: `{VERSION}`.','',f'- Visor histórico: `{VIEWER}`.',f'- Código oficial: `{OFFICIAL_CODE}`.',f'- Cardinalidades oficiales observadas en `output.json`: **{", ".join(map(str,pages))}**.',f'- Posiciones históricas servidas: **{EXPECTED_SOURCE}**.',f'- Hueco histórico: página **{hole.get("viewer_page","")}**, índice **{hole.get("source_image_index","")}**, archivo `{basename(hole)}`.','- Imágenes persistidas: **0**.','','## Candidatos','','| candidato | base oficial | JPEG servidos | SHA idénticos | errores transporte | hueco válido | estado fuerte |','|---|---|---:|---:|---:|---|---|']
    for s in summaries:lines.append(f"| `{s['label']}` | `{s['base']}` | {s['served']}/{EXPECTED_SOURCE} | {s['matches']}/{EXPECTED_SOURCE} | {s['errors']} | {'sí' if s['hole_ok'] else 'no'} | {'sí' if s['strong'] else 'no'} |")
    lines+=['',f'**Estado: `{state}`.**','']
    if len(strong)==1:lines += [f"Candidato fuerte único: `{strong[0]['label']}`; SHA-256 del cuerpo recuperado para el hueco: `{strong[0]['hole_sha']}`.",'']
    lines+=['## Regla','','Una representación sólo puede proponerse para recuperación si las 160 posiciones históricas observables son JPEG válidos y byte-idénticos en el mismo basename/posición, sin errores de transporte, y el hueco exacto existe como JPEG válido. La cardinalidad, la clave corta o el título nunca bastan. Incluso un candidato fuerte requiere una actualización explícita de procedencia y de la compuerta W11; no se sustituye silenciosamente la fuente histórica.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
