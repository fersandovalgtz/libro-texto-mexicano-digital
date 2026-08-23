#!/usr/bin/env python3
"""Cryptographically compare H2014P3MOR with official current P3MOR assets.

The historical manifest is authoritative for positions and hashes. For each
historically served JPEG, the exact basename is requested from the official
current P3MOR route. Bytes are held only in memory long enough to hash them.
No image is persisted. The isolated historical hole is fetched only as a
recovery candidate after the observed-sequence comparison is defined.
"""
from __future__ import annotations
import csv,hashlib,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

VERSION='LTMD_U1_W11_MORELOS_OFFICIAL_SEQUENCE_0.1'
UA='LibroTextoMexicanoDigital/U1-W11 Morelos cryptographic comparator 0.1'
VIEWER='H2014P3MOR';OFFICIAL_CODE='P3MOR';BASE='https://libros.conaliteg.gob.mx/c/P3MOR/'
MAN=Path('data/catalog/ltmd_u1_w11_standard_asset_manifest.csv')
CONFIG=Path('data/catalog/ltmd_u1_conaliteg_output_config.csv')
OUT=Path('data/catalog/ltmd_u1_w11_morelos_official_sequence_comparison.csv')
REPORT=Path('docs/LTMD_U1_W11_MORELOS_OFFICIAL_SEQUENCE_COMPARISON.md')
EXPECTED_SOURCE=160;EXPECTED_HOLES=1;EXPECTED_PAGES=162

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

def basename(row):
    path=urlparse(row['source_asset_url']).path
    return Path(path).name

def compare(row):
    name=basename(row);url=BASE+name;status,ctype,data,error=fetch(url)
    sha=hashlib.sha256(data).hexdigest() if data else ''
    magic=int(len(data)>=3 and data[:3]==b'\xff\xd8\xff')
    return {'comparison_version':VERSION,'viewer_key':VIEWER,'official_code':OFFICIAL_CODE,'viewer_page':row.get('viewer_page',''),'source_image_index':row.get('source_image_index',''),'asset_status_historical':row.get('asset_status',''),'historical_url':row.get('source_asset_url',''),'official_url':url,'http_status':status,'content_type':ctype,'byte_size':len(data),'jpeg_magic':magic,'historical_sha256':row.get('sha256',''),'official_sha256':sha,'sha256_match':int(bool(sha) and sha==row.get('sha256','')),'error':error}

def main():
    rows=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r.get('viewer_key')==VIEWER]
    source=[r for r in rows if r.get('asset_status')=='source_jpeg'];holes=[r for r in rows if r.get('asset_status')=='internal_unserved']
    if len(source)!=EXPECTED_SOURCE or len(holes)!=EXPECTED_HOLES:raise SystemExit(f'historical Morelos contract mismatch source={len(source)} holes={len(holes)}')
    cfg=[r for r in csv.DictReader(CONFIG.open(encoding='utf-8',newline='')) if r.get('target_code')==OFFICIAL_CODE and r.get('field')=='ag_pages']
    pages={int(r['value']) for r in cfg if r.get('value','').isdigit()}
    if EXPECTED_PAGES not in pages:raise SystemExit(f'official P3MOR ag_pages mismatch: {sorted(pages)}')
    results=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs={ex.submit(compare,r):r for r in source}
        for fut in as_completed(futs):results.append(fut.result())
    # Fetch the exact isolated hole as candidate, but do not count it as a match.
    hole=holes[0];candidate=compare(hole);candidate['asset_status_historical']='internal_unserved'
    results.append(candidate)
    results.sort(key=lambda r:(int(r['source_image_index']) if str(r['source_image_index']).isdigit() else 10**9,r['official_url']))
    fields=['comparison_version','viewer_key','official_code','viewer_page','source_image_index','asset_status_historical','historical_url','official_url','http_status','content_type','byte_size','jpeg_magic','historical_sha256','official_sha256','sha256_match','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
    observed=[r for r in results if r['asset_status_historical']=='source_jpeg'];matches=sum(int(r['sha256_match']) for r in observed);served=sum(r['http_status']==200 and r['jpeg_magic']==1 for r in observed)
    cand_ok=candidate['http_status']==200 and candidate['jpeg_magic']==1 and bool(candidate['official_sha256'])
    state='recovery_candidate_strong' if matches==EXPECTED_SOURCE and served==EXPECTED_SOURCE and cand_ok else 'not_recoverable_by_exact_sequence'
    lines=['# LTMD-U1 W11 — comparación criptográfica Morelos histórico ↔ representación oficial','',f'Versión: `{VERSION}`.','',
      f'- Visor histórico: `{VIEWER}`.',f'- Representación oficial comparada: `{OFFICIAL_CODE}`.',f'- Cardinalidad oficial declarada: **{EXPECTED_PAGES}**.',f'- Posiciones históricas servidas comparadas: **{len(observed)}**.',f'- JPEG oficiales recuperados en posiciones observables: **{served}/{EXPECTED_SOURCE}**.',f'- SHA-256 idénticos posición por posición: **{matches}/{EXPECTED_SOURCE}**.',f'- Hueco histórico: página **{hole.get("viewer_page","")}**, índice **{hole.get("source_image_index","")}**, archivo `{basename(hole)}`.',f'- Cuerpo oficial para el hueco: **{"sí" if cand_ok else "no"}**.',f'- SHA-256 candidato: `{candidate["official_sha256"] or "—"}`.','- Imágenes persistidas: **0**.','',f'**Estado: `{state}`.**','',
      '## Regla','',
      'La recuperación sólo puede avanzar si las 160 posiciones históricas observables son byte-idénticas en el mismo basename/posición y la página faltante existe como JPEG válido en la misma representación oficial. Cualquier divergencia conserva la retención. Incluso un resultado fuerte debe actualizar procedencia y compuertas W11 de forma explícita; no se sustituye silenciosamente la fuente histórica.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
