#!/usr/bin/env python3
"""Publish exact W11 retained source holes from the committed asset manifests.

This report never guesses a replacement. It only materializes the exact missing
positions already observed by the two source audits, so recovery work can be
bounded and reproducible.
"""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

ADM=Path('data/catalog/ltmd_u1_w11_source_admissibility.csv')
STD=Path('data/catalog/ltmd_u1_w11_standard_asset_manifest.csv')
NON=Path('data/catalog/ltmd_u1_w11_nonstandard_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w11_retained_source_holes.csv')
REPORT=Path('docs/LTMD_U1_W11_RETAINED_SOURCE_HOLES.md')
VERSION='LTMD_U1_W11_RETAINED_SOURCE_HOLES_0.1'
EXPECTED_IDENTITIES=4
EXPECTED_HOLES=5

def main()->None:
    for p in [ADM,STD,NON]:
        if not p.exists():raise SystemExit(f'missing W11 retained-hole prerequisite: {p}')
    adm=list(csv.DictReader(ADM.open(encoding='utf-8',newline='')))
    retained={r['viewer_key']:r for r in adm if r['ocr_source_admitted']=='0'}
    if len(retained)!=EXPECTED_IDENTITIES:raise SystemExit(f'expected {EXPECTED_IDENTITIES} retained identities, got {len(retained)}')
    manifests=[]
    for route,p in [('standard_dynamic_claves',STD),('nonstandard_html_diagnostics',NON)]:
        for r in csv.DictReader(p.open(encoding='utf-8',newline='')):
            if r['asset_status']=='internal_unserved':
                if r['viewer_key'] not in retained:raise SystemExit(f'internal hole belongs to admitted viewer: {r["viewer_key"]}')
                manifests.append({
                    'diagnostic_version':VERSION,'viewer_key':r['viewer_key'],
                    'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],
                    'title_core':r['title_core'],'technical_route':route,
                    'viewer_page':r['viewer_page'],'source_image_index':r['source_image_index'],
                    'source_asset_url':r['source_asset_url'],'http_status':r['http_status'],
                    'probe_state':r['probe_state'],'asset_status':r['asset_status']})
    manifests.sort(key=lambda r:(r['viewer_key'],int(r['viewer_page'])))
    if len(manifests)!=EXPECTED_HOLES:raise SystemExit(f'expected {EXPECTED_HOLES} internal holes, got {len(manifests)}')
    by=Counter(r['viewer_key'] for r in manifests)
    if set(by)!=set(retained) or any(by[k]!=int(retained[k]['internal_unserved']) for k in retained):
        raise SystemExit(f'retained-hole accounting mismatch: {dict(by)}')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(manifests[0]));w.writeheader();w.writerows(manifests)
    lines=['# LTMD-U1 W11 — posiciones fuente retenidas','',f'Versión: `{VERSION}`.','',
           f'- Identidades retenidas examinadas: **{len(retained)}/{EXPECTED_IDENTITIES}**.',
           f'- Huecos internos materializados: **{len(manifests)}/{EXPECTED_HOLES}**.',
           '- Sustituciones o imputaciones: **0**.','','## Posiciones exactas','','| viewer | ruta | página visor | índice fuente | HTTP | URL oficial |','|---|---|---:|---:|---:|---|']
    for r in manifests:
        lines.append(f"| `{r['viewer_key']}` | `{r['technical_route']}` | {r['viewer_page']} | {r['source_image_index']} | {r['http_status']} | `{r['source_asset_url']}` |")
    lines+=['','## Regla de recuperación','',
            'Este documento no propone páginas sustitutas. Una recuperación sólo puede cerrar un hueco si conserva correspondencia posicional inequívoca y procedencia reproducible, por ejemplo mediante una ruta institucional efectiva, una captura archivada del mismo activo o una relación documental/criptográfica demostrada. Páginas de otros estados, ediciones, grados o títulos no se aceptan por similitud.','',
            '`WAITING_HUMAN_REFERENCE` no se ve afectado por la recuperación técnica de fuente.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
