#!/usr/bin/env python3
"""Audit W10 viewer architecture without inferring or downloading source pages."""
from __future__ import annotations
import csv,re
from concurrent.futures import ThreadPoolExecutor,as_completed
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

SCOPE=Path('data/catalog/ltmd_u1_w10_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w10_viewer_architecture.csv')
REPORT=Path('docs/LTMD_U1_W10_ARCHITECTURE.md')
VERSION='LTMD_U1_W10_ARCHITECTURE_0.1'
UA='LibroTextoMexicanoDigital/U1-W10 integrated-multiarea architecture audit 0.1'
EXPECTED=69
WORKERS=12

def get(url):
    try:
        with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:
            return r.status,r.read().decode('utf-8','replace')
    except HTTPError as e:return e.code,''
    except (URLError,TimeoutError,OSError):return 0,''

def audit(s):
    html_status,html=get(s['source_url'])
    base=s['source_url'].rsplit('/',1)[0]+'/'
    has_x=int(bool(re.search(r'(?:src=["\'][^"\']*/)?x\.js(?:[?"\'])',html,re.I)) or 'x.js' in html)
    x_status,xjs=get(base+'x.js') if has_x else (0,'')
    signals={
        'ag_pages_signal':int('ag_pages' in xjs),
        'ag_clave_signal':int('ag_clave' in xjs),
        'claves_json_signal':int('claves.json' in xjs or 'claves.json' in html),
        'magazine_js_signal':int('magazine.js' in xjs or 'magazine.js' in html),
    }
    standard=int(html_status==200 and has_x and x_status==200 and signals['ag_pages_signal'])
    return {'architecture_version':VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'html_status':html_status,'x_js_discovered':has_x,'x_js_status':x_status,**signals,'standard_dynamic_architecture':standard,'source_url':s['source_url']}

def main():
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    if len(scope)!=EXPECTED or len({r['viewer_key'] for r in scope})!=EXPECTED:
        raise SystemExit(f'W10 architecture: expected {EXPECTED} unique scope rows')
    rows=[]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs={ex.submit(audit,s):s['viewer_key'] for s in scope}
        for fut in as_completed(futs):
            try:rows.append(fut.result())
            except Exception as exc:raise SystemExit(f'W10 architecture worker failed for {futs[fut]}: {type(exc).__name__}: {exc}')
    if len(rows)!=EXPECTED or len({r['viewer_key'] for r in rows})!=EXPECTED:
        raise SystemExit('W10 architecture output cardinality drift')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    standard=sum(int(r['standard_dynamic_architecture']) for r in rows)
    html_ok=sum(int(r['html_status'])==200 for r in rows)
    x_ok=sum(int(r['x_js_status'])==200 for r in rows)
    ag_ok=sum(int(r['ag_pages_signal']) for r in rows)
    bygen=Counter((r['catalog_generation'],r['standard_dynamic_architecture']) for r in rows)
    non=[r for r in rows if not int(r['standard_dynamic_architecture'])]
    lines=['# LTMD-U1 W10 — auditoría de arquitectura de visores','',f'Versión: `{VERSION}`.','',f'- Identidades auditadas: **{EXPECTED}/{EXPECTED}**.',f'- HTML 200: **{html_ok}/{EXPECTED}**.',f'- `x.js` 200: **{x_ok}/{EXPECTED}**.',f'- señal `ag_pages`: **{ag_ok}/{EXPECTED}**.',f'- arquitectura dinámica estándar observada: **{standard}/{EXPECTED}**.',f'- casos no estándar: **{len(non)}**.','','## Arquitectura estándar por generación de catálogo']
    gens=sorted({r['catalog_generation'] for r in rows},key=int)
    for g in gens:
        total=sum(1 for r in rows if r['catalog_generation']==g);ok=bygen[(g,1)];lines.append(f'- {g}: **{ok}/{total}**.')
    lines+=['','## Casos no estándar']
    if non:
        for r in non:lines.append(f"- `{r['viewer_key']}` — HTML {r['html_status']}, x.js {r['x_js_status']}, ag_pages={r['ag_pages_signal']}.")
    else:lines.append('- Ninguno.')
    lines+=['','## Límite de esta compuerta','Esta auditoría observa únicamente la arquitectura servida por cada visor. No acredita disponibilidad página por página, no construye rutas faltantes y no declara fuente admitida. Un caso no estándar se conserva como resultado que requiere una estrategia específica; nunca se corrige por analogía con otro libro.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':
    main()
