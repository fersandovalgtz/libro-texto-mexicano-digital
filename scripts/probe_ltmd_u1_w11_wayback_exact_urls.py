#!/usr/bin/env python3
"""Probe Internet Archive CDX for exact W11 retained source URLs.

Only the exact institutional URL and an http/https transport variant of the
same host+path are queried. This stage records capture metadata only; it never
downloads or substitutes source images. Each query receives an explicit log
row so archive timeouts remain distinguishable from a successful zero-result
query.
"""
from __future__ import annotations
import csv,json,time
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlencode,urlparse,urlunparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

HOLES=Path('data/catalog/ltmd_u1_w11_retained_source_holes.csv')
OUT=Path('data/catalog/ltmd_u1_w11_wayback_capture_candidates.csv')
QUERY_LOG=Path('data/catalog/ltmd_u1_w11_wayback_query_log.csv')
REPORT=Path('docs/LTMD_U1_W11_WAYBACK_PROBE.md')
VERSION='LTMD_U1_W11_WAYBACK_PROBE_0.2'
UA='LibroTextoMexicanoDigital/U1-W11 exact-source archive probe 0.2'
EXPECTED_HOLES=5
MAX_WORKERS=5
ATTEMPTS=2
TIMEOUT=25
FIELDS=['probe_version','viewer_key','viewer_page','source_image_index','query_role','queried_url','timestamp','original','statuscode','mimetype','digest','length']
QUERY_FIELDS=['probe_version','viewer_key','viewer_page','source_image_index','query_role','queried_url','query_state','attempts_used','capture_count','error']

def transport_http(url:str)->str:
    p=urlparse(url)
    return urlunparse(('http',p.netloc,p.path,p.params,p.query,p.fragment))

def cdx(url:str)->tuple[list[dict[str,str]],int,str]:
    qs=urlencode({'url':url,'output':'json','filter':'statuscode:200','fl':'timestamp,original,statuscode,mimetype,digest,length','collapse':'digest'})
    endpoint='https://web.archive.org/cdx/search/cdx?'+qs
    last=''
    for attempt in range(1,ATTEMPTS+1):
        try:
            with urlopen(Request(endpoint,headers={'User-Agent':UA}),timeout=TIMEOUT) as r:
                raw=r.read().decode('utf-8','replace')
            data=json.loads(raw)
            if not data:return [],attempt,''
            header=data[0]
            return [dict(zip(header,row)) for row in data[1:]],attempt,''
        except (HTTPError,URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:
            last=f'{type(exc).__name__}: {exc}'
            if attempt<ATTEMPTS:time.sleep(attempt)
    return [],ATTEMPTS,last

def one_query(h:dict[str,str],role:str,url:str)->tuple[list[dict[str,str]],dict[str,str]]:
    captures,attempts,error=cdx(url)
    state='error' if error else ('success_capture' if captures else 'success_no_capture')
    q={'probe_version':VERSION,'viewer_key':h['viewer_key'],'viewer_page':h['viewer_page'],'source_image_index':h['source_image_index'],'query_role':role,'queried_url':url,'query_state':state,'attempts_used':attempts,'capture_count':len(captures),'error':error}
    rows=[]
    for c in captures:
        rows.append({'probe_version':VERSION,'viewer_key':h['viewer_key'],'viewer_page':h['viewer_page'],'source_image_index':h['source_image_index'],'query_role':role,'queried_url':url,'timestamp':c.get('timestamp',''),'original':c.get('original',''),'statuscode':c.get('statuscode',''),'mimetype':c.get('mimetype',''),'digest':c.get('digest',''),'length':c.get('length','')})
    return rows,q

def main()->None:
    holes=list(csv.DictReader(HOLES.open(encoding='utf-8',newline='')))
    if len(holes)!=EXPECTED_HOLES:raise SystemExit(f'expected {EXPECTED_HOLES} retained holes, got {len(holes)}')
    jobs=[]
    for h in holes:
        exact=h['source_asset_url'];jobs.append((h,'exact_https',exact))
        http=transport_http(exact)
        if http!=exact:jobs.append((h,'http_transport_variant',http))
    if len(jobs)!=EXPECTED_HOLES*2:raise SystemExit(f'unexpected W11 Wayback query cardinality: {len(jobs)}')
    rows=[];query_log=[]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures={ex.submit(one_query,*job):job for job in jobs}
        for fut in as_completed(futures):
            rr,q=fut.result();rows.extend(rr);query_log.append(q)
    rows.sort(key=lambda r:(r['viewer_key'],int(r['viewer_page']),r['query_role'],r['timestamp'],r['digest']))
    query_log.sort(key=lambda r:(r['viewer_key'],int(r['viewer_page']),r['query_role']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    with QUERY_LOG.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=QUERY_FIELDS);w.writeheader();w.writerows(query_log)
    by=defaultdict(list)
    for r in rows:by[(r['viewer_key'],r['viewer_page'])].append(r)
    role_counts=Counter(r['query_role'] for r in rows);state_counts=Counter(r['query_state'] for r in query_log)
    holes_with=sum(bool(by[(h['viewer_key'],h['viewer_page'])]) for h in holes)
    lines=['# LTMD-U1 W11 — sondeo archivístico de URLs fuente retenidas','',f'Versión: `{VERSION}`.','',
           f'- Huecos consultados: **{len(holes)}/{EXPECTED_HOLES}**.',f'- Consultas exactas/transportes ejecutadas: **{len(query_log)}/{len(jobs)}**.',
           f'- Huecos con ≥1 captura CDX 200: **{holes_with}/{EXPECTED_HOLES}**.',f'- Registros de captura únicos por digest/consulta: **{len(rows)}**.',
           f'- Consultas concluyentes sin captura: **{state_counts["success_no_capture"]}**.',f'- Consultas fallidas tras reintentos: **{state_counts["error"]}**.','','## Resultado por posición','','| viewer | página | índice | capturas | primera | última | roles |','|---|---:|---:|---:|---|---|---|']
    for h in holes:
        rr=by[(h['viewer_key'],h['viewer_page'])];ts=sorted(r['timestamp'] for r in rr if r['timestamp']);roles=sorted({r['query_role'] for r in rr})
        lines.append(f"| `{h['viewer_key']}` | {h['viewer_page']} | {h['source_image_index']} | {len(rr)} | {ts[0] if ts else '—'} | {ts[-1] if ts else '—'} | {', '.join(roles) if roles else '—'} |")
    if role_counts:
        lines+=['','## Registros de captura por tipo de consulta']
        for role,n in sorted(role_counts.items()):lines.append(f'- `{role}`: **{n}**.')
    errors=[r for r in query_log if r['query_state']=='error']
    if errors:
        lines+=['','## Consultas no concluyentes']
        for r in errors:lines.append(f"- `{r['viewer_key']}` página {r['viewer_page']}, `{r['query_role']}` — `{r['error']}`.")
    lines+=['','## Regla','',
            'Una captura CDX sólo demuestra que Internet Archive indexó una respuesta 200 para la misma ruta institucional (o su variante de transporte HTTP). No demuestra todavía que el cuerpo archivado sea un JPEG válido ni autoriza su incorporación. Cualquier candidato debe verificarse temporalmente por firma JPEG, tamaño, SHA-256 y digest CDX, conservando timestamp, URL original y procedencia archivística. No se consultan páginas de otros libros como sustitutos.','',
            'El log de consultas distingue `success_no_capture` de `error`: un timeout o fallo del servicio no se interpreta como ausencia de captura. La ausencia concluyente en este sondeo sigue siendo un resultado negativo acotado, no prueba de inexistencia de otras copias.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
