#!/usr/bin/env python3
"""Combine and audit the 19 per-book OCR shards of CN Wave 2."""
from __future__ import annotations
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path

QUEUE=Path('data/expansion/cn_wave2_ingestion_queue.csv')
MAN=Path('data/expansion/cn_wave2_page_manifest.csv')
OUT=Path('data/expansion/cn_wave2_ocr_page_metrics.csv')
SUMMARY=Path('data/expansion/cn_wave2_ocr_summary.csv')
REPORT=Path('data/expansion/cn_wave2_ocr_report.md')
VERSION='CN_WAVE2_OCR_0.1'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/cn_wave2_ocr');args=ap.parse_args()
    queue=list(csv.DictReader(QUEUE.open(encoding='utf-8')));books={r['book_id']:r for r in queue}
    if len(books)!=19:raise SystemExit(f'expected 19 queued books, got {len(books)}')
    manifest=list(csv.DictReader(MAN.open(encoding='utf-8')));expected={(r['book_id'],r['page_id']) for r in manifest if r['asset_status']=='source_jpeg'}
    if len(expected)!=3177:raise SystemExit(f'expected 3177 Wave2 source pages, got {len(expected)}')
    files=sorted(Path(args.input_dir).rglob('ocr_*.csv'))
    if len(files)!=19:raise SystemExit(f'expected 19 OCR shard CSVs, got {len(files)}')
    rows=[];seen_books=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty OCR shard {p}')
        b={r['book_id'] for r in rr};v={r['ocr_version'] for r in rr}
        if len(b)!=1 or len(v)!=1 or next(iter(v))!=VERSION:raise SystemExit(f'invalid shard {p}: books={b}, versions={v}')
        seen_books+=list(b);rows+=rr
    if set(seen_books)!=set(books) or len(seen_books)!=19:raise SystemExit(f'book coverage mismatch: {seen_books}')
    keys=[(r['book_id'],r['page_id']) for r in rows]
    if len(keys)!=len(set(keys)):raise SystemExit(f'duplicate OCR page keys: {len(keys)-len(set(keys))}')
    if set(keys)!=expected:raise SystemExit(f'OCR coverage mismatch missing={len(expected-set(keys))} extra={len(set(keys)-expected)}')
    if any(str(r['source_sha256_verified'])!='1' for r in rows):raise SystemExit('one or more Wave2 OCR rows failed SHA verification')
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=[]
    for bid in sorted(books,key=lambda b:(int(books[b]['catalog_generation']),int(books[b]['grade']))):
        rr=[r for r in rows if r['book_id']==bid];c=Counter(r['ocr_class'] for r in rr)
        summary.append({'ocr_version':VERSION,'book_id':bid,'catalog_generation':books[bid]['catalog_generation'],'grade':books[bid]['grade'],'source_pages':len(rr),'sha_verified':sum(str(r['source_sha256_verified'])=='1' for r in rr),'text_detected':c['text_detected'],'no_text_detected':c['no_text_detected'],'unresolved':c['unresolved'],'psm3':sum(str(r['selected_psm'])=='3' for r in rr),'psm11':sum(str(r['selected_psm'])=='11' for r in rr),'psm6':sum(str(r['selected_psm'])=='6' for r in rr)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    total=len(rows);text=sum(r['ocr_class']=='text_detected' for r in rows);no=sum(r['ocr_class']=='no_text_detected' for r in rows);unres=sum(r['ocr_class']=='unresolved' for r in rows)
    lines=['# OCR técnico — Ciencias Naturales Ola 2','',f'Versión: `{VERSION}`.','',f'- Libros: **{len(books)}**.\n- JPEG procesados: **{total:,}**.\n- SHA-256 verificados antes de OCR: **{total:,}/{total:,}**.\n- Texto detectado: **{text:,}/{total:,} ({100*text/total:.2f}%)**.\n- `no_text_detected`: **{no}**.\n- `unresolved`: **{unres}**.','', '## Por libro']
    for s in summary:lines.append(f"- `{s['book_id']}`: {s['text_detected']}/{s['source_pages']} text; no-text={s['no_text_detected']}; unresolved={s['unresolved']}; psm3={s['psm3']}, psm11={s['psm11']}, psm6={s['psm6']}.")
    lines+=['','## Restricción','La transcripción completa no se persiste. `text_detected` es una métrica de cobertura técnica y no equivale a exactitud CER/WER ni a validación semántica. SEMB 0.3 permanece fuera de esta ola.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
