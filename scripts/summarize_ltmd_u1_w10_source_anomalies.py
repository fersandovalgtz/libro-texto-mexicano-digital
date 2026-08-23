#!/usr/bin/env python3
"""Publish a compact, auditable view of non-source-JPEG W10 positions."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

MAN=Path('data/catalog/ltmd_u1_w10_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w10_source_anomalies.csv')
REPORT=Path('docs/LTMD_U1_W10_SOURCE_ANOMALIES.md')
VERSION='LTMD_U1_W10_SOURCE_ANOMALIES_0.1'
EXPECTED_DECLARED=12174
EXPECTED_VIEWERS=69

def main():
    rows=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    if len(rows)!=EXPECTED_DECLARED or len({r['viewer_key'] for r in rows})!=EXPECTED_VIEWERS:
        raise SystemExit(f'W10 anomaly report input mismatch rows={len(rows)} viewers={len({r["viewer_key"] for r in rows})}')
    anomal=[r for r in rows if r['asset_status']!='source_jpeg']
    if not anomal:raise SystemExit('W10 anomaly report expected non-source positions but found none')
    fields=['anomaly_version','viewer_key','catalog_generation','grade_code','title_core','viewer_page','declared_positions','source_image_index','source_asset_url','probe_state','http_status','asset_status','is_final_declared_position','attempts','error']
    out=[]
    for r in anomal:
        out.append({
            'anomaly_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'viewer_page':r['viewer_page'],'declared_positions':r['declared_positions'],'source_image_index':r['source_image_index'],'source_asset_url':r['source_asset_url'],'probe_state':r['probe_state'],'http_status':r['http_status'],'asset_status':r['asset_status'],'is_final_declared_position':r['is_final_declared_position'],'attempts':r['attempts'],'error':r['error']})
    out.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    c=Counter(r['asset_status'] for r in out);internal=[r for r in out if r['asset_status']=='internal_unserved']
    lines=['# LTMD-U1 W10 — posiciones fuente anómalas','',f'Versión: `{VERSION}`.','',f'- Posiciones declaradas auditadas: **{EXPECTED_DECLARED:,}**.',f'- Posiciones no clasificadas como `source_jpeg`: **{len(out)}**.',f'- `terminal_synthetic_candidate`: **{c["terminal_synthetic_candidate"]}**.',f'- `internal_unserved`: **{c["internal_unserved"]}**.',f'- `probe_error`: **{c["probe_error"]}**.','','## Huecos internos']
    if internal:
        lines+=['','| visor | página del visor | índice fuente | HTTP | URL observada |','|---|---:|---:|---:|---|']
        for r in internal:lines.append(f"| `{r['viewer_key']}` | {r['viewer_page']} | {r['source_image_index']} | {r['http_status'] or '—'} | `{r['source_asset_url']}` |")
    else:lines.append('- Ninguno.')
    lines+=['','## Regla','Este producto no reinterpreta 404 ni construye rutas alternativas. Expone exactamente las posiciones no servidas observadas por la auditoría byte a byte para facilitar investigación documental acotada. Los candidatos terminales sintéticos permanecen diferenciados de los huecos internos.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
