#!/usr/bin/env python3
"""Combine the two LTMD-U1 W1 1966 OCR shards with strict invariants."""
from __future__ import annotations
import argparse,csv
from pathlib import Path

VERSION='LTMD_U1_W1_1966_OCR_0.1'
MAN=Path('data/catalog/ltmd_u1_w1_1966_page_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w1_1966_ocr_metrics.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w1_1966_ocr_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w1_1966_ocr.md')
EXPECTED_BOOKS={'U1-H1966P6CI374','U1-H1966P6CI375'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w1_1966_ocr');args=ap.parse_args()
    inp=Path(args.input_dir);files=sorted(inp.glob('ocr_*.csv'))
    if len(files)!=2:raise SystemExit(f'expected 2 OCR shards, found {len(files)}')
    rows=[]
    for p in files:
        rows += list(csv.DictReader(p.open(encoding='utf-8',newline='')))
    src=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r['asset_status']=='source_jpeg']
    expected_ids={r['page_id'] for r in src}; got_ids=[r['page_id'] for r in rows]
    if len(rows)!=len(expected_ids) or len(set(got_ids))!=len(got_ids) or set(got_ids)!=expected_ids:
        raise SystemExit(f'OCR coverage mismatch rows={len(rows)} expected={len(expected_ids)} unique={len(set(got_ids))}')
    if {r['book_id'] for r in rows}!=EXPECTED_BOOKS:raise SystemExit('OCR book set mismatch')
    if any(r['ocr_version']!=VERSION for r in rows):raise SystemExit('OCR version mismatch')
    if any(str(r['source_sha256_verified'])!='1' for r in rows):raise SystemExit('one or more SHA checks failed')
    if any(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in rows):raise SystemExit('one or more OCR rows unresolved/error')
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summaries=[]
    for b in sorted(EXPECTED_BOOKS):
        rr=[r for r in rows if r['book_id']==b]
        summaries.append({'ocr_version':VERSION,'book_id':b,'pages':len(rr),'sha_verified':sum(r['source_sha256_verified']=='1' for r in rr),'text_detected':sum(r['ocr_class']=='text_detected' for r in rr),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in rr),'unresolved':sum(r['ocr_class']=='unresolved' for r in rr),'recognized_words':sum(int(r['recognized_words'] or 0) for r in rr),'ocr_chars':sum(int(r['ocr_chars'] or 0) for r in rr)})
    with SUMMARY.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    total=len(rows); text=sum(r['ocr_class']=='text_detected' for r in rows); no=sum(r['ocr_class']=='no_text_detected' for r in rows)
    REPORT.write_text('\n'.join(['# LTMD-U1 W1 — OCR técnico 1966','',f'Versión: `{VERSION}`.','',f'- Páginas fuente procesadas: **{total}**.\n- SHA-256 verificados: **{total}/{total}**.\n- Texto detectado: **{text}/{total} ({100*text/total:.2f}%)**.\n- `no_text_detected`: **{no}**.\n- `unresolved`: **0**.','', 'El OCR íntegro no se persiste. Esta capa conserva sólo métricas técnicas y provenance checks.'])+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
