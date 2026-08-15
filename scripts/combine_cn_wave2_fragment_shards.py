#!/usr/bin/env python3
"""Combine per-book CN Wave 2 FRAGSEG shards with conservative integrity checks."""
from __future__ import annotations
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path

QUEUE=Path('data/expansion/cn_wave2_ingestion_queue.csv')
STRUCT=Path('data/expansion/cn_wave2_page_structure.csv')
OUT=Path('data/expansion/cn_wave2_fragment_manifest.csv')
SUMMARY=Path('data/expansion/cn_wave2_fragment_manifest_summary.csv')
GAPS=Path('data/expansion/cn_wave2_fragment_sequence_gaps.csv')
REPORT=Path('data/expansion/cn_wave2_fragment_manifest_report.md')
VERSION='FRAGSEG_CN_WAVE2_0.1';ELIGIBLE={'textual','mixed_text_image'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/cn_wave2_fragments');args=ap.parse_args()
    queue=list(csv.DictReader(QUEUE.open(encoding='utf-8')));books={r['book_id']:r for r in queue}
    if len(books)!=19:raise SystemExit(f'expected 19 books, got {len(books)}')
    structure=list(csv.DictReader(STRUCT.open(encoding='utf-8')));eligible={(r['book_id'],r['page_id']) for r in structure if r['primary_structure'] in ELIGIBLE}
    files=sorted(p for p in Path(args.input_dir).rglob('fragment_*.csv') if not p.name.endswith('_failures.csv'))
    failfiles=sorted(Path(args.input_dir).rglob('fragment_*_failures.csv'))
    if len(files)!=19 or len(failfiles)!=19:raise SystemExit(f'expected 19 fragment and 19 failure shards, got {len(files)} / {len(failfiles)}')
    rows=[];seen_books=[];empty_pages=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty fragment shard {p}')
        b={r['book_id'] for r in rr};v={r['segmenter_version'] for r in rr}
        if len(b)!=1 or len(v)!=1 or next(iter(v))!=VERSION:raise SystemExit(f'invalid shard {p}')
        seen_books+=list(b);rows+=rr
    for p in failfiles:
        for r in csv.DictReader(p.open(encoding='utf-8')):
            if r['status']!='ok':raise SystemExit(f"fatal FRAGSEG failure persisted: {r}")
            empty_pages.append((r['book_id'],r['page_id']))
    if set(seen_books)!=set(books) or len(seen_books)!=19:raise SystemExit(f'book coverage mismatch {seen_books}')
    ids=[r['fragment_id'] for r in rows]
    if len(ids)!=len(set(ids)):raise SystemExit(f'duplicate fragment IDs: {len(ids)-len(set(ids))}')
    pagekeys={(r['book_id'],r['page_id']) for r in rows}|set(empty_pages)
    if pagekeys!=eligible:raise SystemExit(f'eligible PAGESTRUCT coverage mismatch missing={len(eligible-pagekeys)} extra={len(pagekeys-eligible)}')
    bypage=defaultdict(list)
    for r in rows:bypage[(r['book_id'],r['page_id'])].append(int(r['fragment_sequence']))
    gaprows=[]
    for (bid,pid),vals in sorted(bypage.items()):
        sv=sorted(vals)
        if any(v<=0 for v in sv) or len(sv)!=len(set(sv)):raise SystemExit(f'invalid fragment sequence {bid} {pid}: {sv}')
        missing=[x for x in range(1,max(sv)+1) if x not in set(sv)] if sv else []
        if missing:gaprows.append({'book_id':bid,'page_id':pid,'observed_fragment_count':len(sv),'max_sequence':max(sv),'missing_sequence_slots':' '.join(map(str,missing)),'missing_slot_count':len(missing)})
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page']),int(r['fragment_sequence'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    if gaprows:
        with GAPS.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(gaprows[0]));w.writeheader();w.writerows(gaprows)
    else:GAPS.write_text('book_id,page_id,observed_fragment_count,max_sequence,missing_sequence_slots,missing_slot_count\n',encoding='utf-8')
    types=sorted({r['candidate_type'] for r in rows});counts=defaultdict(Counter);pages=defaultdict(set)
    for r in rows:counts[r['book_id']][r['candidate_type']]+=1;counts['ALL'][r['candidate_type']]+=1;pages[r['book_id']].add(r['page_id']);pages['ALL'].add(r['page_id'])
    summary=[]
    for bid in sorted(books,key=lambda b:(int(books[b]['catalog_generation']),int(books[b]['grade'])))+['ALL']:
        c=counts[bid];row={'segmenter_version':VERSION,'book_id':bid,'fragment_count':sum(c.values()),'segmented_page_count':len(pages[bid])};row.update({t:c[t] for t in types});summary.append(row)
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    allc=summary[-1];gap_slots=sum(int(r['missing_slot_count']) for r in gaprows)
    lines=['# FRAGSEG — Ciencias Naturales Ola 2','',f'Versión: `{VERSION}`.','',f'- Libros: **{len(books)}**.\n- Páginas elegibles PAGESTRUCT: **{len(eligible):,}**.\n- Páginas con ≥1 fragmento: **{allc["segmented_page_count"]:,}**.\n- Páginas elegibles sin fragmentos: **{len(empty_pages)}**.\n- Fragmentos: **{allc["fragment_count"]:,}**.\n- IDs únicos: **{len(set(ids)):,}**.\n- Páginas con huecos legítimos de secuencia: **{len(gaprows)}**.\n- Slots omitidos: **{gap_slots}**.','', '## Tipos candidatos']
    for t in types:lines.append(f'- `{t}`: {allc[t]:,}.')
    lines+=['','## Regla','`fragment_sequence` conserva la posición previa al descarte de candidatos de 0 tokens; por eso se admiten huecos positivos y auditados sin renumerar IDs. Cualquier fallo de descarga, SHA u OCR de ejecución hace fallar el shard. El texto completo no se persiste. Esta capa sigue siendo técnica, no `semantic_ready`.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
