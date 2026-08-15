#!/usr/bin/env python3
"""Discover Ciencias Naturales grade 4/6 viewers from CONALITEG's own catalog JS.

Reads the public libros_2023.js used by the historical catalog, extracts object-like
records for target generations/grades, filters science candidates, then verifies
candidate viewer HTML titles. Does not download book page assets.
"""
from __future__ import annotations

import csv,html,json,re
from pathlib import Path
from urllib.request import Request,urlopen

BASE='https://historico.conaliteg.gob.mx/'
CATALOG=BASE+'libros_2023.js'
UA='LibroTextoMexicanoDigital/0.1 expansion discovery'
GENS=('1972','1988','1993','2014')
GRADES=('4','6')
OUT=Path('data/expansion/cn46_viewer_candidates.csv')
REPORT=Path('data/expansion/cn46_discovery_report.md')
RAW=Path('data/expansion/cn46_discovery_metadata.json')
KEY_RE=re.compile(r'H(?P<gen>1972|1988|1993|2014)P(?P<grade>[46])(?P<tail>[A-Z0-9]+)',re.I)
TITLE_RE=re.compile(r'<title[^>]*>(.*?)</title>',re.I|re.S)

def fetch(url):
    req=Request(url,headers={'User-Agent':UA})
    with urlopen(req,timeout=30) as r:
        raw=r.read();cs=r.headers.get_content_charset() or 'utf-8'
        return raw.decode(cs,errors='replace'),getattr(r,'status',None),r.geturl(),r.headers.get('Content-Type','')

def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()

def candidate_blocks(js):
    # Catalog records are shallow JS object literals. Keep a broad fallback context
    # around any viewer key so minor formatting changes do not break discovery.
    blocks=[]
    seen=set()
    for m in KEY_RE.finditer(js):
        key=m.group(0)
        if key.upper() in seen:continue
        seen.add(key.upper())
        left=js.rfind('{',max(0,m.start()-2500),m.start())
        right=js.find('}',m.end(),min(len(js),m.end()+2500))
        if left!=-1 and right!=-1:snippet=js[left:right+1]
        else:snippet=js[max(0,m.start()-700):min(len(js),m.end()+700)]
        blocks.append((key,m.group('gen'),m.group('grade'),snippet))
    return blocks

def science_signal(key,snippet):
    low=snippet.lower()
    return ('ciencia' in low or 'naturales' in low or re.search(r'P[46](?:CI|CN|CNA)',key,re.I) is not None)

def verify(key):
    url=BASE+key+'.htm'
    try:
        text,status,final,ctype=fetch(url)
        mt=TITLE_RE.search(text);title=clean(mt.group(1)) if mt else ''
        science=('ciencias naturales' in title.lower() or ('ciencia' in title.lower() and 'natural' in title.lower()))
        return {'source_url':url,'http_status':status,'final_url':final,'content_type':ctype,'viewer_title':title,'title_science_match':int(science),'verification_status':'verified_title' if science and status==200 else 'reachable_unconfirmed'}
    except Exception as e:
        return {'source_url':url,'http_status':'','final_url':'','content_type':'','viewer_title':'','title_science_match':0,'verification_status':'error','error':f'{type(e).__name__}: {e}'}

def main():
    js,status,final,ctype=fetch(CATALOG)
    rows=[]
    for key,g,grade,snip in candidate_blocks(js):
        if not science_signal(key,snip):continue
        v=verify(key)
        rows.append({'discovery_version':'CN46_DISCOVERY_0.1','catalog_generation':g,'grade':grade,'subject_or_field':'Ciencias Naturales','viewer_key':key,**v,'catalog_evidence':clean(snip)[:500]})
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['discovery_version','catalog_generation','grade','subject_or_field','viewer_key','source_url','http_status','final_url','content_type','viewer_title','title_science_match','verification_status','catalog_evidence','error']
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    verified=[r for r in rows if r['verification_status']=='verified_title']
    meta={'version':'CN46_DISCOVERY_0.1','catalog_url':CATALOG,'catalog_http_status':status,'catalog_final_url':final,'catalog_content_type':ctype,'catalog_bytes':len(js.encode('utf-8')),'target_generations':list(GENS),'target_grades':list(GRADES),'candidate_n':len(rows),'verified_title_n':len(verified),'rows':[{k:r.get(k,'') for k in ('catalog_generation','grade','viewer_key','source_url','viewer_title','verification_status')} for r in rows]}
    RAW.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Descubrimiento reproducible de Ciencias Naturales 4º y 6º','',f"Versión: `{meta['version']}`. Fuente de catálogo: `libros_2023.js` utilizada por el Catálogo Histórico.",'',f"Candidatos detectados: **{len(rows)}**. Visores cuyo `<title>` confirma Ciencias Naturales: **{len(verified)}**.",'','## Objetos verificados']
    for r in verified:lines.append(f"- {r['catalog_generation']} · {r['grade']}º · `{r['viewer_key']}` · {r['viewer_title']}")
    un=[r for r in rows if r['verification_status']!='verified_title']
    if un:
        lines+=['','## Candidatos no confirmados automáticamente']
        for r in un:lines.append(f"- {r['catalog_generation']} · {r['grade']}º · `{r['viewer_key']}` · `{r['verification_status']}` · {r.get('viewer_title','')}")
    lines+=['','## Restricción','El descubrimiento sólo establece identidad del visor/catálogo. No asigna año bibliográfico, edición ni equivalencia curricular; esos campos requieren auditoría del objeto.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
