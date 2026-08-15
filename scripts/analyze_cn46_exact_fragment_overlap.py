#!/usr/bin/env python3
"""Analyze exact normalized-text SHA overlap among CN4/CN6 fragment manifests.

`text_sha256` represents the normalized fragment text produced ephemerally during
FRAGSEG. Exact matches are used only as document-dependence signals; no source text
is reconstructed or persisted here.
"""
from __future__ import annotations
import csv,itertools
from collections import defaultdict
from pathlib import Path

MAN=Path('data/expansion/cn46_fragment_manifest.csv')
OUT=Path('data/expansion/cn46_exact_fragment_overlap.csv')
REPORT=Path('data/expansion/cn46_exact_fragment_overlap.md')
CN4OUT=Path('data/expansion/cn4_1972_1988_fragment_reuse.csv')
VERSION='CN46_FRAGMENT_OVERLAP_0.1'
A='LTMD-CN4-G1972';B='LTMD-CN4-G1988'

def main():
    rows=list(csv.DictReader(MAN.open(encoding='utf-8')))
    if len(rows)!=19067:raise SystemExit(f'expected 19067 fragments, found {len(rows)}')
    bybook=defaultdict(list)
    for r in rows:bybook[r['book_id']].append(r)
    results=[]
    for a,b in itertools.combinations(sorted(bybook),2):
        aa=bybook[a];bb=bybook[b];ha={r['text_sha256'] for r in aa};hb={r['text_sha256'] for r in bb};inter=ha&hb
        results.append({'overlap_version':VERSION,'book_a':a,'book_b':b,'fragments_a':len(aa),'fragments_b':len(bb),'unique_text_hashes_a':len(ha),'unique_text_hashes_b':len(hb),'shared_text_hashes':len(inter),'share_unique_a':f'{len(inter)/len(ha):.6f}','share_unique_b':f'{len(inter)/len(hb):.6f}'})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)

    # CN4 72/88: preserve each fragment occurrence and mark whether its exact text
    # appears in the other object. This is reversible and does not deduplicate rows.
    ha={r['text_sha256'] for r in bybook[A]};hb={r['text_sha256'] for r in bybook[B]}
    cn=[]
    for r in bybook[A]+bybook[B]:
        other=hb if r['book_id']==A else ha
        cn.append({'analysis_version':VERSION,'book_id':r['book_id'],'page_id':r['page_id'],'viewer_page':r['viewer_page'],'fragment_id':r['fragment_id'],'candidate_type':r['candidate_type'],'token_count':r['token_count'],'text_sha256':r['text_sha256'],'exact_text_present_in_other_book':int(r['text_sha256'] in other)})
    with CN4OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(cn[0]));w.writeheader();w.writerows(cn)

    top=sorted(results,key=lambda r:int(r['shared_text_hashes']),reverse=True)
    lines=['# Solapamiento exacto de fragmentos — expansión CN4/CN6','',f'Versión: `{VERSION}`. Fragmentos analizados: **{len(rows):,}**.','', '## Pares con mayor número de textos exactos compartidos']
    for r in top[:15]:
        lines.append(f"- `{r['book_a']}` ↔ `{r['book_b']}`: hashes textuales compartidos={r['shared_text_hashes']}; {100*float(r['share_unique_a']):.1f}% de los textos únicos de A y {100*float(r['share_unique_b']):.1f}% de B.")
    for bid in (A,B):
        rr=[r for r in cn if r['book_id']==bid];shared=sum(int(r['exact_text_present_in_other_book']) for r in rr)
        lines.append(f"- `{bid}`: {shared}/{len(rr)} ocurrencias de fragmento ({100*shared/len(rr):.1f}%) tienen texto exacto presente en el otro CN4 1972/1988.")
    lines+=['','## Regla','Un `text_sha256` idéntico prueba identidad del texto normalizado de la unidad, no necesariamente identidad de layout ni equivalencia funcional. La deduplicación futura se implementará como vista analítica reversible y conservará todas las ocurrencias/procedencias.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
