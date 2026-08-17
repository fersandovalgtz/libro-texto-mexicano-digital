#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from collections import Counter
from pathlib import Path

SCOPE=Path('data/catalog/ltmd_u1_w9_scope.csv');DECL=Path('data/catalog/ltmd_u1_w9_declared_inventory.csv')
OUT=Path('data/catalog/ltmd_u1_w9_educacion_fisica_asset_manifest.csv');SUMMARY=Path('data/catalog/ltmd_u1_w9_educacion_fisica_asset_summary.csv');REPORT=Path('data/catalog/ltmd_u1_w9_educacion_fisica_asset_audit.md')
VERSION='LTMD_U1_W9_EDUCACION_FISICA_ASSET_AUDIT_0.1';EXPECTED=4

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w9_educacion_fisica_assets');a=ap.parse_args()
    scope={r['viewer_key']:r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))};decl={r['viewer_key']:r for r in csv.DictReader(DECL.open(encoding='utf-8'))};files=sorted(Path(a.input_dir).rglob('asset_*.csv'))
    if len(scope)!=EXPECTED or len(decl)!=EXPECTED or len(files)!=EXPECTED:raise SystemExit(f'W9 scope/declared/files mismatch {len(scope)}/{len(decl)}/{len(files)}')
    rows=[];seen=[]
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8')))
        if not rr:raise SystemExit(f'empty shard {p}')
        ks={r['viewer_key'] for r in rr};vs={r['audit_version'] for r in rr}
        if len(ks)!=1 or vs!={VERSION}:raise SystemExit(f'invalid W9 shard {p}')
        key=next(iter(ks));seen.append(key)
        if key not in decl:raise SystemExit(f'viewer outside W9 scope: {key}')
        expected=int(decl[key]['declared_positions'])
        if len(rr)!=expected:raise SystemExit(f'W9 cardinality mismatch {key}: {len(rr)} vs {expected}')
        if any(r['probe_state']=='probe_error' or r['asset_status']=='probe_error' for r in rr):raise SystemExit(f'W9 probe error persisted {key}')
        if {r['ag_clave'] for r in rr}!={decl[key]['ag_clave']}:raise SystemExit(f'W9 ag_clave drift {key}')
        terminal=[r for r in rr if r['asset_status']=='terminal_synthetic_candidate']
        if len(terminal)>1:raise SystemExit(f'W9 multiple terminal candidates {key}')
        if terminal:
            t=terminal[0]
            if t['is_final_declared_position']!='1':raise SystemExit(f'W9 non-final terminal candidate {key}')
            prior=[r for r in rr if int(r['viewer_page'])<int(t['viewer_page'])]
            if not prior or any(r['asset_status']!='source_jpeg' for r in prior):raise SystemExit(f'W9 invalid terminal candidate with incomplete prior sequence {key}')
        rows+=rr
    if set(seen)!=set(scope) or len(seen)!=len(set(seen)):raise SystemExit('W9 viewer coverage/duplicate mismatch')
    if len(rows)!=sum(int(r['declared_positions']) for r in decl.values()):raise SystemExit('W9 total declared-position mismatch')
    rows.sort(key=lambda r:(int(r['grade_code']),r['viewer_key'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summaries=[]
    for key in sorted(scope,key=lambda k:(int(scope[k]['grade_code']),k)):
        rr=[r for r in rows if r['viewer_key']==key];c=Counter(r['asset_status'] for r in rr);served=[r for r in rr if r['asset_status']=='source_jpeg'];terminal=c['terminal_synthetic_candidate'];internal=c['internal_unserved'];ready=int(internal==0 and c['probe_error']==0 and len(served)>0);ui=rr[0]['viewer_ui']
        summaries.append({'audit_version':VERSION,'viewer_key':key,'catalog_generation':scope[key]['catalog_generation'],'grade_code':scope[key]['grade_code'],'title_core':scope[key]['title_core'],'viewer_ui':ui,'ag_clave':rr[0]['ag_clave'],'declared_positions':len(rr),'source_jpegs':len(served),'terminal_synthetic_candidates':terminal,'internal_unserved':internal,'probe_errors':c['probe_error'],'source_bytes':sum(int(r['byte_size']) for r in served),'unique_source_hashes':len({r['sha256'] for r in served}),'direct_asset_ready':ready})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    ready=sum(int(r['direct_asset_ready']) for r in summaries);internal=sum(int(r['internal_unserved']) for r in summaries);served=sum(int(r['source_jpegs']) for r in summaries);terminal=sum(int(r['terminal_synthetic_candidates']) for r in summaries);nonstandard=sum(r['viewer_ui']=='nonstandard_viewer_architecture' for r in summaries)
    lines=['# LTMD-U1 W9 — auditoría de activos Educación Física','',f'Versión: `{VERSION}`.','',f'- Visores auditados: **{len(summaries)}/{EXPECTED}**.',f'- Visores de arquitectura HTML no estándar: **{nonstandard}**.',f'- Posiciones declaradas: **{len(rows):,}**.',f'- JPEG servidos y hasheados: **{served:,}**.',f'- Candidatos terminales sintéticos estrictos: **{terminal}**.',f'- Posiciones no servidas: **{internal}**.',f'- Visores `direct_asset_ready`: **{ready}/{EXPECTED}**.','','## Por visor','', '| visor | grado | declaradas | JPEG | terminal estricto | no servidas | ready |','|---|---:|---:|---:|---:|---:|---:|']
    for r in summaries:lines.append(f"| `{r['viewer_key']}` | {r['grade_code']} | {r['declared_positions']} | {r['source_jpegs']} | {r['terminal_synthetic_candidates']} | {r['internal_unserved']} | {r['direct_asset_ready']} |")
    lines+=['','## Regla','Cada byte servido se recorre sólo para SHA-256 y tamaño; no se persisten JPEG. Un 404 final sólo es `terminal_synthetic_candidate` si **todas** las posiciones anteriores fueron servidas como imagen. Cualquier hueco previo, incluido un subtree ausente, mantiene el final como `internal_unserved`. `direct_asset_ready` es sólo un estado técnico de fuente.','','OCR W9 permanece cerrado hasta que una compuerta de admisibilidad reconcilie exactamente alcance, arquitectura, inventario y esta auditoría.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
