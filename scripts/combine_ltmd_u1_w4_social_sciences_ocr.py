#!/usr/bin/env python3
"""Combine LTMD-U1 W4 Social Sciences OCR shards with strict invariants."""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path

VERSION='LTMD_U1_W4_SOCIAL_SCIENCES_OCR_0.1'
MAN=Path('data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv')
PROC=Path('data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv')
OUT=Path('data/catalog/ltmd_u1_w4_social_sciences_ocr_metrics.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w4_social_sciences_ocr_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w4_social_sciences_ocr.md')
EXPECTED_IDENTITIES=14
EXPECTED_CANONICAL=14
EXPECTED_SOURCE_PAGES=2414

def pid(r):return f"U1-{r['viewer_key']}-P{int(r['viewer_page']):03d}"

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w4_social_sciences_ocr');a=ap.parse_args()
    proc_rows=list(csv.DictReader(PROC.open(encoding='utf-8',newline='')));proc={r['viewer_key']:r for r in proc_rows}
    if len(proc_rows)!=EXPECTED_IDENTITIES or len(proc)!=EXPECTED_IDENTITIES:raise SystemExit('W4 processing inventory cardinality mismatch')
    canonical={k for k,r in proc.items() if r['is_canonical_processing_object']=='1'};eligible={k for k,r in proc.items() if r['ocr_identity_eligible']=='1'}
    if canonical!=eligible or len(canonical)!=EXPECTED_CANONICAL:raise SystemExit('W4 canonical/eligible topology mismatch')
    manifest=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    if len(manifest)!=EXPECTED_SOURCE_PAGES or {r['viewer_key'] for r in manifest}!=canonical:raise SystemExit('W4 canonical page manifest mismatch')
    expected_ids={pid(r) for r in manifest}
    if len(expected_ids)!=EXPECTED_SOURCE_PAGES:raise SystemExit('duplicate W4 canonical page IDs')
    files=sorted(Path(a.input_dir).rglob('ocr_*.csv'))
    if len(files)!=EXPECTED_CANONICAL:raise SystemExit(f'expected {EXPECTED_CANONICAL} OCR shards, found {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
        if not rr:raise SystemExit(f'empty OCR shard {p}')
        keys={r['viewer_key'] for r in rr};versions={r['ocr_version'] for r in rr}
        if len(keys)!=1 or versions!={VERSION}:raise SystemExit(f'invalid W4 OCR shard {p}')
        seen.append(next(iter(keys)));rows+=rr
    if set(seen)!=canonical or len(seen)!=len(set(seen)):raise SystemExit('W4 OCR viewer coverage mismatch')
    got=[r['page_id'] for r in rows]
    if len(rows)!=EXPECTED_SOURCE_PAGES or len(set(got))!=len(got) or set(got)!=expected_ids:raise SystemExit('W4 OCR page coverage mismatch')
    if any(r['source_sha256_verified']!='1' for r in rows):raise SystemExit('W4 SHA verification failure')
    if any(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in rows):raise SystemExit('W4 unresolved OCR row')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    by=defaultdict(list)
    for r in rows:by[r['viewer_key']].append(r)
    summaries=[]
    for k in sorted(canonical,key=lambda k:(int(proc[k]['catalog_generation']),int(proc[k]['grade_code']),k)):
        rr=by[k];summaries.append({'ocr_version':VERSION,'viewer_key':k,'catalog_generation':proc[k]['catalog_generation'],'grade_code':proc[k]['grade_code'],'title_core':proc[k]['title_core'],'processing_mode':proc[k]['processing_mode'],'pages':len(rr),'sha_verified':sum(r['source_sha256_verified']=='1' for r in rr),'text_detected':sum(r['ocr_class']=='text_detected' for r in rr),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in rr),'unresolved':sum(r['ocr_class']=='unresolved' for r in rr),'recognized_words':sum(int(r['recognized_words'] or 0) for r in rr),'ocr_chars':sum(int(r['ocr_chars'] or 0) for r in rr)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    text=sum(r['ocr_class']=='text_detected' for r in rows);no_text=sum(r['ocr_class']=='no_text_detected' for r in rows)
    lines=['# LTMD-U1 W4 — OCR técnico Ciencias Sociales','',f'Versión: `{VERSION}`.','',f'- Identidades procesadas: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}**.',f'- Objetos canónicos: **{EXPECTED_CANONICAL}**.',f'- Páginas fuente canónicas: **{len(rows):,}**.',f'- SHA-256 verificados: **{len(rows):,}/{len(rows):,}**.',f'- Texto detectado: **{text:,}/{len(rows):,} ({100*text/len(rows):.2f}%)**.',f'- `no_text_detected`: **{no_text:,}**.','- `unresolved`: **0**.','','El OCR íntegro no se persiste. Esta capa conserva métricas técnicas y provenance; la confianza interna de Tesseract no equivale a exactitud textual validada.','','## Límite epistemológico','', 'El proyecto opera temporalmente sin referencia humana. Este producto puede alimentar PAGESTRUCT/FRAGSEG y análisis técnicos de dependencia, pero no valida categorías semánticas ni autoriza conclusiones históricas basadas en clasificación automática no validada.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
