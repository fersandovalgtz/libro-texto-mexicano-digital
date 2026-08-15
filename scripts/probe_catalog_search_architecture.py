#!/usr/bin/env python3
"""Probe CONALITEG historical catalog search architecture without downloading books.

Fetches the catalog landing page and same-origin JS assets. Extracts form controls,
inline handlers, endpoint-like strings and generation-related code snippets so the
catalog discovery mechanism can be reproduced rather than guessed.
"""
from __future__ import annotations

import json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen

BASE='https://historico.conaliteg.gob.mx/'
UA='LibroTextoMexicanoDigital/0.1 catalog architecture audit'
OUT=Path('data/derived/catalog_search_architecture_probe.json')
REPORT=Path('data/derived/catalog_search_architecture_probe.md')

class P(HTMLParser):
    def __init__(self,base):
        super().__init__();self.base=base;self.scripts=[];self.forms=[];self.handlers=[];self.inputs=[];self.current_form=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('src'):self.scripts.append(urljoin(self.base,a['src']))
        if tag=='form':
            self.current_form={'action':urljoin(self.base,a.get('action','')) if a.get('action') else '', 'method':a.get('method','get').lower(), 'id':a.get('id',''),'name':a.get('name',''),'inputs':[]};self.forms.append(self.current_form)
        if tag in {'input','select','button'}:
            rec={'tag':tag,'name':a.get('name',''),'id':a.get('id',''),'type':a.get('type',''),'value':a.get('value','')}
            self.inputs.append(rec)
            if self.current_form is not None:self.current_form['inputs'].append(rec)
        for k,v in a.items():
            if k.lower().startswith('on') and v:self.handlers.append({'tag':tag,'event':k,'code':v[:1000]})
    def handle_endtag(self,tag):
        if tag=='form':self.current_form=None

def fetch(url):
    req=Request(url,headers={'User-Agent':UA})
    with urlopen(req,timeout=30) as r:
        raw=r.read();cs=r.headers.get_content_charset() or 'utf-8'
        return raw.decode(cs,errors='replace'),{'status':getattr(r,'status',None),'bytes':len(raw),'content_type':r.headers.get('Content-Type',''),'final_url':r.geturl()}

def signals(text):
    keys=('generacion','grado','asignatura','materia','ajax','fetch(','xmlhttprequest','$.','post(','get(','php','json','buscar','search','historico','libro')
    out=[]
    for i,line in enumerate(text.splitlines(),1):
        low=line.lower()
        if any(k in low for k in keys):out.append({'line':i,'text':line.strip()[:1600]})
        if len(out)>=300:break
    return out

def endpoints(text,base):
    vals=set()
    for q,v in re.findall(r"(['\"])(.{1,300}?)\1",text,re.S):
        s=v.strip();low=s.lower()
        if any(x in low for x in ('.php','.json','ajax','api','buscar','search','generacion')):
            if s.startswith(('http://','https://','/','./','../')): vals.add(urljoin(base,s))
            else: vals.add(s[:500])
    return sorted(vals)

def main():
    html,meta=fetch(BASE);p=P(BASE);p.feed(html)
    origin=urlparse(BASE).netloc
    assets=[]
    for src in p.scripts:
        if urlparse(src).netloc!=origin:continue
        try:
            text,m=fetch(src);assets.append({'url':src,**m,'signals':signals(text),'endpoint_candidates':endpoints(text,src)})
        except Exception as e:assets.append({'url':src,'error':f'{type(e).__name__}: {e}'})
    result={'version':'CONALITEG_CATALOG_PROBE_0.1','base':BASE,'html':meta,'forms':p.forms,'inputs':p.inputs,'inline_handlers':p.handlers,'html_signals':signals(html),'html_endpoint_candidates':endpoints(html,BASE),'same_origin_scripts':assets}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Arquitectura de búsqueda del Catálogo Histórico CONALITEG','',f"Versión: `{result['version']}`.",'',f"Formularios detectados: **{len(p.forms)}**. Handlers inline: **{len(p.handlers)}**. Scripts same-origin auditados: **{len(assets)}**.",'','## Formularios']
    for f in p.forms:lines.append(f"- action=`{f['action'] or '(vacío)'}`, method=`{f['method']}`, id=`{f['id']}`; campos: "+', '.join((x['name'] or x['id'] or x['tag']) for x in f['inputs']))
    lines+=['','## Candidatos de endpoint']
    cand=list(result['html_endpoint_candidates'])
    for a in assets:cand+=a.get('endpoint_candidates',[])
    for x in sorted(set(cand)):lines.append(f'- `{x}`')
    lines+=['','## Regla','Este artefacto documenta la arquitectura pública del catálogo. No descarga páginas de libros ni presupone claves de visor.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'forms':p.forms,'handlers':p.handlers,'candidates':sorted(set(cand))},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
