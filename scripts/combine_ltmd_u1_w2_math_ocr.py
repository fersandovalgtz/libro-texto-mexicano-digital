#!/usr/bin/env python3
"""Combine all 64 LTMD-U1 W2 Mathematics OCR shards with strict invariants."""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path

VERSION='LTMD_U1_W2_MATH_OCR_0.1'
MAN=Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv')
SCOPE=Path('data/catalog/ltmd_u1_w2_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w2_math_ocr_metrics.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w2_math_ocr_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w2_math_ocr.md')
EXPECTED=64

def pid(r): return f"U1-{r['viewer_key']}-P{int(r['viewer_page']):03d}"

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w2_math_ocr');args=ap.parse_args()
    scope={r['viewer_key']:r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))}
    if len(scope)!=EXPECTED: raise SystemExit(f'expected {EXPECTED} W2 viewers, found {len(scope)}')
    files=sorted(Path(args.input_dir).rglob('ocr_*.csv'))
    if len(files)!=EXPECTED: raise SystemExit(f'expected {EXPECTED} OCR shards, found {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
        if not rr: raise SystemExit(f'empty OCR shard {p}')
        keys={r['viewer_key'] for r in rr};versions={r['ocr_version'] for r in rr}
        if len(keys)!=1 or versions!={VERSION}: raise SystemExit(f'invalid OCR shard {p}')
        seen.append(next(iter(keys)));rows+=rr
    if set(seen)!=set(scope) or len(seen)!=len(set(seen)): raise SystemExit('OCR viewer coverage/duplicate mismatch')
    source=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r['asset_status']=='source_jpeg']
    expected_ids={pid(r) for r in source};got_ids=[r['page_id'] for r in rows]
    if len(rows)!=len(expected_ids) or len(set(got_ids))!=len(got_ids) or set(got_ids)!=expected_ids:
        raise SystemExit(f'OCR page coverage mismatch rows={len(rows)} expected={len(expected_ids)} unique={len(set(got_ids))}')
    if any(r['source_sha256_verified']!='1' for r in rows): raise SystemExit('one or more W2 SHA checks failed')
    if any(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in rows): raise SystemExit('one or more W2 OCR rows unresolved/error')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    by=defaultdict(list)
    for r in rows: by[r['viewer_key']].append(r)
    summaries=[]
    for key in sorted(scope,key=lambda k:(int(scope[k]['catalog_generation']),int(scope[k]['grade_code']),k)):
        rr=by[key]
        summaries.append({'ocr_version':VERSION,'viewer_key':key,'book_id':scope[key]['book_id'],'catalog_generation':scope[key]['catalog_generation'],'grade_code':scope[key]['grade_code'],'pages':len(rr),'sha_verified':sum(r['source_sha256_verified']=='1' for r in rr),'text_detected':sum(r['ocr_class']=='text_detected' for r in rr),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in rr),'unresolved':sum(r['ocr_class']=='unresolved' for r in rr),'recognized_words':sum(int(r['recognized_words'] or 0) for r in rr),'ocr_chars':sum(int(r['ocr_chars'] or 0) for r in rr)})
    with SUMMARY.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    total=len(rows);text=sum(r['ocr_class']=='text_detected' for r in rows);no=sum(r['ocr_class']=='no_text_detected' for r in rows)
    REPORT.write_text('\n'.join(['# LTMD-U1 W2 — OCR técnico de Matemáticas','',f'Versión: `{VERSION}`.','',f'- Visores procesados: **{len(summaries)}/{EXPECTED}**.\n- Páginas fuente procesadas: **{total:,}**.\n- SHA-256 verificados: **{total:,}/{total:,}**.\n- Texto detectado: **{text:,}/{total:,} ({100*text/total:.2f}%)**.\n- `no_text_detected`: **{no:,}**.\n- `unresolved`: **0**.','', 'El OCR íntegro no se persiste. Esta capa conserva sólo métricas técnicas y controles de procedencia.'])+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__': main()
