#!/usr/bin/env python3
"""Combine per-book CN4/CN6 FRAGSEG shards and publish integrity summaries."""
from __future__ import annotations
import argparse,csv,glob
from collections import Counter,defaultdict
from pathlib import Path

VERSION='FRAGSEG_CN46_0.1'
BOOKS=('LTMD-CN4-G1972','LTMD-CN6-G1972','LTMD-CN4-G1988','LTMD-CN6-G1988','LTMD-CN4-G1993','LTMD-CN6-G1993-DH','LTMD-CN6-G1993-CN','LTMD-CN4-G2014','LTMD-CN6-G2014')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/cn46_fragments');ap.add_argument('--out',default='data/expansion/cn46_fragment_manifest.csv');args=ap.parse_args()
    root=Path(args.input_dir);files=sorted(root.rglob('fragment_*.csv'))
    if len(files)!=len(BOOKS):raise SystemExit(f'expected {len(BOOKS)} shard CSVs, found {len(files)}: {files}')
    rows=[];seen_books=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty shard {p}')
        b={r['book_id'] for r in rr};v={r['segmenter_version'] for r in rr}
        if len(b)!=1 or len(v)!=1 or next(iter(v))!=VERSION:raise SystemExit(f'invalid shard {p}: books={b}, versions={v}')
        seen_books+=list(b);rows+=rr
    if set(seen_books)!=set(BOOKS) or len(seen_books)!=len(BOOKS):raise SystemExit(f'book coverage mismatch {seen_books}')
    ids=[r['fragment_id'] for r in rows]
    if len(ids)!=len(set(ids)):raise SystemExit(f'duplicate fragment IDs: {len(ids)-len(set(ids))}')
    # Per-page sequence must be contiguous 1..n.
    bypage=defaultdict(list)
    for r in rows:bypage[r['page_id']].append(int(r['fragment_sequence']))
    bad=[p for p,v in bypage.items() if sorted(v)!=list(range(1,len(v)+1))]
    if bad:raise SystemExit(f'non-contiguous sequences on {len(bad)} pages')
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page']),int(r['fragment_sequence'])))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0])
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    types=sorted({r['candidate_type'] for r in rows});counts=defaultdict(Counter);pages=defaultdict(set)
    for r in rows:counts[r['book_id']][r['candidate_type']]+=1;counts['ALL'][r['candidate_type']]+=1;pages[r['book_id']].add(r['page_id']);pages['ALL'].add(r['page_id'])
    summary=[]
    for bid in list(BOOKS)+['ALL']:
        c=counts[bid];row={'segmenter_version':VERSION,'book_id':bid,'fragment_count':sum(c.values()),'segmented_page_count':len(pages[bid])};row.update({t:c[t] for t in types});summary.append(row)
    summary_path=out.with_name('cn46_fragment_manifest_summary.csv')
    with summary_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    report=out.with_name('cn46_fragment_manifest_report.md');allc=summary[-1]
    lines=['# FRAGSEG — expansión CN4/CN6','',f'Versión: `{VERSION}`.','',f'- Libros: **{len(BOOKS)}**.\n- Páginas con al menos un fragmento: **{allc["segmented_page_count"]:,}**.\n- Fragmentos: **{allc["fragment_count"]:,}**.\n- IDs de fragmento únicos: **{len(set(ids)):,}**.','', '## Tipos candidatos']
    for t in types:lines.append(f"- `{t}`: {allc[t]:,}.")
    lines+=['','## Regla','La expansión usa `short_residual_candidate` desde su primera versión; no se reutiliza el nombre `heading_candidate`. Cada página fuente fue reconstruida y verificada por SHA-256 antes de OCR/segmentación. El texto no se persiste, sólo `text_sha256` y metadatos de unidad.','', '## Por libro']
    for r in summary[:-1]:lines.append(f"- `{r['book_id']}`: páginas={r['segmented_page_count']}; fragmentos={r['fragment_count']}.")
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(report.read_text(encoding='utf-8'))

if __name__=='__main__':main()
