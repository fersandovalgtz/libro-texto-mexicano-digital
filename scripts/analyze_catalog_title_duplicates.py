#!/usr/bin/env python3
"""List repeated normalized viewer titles in the full CONALITEG historical catalog."""
from __future__ import annotations
import csv,re,unicodedata
from collections import defaultdict
from pathlib import Path

INV=Path('data/catalog/conaliteg_historical_title_inventory.csv')
OUT=Path('data/catalog/conaliteg_duplicate_title_groups.csv')
REPORT=Path('data/catalog/conaliteg_duplicate_title_groups.md')
VERSION='CONALITEG_DUPTITLE_0.1'

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',s).strip()

def main():
    rows=list(csv.DictReader(INV.open(encoding='utf-8')))
    if len(rows)!=542:raise SystemExit(f'expected 542 title rows, found {len(rows)}')
    groups=defaultdict(list)
    for r in rows:
        if r['viewer_title'].strip():groups[norm(r['viewer_title'])].append(r)
    dup=[g for g in groups.values() if len(g)>1];out=[]
    for idx,g in enumerate(sorted(dup,key=lambda x:(norm(x[0]['viewer_title']),x[0]['viewer_key'])),1):
        gid=f'DUPTITLE-{idx:03d}'
        for r in sorted(g,key=lambda x:(int(x['catalog_generation']),int(x['grade_code']),x['viewer_key'])):
            out.append({'analysis_version':VERSION,'duplicate_title_group':gid,'viewer_title':r['viewer_title'],'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'tail_code':r['tail_code'],'group_size':len(g)})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['analysis_version','duplicate_title_group','viewer_title','viewer_key','catalog_generation','grade_code','tail_code','group_size']
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    lines=['# Títulos repetidos en el Catálogo Histórico CONALITEG','',f'Versión: `{VERSION}`. Grupos: **{len(dup)}**; claves involucradas: **{len(out)}**.','']
    for g in dup:
        lines.append(f"- *{g[0]['viewer_title']}*: "+', '.join(f"`{r['viewer_key']}` ({r['catalog_generation']}, grado {r['grade_code']})" for r in sorted(g,key=lambda x:(int(x['catalog_generation']),int(x['grade_code']),x['viewer_key']))))
    lines+=['','## Regla','Títulos idénticos no prueban identidad del objeto. Cada grupo es una cola de auditoría para página legal y hashes; no una instrucción de deduplicación.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
