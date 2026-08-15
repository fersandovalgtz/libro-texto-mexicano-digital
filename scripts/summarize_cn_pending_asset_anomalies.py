#!/usr/bin/env python3
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

SRC=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
OUT=Path('data/catalog/ciencias_naturales_pending_asset_anomaly_summary.md')

def compress(xs):
    xs=sorted(xs)
    if not xs:return '—'
    out=[];a=b=xs[0]
    for x in xs[1:]:
        if x==b+1:b=x;continue
        out.append(str(a) if a==b else f'{a}-{b}');a=b=x
    out.append(str(a) if a==b else f'{a}-{b}')
    return ', '.join(out)

def main():
    rows=list(csv.DictReader(SRC.open(encoding='utf-8')))
    bad=[r for r in rows if r['asset_status']=='internal_missing']
    by=defaultdict(list)
    for r in bad:by[(r['book_id'],r['viewer_key'])].append(int(r['viewer_page']))
    lines=['# Resumen compacto de anomalías de activos — Ciencias Naturales','',f'Huecos internos: **{len(bad)}** en **{len(by)} objetos**.','']
    for (bid,key),pages in sorted(by.items()):lines.append(f'- `{bid}` / `{key}`: {len(pages)} huecos — VP {compress(pages)}.')
    OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(OUT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
