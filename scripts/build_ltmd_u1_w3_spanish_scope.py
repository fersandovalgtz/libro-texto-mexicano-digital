#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT=Path('data/catalog/ltmd_u1_w3_scope.csv')
REPORT=Path('data/catalog/ltmd_u1_w3_scope.md')
VERSION='LTMD_U1_W3_SCOPE_0.1'
DOMAIN='espanol_lengua'
EXPECTED=130
FIELDS=['scope_version','viewer_key','catalog_generation','grade_code','title_core','source_url','operational_domain']

def main():
    with QUEUE.open(encoding='utf-8',newline='') as f: rows=[r for r in csv.DictReader(f) if r['operational_domain']==DOMAIN]
    if len(rows)!=EXPECTED: raise SystemExit(f'expected {EXPECTED} {DOMAIN} viewers, got {len(rows)}')
    if len({r['viewer_key'] for r in rows})!=EXPECTED: raise SystemExit('duplicate W3 viewer keys')
    out=[{'scope_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'source_url':r['source_url'],'operational_domain':DOMAIN} for r in rows]
    out.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    gens={}
    for r in out:gens[int(r['catalog_generation'])]=gens.get(int(r['catalog_generation']),0)+1
    lines=['# LTMD-U1 W3 — alcance congelado Español/Lengua','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.','','## Por generación','', '| generación | visores |','|---:|---:|']
    for g,n in sorted(gens.items()):lines.append(f'| {g} | {n} |')
    lines+=['','La asignación `espanol_lengua` es operacional y logística. No constituye todavía una ontología curricular ni una clasificación semántica. W3 no hereda automáticamente SEMB de Ciencias Naturales.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
