#!/usr/bin/env python3
"""Inspect W11 nonstandard viewer HTML for declared resource routes, without downloading source assets."""
from __future__ import annotations
import csv,re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

ROUTING=Path('data/catalog/ltmd_u1_w11_technical_routing.csv')
OUT=Path('data/catalog/ltmd_u1_w11_nonstandard_html_diagnostics.csv')
RES=Path('data/catalog/ltmd_u1_w11_nonstandard_resource_candidates.csv')
REPORT=Path('docs/LTMD_U1_W11_NONSTANDARD_HTML.md')
ROUTING_VERSION='LTMD_U1_W11_TECHNICAL_ROUTING_0.1'
VERSION='LTMD_U1_W11_NONSTANDARD_HTML_0.3'
EXPECTED_TOTAL=111
EXPECTED_NONSTANDARD=11
UA='LibroTextoMexicanoDigital/U1-W11 nonstandard HTML diagnostics 0.3'
UI_PATHS={'/pics/der.png','/pics/go.png','/pics/h.png','/pics/izq.png'}
SITE_CHROME={
    ('historico.conaliteg.gob.mx','/tw.jpg'),
    ('www.conaliteg.gob.mx','/images/tw_conaliteg.jpg'),
}
ATTRS={'href','src','data','action','poster','background'}
RESOURCE_RE=re.compile(r'''["']([^"']+\.(?:pdf|jpe?g|png|gif|webp|swf|zip|mp4|json)(?:\?[^"']*)?)["']''',re.I)

class Parser(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.tags=Counter()
    def handle_starttag(self,tag,attrs):
        tag=tag.lower();self.tags[tag]+=1
        for k,v in attrs:
            if v and k.lower() in ATTRS:self.refs.append((tag,k.lower(),v.strip(),'attribute'))

def get(url:str)->tuple[int,str]:
    try:
        with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:return r.status,r.read().decode('utf-8','replace')
    except HTTPError as e:return e.code,''
    except (URLError,TimeoutError,OSError):return 0,''

def classify(url:str)->str:
    path=urlparse(url).path.lower()
    for ext in ['.pdf','.jpg','.jpeg','.png','.gif','.webp','.svg','.swf','.zip','.mp4','.js','.json']:
        if path.endswith(ext):return ext[1:]
    return 'other'

def is_candidate(url:str,tag:str)->bool:
    u=url.lower();kind=classify(url)
    if kind in {'pdf','jpg','jpeg','png','gif','webp','swf','zip','mp4','json'}:return True
    if tag in {'iframe','embed','object'}:return True
    return any(token in u for token in ['/c/','viewer','book','libro','magazine','flip','page','media','asset'])

def role(url:str)->str:
    p=urlparse(url);host=p.netloc.lower();path=p.path.lower()
    if host=='historico.conaliteg.gob.mx' and path in UI_PATHS:return 'shared_ui_control'
    if (host,path) in SITE_CHROME:return 'shared_site_chrome'
    return 'source_or_document_candidate'

def main()->None:
    routing=list(csv.DictReader(ROUTING.open(encoding='utf-8',newline='')))
    if len(routing)!=EXPECTED_TOTAL or len({r['viewer_key'] for r in routing})!=EXPECTED_TOTAL:raise SystemExit('W11 nonstandard diagnostics routing cardinality drift')
    if {r['routing_version'] for r in routing}!={ROUTING_VERSION}:raise SystemExit('W11 nonstandard diagnostics routing version drift')
    cohort=[r for r in routing if r['technical_route']=='nonstandard_html_diagnostics']
    if len(cohort)!=EXPECTED_NONSTANDARD:raise SystemExit(f'expected {EXPECTED_NONSTANDARD} nonstandard viewers, got {len(cohort)}')
    rows=[];resources=[]
    for r in cohort:
        status,html=get(r['source_url']);p=Parser();p.feed(html)
        refs=list(p.refs)
        for raw in RESOURCE_RE.findall(html):refs.append(('inline','literal',raw.strip(),'inline_literal'))
        seen_urls=set();candidates=[]
        for tag,attr,raw,method in refs:
            if raw.lower().startswith(('javascript:','data:','mailto:','#')):continue
            url=urljoin(r['source_url'],raw)
            if url in seen_urls:continue
            if is_candidate(url,tag):
                seen_urls.add(url);ro=role(url);candidates.append((tag,attr,url,method,ro))
                resources.append({'diagnostic_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'discovery_method':method,'tag':tag,'attribute':attr,'resource_type':classify(url),'candidate_role':ro,'resource_url':url})
        kinds=Counter(classify(u) for _,_,u,_,_ in candidates);roles=Counter(ro for *_,ro in candidates);text=html.lower()
        rows.append({'diagnostic_version':VERSION,'routing_version':ROUTING_VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'html_status':status,'candidate_resource_count':len(candidates),'shared_ui_control_count':roles['shared_ui_control'],'shared_site_chrome_count':roles['shared_site_chrome'],'source_or_document_candidate_count':roles['source_or_document_candidate'],'iframe_count':p.tags['iframe'],'embed_count':p.tags['embed'],'object_count':p.tags['object'],'img_count':p.tags['img'],'pdf_candidate_count':kinds['pdf'],'image_candidate_count':sum(kinds[k] for k in ['jpg','jpeg','png','gif','webp']),'json_candidate_count':kinds['json'],'inline_pdf_signal':int('pdf' in text),'inline_claves_signal':int('claves.json' in text),'inline_magazine_signal':int('magazine' in text),'source_url':r['source_url']})
    rows.sort(key=lambda r:(int(r['catalog_generation']),r['viewer_key']));resources.sort(key=lambda r:(r['viewer_key'],r['candidate_role'],r['resource_type'],r['resource_url']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    res_fields=['diagnostic_version','viewer_key','catalog_generation','grade_code','discovery_method','tag','attribute','resource_type','candidate_role','resource_url']
    with RES.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=res_fields);w.writeheader();w.writerows(resources)
    type_counts=Counter(r['resource_type'] for r in resources);role_counts=Counter(r['candidate_role'] for r in resources)
    lines=['# LTMD-U1 W11 — diagnóstico HTML de la ruta no estándar','',f'Versión: `{VERSION}`.','',f'- Visores no estándar auditados: **{len(rows)}/{EXPECTED_NONSTANDARD}**.',f'- HTML 200: **{sum(int(r["html_status"])==200 for r in rows)}/{EXPECTED_NONSTANDARD}**.',f'- Recursos únicos observados por visor y consolidados: **{len(resources)}**.',f'- Controles UI compartidos: **{role_counts["shared_ui_control"]}**.',f'- Recursos globales de interfaz/sitio: **{role_counts["shared_site_chrome"]}**.',f'- Candidatos de fuente/documento: **{role_counts["source_or_document_candidate"]}**.','','## Tipos de recurso observado']
    if type_counts:
        for k,v in sorted(type_counts.items()):lines.append(f'- `{k}`: **{v}**.')
    else:lines.append('- Ninguno detectado por las reglas declaradas.')
    lines+=['','## Por visor','','| viewer | HTML | recursos | UI | sitio | fuente/doc | iframe | embed | object | PDF | imágenes | JSON |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:lines.append(f"| `{r['viewer_key']}` | {r['html_status']} | {r['candidate_resource_count']} | {r['shared_ui_control_count']} | {r['shared_site_chrome_count']} | {r['source_or_document_candidate_count']} | {r['iframe_count']} | {r['embed_count']} | {r['object_count']} | {r['pdf_candidate_count']} | {r['image_candidate_count']} | {r['json_candidate_count']} |")
    lines+=['','## Regla de interpretación','Los cuatro `/pics/*.png` de navegación y los dos JPG globales `tw.jpg`/`tw_conaliteg.jpg` se clasifican como chrome compartido, no como fuente documental. El diagnóstico deduplica URLs dentro de cada visor y examina atributos/literales con extensiones documentales o multimedia. La evidencia HTML se interpreta junto con `claves.json`; en esta cohorte la configuración oficial constituye una ruta independiente que aún debe verificarse activo por activo.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
