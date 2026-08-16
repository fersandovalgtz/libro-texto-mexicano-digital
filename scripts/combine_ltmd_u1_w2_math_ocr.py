#!/usr/bin/env python3
"""Combine LTMD-U1 W2 Mathematics OCR 0.2 canonical shards with strict invariants."""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path

VERSION='LTMD_U1_W2_MATH_OCR_0.2'
MAN=Path('data/catalog/ltmd_u1_w2_math_reconciled_manifest.csv')
REC_SUMMARY=Path('data/catalog/ltmd_u1_w2_math_reconciled_summary.csv')
ALIASES=Path('data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv')
SCOPE=Path('data/catalog/ltmd_u1_w2_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w2_math_ocr_metrics.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w2_math_ocr_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w2_math_ocr.md')
EXPECTED_SCOPE=64
EXPECTED_READY=60
EXPECTED_ALIASES=3
EXPECTED_CANONICAL=57

def pid(r): return f"U1-{r['viewer_key']}-P{int(r['viewer_page']):03d}"

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w2_math_ocr');args=ap.parse_args()
    scope={r['viewer_key']:r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))}
    rec={r['viewer_key']:r for r in csv.DictReader(REC_SUMMARY.open(encoding='utf-8'))}
    aliases=list(csv.DictReader(ALIASES.open(encoding='utf-8')))
    if len(scope)!=EXPECTED_SCOPE or len(rec)!=EXPECTED_SCOPE: raise SystemExit('W2 scope/reconciled summary cardinality mismatch')
    ready={k for k,r in rec.items() if r['effective_asset_ready']=='1'}
    alias={r['viewer_key'] for r in aliases if r.get('all_effective_pages_byte_identical_aligned')=='1'}
    canonical=ready-alias
    if len(ready)!=EXPECTED_READY or len(alias)!=EXPECTED_ALIASES or len(canonical)!=EXPECTED_CANONICAL:
        raise SystemExit(f'W2 topology mismatch ready={len(ready)} alias={len(alias)} canonical={len(canonical)}')
    files=sorted(Path(args.input_dir).rglob('ocr_*.csv'))
    if len(files)!=EXPECTED_CANONICAL: raise SystemExit(f'expected {EXPECTED_CANONICAL} OCR shards, found {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
        if not rr: raise SystemExit(f'empty OCR shard {p}')
        keys={r['viewer_key'] for r in rr};versions={r['ocr_version'] for r in rr}
        if len(keys)!=1 or versions!={VERSION}: raise SystemExit(f'invalid OCR shard {p}')
        seen.append(next(iter(keys)));rows+=rr
    if set(seen)!=canonical or len(seen)!=len(set(seen)): raise SystemExit('OCR canonical viewer coverage/duplicate mismatch')
    source=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r['viewer_key'] in canonical and r['effective_asset_status'] in ('source_jpeg','source_jpeg_recovered')]
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
    for key in sorted(canonical,key=lambda k:(int(scope[k]['catalog_generation']),int(scope[k]['grade_code']),k)):
        rr=by[key]
        summaries.append({'ocr_version':VERSION,'viewer_key':key,'book_id':scope[key]['book_id'],'catalog_generation':scope[key]['catalog_generation'],'grade_code':scope[key]['grade_code'],'pages':len(rr),'sha_verified':sum(r['source_sha256_verified']=='1' for r in rr),'text_detected':sum(r['ocr_class']=='text_detected' for r in rr),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in rr),'unresolved':sum(r['ocr_class']=='unresolved' for r in rr),'recognized_words':sum(int(r['recognized_words'] or 0) for r in rr),'ocr_chars':sum(int(r['ocr_chars'] or 0) for r in rr)})
    with SUMMARY.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    total=len(rows);text=sum(r['ocr_class']=='text_detected' for r in rows);no=sum(r['ocr_class']=='no_text_detected' for r in rows)
    unresolved_viewers=EXPECTED_SCOPE-EXPECTED_READY
    REPORT.write_text('\n'.join(['# LTMD-U1 W2 — OCR técnico de Matemáticas','',f'Versión: `{VERSION}`.','',f'- Visores canónicos procesados: **{len(summaries)}/{EXPECTED_CANONICAL}**.',f'- Identidades de catálogo efectivamente representadas por esos contenidos: **{EXPECTED_READY}/{EXPECTED_SCOPE}**.',f'- Aliases exactos cubiertos sin recomputar OCR: **{EXPECTED_ALIASES}**.',f'- Excepciones de routing aún no resueltas: **{unresolved_viewers}**.',f'- Páginas fuente canónicas procesadas: **{total:,}**.',f'- SHA-256 verificados: **{total:,}/{total:,}**.',f'- Texto detectado: **{text:,}/{total:,} ({100*text/total:.2f}%)**.',f'- `no_text_detected`: **{no:,}**.',f'- `unresolved` en contenidos procesados: **0**.','', 'El OCR íntegro no se persiste. Esta capa conserva sólo métricas técnicas y controles de procedencia. Los cuatro DMA 2018 no se imputan ni se procesan mientras permanezcan sin resolución suficiente.'])+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__': main()
