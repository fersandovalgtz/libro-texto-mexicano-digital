#!/usr/bin/env python3
"""Extract the complete normalized Ciencias Naturales title family from catalog data."""
from __future__ import annotations
import csv
from collections import Counter,defaultdict
from pathlib import Path

CORES=Path('data/catalog/conaliteg_title_cores.csv')
OUT=Path('data/catalog/ciencias_naturales_family_inventory.csv')
REPORT=Path('data/catalog/ciencias_naturales_family_inventory.md')
VERSION='CN_FAMILY_INVENTORY_0.1'
TARGET='ciencias naturales'

def main():
    rows=[r for r in csv.DictReader(CORES.open(encoding='utf-8')) if r['title_core_normalized']==TARGET]
    if len(rows)!=37:raise SystemExit(f'expected 37 Ciencias Naturales viewers from title-core summary, found {len(rows)}')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    out=[]
    for r in rows:out.append({'inventory_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'viewer_title':r['viewer_title'],'audit_status':'catalog_title_verified','corpus_status':'not_yet_audited' if r['viewer_key'] not in {'H1972P4CI077','H1972P5CI084','H1972P6CI090','H1988P4CI119','H1988P5CI123','H1988P6CI128','H1993P4CI191','H1993P5CI200','H1993P6CI209','H1993P6CI210','H2014P4CNA','H2014P5CNA','H2014P6CNA'} else 'pilot_or_expansion_audited'})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    gens=defaultdict(Counter)
    for r in out:gens[r['catalog_generation']][r['grade_code']]+=1
    lines=['# Familia completa “Ciencias Naturales” en el Catálogo Histórico CONALITEG','',f'Versión: `{VERSION}`. Visores: **{len(out)}**.','', '## Cobertura generación × grado']
    for g in sorted(gens,key=int):
        cells=', '.join(f'{grade}º={n}' for grade,n in sorted(gens[g].items(),key=lambda x:int(x[0])))
        lines.append(f'- {g}: {cells}.')
    audited=sum(r['corpus_status']=='pilot_or_expansion_audited' for r in out)
    lines+=['',f'Objetos ya cubiertos por el piloto CN5 o la expansión CN4/CN6 actual: **{audited}/{len(out)}**.','', '## Regla','La familia se define sólo por coincidencia del título nuclear normalizado `ciencias naturales`. Materiales relacionados con títulos distintos —por ejemplo *Ciencias Naturales y desarrollo humano*— se registran aparte y pueden incorporarse por relación histórica, no por forzar su título a la familia.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
