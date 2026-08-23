#!/usr/bin/env python3
"""Combine all 100 standard-route W11 asset shards with exact cardinality checks."""
from __future__ import annotations
import argparse,csv
from collections import Counter
from pathlib import Path

DECL=Path('data/catalog/ltmd_u1_w11_standard_declared_inventory.csv')
OUT=Path('data/catalog/ltmd_u1_w11_standard_asset_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w11_standard_asset_summary.csv')
REPORT=Path('docs/LTMD_U1_W11_STANDARD_ASSET_AUDIT.md')
VERSION='LTMD_U1_W11_STANDARD_ASSET_AUDIT_0.1'
EXPECTED=100
EXPECTED_POSITIONS=19576

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w11_standard_assets');a=ap.parse_args()
    decl={r['viewer_key']:r for r in csv.DictReader(DECL.open(encoding='utf-8'))}
    files=sorted(Path(a.input_dir).rglob('asset_*.csv'))
    if len(decl)!=EXPECTED or len(files)!=EXPECTED:raise SystemExit(f'W11 standard declared/files mismatch {len(decl)}/{len(files)}')
    if sum(int(r['declared_positions']) for r in decl.values())!=EXPECTED_POSITIONS:raise SystemExit('W11 standard declared-position invariant drift')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty shard {p}')
        ks={r['viewer_key'] for r in rr};vs={r['audit_version'] for r in rr}
        if len(ks)!=1 or vs!={VERSION}:raise SystemExit(f'invalid W11 standard shard {p}')
        key=next(iter(ks));seen.append(key)
        if key not in decl:raise SystemExit(f'viewer outside W11 standard route: {key}')
        expected=int(decl[key]['declared_positions'])
        if len(rr)!=expected:raise SystemExit(f'W11 cardinality mismatch {key}: {len(rr)} vs {expected}')
        if any(r['probe_state']=='probe_error' or r['asset_status']=='probe_error' for r in rr):raise SystemExit(f'W11 probe error persisted {key}')
        if {r['ag_clave'] for r in rr}!={decl[key]['ag_clave']}:raise SystemExit(f'W11 ag_clave drift {key}')
        terminal=[r for r in rr if r['asset_status']=='terminal_synthetic_candidate']
        if len(terminal)>1:raise SystemExit(f'W11 multiple terminal candidates {key}')
        if terminal:
            t=terminal[0]
            if t['is_final_declared_position']!='1':raise SystemExit(f'W11 non-final terminal candidate {key}')
            prior=[r for r in rr if int(r['viewer_page'])<int(t['viewer_page'])]
            if not prior or any(r['asset_status']!='source_jpeg' for r in prior):raise SystemExit(f'W11 invalid terminal candidate {key}')
        rows+=rr
    if set(seen)!=set(decl) or len(seen)!=len(set(seen)):raise SystemExit('W11 standard viewer coverage/duplicate mismatch')
    if len(rows)!=EXPECTED_POSITIONS:raise SystemExit(f'W11 total declared mismatch {len(rows)} vs {EXPECTED_POSITIONS}')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summaries=[]
    for key in sorted(decl,key=lambda k:(int(decl[k]['catalog_generation']),int(decl[k]['grade_code']),k)):
        rr=[r for r in rows if r['viewer_key']==key];c=Counter(r['asset_status'] for r in rr);served=[r for r in rr if r['asset_status']=='source_jpeg'];ready=int(c['internal_unserved']==0 and c['probe_error']==0 and len(served)>0)
        summaries.append({'audit_version':VERSION,'viewer_key':key,'catalog_generation':decl[key]['catalog_generation'],'grade_code':decl[key]['grade_code'],'title_core':decl[key]['title_core'],'ag_clave':rr[0]['ag_clave'],'declared_positions':len(rr),'source_jpegs':len(served),'terminal_synthetic_candidates':c['terminal_synthetic_candidate'],'internal_unserved':c['internal_unserved'],'probe_errors':c['probe_error'],'source_bytes':sum(int(r['byte_size']) for r in served),'unique_source_hashes':len({r['sha256'] for r in served}),'direct_asset_ready':ready})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    ready=sum(int(r['direct_asset_ready']) for r in summaries);internal=sum(int(r['internal_unserved']) for r in summaries);served=sum(int(r['source_jpegs']) for r in summaries);terminal=sum(int(r['terminal_synthetic_candidates']) for r in summaries)
    bygen={}
    for g in sorted({r['catalog_generation'] for r in summaries},key=int):
        sr=[r for r in summaries if r['catalog_generation']==g];bygen[g]=(len(sr),sum(int(r['direct_asset_ready']) for r in sr),sum(int(r['source_jpegs']) for r in sr),sum(int(r['internal_unserved']) for r in sr))
    lines=['# LTMD-U1 W11 — auditoría estricta de activos de la ruta estándar','',f'Versión: `{VERSION}`.','',f'- Visores estándar auditados: **{len(summaries)}/{EXPECTED}**.',f'- Posiciones declaradas: **{len(rows):,}**.',f'- JPEG servidos y hasheados: **{served:,}**.',f'- Candidatos terminales sintéticos estrictos: **{terminal}**.',f'- Posiciones internas no servidas: **{internal}**.',f'- Visores estándar `direct_asset_ready`: **{ready}/{EXPECTED}**.','','## Por generación','','| generación | visores | direct ready | JPEG | no servidas |','|---:|---:|---:|---:|---:|']
    for g,(n,rdy,jpg,miss) in bygen.items():lines.append(f'| {g} | {n} | {rdy} | {jpg:,} | {miss:,} |')
    lines+=['','## Casos con retenciones potenciales']
    bad=[r for r in summaries if r['direct_asset_ready']!='1']
    if bad:
        for r in bad:lines.append(f"- `{r['viewer_key']}` — declaradas {r['declared_positions']}, JPEG {r['source_jpegs']}, no servidas {r['internal_unserved']}, terminal estricto {r['terminal_synthetic_candidates']}.")
    else:lines.append('- Ninguno.')
    lines+=['','## Regla','Cada activo servido se recorre únicamente para verificar tipo, tamaño y SHA-256; los JPEG no se persisten. Un 404 final sólo se clasifica como `terminal_synthetic_candidate` cuando toda la secuencia previa fue servida. Cualquier hueco previo permanece `internal_unserved`. Esta auditoría cubre sólo la ruta estándar; los 11 visores no estándar permanecen sujetos a su propia cadena de evidencia.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
