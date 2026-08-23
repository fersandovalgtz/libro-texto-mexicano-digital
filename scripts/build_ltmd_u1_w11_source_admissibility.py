#!/usr/bin/env python3
"""Consolidate W11 source admissibility across standard and nonstandard technical routes."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

SCOPE=Path('data/catalog/ltmd_u1_w11_scope.csv')
ROUTING=Path('data/catalog/ltmd_u1_w11_technical_routing.csv')
STD=Path('data/catalog/ltmd_u1_w11_standard_asset_summary.csv')
NON=Path('data/catalog/ltmd_u1_w11_nonstandard_asset_summary.csv')
OUT=Path('data/catalog/ltmd_u1_w11_source_admissibility.csv')
REPORT=Path('docs/LTMD_U1_W11_SOURCE_ADMISSIBILITY.md')
VERSION='LTMD_U1_W11_SOURCE_ADMISSIBILITY_0.1'
EXPECTED=111
EXPECTED_STD=100
EXPECTED_NON=11

def read_index(path:Path)->dict[str,dict[str,str]]:
    return {r['viewer_key']:r for r in csv.DictReader(path.open(encoding='utf-8',newline=''))}

def main()->None:
    for p in [SCOPE,ROUTING,STD,NON]:
        if not p.exists():raise SystemExit(f'W11 source gate missing prerequisite: {p}')
    scope=read_index(SCOPE);routing=read_index(ROUTING);std=read_index(STD);non=read_index(NON)
    if len(scope)!=EXPECTED or len(routing)!=EXPECTED or set(scope)!=set(routing):
        raise SystemExit(f'W11 source gate scope/routing drift {len(scope)}/{len(routing)}')
    if len(std)!=EXPECTED_STD or len(non)!=EXPECTED_NON or set(std)&set(non) or set(std)|set(non)!=set(scope):
        raise SystemExit(f'W11 source gate route partition drift std={len(std)} non={len(non)}')
    rows=[]
    for key,s in scope.items():
        route=routing[key]['technical_route'];a=(std if key in std else non)[key]
        if key in std and route!='standard_dynamic_claves':raise SystemExit(f'W11 route mismatch {key}: {route}')
        if key in non and route!='nonstandard_html_diagnostics':raise SystemExit(f'W11 route mismatch {key}: {route}')
        internal=int(a['internal_unserved']);probes=int(a['probe_errors']);jpg=int(a['source_jpegs']);ready=int(a['direct_asset_ready'])
        if probes:state='withheld_probe_error';admit=0
        elif internal:state='withheld_internal_unserved';admit=0
        elif not jpg:state='withheld_no_source_jpeg';admit=0
        elif ready==1:state='admitted_direct';admit=1
        else:state='withheld_unclassified';admit=0
        rows.append({
            'admissibility_version':VERSION,'viewer_key':key,'catalog_generation':s['catalog_generation'],
            'grade_code':s['grade_code'],'title_core':s['title_core'],'technical_route':route,
            'source_state':state,'ocr_source_admitted':admit,'declared_positions':a['declared_positions'],
            'source_jpegs':jpg,'terminal_synthetic_candidates':a['terminal_synthetic_candidates'],
            'internal_unserved':internal,'probe_errors':probes,'source_bytes':a['source_bytes'],
            'unique_source_hashes':a['unique_source_hashes']})
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    admitted=sum(int(r['ocr_source_admitted']) for r in rows);states=Counter(r['source_state'] for r in rows);routes=Counter(r['technical_route'] for r in rows)
    lines=['# LTMD-U1 W11 — compuerta consolidada de admisibilidad de fuente','',f'Versión: `{VERSION}`.','',
           f'- Identidades evaluadas: **{EXPECTED}/{EXPECTED}**.',f'- Fuente admitida para procesamiento técnico: **{admitted}/{EXPECTED}**.',
           f'- Retenidas: **{EXPECTED-admitted}/{EXPECTED}**.','','## Rutas técnicas evaluadas']
    for route,n in sorted(routes.items()):lines.append(f'- `{route}`: **{n}** identidades.')
    lines+=['','## Estados']
    for state,n in sorted(states.items()):lines.append(f'- `{state}`: **{n}**.')
    bad=[r for r in rows if r['ocr_source_admitted']=='0']
    lines+=['','## Retenciones explícitas']
    if bad:
        for r in bad:lines.append(f"- `{r['viewer_key']}` — `{r['source_state']}`; ruta `{r['technical_route']}`; JPEG {r['source_jpegs']}/{r['declared_positions']}, huecos internos {r['internal_unserved']}.")
    else:lines.append('- Ninguna.')
    lines+=['','## Regla',
            '`ocr_source_admitted=1` exige al menos un JPEG oficial servido, cero huecos internos, cero errores de probe y `direct_asset_ready=1`. Un terminal sintético estricto puede coexistir con admisibilidad porque no representa una página fuente omitida. La anomalía de HTML de la ruta no estándar permanece documentada y no invalida por sí sola una secuencia fuente que `claves.json` declara y la auditoría verifica posición por posición. Ninguna retención se sustituye por semejanza de título, año, grado, OCR o apariencia visual.','',
            '`WAITING_HUMAN_REFERENCE` continúa vigente. Esta compuerta sólo autoriza topología canónica y procesamiento técnico.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
