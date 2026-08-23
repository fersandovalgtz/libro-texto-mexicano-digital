#!/usr/bin/env python3
"""Verify Wayback bodies for exact W11 retained-source capture candidates.

Archived images are streamed into memory only long enough to compute integrity
metadata; no source image is written to the repository or retained on disk.
A capture is technically verified only when replay returns a JPEG body and its
SHA-1/Base32 matches the CDX digest when that digest is available.
"""
from __future__ import annotations
import base64,csv,hashlib,time
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

CAND=Path('data/catalog/ltmd_u1_w11_wayback_capture_candidates.csv')
HOLES=Path('data/catalog/ltmd_u1_w11_retained_source_holes.csv')
OUT=Path('data/catalog/ltmd_u1_w11_wayback_verified_candidates.csv')
REPORT=Path('docs/LTMD_U1_W11_WAYBACK_VERIFICATION.md')
VERSION='LTMD_U1_W11_WAYBACK_VERIFY_0.1'
UA='LibroTextoMexicanoDigital/U1-W11 archived-body verifier 0.1'
FIELDS=['verification_version','viewer_key','viewer_page','source_image_index','query_role','timestamp','original','cdx_digest','cdx_length','replay_url','http_status','content_type','byte_size','sha256','sha1_base32','jpeg_magic','cdx_digest_match','verified_body','error']

def replay_url(ts:str,original:str)->str:
    return f'https://web.archive.org/web/{ts}id_/{original}'

def fetch(url:str,attempts:int=3)->tuple[int,str,bytes,str]:
    last=''
    for attempt in range(1,attempts+1):
        try:
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=90) as r:
                status=getattr(r,'status',0);ctype=r.headers.get('Content-Type','');data=r.read()
            return int(status or 0),ctype,data,''
        except HTTPError as exc:
            if exc.code in {404,410}:return exc.code,exc.headers.get('Content-Type','') if exc.headers else '',b'',f'HTTP {exc.code}'
            last=f'HTTPError {exc.code}'
        except (URLError,TimeoutError,OSError) as exc:last=f'{type(exc).__name__}: {exc}'
        if attempt<attempts:time.sleep(attempt*2)
    return 0,'',b'',last

def main()->None:
    if not CAND.exists() or not HOLES.exists():raise SystemExit('missing W11 Wayback verification prerequisites')
    candidates=list(csv.DictReader(CAND.open(encoding='utf-8',newline='')));holes=list(csv.DictReader(HOLES.open(encoding='utf-8',newline='')))
    hole_keys={(r['viewer_key'],r['viewer_page']) for r in holes}
    rows=[]
    for c in candidates:
        key=(c['viewer_key'],c['viewer_page'])
        if key not in hole_keys:raise SystemExit(f'Wayback candidate outside retained holes: {key}')
        url=replay_url(c['timestamp'],c['original']);status,ctype,data,error=fetch(url)
        sha256=hashlib.sha256(data).hexdigest() if data else ''
        sha1b32=base64.b32encode(hashlib.sha1(data).digest()).decode('ascii').rstrip('=') if data else ''
        magic=int(len(data)>=3 and data[:3]==b'\xff\xd8\xff')
        digest=(c.get('digest') or '').strip().upper();match=int(bool(data) and (not digest or sha1b32.upper()==digest))
        verified=int(status==200 and magic==1 and len(data)>0 and match==1)
        rows.append({'verification_version':VERSION,'viewer_key':c['viewer_key'],'viewer_page':c['viewer_page'],'source_image_index':c['source_image_index'],'query_role':c['query_role'],'timestamp':c['timestamp'],'original':c['original'],'cdx_digest':c.get('digest',''),'cdx_length':c.get('length',''),'replay_url':url,'http_status':status,'content_type':ctype,'byte_size':len(data),'sha256':sha256,'sha1_base32':sha1b32,'jpeg_magic':magic,'cdx_digest_match':match,'verified_body':verified,'error':error})
    rows.sort(key=lambda r:(r['viewer_key'],int(r['viewer_page']),r['sha256'],r['timestamp'],r['query_role']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    by=defaultdict(list)
    for r in rows:by[(r['viewer_key'],r['viewer_page'])].append(r)
    lines=['# LTMD-U1 W11 — verificación de cuerpos archivados','',f'Versión: `{VERSION}`.','',f'- Capturas candidatas recibidas: **{len(candidates)}**.',f'- Cuerpos archivados verificados: **{sum(int(r["verified_body"]) for r in rows)}**.',f'- Imágenes fuente persistidas: **0**.','','## Estado por hueco','','| viewer | página | capturas | verificadas | SHA-256 verificados distintos | estado |','|---|---:|---:|---:|---:|---|']
    recoverable=0
    for h in holes:
        key=(h['viewer_key'],h['viewer_page']);rr=by[key];ok=[r for r in rr if r['verified_body']=='1'];hashes={r['sha256'] for r in ok};state='no_verified_capture'
        if len(hashes)==1 and ok:state='single_verified_archived_body';recoverable+=1
        elif len(hashes)>1:state='archived_version_ambiguity'
        lines.append(f"| `{h['viewer_key']}` | {h['viewer_page']} | {len(rr)} | {len(ok)} | {len(hashes)} | `{state}` |")
    lines+=['',f'- Huecos con exactamente un cuerpo archivado verificable por hash: **{recoverable}/{len(holes)}**.','','## Regla','',
            'Este resultado todavía no altera la admisibilidad W11. `single_verified_archived_body` significa que todas las capturas verificadas de esa posición convergen en un único SHA-256 y que el cuerpo recuperado es JPEG con digest CDX coherente; la incorporación requiere una revisión de procedencia que preserve URL institucional original, timestamp de captura y URL de replay. `archived_version_ambiguity` bloquea la recuperación automática.','',
            'Las imágenes archivadas se usan de forma temporal para verificación y no se incorporan a Git.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
