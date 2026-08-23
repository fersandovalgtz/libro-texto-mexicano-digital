#!/usr/bin/env python3
"""Classify W10 source admissibility strictly from the full asset audit."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

SCOPE=Path('data/catalog/ltmd_u1_w10_scope.csv')
ASSETS=Path('data/catalog/ltmd_u1_w10_asset_summary.csv')
OUT=Path('data/catalog/ltmd_u1_w10_source_admissibility.csv')
REPORT=Path('docs/LTMD_U1_W10_SOURCE_ADMISSIBILITY.md')
VERSION='LTMD_U1_W10_SOURCE_ADMISSIBILITY_0.1'
EXPECTED=69

def main():
    scope={r['viewer_key']:r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))}
    assets={r['viewer_key']:r for r in csv.DictReader(ASSETS.open(encoding='utf-8'))}
    if len(scope)!=EXPECTED or len(assets)!=EXPECTED or set(scope)!=set(assets):
        raise SystemExit(f'W10 source gate scope/assets mismatch {len(scope)}/{len(assets)}')
    rows=[]
    for key,s in scope.items():
        a=assets[key];internal=int(a['internal_unserved']);probes=int(a['probe_errors']);jpg=int(a['source_jpegs']);ready=int(a['direct_asset_ready'])
        if probes:state='withheld_probe_error';admit=0
        elif internal:state='withheld_internal_unserved';admit=0
        elif not jpg:state='withheld_no_source_jpeg';admit=0
        elif ready==1:state='admitted_direct';admit=1
        else:state='withheld_unclassified';admit=0
        rows.append({'admissibility_version':VERSION,'viewer_key':key,'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'source_state':state,'ocr_source_admitted':admit,'declared_positions':a['declared_positions'],'source_jpegs':jpg,'terminal_synthetic_candidates':a['terminal_synthetic_candidates'],'internal_unserved':internal,'probe_errors':probes,'source_bytes':a['source_bytes'],'unique_source_hashes':a['unique_source_hashes']})
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    admitted=sum(int(r['ocr_source_admitted']) for r in rows);states=Counter(r['source_state'] for r in rows)
    lines=['# LTMD-U1 W10 — compuerta de admisibilidad de fuente','',f'Versión: `{VERSION}`.','',f'- Identidades evaluadas: **{EXPECTED}/{EXPECTED}**.',f'- Fuente admitida para procesamiento técnico: **{admitted}/{EXPECTED}**.',f'- Retenidas: **{EXPECTED-admitted}/{EXPECTED}**.','','## Estados']
    for state,n in sorted(states.items()):lines.append(f'- `{state}`: **{n}**.')
    lines+=['','## Regla','`ocr_source_admitted=1` exige simultáneamente al menos un JPEG oficial servido, cero huecos internos, cero errores de probe y `direct_asset_ready=1`. Un terminal sintético estricto puede coexistir con admisibilidad porque no representa una página fuente omitida. Ninguna retención se sustituye por una fuente vecina, por una edición próxima o por similitud.','','Esta compuerta autoriza únicamente la construcción de topología canónica y procesamiento técnico. No valida edición bibliográfica, semántica ni interpretación histórica.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
