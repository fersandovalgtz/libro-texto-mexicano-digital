#!/usr/bin/env python3
"""Audit titles and reachability for all snapped CONALITEG historical viewer keys.

Fetches only each viewer HTML landing page, never page images. Extracts <title>,
normalizes display title, and summarizes reachability/duplicates by catalog generation.
"""
from __future__ import annotations
import csv,html,re
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.request import Request,urlopen

KEYS=Path('data/catalog/conaliteg_historical_viewer_keys.csv')
OUT=Path('data/catalog/conaliteg_historical_title_inventory.csv')
REPORT=Path('data/catalog/conaliteg_historical_title_inventory.md')
VERSION='CONALITEG_TITLE_AUDIT_0.1'
BASE='https://historico.conaliteg.gob.mx/'
UA='LibroTextoMexicanoDigital/0.1 title inventory'
TITLE=re.compile(r'<title[^>]*>(.*?)</title>',re.I|re.S)

def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def fetch(row):
    key=row['viewer_key'];url=BASE+key+'.htm'
    try:
        with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:
            raw=r.read(512*1024);status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','');final=r.geturl()
        text=raw.decode('utf-8',errors='replace');m=TITLE.search(text);title=clean(m.group(1)) if m else ''
        return {**row,'audit_version':VERSION,'source_url':url,'http_status':status,'content_type':ctype,'final_url':final,'viewer_title':title,'reachable':int(status==200),'title_present':int(bool(title)),'error':''}
    except Exception as e:return {**row,'audit_version':VERSION,'source_url':url,'http_status':'','content_type':'','final_url':'','viewer_title':'','reachable':0,'title_present':0,'error':f'{type(e).__name__}: {e}'}

def main():
    keys=list(csv.DictReader(KEYS.open(encoding='utf-8')))
    if len(keys)!=542:raise SystemExit(f'expected 542 snapped keys, found {len(keys)}')
    rows=[]
    with ThreadPoolExecutor(max_workers=16) as pool:
        fut=[pool.submit(fetch,r) for r in keys]
        for f in as_completed(fut):rows.append(f.result())
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['audit_version','viewer_key','catalog_generation','grade_code','tail_code','occurrences','source_url','http_status','content_type','final_url','viewer_title','reachable','title_present','error']
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    reachable=sum(int(r['reachable']) for r in rows);titles=sum(int(r['title_present']) for r in rows);bygen=defaultdict(lambda:Counter())
    for r in rows:bygen[r['catalog_generation']].update(total=1,reachable=int(r['reachable']),title=int(r['title_present']))
    title_groups=defaultdict(list)
    for r in rows:
        t=r['viewer_title'].casefold().strip()
        if t:title_groups[t].append(r)
    duplicates={t:g for t,g in title_groups.items() if len(g)>1}
    lines=['# Inventario maestro de títulos — Catálogo Histórico CONALITEG','',f'Versión: `{VERSION}`.','',f'- Claves auditadas: **{len(rows):,}**.\n- Visores alcanzables: **{reachable:,}**.\n- Títulos HTML recuperados: **{titles:,}**.\n- Títulos normalizados repetidos en más de una clave: **{len(duplicates):,}**.','', '## Cobertura por generación']
    for g in sorted(bygen,key=int):
        c=bygen[g];lines.append(f"- {g}: {c['reachable']}/{c['total']} alcanzables; {c['title']} con título.")
    lines+=['','## Duplicación de título','La duplicación textual de `<title>` se reporta como señal de catálogo, no como identidad bibliográfica. Diferentes claves con el mismo título deben compararse por página legal y hashes antes de fusionarse.','', '## Alcance','Este inventario sólo accede al HTML principal de los visores. No descarga JPEG, PDF ni OCR.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
