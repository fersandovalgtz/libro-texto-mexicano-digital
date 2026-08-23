#!/usr/bin/env python3
"""Combine W11 OCR shards using the published topology as the only cardinality authority."""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path

VERSION='LTMD_U1_W11_OCR_0.1'
TOPOLOGY_VERSION='LTMD_U1_W11_PROCESSING_TOPOLOGY_0.1'
PROC=Path('data/catalog/ltmd_u1_w11_processing_inventory.csv')
MAN=Path('data/catalog/ltmd_u1_w11_canonical_page_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w11_ocr_metrics.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w11_ocr_summary.csv')
REPORT=Path('docs/LTMD_U1_W11_OCR.md')
EXPECTED_IDENTITIES=111

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w11_ocr');a=ap.parse_args()
    pr=list(csv.DictReader(PROC.open(encoding='utf-8',newline='')));proc={r['viewer_key']:r for r in pr}
    if len(pr)!=EXPECTED_IDENTITIES or len(proc)!=EXPECTED_IDENTITIES:raise SystemExit('W11 processing inventory cardinality mismatch')
    if {r['topology_version'] for r in pr}!={TOPOLOGY_VERSION}:raise SystemExit('W11 topology version mismatch')
    admitted={k for k,r in proc.items() if r['source_admitted']=='1'};canonical={k for k,r in proc.items() if r['source_admitted']=='1' and r['is_canonical_processing_object']=='1'};withheld={k for k,r in proc.items() if r['source_admitted']=='0'};aliases={k for k,r in proc.items() if r['processing_mode']=='exact_source_alias'}
    if not canonical or not canonical<=admitted or admitted|withheld!=set(proc) or admitted&withheld:raise SystemExit('W11 admitted/canonical topology mismatch')
    if any(proc[k]['processing_mode']!='direct_canonical' for k in canonical):raise SystemExit('W11 canonical processing mode mismatch')
    man=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    if not man or {r['viewer_key'] for r in man}!=canonical:raise SystemExit('W11 canonical page manifest viewer mismatch')
    if {r['manifest_version'] for r in man}!={TOPOLOGY_VERSION}:raise SystemExit('W11 canonical manifest version mismatch')
    expected=[r['page_id'] for r in man]
    if len(expected)!=len(set(expected)):raise SystemExit('duplicate W11 canonical page IDs')
    files=sorted(Path(a.input_dir).rglob('ocr_*.csv'))
    if len(files)!=len(canonical):raise SystemExit(f'expected {len(canonical)} W11 OCR shards, found {len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')))
        if not rr:raise SystemExit(f'empty W11 OCR shard {p}')
        keys={r['viewer_key'] for r in rr};versions={r['ocr_version'] for r in rr}
        if len(keys)!=1 or versions!={VERSION}:raise SystemExit(f'invalid W11 OCR shard {p}')
        key=next(iter(keys));seen.append(key)
        if key not in canonical:raise SystemExit(f'noncanonical W11 OCR shard {key}')
        if len(rr)!=int(proc[key]['source_pages']):raise SystemExit(f'W11 OCR shard page count mismatch {key}: {len(rr)}/{proc[key]["source_pages"]}')
        rows+=rr
    if set(seen)!=canonical or len(seen)!=len(set(seen)):raise SystemExit('W11 OCR viewer coverage mismatch')
    got=[r['page_id'] for r in rows]
    if len(got)!=len(set(got)) or set(got)!=set(expected):raise SystemExit(f'W11 OCR page coverage mismatch rows={len(got)} expected={len(expected)}')
    if any(r['source_sha256_verified']!='1' for r in rows):raise SystemExit('W11 SHA verification failure')
    if any(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in rows):raise SystemExit('W11 unresolved OCR row')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    by=defaultdict(list)
    for r in rows:by[r['viewer_key']].append(r)
    summaries=[]
    for k in sorted(canonical,key=lambda k:(int(proc[k]['catalog_generation']),int(proc[k]['grade_code']),k)):
        rr=by[k];summaries.append({'ocr_version':VERSION,'viewer_key':k,'catalog_generation':proc[k]['catalog_generation'],'grade_code':proc[k]['grade_code'],'title_core':proc[k]['title_core'],'technical_route':proc[k]['technical_route'],'processing_mode':proc[k]['processing_mode'],'pages':len(rr),'sha_verified':sum(r['source_sha256_verified']=='1' for r in rr),'text_detected':sum(r['ocr_class']=='text_detected' for r in rr),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in rr),'unresolved':sum(r['ocr_class']=='unresolved' for r in rr),'recognized_words':sum(int(r['recognized_words'] or 0) for r in rr),'ocr_chars':sum(int(r['ocr_chars'] or 0) for r in rr)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    text=sum(r['ocr_class']=='text_detected' for r in rows);no_text=sum(r['ocr_class']=='no_text_detected' for r in rows)
    lines=['# LTMD-U1 W11 — OCR técnico','',f'Versión: `{VERSION}`.','',f'- Identidades históricas preservadas en topología: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}**.',f'- Identidades con fuente admitida: **{len(admitted)}/{EXPECTED_IDENTITIES}**.',f'- Identidades retenidas por fuente: **{len(withheld)}**.',f'- Aliases byte-exactos de secuencia completa: **{len(aliases)}**.',f'- Objetos canónicos procesados: **{len(canonical)}**.',f'- Páginas fuente canónicas: **{len(rows):,}**.',f'- SHA-256 verificados: **{len(rows):,}/{len(rows):,}**.',f'- Texto detectado: **{text:,}/{len(rows):,} ({100*text/len(rows):.2f}%)**.',f'- `no_text_detected`: **{no_text:,}**.','- `unresolved`: **0**.','','El OCR íntegro no se persiste. Sólo se publican métricas técnicas y procedencia. Los aliases proceden exclusivamente de identidad byte-exacta de la secuencia fuente completa, nunca de similitud textual, título o cercanía bibliográfica.','','## Límite epistemológico','','Esta capa abre PAGESTRUCT/FRAGSEG sobre los objetos canónicos admitidos, pero no constituye validación semántica, curricular, pedagógica ni bibliográfica. `WAITING_HUMAN_REFERENCE` continúa vigente.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
