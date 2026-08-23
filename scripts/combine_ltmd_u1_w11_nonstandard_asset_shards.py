#!/usr/bin/env python3
"""Combine the 11 W11 nonstandard official-config asset shards with exact checks."""
from __future__ import annotations
import argparse,csv
from collections import Counter
from pathlib import Path

CONF=Path('data/catalog/ltmd_u1_w11_nonstandard_config.csv')
OUT=Path('data/catalog/ltmd_u1_w11_nonstandard_asset_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w11_nonstandard_asset_summary.csv')
REPORT=Path('docs/LTMD_U1_W11_NONSTANDARD_ASSET_AUDIT.md')
VERSION='LTMD_U1_W11_NONSTANDARD_ASSET_AUDIT_0.1'
EXPECTED=11
EXPECTED_POSITIONS=849

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w11_nonstandard_assets');a=ap.parse_args()
    conf={r['viewer_key']:r for r in csv.DictReader(CONF.open(encoding='utf-8'))}
    files=sorted(Path(a.input_dir).rglob('asset_*.csv'))
    if len(conf)!=EXPECTED or len(files)!=EXPECTED:raise SystemExit(f'W11 nonstandard config/files mismatch {len(conf)}/{len(files)}')
    if any(r['official_config_ready']!='1' for r in conf.values()):raise SystemExit('W11 nonstandard config contains unresolved viewer')
    if sum(int(r['ag_pages']) for r in conf.values())!=EXPECTED_POSITIONS:raise SystemExit('W11 nonstandard declared-position invariant drift')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty shard {p}')
        ks={r['viewer_key'] for r in rr};vs={r['audit_version'] for r in rr}
        if len(ks)!=1 or vs!={VERSION}:raise SystemExit(f'invalid W11 nonstandard shard {p}')
        key=next(iter(ks));seen.append(key)
        if key not in conf:raise SystemExit(f'viewer outside nonstandard cohort: {key}')
        expected=int(conf[key]['ag_pages'])
        if len(rr)!=expected:raise SystemExit(f'W11 nonstandard cardinality mismatch {key}: {len(rr)} vs {expected}')
        if any(r['probe_state']=='probe_error' or r['asset_status']=='probe_error' for r in rr):raise SystemExit(f'W11 nonstandard probe error persisted {key}')
        if {r['ag_clave'] for r in rr}!={conf[key]['ag_clave']}:raise SystemExit(f'W11 nonstandard ag_clave drift {key}')
        terminal=[r for r in rr if r['asset_status']=='terminal_synthetic_candidate']
        if len(terminal)>1:raise SystemExit(f'W11 nonstandard multiple terminal candidates {key}')
        if terminal:
            t=terminal[0]
            if t['is_final_declared_position']!='1':raise SystemExit(f'W11 nonstandard non-final terminal candidate {key}')
            prior=[r for r in rr if int(r['viewer_page'])<int(t['viewer_page'])]
            if not prior or any(r['asset_status']!='source_jpeg' for r in prior):raise SystemExit(f'W11 nonstandard invalid terminal candidate {key}')
        rows+=rr
    if set(seen)!=set(conf) or len(seen)!=len(set(seen)):raise SystemExit('W11 nonstandard viewer coverage/duplicate mismatch')
    if len(rows)!=EXPECTED_POSITIONS:raise SystemExit(f'W11 nonstandard total mismatch {len(rows)} vs {EXPECTED_POSITIONS}')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summaries=[]
    for key in sorted(conf,key=lambda k:(int(conf[k]['catalog_generation']),int(conf[k]['grade_code']),k)):
        rr=[r for r in rows if r['viewer_key']==key];c=Counter(r['asset_status'] for r in rr);served=[r for r in rr if r['asset_status']=='source_jpeg'];ready=int(c['internal_unserved']==0 and c['probe_error']==0 and len(served)>0)
        summaries.append({'audit_version':VERSION,'viewer_key':key,'catalog_generation':conf[key]['catalog_generation'],'grade_code':conf[key]['grade_code'],'title_core':conf[key]['title_core'],'ag_clave':rr[0]['ag_clave'],'declared_positions':len(rr),'source_jpegs':len(served),'terminal_synthetic_candidates':c['terminal_synthetic_candidate'],'internal_unserved':c['internal_unserved'],'probe_errors':c['probe_error'],'source_bytes':sum(int(r['byte_size']) for r in served),'unique_source_hashes':len({r['sha256'] for r in served}),'direct_asset_ready':ready})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    ready=sum(int(r['direct_asset_ready']) for r in summaries);internal=sum(int(r['internal_unserved']) for r in summaries);served=sum(int(r['source_jpegs']) for r in summaries);terminal=sum(int(r['terminal_synthetic_candidates']) for r in summaries)
    lines=['# LTMD-U1 W11 — auditoría estricta de activos de la ruta no estándar con configuración oficial','',f'Versión: `{VERSION}`.','',f'- Visores auditados: **{len(summaries)}/{EXPECTED}**.',f'- Posiciones declaradas: **{len(rows):,}**.',f'- JPEG servidos y hasheados: **{served:,}**.',f'- Candidatos terminales sintéticos estrictos: **{terminal}**.',f'- Posiciones internas no servidas: **{internal}**.',f'- Visores `direct_asset_ready`: **{ready}/{EXPECTED}**.','','## Por visor','','| viewer | declaradas | JPEG | terminal | internas no servidas | direct ready |','|---|---:|---:|---:|---:|---:|']
    for r in summaries:lines.append(f"| `{r['viewer_key']}` | {r['declared_positions']} | {r['source_jpegs']} | {r['terminal_synthetic_candidates']} | {r['internal_unserved']} | {r['direct_asset_ready']} |")
    lines+=['','## Regla','La anomalía de HTML se conserva como hecho técnico. El uso de `claves.json` sólo habilita esta auditoría porque la configuración existe explícitamente para los 11 visores; no se infiere por semejanza con otros. Cada JPEG servido se recorre para tipo, tamaño y SHA-256 y no se persiste.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
