#!/usr/bin/env python3
"""Combine all 69 W10 asset-audit shards with exact scope and cardinality checks."""
from __future__ import annotations
import argparse,csv
from collections import Counter
from pathlib import Path

SCOPE=Path('data/catalog/ltmd_u1_w10_scope.csv')
DECL=Path('data/catalog/ltmd_u1_w10_declared_inventory.csv')
OUT=Path('data/catalog/ltmd_u1_w10_asset_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w10_asset_summary.csv')
REPORT=Path('docs/LTMD_U1_W10_ASSET_AUDIT.md')
VERSION='LTMD_U1_W10_INTEGRADOS_ASSET_AUDIT_0.1'
EXPECTED=69

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w10_integrados_assets');a=ap.parse_args()
    scope={r['viewer_key']:r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))}
    decl={r['viewer_key']:r for r in csv.DictReader(DECL.open(encoding='utf-8'))}
    files=sorted(Path(a.input_dir).rglob('asset_*.csv'))
    if len(scope)!=EXPECTED or len(decl)!=EXPECTED or len(files)!=EXPECTED:
        raise SystemExit(f'W10 scope/declared/files mismatch {len(scope)}/{len(decl)}/{len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty shard {p}')
        ks={r['viewer_key'] for r in rr};vs={r['audit_version'] for r in rr}
        if len(ks)!=1 or vs!={VERSION}:raise SystemExit(f'invalid W10 shard {p}')
        key=next(iter(ks));seen.append(key)
        if key not in decl:raise SystemExit(f'viewer outside W10 scope: {key}')
        expected=int(decl[key]['declared_positions'])
        if len(rr)!=expected:raise SystemExit(f'W10 cardinality mismatch {key}: {len(rr)} vs {expected}')
        if any(r['probe_state']=='probe_error' or r['asset_status']=='probe_error' for r in rr):raise SystemExit(f'W10 probe error persisted {key}')
        if {r['ag_clave'] for r in rr}!={decl[key]['ag_clave']}:raise SystemExit(f'W10 ag_clave drift {key}')
        terminal=[r for r in rr if r['asset_status']=='terminal_synthetic_candidate']
        if len(terminal)>1:raise SystemExit(f'W10 multiple terminal candidates {key}')
        if terminal:
            t=terminal[0]
            if t['is_final_declared_position']!='1':raise SystemExit(f'W10 non-final terminal candidate {key}')
            prior=[r for r in rr if int(r['viewer_page'])<int(t['viewer_page'])]
            if not prior or any(r['asset_status']!='source_jpeg' for r in prior):raise SystemExit(f'W10 invalid terminal candidate {key}')
        rows+=rr
    if set(seen)!=set(scope) or len(seen)!=len(set(seen)):raise SystemExit('W10 viewer coverage/duplicate mismatch')
    declared_total=sum(int(r['declared_positions']) for r in decl.values())
    if len(rows)!=declared_total:raise SystemExit(f'W10 total declared mismatch {len(rows)} vs {declared_total}')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summaries=[]
    for key in sorted(scope,key=lambda k:(int(scope[k]['catalog_generation']),int(scope[k]['grade_code']),k)):
        rr=[r for r in rows if r['viewer_key']==key];c=Counter(r['asset_status'] for r in rr);served=[r for r in rr if r['asset_status']=='source_jpeg'];terminal=c['terminal_synthetic_candidate'];internal=c['internal_unserved'];ready=int(internal==0 and c['probe_error']==0 and len(served)>0)
        summaries.append({'audit_version':VERSION,'viewer_key':key,'catalog_generation':scope[key]['catalog_generation'],'grade_code':scope[key]['grade_code'],'title_core':scope[key]['title_core'],'ag_clave':rr[0]['ag_clave'],'declared_positions':len(rr),'source_jpegs':len(served),'terminal_synthetic_candidates':terminal,'internal_unserved':internal,'probe_errors':c['probe_error'],'source_bytes':sum(int(r['byte_size']) for r in served),'unique_source_hashes':len({r['sha256'] for r in served}),'direct_asset_ready':ready})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    ready=sum(int(r['direct_asset_ready']) for r in summaries);internal=sum(int(r['internal_unserved']) for r in summaries);served=sum(int(r['source_jpegs']) for r in summaries);terminal=sum(int(r['terminal_synthetic_candidates']) for r in summaries)
    bygen={}
    for g in sorted({r['catalog_generation'] for r in summaries},key=int):
        sr=[r for r in summaries if r['catalog_generation']==g];bygen[g]=(len(sr),sum(int(r['direct_asset_ready']) for r in sr),sum(int(r['source_jpegs']) for r in sr),sum(int(r['internal_unserved']) for r in sr))
    lines=['# LTMD-U1 W10 — auditoría estricta de activos','',f'Versión: `{VERSION}`.','',f'- Visores auditados: **{len(summaries)}/{EXPECTED}**.',f'- Posiciones declaradas: **{len(rows):,}**.',f'- JPEG servidos y hasheados: **{served:,}**.',f'- Candidatos terminales sintéticos estrictos: **{terminal}**.',f'- Posiciones internas no servidas: **{internal}**.',f'- Visores `direct_asset_ready`: **{ready}/{EXPECTED}**.','','## Por generación','','| generación | visores | direct ready | JPEG | no servidas |','|---:|---:|---:|---:|---:|']
    for g,(n,rdy,jpg,miss) in bygen.items():lines.append(f'| {g} | {n} | {rdy} | {jpg:,} | {miss:,} |')
    lines+=['','## Casos con retenciones potenciales']
    bad=[r for r in summaries if r['direct_asset_ready']!='1']
    if bad:
        for r in bad:lines.append(f"- `{r['viewer_key']}` — declaradas {r['declared_positions']}, JPEG {r['source_jpegs']}, no servidas {r['internal_unserved']}, terminal estricto {r['terminal_synthetic_candidates']}.")
    else:lines.append('- Ninguno.')
    lines+=['','## Regla','Cada activo servido se recorre únicamente para verificar tipo, tamaño y SHA-256; los JPEG no se persisten. Un 404 final sólo se clasifica como `terminal_synthetic_candidate` cuando toda la secuencia previa fue servida. Cualquier hueco previo permanece `internal_unserved`. `direct_asset_ready` es una condición técnica de fuente, no una validación semántica ni bibliográfica.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':
    main()
