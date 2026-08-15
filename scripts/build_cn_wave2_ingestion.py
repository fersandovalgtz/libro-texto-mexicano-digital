#!/usr/bin/env python3
"""Freeze the next technical ingestion wave for strict Ciencias Naturales."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

READY=Path('data/catalog/ciencias_naturales_family_asset_readiness.csv')
MAN=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
QUEUE=Path('data/expansion/cn_wave2_ingestion_queue.csv')
PAGES=Path('data/expansion/cn_wave2_page_manifest.csv')
REPORT=Path('data/expansion/cn_wave2_ingestion_queue.md')
VERSION='CN_WAVE2_INGESTION_0.1'

def main():
    ready=list(csv.DictReader(READY.open(encoding='utf-8')))
    books=[r for r in ready if r['asset_readiness']=='full_direct' and r['asset_strategy']=='direct_sha256_manifest']
    if len(books)!=19:raise SystemExit(f'expected 19 new full-direct objects, got {len(books)}')
    ids={r['book_id'] for r in books}
    man=list(csv.DictReader(MAN.open(encoding='utf-8')))
    pages=[r for r in man if r['book_id'] in ids and r['asset_status']=='source_jpeg']
    if len(pages)!=3177:raise SystemExit(f'expected 3177 source JPEG rows, got {len(pages)}')
    if any(not r['sha256'] or not r['source_asset_url'] for r in pages):raise SystemExit('wave2 manifest contains incomplete provenance')
    observed=Counter(r['book_id'] for r in pages)
    expected={r['book_id']:int(r['resolved_source_assets']) for r in books}
    if observed!=Counter(expected):raise SystemExit(f'per-book source count mismatch observed={observed} expected={expected}')
    books.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade'])))
    qfields=['wave_version','book_id','viewer_key','catalog_generation','grade','viewer_positions_declared','source_assets','source_url','technical_stage','semantic_stage']
    qrows=[{'wave_version':VERSION,'book_id':r['book_id'],'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_positions_declared':r['viewer_positions_declared'],'source_assets':r['resolved_source_assets'],'source_url':r['source_url'],'technical_stage':'ready_for_ocr','semantic_stage':'blocked_pending_human_validation'} for r in books]
    QUEUE.parent.mkdir(parents=True,exist_ok=True)
    with QUEUE.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=qfields);w.writeheader();w.writerows(qrows)
    pages.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    with PAGES.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(pages[0]));w.writeheader();w.writerows(pages)
    gens=Counter(r['catalog_generation'] for r in books)
    lines=['# Ola técnica 2 — familia Ciencias Naturales','',f'Versión: `{VERSION}`.','',f'- Objetos nuevos `full_direct`: **{len(books)}**.\n- JPEG fuente en el submanifiesto: **{len(pages):,}**.\n- Todos con URL + SHA-256 persistidos: **sí**.\n- Alias 2018 incluidos: **0**.\n- Objetos 2008 parciales incluidos: **0**.\n- Objetos ya procesados en piloto/CN4-CN6 incluidos: **0**.','', '## Por generación']
    for g in sorted(gens,key=int):lines.append(f'- {g}: {gens[g]} objetos.')
    lines+=['','## Objetos']
    for r in qrows:lines.append(f"- `{r['book_id']}` — generación {r['catalog_generation']}, grado {r['grade']}, activos={r['source_assets']}.")
    lines+=['','## Regla','Esta ola puede avanzar por OCR, PAGESTRUCT y FRAGSEG. No adquiere por ello `semantic_ready`; SEMB 0.3 continúa bloqueado a referencia humana.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
