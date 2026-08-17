#!/usr/bin/env python3
"""Combine LTMD-U1 W8 Artes OCR shards with strict invariants."""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path

VERSION='LTMD_U1_W8_ARTES_OCR_0.1'
MAN=Path('data/catalog/ltmd_u1_w8_canonical_page_manifest.csv')
PROC=Path('data/catalog/ltmd_u1_w8_processing_inventory.csv')
OUT=Path('data/catalog/ltmd_u1_w8_artes_ocr_metrics.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w8_artes_ocr_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w8_artes_ocr.md')
EXPECTED_IDENTITIES=20;EXPECTED_CANONICAL=16;EXPECTED_RETAINED=4;EXPECTED_SOURCE_PAGES=1490

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w8_artes_ocr');a=ap.parse_args()
    pr=list(csv.DictReader(PROC.open(encoding='utf-8',newline='')));proc={r['viewer_key']:r for r in pr}
    if len(pr)!=EXPECTED_IDENTITIES or len(proc)!=EXPECTED_IDENTITIES:raise SystemExit('W8 processing inventory cardinality mismatch')
    canonical={k for k,r in proc.items() if r['is_canonical_processing_object']=='1'};eligible={k for k,r in proc.items() if r['ocr_identity_eligible']=='1'}
    if canonical!=eligible or len(canonical)!=EXPECTED_CANONICAL:raise SystemExit('W8 canonical/eligible topology mismatch')
    withheld={k for k,r in proc.items() if r['ocr_identity_eligible']=='0'}
    if len(withheld)!=EXPECTED_RETAINED:raise SystemExit('W8 withheld identity count mismatch')
    if any(proc[k]['processing_mode']!='direct_canonical' for k in canonical) or any(proc[k]['processing_mode']!='withheld_source' for k in withheld):raise SystemExit('W8 processing mode mismatch')
    man=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    if len(man)!=EXPECTED_SOURCE_PAGES or {r['viewer_key'] for r in man}!=canonical:raise SystemExit('W8 canonical page manifest mismatch')
    expected={r['page_id'] for r in man}
    if len(expected)!=EXPECTED_SOURCE_PAGES:raise SystemExit('duplicate W8 canonical page IDs')
    files=sorted(Path(a.input_dir).rglob('ocr_*.csv'))
    if len(files)!=EXPECTED_CANONICAL:raise SystemExit(f'expected {EXPECTED_CANONICAL} OCR shards, found {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
        if not rr:raise SystemExit(f'empty OCR shard {p}')
        keys={r['viewer_key'] for r in rr};versions={r['ocr_version'] for r in rr}
        if len(keys)!=1 or versions!={VERSION}:raise SystemExit(f'invalid W8 OCR shard {p}')
        seen.append(next(iter(keys)));rows+=rr
    if set(seen)!=canonical or len(seen)!=len(set(seen)):raise SystemExit('W8 OCR viewer coverage mismatch')
    got=[r['page_id'] for r in rows]
    if len(rows)!=EXPECTED_SOURCE_PAGES or len(set(got))!=len(got) or set(got)!=expected:raise SystemExit('W8 OCR page coverage mismatch')
    if any(r['source_sha256_verified']!='1' for r in rows):raise SystemExit('W8 SHA verification failure')
    if any(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in rows):raise SystemExit('W8 unresolved OCR row')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    by=defaultdict(list)
    for r in rows:by[r['viewer_key']].append(r)
    summaries=[]
    for k in sorted(canonical,key=lambda k:(int(proc[k]['catalog_generation']),int(proc[k]['grade_code']),k)):
        rr=by[k];summaries.append({'ocr_version':VERSION,'viewer_key':k,'catalog_generation':proc[k]['catalog_generation'],'grade_code':proc[k]['grade_code'],'title_core':proc[k]['title_core'],'processing_mode':proc[k]['processing_mode'],'pages':len(rr),'sha_verified':sum(r['source_sha256_verified']=='1' for r in rr),'text_detected':sum(r['ocr_class']=='text_detected' for r in rr),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in rr),'unresolved':sum(r['ocr_class']=='unresolved' for r in rr),'recognized_words':sum(int(r['recognized_words'] or 0) for r in rr),'ocr_chars':sum(int(r['ocr_chars'] or 0) for r in rr)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    text=sum(r['ocr_class']=='text_detected' for r in rows);no_text=sum(r['ocr_class']=='no_text_detected' for r in rows);retained=', '.join(f'`{k}`' for k in sorted(withheld))
    lines=['# LTMD-U1 W8 — OCR técnico Artes','',f'Versión: `{VERSION}`.','',f'- Identidades W8 preservadas: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}**.',f'- Objetos canónicos procesados: **{EXPECTED_CANONICAL}**.',f'- Identidades retenidas por fuente: **{EXPECTED_RETAINED}**.',f'- Páginas fuente canónicas: **{len(rows):,}**.',f'- SHA-256 verificados: **{len(rows):,}/{len(rows):,}**.',f'- Texto detectado: **{text:,}/{len(rows):,} ({100*text/len(rows):.2f}%)**.',f'- `no_text_detected`: **{no_text:,}**.','- `unresolved`: **0**.','','El OCR íntegro no se persiste. Esta capa conserva métricas técnicas y procedencia; la confianza interna de Tesseract no equivale a exactitud textual validada.','','## Retenciones de fuente','',retained+'.','','Los cuatro visores 2018 no se imputan, sustituyen ni reconstruyen mediante 2019 u otras ediciones.','','## Límite epistemológico','','Este producto habilita PAGESTRUCT/FRAGSEG para la cohorte admitida, pero no demuestra continuidad curricular, equivalencia documental, cambio histórico ni categorías semánticas sin validación humana independiente.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
