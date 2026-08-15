#!/usr/bin/env python3
"""Normalize CONALITEG viewer titles into conservative core-title metadata.

Removes only the standard HTML-title suffix (grade, generation, institutional site
branding) and preserves the original title. Family summaries group by a normalized
ASCII/casefold core while retaining observed display variants.
"""
from __future__ import annotations
import csv,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path

INV=Path('data/catalog/conaliteg_historical_title_inventory.csv')
OUT=Path('data/catalog/conaliteg_title_cores.csv')
SUMMARY=Path('data/catalog/conaliteg_title_core_summary.csv')
REPORT=Path('data/catalog/conaliteg_title_core_summary.md')
VERSION='CONALITEG_TITLECORE_0.2'

def clean(s):return re.sub(r'\s+',' ',s).strip()
def norm_ascii(s):return re.sub(r'\s+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().casefold()).strip()
def core(title):
    s=clean(title)
    s=re.sub(r'\s+Grado\s+\d+\s*[°º]?\s+Generaci[oó]n\s+\d{4}\b.*$','',s,flags=re.I)
    s=re.sub(r'\s*\.:\s*Comisi[oó]n Nacional de Libros de Texto Gratuitos\s*:\..*$','',s,flags=re.I)
    return clean(s).strip(' .:-')

def main():
    rows=list(csv.DictReader(INV.open(encoding='utf-8')))
    if len(rows)!=542:raise SystemExit(f'expected 542 title rows, found {len(rows)}')
    out=[]
    for r in rows:
        c=core(r['viewer_title']);cn=norm_ascii(c)
        out.append({'normalization_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'viewer_title':r['viewer_title'],'title_core':c,'title_core_normalized':cn})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    grouped=defaultdict(list)
    for r in out:grouped[r['title_core_normalized']].append(r)
    summary=[]
    for key,g in grouped.items():
        variants=Counter(r['title_core'] for r in g);canonical=sorted(variants.items(),key=lambda x:(-x[1],x[0].casefold()))[0][0];gens=sorted({r['catalog_generation'] for r in g},key=int)
        summary.append({'normalization_version':VERSION,'title_core_normalized':key,'canonical_title_core':canonical,'display_variants':' | '.join(sorted(variants)),'viewer_count':len(g),'generation_count':len(gens),'generations':';'.join(gens)})
    summary.sort(key=lambda r:(-int(r['viewer_count']),r['title_core_normalized']))
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    lines=['# Familias de título nuclear — Catálogo Histórico CONALITEG','',f'Versión: `{VERSION}`. Claves: **{len(out)}**; familias normalizadas distintas: **{len(summary)}**.','', '## Familias con mayor número de visores']
    for r in summary[:30]:
        variant_note='' if r['display_variants']==r['canonical_title_core'] else f"; variantes: {r['display_variants']}"
        lines.append(f"- *{r['canonical_title_core']}*: {r['viewer_count']} visores, {r['generation_count']} generaciones ({r['generations']}){variant_note}.")
    lines+=['','## Regla','La familia se agrupa por `title_core_normalized` (casefold + eliminación de diacríticos) y conserva las variantes gráficas observadas. Sigue siendo una normalización documental, no una taxonomía disciplinar ni una instrucción de deduplicación.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
