#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_w7_scope.csv')
REPORT=Path('data/catalog/ltmd_u1_w7_scope.md')
VERSION='LTMD_U1_W7_SCOPE_0.1'
DOMAIN='civica_etica'
EXPECTED=30
FIELDS=['scope_version','viewer_key','catalog_generation','grade_code','title_core','source_url','operational_domain']

def main():
    rows=[r for r in csv.DictReader(QUEUE.open(encoding='utf-8',newline='')) if r['wave_label']=='U1-W7-civica_etica' and r['queue_status']=='queued' and r['operational_domain']==DOMAIN]
    if len(rows)!=EXPECTED: raise SystemExit(f'W7 scope drift: expected {EXPECTED}, got {len(rows)}')
    if len({r['viewer_key'] for r in rows})!=EXPECTED: raise SystemExit('duplicate W7 viewer keys')
    out=[{'scope_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'source_url':r['source_url'],'operational_domain':DOMAIN} for r in rows]
    out.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    gens={}
    for r in out: gens[int(r['catalog_generation'])]=gens.get(int(r['catalog_generation']),0)+1
    lines=['# LTMD-U1 W7 — alcance congelado Cívica/Ética','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.','','## Por generación','', '| generación | visores |','|---:|---:|']
    for g,n in sorted(gens.items()): lines.append(f'| {g} | {n} |')
    lines += ['', 'La etiqueta `civica_etica` es operacional y no constituye por sí misma una ontología curricular ni demuestra continuidad semántica entre generaciones.', '', 'Las identidades de catálogo permanecen independientes. Ningún alias se infiere por título, grado, generación o cardinalidad; cualquier relación deberá demostrarse con activos y hashes.', '', 'W7 se abre únicamente en capas de fuente/arquitectura. OCR productivo permanece cerrado hasta reconciliar activos, aliases, routing y huecos internos.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__': main()
