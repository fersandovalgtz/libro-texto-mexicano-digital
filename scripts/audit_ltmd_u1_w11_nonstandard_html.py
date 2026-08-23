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
VERSION='LTMD_U1_W11_NONSTANDARD_HTML_0.1'
EXPECTED_TOTAL=111
EXPECTED_NONSTANDARD=11
UA='LibroTextoMexicanoDigital/U1-W11 nonstandard HTML diagnostics 0.1'

class Parser(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.tags=Counter()
    def handle_starttag(self,tag,attrs):
        self.tags[tag.lower()]+=1
        for k,v in attrs:
            if k.lower() in {'href','src','data'} and v:self.refs.append((tag.lower(),k.lower(),v.strip()))

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

def candidate(url:str,tag:str)->bool:
    u=url.lower();kind=classify(url)
    if kind in {'pdf','jpg','jpeg','png','gif','webp','swf','zip','mp4','json'}:return True
    if tag in {'iframe','embed','object'}:return True
    return any(token in u for token in ['/c/','viewer','book','libro','magazine','flip','page','media','asset'])

def main()->None:
    routing=list(csv.DictReader(ROUTING.open(encoding='utf-8',newline='')))
    if len(routing)!=EXPECTED_TOTAL or len({r['viewer_key'] for r in routing})!=EXPECTED_TOTAL:raise SystemExit('W11 nonstandard diagnostics routing cardinality drift')
    if {r['routing_version'] for r in routing}!={ROUTING_VERSION}:raise SystemExit('W11 nonstandard diagnostics routing version drift')
    cohort=[r for r in routing if r['technical_route']=='nonstandard_html_diagnostics']
    if len(cohort)!=EXPECTED_NONSTANDARD:raise SystemExit(f'expected {EXPECTED_NONSTANDARD} nonstandard viewers, got {len(cohort)}')
    rows=[];resources=[]
    for r in cohort:
        status,html=get(r['source_url']);p=Parser();p.feed(html)
        normalized=[]
        for tag,attr,raw in p.refs:
            if raw.lower().startswith(('javascript:','data:','mailto:','#')):continue
            url=urljoin(r['source_url'],raw);normalized.append((tag,attr,url))
        seen=set();candidates=[]
        for tag,attr,url in normalized:
            key=(tag,attr,url)
            if key in seen:continue
            seen.add(key)
            if candidate(url,tag):
                candidates.append((tag,attr,url));resources.append({'diagnostic_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'tag':tag,'attribute':attr,'resource_type':classify(url),'resource_url':url})
        kinds=Counter(classify(u) for _,_,u in candidates)
        text=html.lower()
        rows.append({'diagnostic_version':VERSION,'routing_version':ROUTING_VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'html_status':status,'declared_ref_count':len(seen),'candidate_resource_count':len(candidates),'iframe_count':p.tags['iframe'],'embed_count':p.tags['embed'],'object_count':p.tags['object'],'img_count':p.tags['img'],'pdf_candidate_count':kinds['pdf'],'image_candidate_count':sum(kinds[k] for k in ['jpg','jpeg','png','gif','webp']),'json_candidate_count':kinds['json'],'inline_pdf_signal':int('pdf' in text),'inline_claves_signal':int('claves.json' in text),'inline_magazine_signal':int('magazine' in text),'source_url':r['source_url']})
    rows.sort(key=lambda r:(int(r['catalog_generation']),r['viewer_key']));resources.sort(key=lambda r:(r['viewer_key'],r['resource_type'],r['resource_url']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    res_fields=['diagnostic_version','viewer_key','catalog_generation','grade_code','tag','attribute','resource_type','resource_url']
    with RES.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=res_fields);w.writeheader();w.writerows(resources)
    type_counts=Counter(r['resource_type'] for r in resources)
    lines=['# LTMD-U1 W11 — diagnóstico HTML de la ruta no estándar','',f'Versión: `{VERSION}`.','',f'- Visores no estándar auditados: **{len(rows)}/{EXPECTED_NONSTANDARD}**.',f'- HTML 200: **{sum(int(r["html_status"])==200 for r in rows)}/{EXPECTED_NONSTANDARD}**.',f'- Recursos candidatos declarados en HTML: **{len(resources)}**.','','## Tipos de recurso candidato']
    if type_counts:
        for k,v in sorted(type_counts.items()):lines.append(f'- `{k}`: **{v}**.')
    else:lines.append('- Ninguno detectado por las reglas declaradas.')
    lines+=['','## Por visor','','| viewer | HTML | refs | candidatos | iframe | embed | object | PDF | imágenes | JSON |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:lines.append(f"| `{r['viewer_key']}` | {r['html_status']} | {r['declared_ref_count']} | {r['candidate_resource_count']} | {r['iframe_count']} | {r['embed_count']} | {r['object_count']} | {r['pdf_candidate_count']} | {r['image_candidate_count']} | {r['json_candidate_count']} |")
    lines+=['','## Límite de esta compuerta','El diagnóstico sólo lee HTML y registra URLs que el propio visor declara. No descarga ni valida los recursos candidatos y no convierte su presencia en fuente admitida. La siguiente fase debe verificar cada candidato explícitamente y conservar cualquier ausencia o ambigüedad como retención.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
