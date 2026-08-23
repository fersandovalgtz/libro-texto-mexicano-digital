#!/usr/bin/env python3
"""Route frozen W11 identities by observed viewer architecture only."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

SCOPE=Path('data/catalog/ltmd_u1_w11_scope.csv')
ARCH=Path('data/catalog/ltmd_u1_w11_viewer_architecture.csv')
OUT=Path('data/catalog/ltmd_u1_w11_technical_routing.csv')
REPORT=Path('docs/LTMD_U1_W11_TECHNICAL_ROUTING.md')
VERSION='LTMD_U1_W11_TECHNICAL_ROUTING_0.1'
EXPECTED=111
FIELDS=['routing_version','viewer_key','catalog_generation','grade_code','title_core','technical_route','architecture_signature','source_url']

def main()->None:
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    arch={r['viewer_key']:r for r in csv.DictReader(ARCH.open(encoding='utf-8',newline=''))}
    if len(scope)!=EXPECTED or len({r['viewer_key'] for r in scope})!=EXPECTED or len(arch)!=EXPECTED:
        raise SystemExit(f'W11 routing cardinality mismatch: scope={len(scope)} arch={len(arch)}')
    if set(arch)!={r['viewer_key'] for r in scope}:raise SystemExit('W11 routing scope/architecture key drift')
    rows=[]
    for s in scope:
        a=arch[s['viewer_key']]
        route='standard_dynamic_claves' if a['standard_dynamic_architecture']=='1' else 'nonstandard_html_diagnostics'
        rows.append({'routing_version':VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'technical_route':route,'architecture_signature':a['architecture_signature'],'source_url':s['source_url']})
    rows.sort(key=lambda r:(r['technical_route'],int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    counts=Counter(r['technical_route'] for r in rows)
    if sum(counts.values())!=EXPECTED:raise SystemExit('W11 routing accounting drift')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    lines=['# LTMD-U1 W11 — enrutamiento técnico por arquitectura','',f'Versión: `{VERSION}`.','',f'- Identidades enrutadas: **{EXPECTED}/{EXPECTED}**.',f'- `standard_dynamic_claves`: **{counts["standard_dynamic_claves"]}**.',f'- `nonstandard_html_diagnostics`: **{counts["nonstandard_html_diagnostics"]}**.','','## Ruta no estándar']
    for r in rows:
        if r['technical_route']=='nonstandard_html_diagnostics':lines.append(f"- `{r['viewer_key']}` — {r['catalog_generation']}, grado {r['grade_code']} — {r['title_core']}.")
    lines+=['','## Regla metodológica','El enrutamiento se deriva exclusivamente de la arquitectura observada y no reclasifica contenido. `standard_dynamic_claves` autoriza consultar la configuración oficial declarada, no asumir disponibilidad de activos. `nonstandard_html_diagnostics` exige inspeccionar recursos realmente declarados por el HTML antes de construir cualquier ruta de fuente. Ninguna de las dos rutas autoriza aliases, OCR ni imputación.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
