#!/usr/bin/env python3
"""Probe Internet Archive CDX for exact W11 retained source URLs.

Only the exact institutional URL and an http/https transport variant of the
same host+path are queried. This stage records capture metadata only; it never
downloads or substitutes source images.
"""
from __future__ import annotations
import csv,json,time
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlencode,urlparse,urlunparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

HOLES=Path('data/catalog/ltmd_u1_w11_retained_source_holes.csv')
OUT=Path('data/catalog/ltmd_u1_w11_wayback_capture_candidates.csv')
REPORT=Path('docs/LTMD_U1_W11_WAYBACK_PROBE.md')
VERSION='LTMD_U1_W11_WAYBACK_PROBE_0.1'
UA='LibroTextoMexicanoDigital/U1-W11 exact-source archive probe 0.1'
EXPECTED_HOLES=5
FIELDS=['probe_version','viewer_key','viewer_page','source_image_index','query_role','queried_url','timestamp','original','statuscode','mimetype','digest','length']

def transport_http(url:str)->str:
    p=urlparse(url)
    return urlunparse(('http',p.netloc,p.path,p.params,p.query,p.fragment))

def cdx(url:str,attempts:int=3)->list[dict[str,str]]:
    qs=urlencode({'url':url,'output':'json','filter':'statuscode:200','fl':'timestamp,original,statuscode,mimetype,digest,length','collapse':'digest'})
    endpoint='https://web.archive.org/cdx/search/cdx?'+qs
    last=''
    for attempt in range(1,attempts+1):
        try:
            with urlopen(Request(endpoint,headers={'User-Agent':UA}),timeout=60) as r:
                raw=r.read().decode('utf-8','replace')
            data=json.loads(raw)
            if not data:return []
            header=data[0]
            return [dict(zip(header,row)) for row in data[1:]]
        except (HTTPError,URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:
            last=f'{type(exc).__name__}: {exc}'
            if attempt<attempts:time.sleep(attempt*2)
    raise RuntimeError(f'CDX probe failed for {url}: {last}')

def main()->None:
    holes=list(csv.DictReader(HOLES.open(encoding='utf-8',newline='')))
    if len(holes)!=EXPECTED_HOLES:raise SystemExit(f'expected {EXPECTED_HOLES} retained holes, got {len(holes)}')
    rows=[];query_failures=[]
    for h in holes:
        exact=h['source_asset_url'];queries=[('exact_https',exact)]
        http=transport_http(exact)
        if http!=exact:queries.append(('http_transport_variant',http))
        for role,url in queries:
            try:captures=cdx(url)
            except Exception as exc:
                query_failures.append((h['viewer_key'],h['viewer_page'],role,str(exc)));continue
            for c in captures:
                rows.append({'probe_version':VERSION,'viewer_key':h['viewer_key'],'viewer_page':h['viewer_page'],'source_image_index':h['source_image_index'],'query_role':role,'queried_url':url,'timestamp':c.get('timestamp',''),'original':c.get('original',''),'statuscode':c.get('statuscode',''),'mimetype':c.get('mimetype',''),'digest':c.get('digest',''),'length':c.get('length','')})
    rows.sort(key=lambda r:(r['viewer_key'],int(r['viewer_page']),r['query_role'],r['timestamp'],r['digest']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    by=defaultdict(list)
    for r in rows:by[(r['viewer_key'],r['viewer_page'])].append(r)
    role_counts=Counter(r['query_role'] for r in rows);holes_with=sum(bool(by[(h['viewer_key'],h['viewer_page'])]) for h in holes)
    lines=['# LTMD-U1 W11 — sondeo archivístico de URLs fuente retenidas','',f'Versión: `{VERSION}`.','',
           f'- Huecos consultados: **{len(holes)}/{EXPECTED_HOLES}**.',f'- Huecos con ≥1 captura CDX 200: **{holes_with}/{EXPECTED_HOLES}**.',
           f'- Registros de captura únicos por digest/consulta: **{len(rows)}**.',f'- Consultas fallidas tras reintentos: **{len(query_failures)}**.','','## Resultado por posición','','| viewer | página | índice | capturas | primera | última | roles |','|---|---:|---:|---:|---|---|---|']
    for h in holes:
        rr=by[(h['viewer_key'],h['viewer_page'])];ts=sorted(r['timestamp'] for r in rr if r['timestamp']);roles=sorted({r['query_role'] for r in rr})
        lines.append(f"| `{h['viewer_key']}` | {h['viewer_page']} | {h['source_image_index']} | {len(rr)} | {ts[0] if ts else '—'} | {ts[-1] if ts else '—'} | {', '.join(roles) if roles else '—'} |")
    if role_counts:
        lines+=['','## Registros por tipo de consulta']
        for role,n in sorted(role_counts.items()):lines.append(f'- `{role}`: **{n}**.')
    if query_failures:
        lines+=['','## Consultas no concluyentes']
        for key,page,role,error in query_failures:lines.append(f'- `{key}` página {page}, `{role}` — `{error}`.')
    lines+=['','## Regla','',
            'Una captura CDX sólo demuestra que Internet Archive indexó una respuesta 200 para la misma ruta institucional (o su variante de transporte HTTP). No demuestra todavía que el cuerpo archivado sea un JPEG válido ni autoriza su incorporación. Cualquier candidato deberá descargarse de forma temporal desde la captura identificada, verificarse por tipo/tamaño/SHA-256 y conservar timestamp, URL original y procedencia archivística. No se consultan páginas de otros libros como sustitutos.','',
            'La ausencia de captura en este sondeo se conserva como resultado negativo acotado; no prueba que nunca haya existido otra copia fuera de los índices consultados.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
