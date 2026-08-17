#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

SCOPE=Path('data/catalog/ltmd_u1_w8_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w8_viewer_architecture.csv')
REPORT=Path('data/catalog/ltmd_u1_w8_viewer_architecture.md')
VERSION='LTMD_U1_W8_ARCHITECTURE_0.1'
UA='LibroTextoMexicanoDigital/U1-W8 Arts architecture audit'
EXPECTED=20

def get(url):
    try:
        with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:
            return r.status,r.read().decode('utf-8','replace')
    except HTTPError as e:return e.code,''
    except (URLError,TimeoutError,OSError):return 0,''

def main():
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    if len(scope)!=EXPECTED:raise SystemExit(f'W8 architecture: expected {EXPECTED} scope rows, got {len(scope)}')
    rows=[]
    for s in scope:
        html_status,html=get(s['source_url'])
        base=s['source_url'].rsplit('/',1)[0]+'/'
        has_x=int(bool(re.search(r'(?:src=["\'][^"\']*/)?x\.js(?:[?"\'])',html,re.I)) or 'x.js' in html)
        x_status,xjs=get(base+'x.js') if has_x else (0,'')
        ag=int('ag_pages' in xjs)
        rows.append({'architecture_version':VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'html_status':html_status,'x_js_discovered':has_x,'x_js_status':x_status,'ag_pages_signal':ag,'standard_dynamic_architecture':int(html_status==200 and has_x and x_status==200 and ag),'source_url':s['source_url']})
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    standard=sum(int(r['standard_dynamic_architecture']) for r in rows)
    html_ok=sum(int(r['html_status'])==200 for r in rows)
    x_ok=sum(int(r['x_js_status'])==200 for r in rows)
    ag_ok=sum(int(r['ag_pages_signal']) for r in rows)
    gens={}
    for r in rows:
        g=r['catalog_generation'];gens.setdefault(g,[0,0]);gens[g][0]+=1;gens[g][1]+=int(r['standard_dynamic_architecture'])
    lines=['# LTMD-U1 W8 — arquitectura de visores Artes','',f'Versión: `{VERSION}`.','',f'- Visores congelados: **{EXPECTED}**.',f'- HTML 200: **{html_ok}/{EXPECTED}**.',f'- `x.js` 200: **{x_ok}/{EXPECTED}**.',f'- señal `ag_pages`: **{ag_ok}/{EXPECTED}**.',f'- arquitectura dinámica estándar: **{standard}/{EXPECTED}**.',f'- casos no estándar: **{EXPECTED-standard}**.','','## Por generación','', '| generación | visores | estándar |','|---:|---:|---:|']
    for g,(n,st) in sorted(gens.items(),key=lambda x:int(x[0])):lines.append(f'| {g} | {n} | {st} |')
    lines += ['', 'Este probe verifica únicamente la arquitectura necesaria para auditar conteos declarados y activos institucionales. No acredita disponibilidad página por página, identidad entre generaciones ni continuidad curricular.', '', 'Un visor HTML accesible no se considera por sí mismo fuente admitida para OCR.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
