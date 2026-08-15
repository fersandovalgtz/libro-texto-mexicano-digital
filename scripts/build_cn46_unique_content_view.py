#!/usr/bin/env python3
"""Build reversible unique-content metadata for CN4/CN6 fragment occurrences.

Does not remove any row. Assigns a stable content-unit ID per `text_sha256`, counts
occurrences/books/pages, and produces object-level duplicate-pressure diagnostics.
"""
from __future__ import annotations
import csv,hashlib
from collections import Counter,defaultdict
from pathlib import Path

MAN=Path('data/expansion/cn46_fragment_manifest.csv')
UNITS=Path('data/expansion/cn46_unique_content_units.csv')
OCC=Path('data/expansion/cn46_fragment_unique_content_map.csv')
SUMMARY=Path('data/expansion/cn46_unique_content_summary.csv')
REPORT=Path('data/expansion/cn46_unique_content_report.md')
VERSION='CN46_UNIQUE_CONTENT_0.1'

def uid(textsha):return 'CNU-'+hashlib.sha256(('LTMD|CN46|'+textsha).encode()).hexdigest()[:20].upper()

def main():
    rows=list(csv.DictReader(MAN.open(encoding='utf-8')))
    if len(rows)!=19067:raise SystemExit(f'expected 19067 fragments, found {len(rows)}')
    groups=defaultdict(list)
    for r in rows:groups[r['text_sha256']].append(r)
    unit_rows=[];occ_rows=[]
    for h,g in sorted(groups.items()):
        u=uid(h);books=sorted({r['book_id'] for r in g});pages={r['page_id'] for r in g};types=Counter(r['candidate_type'] for r in g)
        unit_rows.append({'view_version':VERSION,'content_unit_id':u,'text_sha256':h,'occurrence_count':len(g),'book_count':len(books),'page_count':len(pages),'books':';'.join(books),'candidate_type_variants':';'.join(sorted(types)),'cross_book_reuse':int(len(books)>1),'within_book_repeat':int(any(sum(r['book_id']==b for r in g)>1 for b in books))})
        for r in g:occ_rows.append({'view_version':VERSION,'fragment_id':r['fragment_id'],'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'candidate_type':r['candidate_type'],'token_count':r['token_count'],'text_sha256':h,'content_unit_id':u,'content_occurrence_count':len(g),'content_book_count':len(books),'cross_book_reuse':int(len(books)>1)})
    UNITS.parent.mkdir(parents=True,exist_ok=True)
    for path,data in ((UNITS,unit_rows),(OCC,occ_rows)):
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    summary=[]
    for bid in sorted({r['book_id'] for r in rows})+['ALL']:
        rr=rows if bid=='ALL' else [r for r in rows if r['book_id']==bid];hs=[r['text_sha256'] for r in rr];uniq=set(hs)
        cross={h for h in uniq if len({x['book_id'] for x in groups[h]})>1}
        summary.append({'view_version':VERSION,'book_id':bid,'fragment_occurrences':len(rr),'unique_text_units':len(uniq),'duplicate_occurrences_within_view':len(rr)-len(uniq),'cross_book_reused_unique_units':len(cross),'unique_unit_ratio':f'{len(uniq)/len(rr):.6f}'})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    allrow=summary[-1];crossunits=sum(int(r['cross_book_reuse']) for r in unit_rows);multi=sum(int(r['occurrence_count'])>1 for r in unit_rows)
    lines=['# Vista reversible de contenido único — CN4/CN6','',f'Versión: `{VERSION}`.','',f'- Ocurrencias de fragmento conservadas: **{len(rows):,}**.\n- Unidades textuales únicas por SHA normalizado: **{allrow["unique_text_units"]:,}**.\n- Unidades que aparecen más de una vez: **{multi:,}**.\n- Unidades compartidas entre ≥2 libros: **{crossunits:,}**.\n- Ratio global unidades únicas / ocurrencias: **{100*float(allrow["unique_unit_ratio"]):.1f}%**.','', '## Por libro']
    for r in summary[:-1]:lines.append(f"- `{r['book_id']}`: ocurrencias={r['fragment_occurrences']}; textos únicos={r['unique_text_units']} ({100*float(r['unique_unit_ratio']):.1f}%); unidades compartidas con otro libro={r['cross_book_reused_unique_units']}.")
    lines+=['','## Regla','`content_unit_id` agrupa únicamente igualdad exacta de `text_sha256`. Todas las ocurrencias originales permanecen en el corpus y la vista es reversible. No se interpretan coincidencias como equivalencia histórica o pedagógica sin contexto documental.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
