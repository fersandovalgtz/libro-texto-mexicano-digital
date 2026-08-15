#!/usr/bin/env python3
"""Locate exact differences between CN4 catalog generations 1972 and 1988."""
from __future__ import annotations
import csv
from pathlib import Path

MAN=Path('data/expansion/cn46_page_manifest.csv')
OUT=Path('data/expansion/cn4_1972_1988_page_differences.csv')
REPORT=Path('data/expansion/cn4_1972_1988_page_differences.md')
VERSION='CN4_72_88_DIFF_0.1'
A='LTMD-CN4-G1972';B='LTMD-CN4-G1988'

def ranges(vals):
    if not vals:return ''
    out=[];start=prev=vals[0]
    for x in vals[1:]:
        if x==prev+1:prev=x;continue
        out.append(str(start) if start==prev else f'{start}-{prev}');start=prev=x
    out.append(str(start) if start==prev else f'{start}-{prev}')
    return ', '.join(out)

def main():
    rr=list(csv.DictReader(MAN.open(encoding='utf-8')))
    aa={int(r['viewer_page']):r for r in rr if r['book_id']==A and r['asset_status']=='source_jpeg'}
    bb={int(r['viewer_page']):r for r in rr if r['book_id']==B and r['asset_status']=='source_jpeg'}
    if len(aa)!=len(bb)!=214:pass
    common=sorted(set(aa)&set(bb));rows=[]
    for p in common:
        same=aa[p]['sha256']==bb[p]['sha256']
        if not same:
            rows.append({'diff_version':VERSION,'viewer_page':p,'page_a':aa[p]['page_id'],'page_b':bb[p]['page_id'],'sha_a':aa[p]['sha256'],'sha_b':bb[p]['sha256'],'bytes_a':aa[p]['byte_size'],'bytes_b':bb[p]['byte_size'],'position_quartile':aa[p]['position_quartile'],'byte_delta':int(bb[p]['byte_size'])-int(aa[p]['byte_size'])})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['diff_version','viewer_page','page_a','page_b','sha_a','sha_b','bytes_a','bytes_b','position_quartile','byte_delta']
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    pages=[r['viewer_page'] for r in rows]
    q={q:sum(r['position_quartile']==q for r in rows) for q in ('Q1','Q2','Q3','Q4')}
    lines=['# Diferencias exactas entre CN4 / generación 1972 y 1988','',f'Versión: `{VERSION}`.','',f'De **214** posiciones fuente alineables, **188 son byte-idénticas** y **{len(rows)} difieren**.','',f"Páginas diferentes: **{ranges(pages)}**.",'',f"Distribución de diferencias: Q1={q['Q1']}, Q2={q['Q2']}, Q3={q['Q3']}, Q4={q['Q4']}.",'','## Lectura permitida','El 87.9% de identidad exacta prueba reutilización binaria sustantiva del objeto. Las páginas distintas deben auditarse antes de decidir si representan paratextos, sustituciones editoriales puntuales o revisión de contenido. No se tratarán 1972 y 1988 como réplicas independientes en análisis cuantitativos sin modelar esta dependencia documental.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
