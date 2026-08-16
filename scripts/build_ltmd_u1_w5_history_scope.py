#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_w5_scope.csv')
REPORT=Path('data/catalog/ltmd_u1_w5_scope.md')
VERSION='LTMD_U1_W5_SCOPE_0.1'
DOMAIN='historia'
EXPECTED=18
FIELDS=['scope_version','viewer_key','catalog_generation','grade_code','title_core','source_url','operational_domain']

def main():
    rows=[r for r in csv.DictReader(QUEUE.open(encoding='utf-8',newline='')) if r['wave_label']=='U1-W5-historia' and r['queue_status']=='queued' and r['operational_domain']==DOMAIN]
    if len(rows)!=EXPECTED: raise SystemExit(f'W5 scope drift: expected {EXPECTED}, got {len(rows)}')
    if len({r['viewer_key'] for r in rows})!=EXPECTED: raise SystemExit('duplicate W5 viewer keys')
    out=[{'scope_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'source_url':r['source_url'],'operational_domain':DOMAIN} for r in rows]
    out.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    gens={}
    for r in out: gens[int(r['catalog_generation'])]=gens.get(int(r['catalog_generation']),0)+1
    lines=['# LTMD-U1 W5 — alcance congelado Historia','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.','','## Por generación','', '| generación | visores |','|---:|---:|']
    for g,n in sorted(gens.items()): lines.append(f'| {g} | {n} |')
    lines += ['', 'La etiqueta `historia` es una clasificación operacional del tablero U1 y no constituye por sí misma una ontología curricular ni una afirmación de continuidad semántica entre generaciones.', '', 'Los visores 2018 y 2019 se mantienen como identidades de catálogo independientes. Ninguna cobertura se hereda por similitud de título, grado o ruta: cualquier alias deberá probarse posteriormente mediante evidencia de activos y hashes.', '', 'W5 se inicia únicamente en capas de fuente/arquitectura. No se autoriza OCR productivo hasta reconciliar activos, aliases, routing y huecos internos.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__': main()
