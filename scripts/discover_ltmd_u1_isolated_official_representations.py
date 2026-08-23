#!/usr/bin/env python3
"""Discover official CONALITEG representations for selected isolated U1 holes.

This stage is intentionally diagnostic. It fetches only official HTML/JS text,
records redirects/resources/hashes, and never declares equivalence with a
historical viewer. Source images are not persisted.
"""
from __future__ import annotations
import csv,hashlib,re
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

OUT=Path('data/catalog/ltmd_u1_isolated_official_representation_discovery.csv')
REPORT=Path('docs/LTMD_U1_ISOLATED_OFFICIAL_REPRESENTATION_DISCOVERY.md')
VERSION='LTMD_U1_ISOLATED_OFFICIAL_REPRESENTATION_DISCOVERY_0.1'
UA='LibroTextoMexicanoDigital/U1 official-representation discovery 0.1'
CASES=[
    {'wave':'W11','viewer_key':'H2014P3COL','viewer_page':'130','official_code':'P3COL','entry_url':'https://libros.conaliteg.gob.mx/P3COL.htm'},
    {'wave':'W11','viewer_key':'H2014P3MOR','viewer_page':'15','official_code':'P3MOR','entry_url':'https://libros.conaliteg.gob.mx/P3MOR.htm'},
]
TEXT_EXT={'.htm','.html','.js','.json','.txt'}
RESOURCE_RE=re.compile(r'''(?:src|href)\s*=\s*["']([^"']+)["']|["']([^"']+\.(?:js|json|jpg|jpeg|png|webp|pdf)(?:\?[^"']*)?)["']''',re.I)
ROUTE_RE=re.compile(r'''(?:https?://[^\s"']+|\.\.?/[^\s"']+|/[A-Za-z0-9_./?=&%-]+)''')

def fetch(url:str,limit:int=2_000_000):
    req=Request(url,headers={'User-Agent':UA})
    with urlopen(req,timeout=45) as r:
        final=r.geturl();status=int(getattr(r,'status',200) or 200);ctype=r.headers.get('Content-Type','');data=r.read(limit+1)
    if len(data)>limit:raise RuntimeError(f'text resource exceeds {limit} bytes: {url}')
    return status,final,ctype,data

def textual(url:str,ctype:str)->bool:
    ext=Path(urlparse(url).path).suffix.lower()
    return 'text/' in ctype.lower() or 'javascript' in ctype.lower() or 'json' in ctype.lower() or ext in TEXT_EXT

def resources(base:str,text:str):
    out=[]
    for m in RESOURCE_RE.finditer(text):
        raw=(m.group(1) or m.group(2) or '').strip()
        if not raw or raw.startswith(('data:','javascript:','#')):continue
        out.append(urljoin(base,raw))
    return sorted(set(out))

def main():
    rows=[]
    for case in CASES:
        try:
            status,final,ctype,data=fetch(case['entry_url'])
            text=data.decode('utf-8','replace')
            rows.append({**case,'resource_role':'entry_html','requested_url':case['entry_url'],'final_url':final,'http_status':status,'content_type':ctype,'byte_size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'discovered_from':'','error':''})
            res=resources(final,text)
            for u in res:
                ext=Path(urlparse(u).path).suffix.lower()
                role='linked_text' if ext in TEXT_EXT else 'linked_binary'
                if role=='linked_binary':
                    rows.append({**case,'resource_role':role,'requested_url':u,'final_url':'','http_status':'','content_type':'','byte_size':'','sha256':'','discovered_from':final,'error':''})
                    continue
                try:
                    s2,f2,c2,d2=fetch(u)
                    rows.append({**case,'resource_role':role,'requested_url':u,'final_url':f2,'http_status':s2,'content_type':c2,'byte_size':len(d2),'sha256':hashlib.sha256(d2).hexdigest(),'discovered_from':final,'error':''})
                    if textual(f2,c2):
                        t2=d2.decode('utf-8','replace')
                        for u2 in resources(f2,t2):
                            if u2 not in {r['requested_url'] for r in rows if r['viewer_key']==case['viewer_key']}:
                                rows.append({**case,'resource_role':'nested_reference','requested_url':u2,'final_url':'','http_status':'','content_type':'','byte_size':'','sha256':'','discovered_from':f2,'error':''})
                except Exception as exc:
                    rows.append({**case,'resource_role':role,'requested_url':u,'final_url':'','http_status':'','content_type':'','byte_size':'','sha256':'','discovered_from':final,'error':f'{type(exc).__name__}: {exc}'})
        except Exception as exc:
            rows.append({**case,'resource_role':'entry_html','requested_url':case['entry_url'],'final_url':'','http_status':'','content_type':'','byte_size':'','sha256':'','discovered_from':'','error':f'{type(exc).__name__}: {exc}'})
    fields=['wave','viewer_key','viewer_page','official_code','entry_url','resource_role','requested_url','final_url','http_status','content_type','byte_size','sha256','discovered_from','error']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    lines=['# LTMD-U1 — descubrimiento de representaciones oficiales para huecos aislados','',f'Versión: `{VERSION}`.','',
           'Esta etapa descubre rutas y recursos de visores oficiales CONALITEG actuales. No declara identidad con el visor histórico y no persiste imágenes fuente.','']
    for case in CASES:
        rr=[r for r in rows if r['viewer_key']==case['viewer_key']]
        entry=next((r for r in rr if r['resource_role']=='entry_html'),None)
        refs=[r for r in rr if r['resource_role']!='entry_html']
        errors=[r for r in rr if r['error']]
        lines += [f"## `{case['viewer_key']}` → `{case['official_code']}`",'',
                  f"- Hueco histórico: página **{case['viewer_page']}**.",
                  f"- Entrada oficial consultada: `{case['entry_url']}`.",
                  f"- URL final: `{entry['final_url'] if entry else '—'}`.",
                  f"- HTTP: **{entry['http_status'] if entry else '—'}**.",
                  f"- Referencias descubiertas: **{len(refs)}**.",
                  f"- Errores de recursos textuales: **{len(errors)}**.",'']
        candidates=[r['requested_url'] for r in refs if any(x in r['requested_url'].lower() for x in ('.jpg','.jpeg','.pdf','.json','.js'))]
        if candidates:
            lines.append('Referencias candidatas de arquitectura:')
            for u in candidates[:20]:lines.append(f'- `{u}`')
            lines.append('')
    lines += ['## Regla de aceptación','',
              'Una representación oficial descubierta sólo podrá contribuir a resolver el hueco si una segunda etapa demuestra correspondencia posicional determinista con el visor histórico mediante la secuencia observable y hashes. La coincidencia de clave corta, título, grado o cardinalidad no basta.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
