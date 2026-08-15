#!/usr/bin/env python3
"""Normalize CONALITEG viewer titles into conservative core-title metadata.

Removes only the standard HTML-title suffix (grade, generation, institutional site
branding) and preserves the original title. Does not infer subject ontology beyond
reporting normalized title cores.
"""
from __future__ import annotations
import csv,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

INV=Path('data/catalog/conaliteg_historical_title_inventory.csv')
OUT=Path('data/catalog/conaliteg_title_cores.csv')
SUMMARY=Path('data/catalog/conaliteg_title_core_summary.csv')
REPORT=Path('data/catalog/conaliteg_title_core_summary.md')
VERSION='CONALITEG_TITLECORE_0.1'

def clean(s):return re.sub(r'\s+',' ',s).strip()
def norm_ascii(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().casefold()).strip()
def core(title):
    s=clean(title)
    # Observed pattern: "<title> Grado N° Generación YYYY .: Comisión ... :.*"
    s=re.sub(r'\s+Grado\s+\d+\s*[°º]?\s+Generaci[oó]n\s+\d{4}\b.*$','',s,flags=re.I)
    # Fallback removes site branding only if standard grade/generation suffix was absent.
    s=re.sub(r'\s*\.:\s*Comisi[oó]n Nacional de Libros de Texto Gratuitos\s*:\..*$','',s,flags=re.I)
    return clean(s).strip(' .:-')

def main():
    rows=list(csv.DictReader(INV.open(encoding='utf-8')))
    if len(rows)!=542:raise SystemExit(f'expected 542 title rows, found {len(rows)}')
    out=[]
    for r in rows:
        c=core(r['viewer_title'])
        out.append({'normalization_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'viewer_title':r['viewer_title'],'title_core':c,'title_core_normalized':norm_ascii(c)})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    ctr=Counter(r['title_core'] for r in out);gens=defaultdict(set)
    for r in out:gens[r['title_core']].add(r['catalog_generation'])
    summary=[]
    for t,n in sorted(ctr.items(),key=lambda x:(-x[1],x[0].casefold())):
        summary.append({'normalization_version':VERSION,'title_core':t,'viewer_count':n,'generation_count':len(gens[t]),'generations':';'.join(sorted(gens[t],key=int))})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    lines=['# Familias de título nuclear — Catálogo Histórico CONALITEG','',f'Versión: `{VERSION}`. Claves: **{len(out)}**; títulos nucleares distintos: **{len(summary)}**.','', '## Títulos con mayor número de visores']
    for r in summary[:30]:lines.append(f"- *{r['title_core']}*: {r['viewer_count']} visores, {r['generation_count']} generaciones ({r['generations']}).")
    lines+=['','## Regla','`title_core` es normalización documental del título HTML, no una taxonomía disciplinar. Dos visores con el mismo núcleo pueden representar ediciones, variantes o materiales distintos y conservan su `viewer_key`.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
