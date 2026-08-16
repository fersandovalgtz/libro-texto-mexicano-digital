#!/usr/bin/env python3
"""Per-book OCR for reconciled LTMD-U1 W1 2008 manifests.

Reuses the exact adaptive OCR process already used for W1 1966 after adapting
only the manifest field names. Source bytes remain temporary.
"""
from __future__ import annotations
import argparse,csv,tempfile
from pathlib import Path
from ocr_ltmd_u1_w1_1966_book import process,FIELDS

MAN=Path('data/catalog/ltmd_u1_w1_2008_page_manifest.csv')
VERSION='LTMD_U1_W1_2008_OCR_0.1'
BOOKS={'LTMD-CN3-G2008','LTMD-CN4-G2008'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--book-id',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w1_2008_ocr');args=ap.parse_args()
    if args.book_id not in BOOKS:raise SystemExit('unexpected W1 2008 book')
    raw=[r for r in csv.DictReader(MAN.open(encoding='utf-8')) if r['book_id']==args.book_id and r['effective_asset_status'].startswith('source_jpeg')]
    rows=[]
    for r in raw:
        x=dict(r);x['source_asset_url']=r['effective_source_asset_url'];x['asset_status']=r['effective_asset_status'];x['grade_code']=r['grade'];rows.append(x)
    if not rows:raise SystemExit(f'no effective source rows for {args.book_id}')
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w1-2008-ocr-') as td:
        out=[]
        for r in rows:
            z=process(r,Path(td));z['ocr_version']=VERSION;out.append(z)
    out.sort(key=lambda r:int(r['viewer_page']))
    verified=sum(str(r['source_sha256_verified'])=='1' for r in out);unresolved=sum(r['ocr_class']=='unresolved' for r in out)
    if verified!=len(out) or unresolved:raise SystemExit(f'{args.book_id}: sha={verified}/{len(out)} unresolved={unresolved}')
    d=Path(args.output_dir);d.mkdir(parents=True,exist_ok=True);p=d/f"ocr_{args.book_id.lower()}.csv"
    with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    print(f'{args.book_id}: pages={len(out)} sha={verified} text={sum(r["ocr_class"]=="text_detected" for r in out)} no_text={sum(r["ocr_class"]=="no_text_detected" for r in out)} unresolved=0')

if __name__=='__main__':main()
