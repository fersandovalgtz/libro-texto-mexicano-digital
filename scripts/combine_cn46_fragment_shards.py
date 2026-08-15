#!/usr/bin/env python3
"""Combine per-book CN4/CN6 FRAGSEG shards and publish integrity summaries."""
from __future__ import annotations
import argparse,csv
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

    # `fragment_sequence` is the sequence of candidate units before zero-token
    # candidates are dropped. Gaps are therefore legitimate and must not trigger
    # renumbering, because the already-materialized fragment IDs encode that sequence.
    # The integrity invariant is positive + unique + strictly ordered after sorting.
    bypage=defaultdict(list)
    for r in rows:bypage[r['page_id']].append(int(r['fragment_sequence']))
    invalid=[];gap_pages=[];missing_slots=0
    for page,seqs in bypage.items():
        s=sorted(seqs)
        if any(x<=0 for x in s) or len(s)!=len(set(s)):
            invalid.append(page);continue
        if s!=list(range(s[0],s[-1]+1)):
            gap_pages.append(page);missing_slots+=(s[-1]-s[0]+1)-len(s)
    if invalid:raise SystemExit(f'invalid nonpositive/duplicate sequences on {len(invalid)} pages')

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
    gap_path=out.with_name('cn46_fragment_sequence_gap_audit.csv')
    with gap_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['audit_version','page_id','observed_sequences','missing_sequence_slots'])
        for page in sorted(gap_pages):
            s=sorted(bypage[page]);w.writerow(['FRAGSEG_CN46_SEQ_AUDIT_0.1',page,';'.join(map(str,s)),(s[-1]-s[0]+1)-len(s)])
    report=out.with_name('cn46_fragment_manifest_report.md');allc=summary[-1]
    lines=['# FRAGSEG — expansión CN4/CN6','',f'Versión: `{VERSION}`.','',f'- Libros: **{len(BOOKS)}**.\n- Páginas con al menos un fragmento: **{allc["segmented_page_count"]:,}**.\n- Fragmentos: **{allc["fragment_count"]:,}**.\n- IDs de fragmento únicos: **{len(set(ids)):,}**.\n- Páginas con huecos legítimos de secuencia: **{len(gap_pages)}**.\n- Slots omitidos por descarte de candidatos de 0 tokens: **{missing_slots}**.','', '## Tipos candidatos']
    for t in types:lines.append(f"- `{t}`: {allc[t]:,}.")
    lines+=['','## Regla','La expansión usa `short_residual_candidate` desde su primera versión; no se reutiliza el nombre `heading_candidate`. Cada página fuente fue reconstruida y verificada por SHA-256 antes de OCR/segmentación. El texto no se persiste, sólo `text_sha256` y metadatos de unidad.','', '## Integridad de secuencia','`fragment_sequence` conserva la posición de la unidad candidata anterior al descarte de unidades de 0 tokens. Por ello pueden existir huecos sin que falten fragmentos válidos. Los IDs no se renumeran retrospectivamente; se auditan secuencias positivas y únicas y se publica la lista de páginas con huecos.','', '## Por libro']
    for r in summary[:-1]:lines.append(f"- `{r['book_id']}`: páginas={r['segmented_page_count']}; fragmentos={r['fragment_count']}.")
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(report.read_text(encoding='utf-8'))

if __name__=='__main__':main()
