#!/usr/bin/env python3
"""Probe Wayback CDX only for the exact retained P1ENA source URL and HTTP variant."""
from __future__ import annotations
import csv,json,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

VERSION='LTMD_U1_W10_P1ENA_WAYBACK_PROBE_0.1'
HTTPS='https://historico.conaliteg.gob.mx/c/H2014P1ENA/114.jpg'
URLS=[('https_exact',HTTPS),('http_transport',HTTPS.replace('https://','http://',1))]
CDX='https://web.archive.org/cdx/search/cdx'
UA='LibroTextoMexicanoDigital/U1-W10 P1ENA Wayback probe 0.1'
OUT=Path('data/catalog/ltmd_u1_w10_p1ena_wayback_probe.csv')
REPORT=Path('docs/LTMD_U1_W10_P1ENA_WAYBACK_PROBE.md')

def query(role,url,attempts=3):
    params={'url':url,'output':'json','fl':'timestamp,original,statuscode,mimetype,digest,length','filter':['statuscode:200'],'collapse':'digest','from':'1996','to':'2026'}
    # urllib.urlencode needs doseq for repeated filter parameters.
    endpoint=CDX+'?'+urlencode(params,doseq=True);last=''
    for attempt in range(1,attempts+1):
        try:
            req=Request(endpoint,headers={'User-Agent':UA})
            with urlopen(req,timeout=25) as r:data=r.read().decode('utf-8','replace')
            obj=json.loads(data)
            rows=obj[1:] if isinstance(obj,list) and obj and isinstance(obj[0],list) else []
            captures=[]
            for x in rows:
                if len(x)<6:continue
                captures.append({'timestamp':x[0],'original':x[1],'statuscode':x[2],'mimetype':x[3],'digest':x[4],'length':x[5]})
            return {'role':role,'query_url':url,'endpoint':endpoint,'query_state':'success_capture' if captures else 'success_no_capture','attempts':attempt,'error':'','captures':captures}
        except (HTTPError,URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:
            last=f'{type(exc).__name__}: {exc}'
            if attempt<attempts:time.sleep(attempt)
    return {'role':role,'query_url':url,'endpoint':endpoint,'query_state':'error','attempts':attempts,'error':last,'captures':[]}

def main():
    results=[]
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs=[ex.submit(query,role,url) for role,url in URLS]
        for fut in as_completed(futs):results.append(fut.result())
    results.sort(key=lambda r:r['role']);rows=[]
    for r in results:
        if r['captures']:
            for c in r['captures']:rows.append({'probe_version':VERSION,'role':r['role'],'query_url':r['query_url'],'query_state':r['query_state'],'attempts':r['attempts'],'error':r['error'],**c})
        else:rows.append({'probe_version':VERSION,'role':r['role'],'query_url':r['query_url'],'query_state':r['query_state'],'attempts':r['attempts'],'error':r['error'],'timestamp':'','original':'','statuscode':'','mimetype':'','digest':'','length':''})
    fields=['probe_version','role','query_url','query_state','attempts','error','timestamp','original','statuscode','mimetype','digest','length']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    captures=sum(len(r['captures']) for r in results);failures=sum(r['query_state']=='error' for r in results);no_capture=sum(r['query_state']=='success_no_capture' for r in results)
    lines=['# LTMD-U1 W10 — sondeo Wayback del hueco P1ENA','',f'Versión: `{VERSION}`.','',f'- URL histórica exacta: `{HTTPS}`.',f'- Consultas ejecutadas: **{len(results)}/2**.',f'- Consultas concluyentes sin captura: **{no_capture}**.',f'- Consultas fallidas: **{failures}**.',f'- Capturas CDX 200 únicas observadas: **{captures}**.','','| rol | estado | capturas | intentos |','|---|---|---:|---:|']
    for r in results:lines.append(f"| `{r['role']}` | `{r['query_state']}` | {len(r['captures'])} | {r['attempts']} |")
    lines+=['','## Regla','','Una ausencia concluyente en CDX sólo cierra esta vía archivística exacta; no demuestra inexistencia absoluta de otras copias. Un error de consulta nunca se interpreta como ausencia. Ninguna captura se incorpora automáticamente: requeriría verificar cuerpo, tipo, posición, digest archivístico y SHA-256.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
