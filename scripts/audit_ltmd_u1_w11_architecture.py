#!/usr/bin/env python3
"""Audit frozen W11 viewer architecture without downloading source pages."""
from __future__ import annotations
import csv,re
from concurrent.futures import ThreadPoolExecutor,as_completed
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

SCOPE=Path('data/catalog/ltmd_u1_w11_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w11_viewer_architecture.csv')
REPORT=Path('docs/LTMD_U1_W11_ARCHITECTURE.md')
SCOPE_VERSION='LTMD_U1_W11_OTROS_SCOPE_0.1'
VERSION='LTMD_U1_W11_ARCHITECTURE_0.1'
UA='LibroTextoMexicanoDigital/U1-W11 architecture audit 0.1'
EXPECTED=111
WORKERS=12

def get(url:str)->tuple[int,str]:
    try:
        with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:
            return r.status,r.read().decode('utf-8','replace')
    except HTTPError as e:return e.code,''
    except (URLError,TimeoutError,OSError):return 0,''

def discover_xjs(source_url:str,html:str)->tuple[int,str]:
    candidates=re.findall(r'<script[^>]+src=["\']([^"\']*x\.js(?:\?[^"\']*)?)["\']',html,re.I)
    if candidates:
        return 1,urljoin(source_url,candidates[0])
    if 'x.js' in html:
        return 1,urljoin(source_url,'x.js')
    return 0,''

def audit(s:dict[str,str])->dict[str,object]:
    html_status,html=get(s['source_url'])
    has_x,x_url=discover_xjs(s['source_url'],html)
    x_status,xjs=get(x_url) if has_x else (0,'')
    signals={
        'ag_pages_signal':int('ag_pages' in xjs),
        'ag_clave_signal':int('ag_clave' in xjs),
        'claves_json_signal':int('claves.json' in xjs or 'claves.json' in html),
        'magazine_js_signal':int('magazine.js' in xjs or 'magazine.js' in html),
    }
    standard=int(html_status==200 and has_x and x_status==200 and signals['ag_pages_signal'])
    sig='|'.join([
        f"html{html_status}",f"x{has_x}:{x_status}",
        f"agp{signals['ag_pages_signal']}",f"agc{signals['ag_clave_signal']}",
        f"clv{signals['claves_json_signal']}",f"mag{signals['magazine_js_signal']}"
    ])
    return {
        'architecture_version':VERSION,'scope_version':s['scope_version'],'viewer_key':s['viewer_key'],
        'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],
        'html_status':html_status,'x_js_discovered':has_x,'x_js_url':x_url,'x_js_status':x_status,
        **signals,'standard_dynamic_architecture':standard,'architecture_signature':sig,'source_url':s['source_url']
    }

def main()->None:
    if not SCOPE.exists():raise SystemExit(f'missing frozen W11 scope: {SCOPE}')
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    if len(scope)!=EXPECTED or len({r['viewer_key'] for r in scope})!=EXPECTED:raise SystemExit(f'W11 architecture: expected {EXPECTED} unique scope rows')
    if {r['scope_version'] for r in scope}!={SCOPE_VERSION}:raise SystemExit('W11 architecture: scope version drift')
    rows=[]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs={ex.submit(audit,s):s['viewer_key'] for s in scope}
        for fut in as_completed(futs):
            try:rows.append(fut.result())
            except Exception as exc:raise SystemExit(f'W11 architecture worker failed for {futs[fut]}: {type(exc).__name__}: {exc}')
    if len(rows)!=EXPECTED or len({r['viewer_key'] for r in rows})!=EXPECTED:raise SystemExit('W11 architecture output cardinality drift')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    standard=sum(int(r['standard_dynamic_architecture']) for r in rows);html_ok=sum(int(r['html_status'])==200 for r in rows);x_ok=sum(int(r['x_js_status'])==200 for r in rows);ag_ok=sum(int(r['ag_pages_signal']) for r in rows)
    non=[r for r in rows if not int(r['standard_dynamic_architecture'])]
    sigs=Counter(r['architecture_signature'] for r in rows)
    gens=sorted({r['catalog_generation'] for r in rows},key=int)
    lines=['# LTMD-U1 W11 — auditoría de arquitectura de visores','',f'Versión: `{VERSION}`.','',
           f'- Identidades auditadas: **{EXPECTED}/{EXPECTED}**.',f'- HTML 200: **{html_ok}/{EXPECTED}**.',f'- `x.js` 200: **{x_ok}/{EXPECTED}**.',f'- señal `ag_pages`: **{ag_ok}/{EXPECTED}**.',f'- arquitectura dinámica estándar observada: **{standard}/{EXPECTED}**.',f'- casos no estándar: **{len(non)}**.','',
           '## Firmas técnicas observadas']
    for sig,n in sigs.most_common():lines.append(f'- `{sig}`: **{n}**.')
    lines+=['','## Arquitectura estándar por generación de catálogo']
    for g in gens:
        rr=[r for r in rows if r['catalog_generation']==g];ok=sum(int(r['standard_dynamic_architecture']) for r in rr);lines.append(f'- {g}: **{ok}/{len(rr)}**.')
    lines+=['','## Casos no estándar']
    if non:
        for r in non:lines.append(f"- `{r['viewer_key']}` — HTML {r['html_status']}, x.js {r['x_js_status']}, `ag_pages`={r['ag_pages_signal']}, firma `{r['architecture_signature']}`.")
    else:lines.append('- Ninguno.')
    lines+=['','## Límite de esta compuerta','Esta auditoría observa únicamente arquitectura y configuración técnica servida por cada visor. No acredita disponibilidad página por página, no declara fuente admitida, no mueve identidades entre dominios y no crea aliases. Una firma compartida habilita una estrategia común de auditoría de fuente; no demuestra equivalencia documental, curricular o semántica.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
