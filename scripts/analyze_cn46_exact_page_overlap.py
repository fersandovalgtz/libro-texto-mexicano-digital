#!/usr/bin/env python3
"""Analyze exact SHA-256 page overlap among CN4/CN6 expansion books.

Requires the complete hashed page manifest. Exact byte identity is treated as a
technical/documentary signal only; it does not by itself establish edition identity.
"""
from __future__ import annotations
import csv,itertools
from pathlib import Path

MAN=Path('data/expansion/cn46_page_manifest.csv')
OUT=Path('data/expansion/cn46_exact_page_overlap.csv')
REPORT=Path('data/expansion/cn46_exact_page_overlap.md')
VERSION='CN46_EXACT_OVERLAP_0.1'

def main():
    rows=[r for r in csv.DictReader(MAN.open(encoding='utf-8')) if r['asset_status']=='source_jpeg']
    if len(rows)!=1888:raise SystemExit(f'expected 1888 hashed source pages, found {len(rows)}')
    if any(not r['sha256'] for r in rows):raise SystemExit('incomplete hashes')
    bybook={}
    for r in rows:bybook.setdefault(r['book_id'],[]).append(r)
    results=[]
    for a,b in itertools.combinations(sorted(bybook),2):
        aa=bybook[a];bb=bybook[b]
        ha={r['sha256'] for r in aa};hb={r['sha256'] for r in bb};inter=ha&hb
        amap={int(r['viewer_page']):r['sha256'] for r in aa};bmap={int(r['viewer_page']):r['sha256'] for r in bb}
        common_pos=set(amap)&set(bmap);aligned=sum(amap[p]==bmap[p] for p in common_pos)
        results.append({'overlap_version':VERSION,'book_a':a,'book_b':b,'pages_a':len(aa),'pages_b':len(bb),'exact_shared_hashes':len(inter),'share_of_a':f'{len(inter)/len(aa):.6f}','share_of_b':f'{len(inter)/len(bb):.6f}','common_viewer_positions':len(common_pos),'aligned_exact_matches':aligned,'aligned_match_rate':f'{aligned/len(common_pos):.6f}' if common_pos else ''})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    top=sorted(results,key=lambda r:(int(r['exact_shared_hashes']),float(r['aligned_match_rate'] or 0)),reverse=True)
    lines=['# Solapamiento exacto de páginas — expansión CN4/CN6','',f'Versión: `{VERSION}`. Comparación por SHA-256 sobre **{len(rows):,}** JPEG fuente.','', '## Pares con identidad exacta detectable']
    shown=0
    for r in top:
        if int(r['exact_shared_hashes'])==0:continue
        shown+=1
        lines.append(f"- `{r['book_a']}` ↔ `{r['book_b']}`: hashes compartidos={r['exact_shared_hashes']}; alineados exactos={r['aligned_exact_matches']}/{r['common_viewer_positions']} ({float(r['aligned_match_rate'])*100:.1f}%).")
    if not shown:lines.append('- Ningún par comparte páginas byte-idénticas.')
    lines+=['','## Interpretación','Una coincidencia SHA-256 prueba identidad binaria de una página recuperada desde dos rutas de visor. Un solapamiento alto puede revelar reutilización/republicación documental; no autoriza por sí solo a fusionar libros o asignarles la misma edición bibliográfica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
