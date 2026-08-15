#!/usr/bin/env python3
"""Audit the three internal unserved positions in strict Ciencias Naturales 2008.

This is deliberately narrow. It does not infer a missing bibliographic page and
never shifts indices to manufacture continuity. The target URL is retried; the
immediate neighbours are re-fetched and must reproduce their persisted SHA-256.
If the target remains unavailable while both neighbours verify, the state is
`internal_unserved_position_observed`.
"""
from __future__ import annotations
import csv, hashlib, time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MAN=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
OUT=Path('data/catalog/cn2008_internal_unserved_audit.csv')
REPORT=Path('data/catalog/cn2008_internal_unserved_audit.md')
VERSION='CN2008_INTERNAL_UNSERVED_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN2008 internal unserved audit'
TARGETS=(('LTMD-CN3-G2008',94),('LTMD-CN4-G2008',76),('LTMD-CN4-G2008',96))

def fetch(u,max_attempts=5):
    attempts=[]
    for attempt in range(1,max_attempts+1):
        try:
            h=hashlib.sha256();size=0
            with urlopen(Request(u,headers={'User-Agent':UA}),timeout=45) as r:
                status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    h.update(b);size+=len(b)
            attempts.append(f'{attempt}:{status}:{ctype}:{size}')
            if status==200 and 'image' in ctype.lower() and size:
                return {'reachable':1,'status':status,'content_type':ctype,'byte_size':size,'sha256':h.hexdigest(),'attempts':attempt,'attempt_log':'|'.join(attempts),'error':''}
        except HTTPError as e:
            attempts.append(f'{attempt}:HTTP{e.code}')
            # Retry even 404: this audit tests persistence of the observed gap.
        except (URLError,TimeoutError,OSError) as e:
            attempts.append(f'{attempt}:{type(e).__name__}:{e}')
        if attempt<max_attempts:time.sleep(.7*attempt)
    return {'reachable':0,'status':'','content_type':'','byte_size':'','sha256':'','attempts':max_attempts,'attempt_log':'|'.join(attempts),'error':'target remained unavailable'}

def main():
    rows=list(csv.DictReader(MAN.open(encoding='utf-8')))
    idx={(r['book_id'],int(r['viewer_page'])):r for r in rows}
    out=[]
    for book,p in TARGETS:
        t=idx[(book,p)]
        if t['asset_status']!='internal_missing':raise SystemExit(f'{book} VP{p} no longer internal_missing in source manifest')
        observed=fetch(t['source_asset_url'],5)
        neighbour_results=[]
        for np in (p-1,p+1):
            n=idx[(book,np)]
            if n['asset_status']!='source_jpeg' or not n['sha256']:raise SystemExit(f'neighbour not reference-ready: {book} VP{np}')
            got=fetch(n['source_asset_url'],3)
            ok=int(got['reachable'] and got['sha256']==n['sha256'] and str(got['byte_size'])==str(n['byte_size']))
            neighbour_results.append((np,n,got,ok))
        neighbours_ok=all(x[3] for x in neighbour_results)
        state='unexpectedly_recovered' if observed['reachable'] else ('internal_unserved_position_observed' if neighbours_ok else 'audit_inconclusive')
        out.append({'audit_version':VERSION,'book_id':book,'viewer_key':t['viewer_key'],'catalog_generation':t['catalog_generation'],'grade':t['grade'],'viewer_page':p,
                    'source_image_index':t['source_image_index'],'target_url':t['source_asset_url'],'target_state':state,
                    'target_reachable':observed['reachable'],'target_attempts':observed['attempts'],'target_attempt_log':observed['attempt_log'],
                    'prev_page':neighbour_results[0][0],'prev_url':neighbour_results[0][1]['source_asset_url'],'prev_sha256_match':neighbour_results[0][3],
                    'next_page':neighbour_results[1][0],'next_url':neighbour_results[1][1]['source_asset_url'],'next_sha256_match':neighbour_results[1][3],
                    'neighbours_sha_verified':int(neighbours_ok),
                    'interpretive_limit':'Observed internal URL gap; does not by itself prove that a bibliographic page is absent from the physical/edition source.'})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    observed_count=sum(r['target_state']=='internal_unserved_position_observed' for r in out)
    recovered=sum(r['target_state']=='unexpectedly_recovered' for r in out)
    inconclusive=sum(r['target_state']=='audit_inconclusive' for r in out)
    lines=['# Auditoría focal de posiciones internas no servidas — Ciencias Naturales 2008','',f'Versión: `{VERSION}`.','',
           f'- Posiciones auditadas: **{len(out)}**.\n- `internal_unserved_position_observed`: **{observed_count}**.\n- Recuperadas inesperadamente: **{recovered}**.\n- Inconclusas: **{inconclusive}**.','', '## Casos']
    for r in out:lines.append(f"- `{r['book_id']}` VP{r['viewer_page']}: `{r['target_state']}`; intentos objetivo={r['target_attempts']}; vecino anterior SHA={'OK' if int(r['prev_sha256_match']) else 'FAIL'}; vecino posterior SHA={'OK' if int(r['next_sha256_match']) else 'FAIL'}.")
    lines+=['','## Interpretación','La clasificación describe el comportamiento del activo digital público observado. No se transforma automáticamente en “página faltante del libro”: esa inferencia exigiría cotejo bibliográfico/visual independiente. Tampoco se renumeran ni desplazan páginas para ocultar el hueco.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))
    if inconclusive:raise SystemExit('one or more audits inconclusive')

if __name__=='__main__':main()
