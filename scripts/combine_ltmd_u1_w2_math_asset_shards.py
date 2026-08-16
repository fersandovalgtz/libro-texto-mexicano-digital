#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path
SCOPE=Path('data/catalog/ltmd_u1_w2_scope.csv');DECL=Path('data/catalog/ltmd_u1_w2_declared_inventory.csv');OUT=Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv');SUMMARY=Path('data/catalog/ltmd_u1_w2_math_asset_summary.csv');REPORT=Path('data/catalog/ltmd_u1_w2_math_asset_audit.md');VERSION='LTMD_U1_W2_MATH_ASSET_AUDIT_0.1';EXPECTED=64
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w2_math_assets');a=ap.parse_args();scope={r['viewer_key']:r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))};decl={r['viewer_key']:int(r['declared_positions']) for r in csv.DictReader(DECL.open(encoding='utf-8'))};files=sorted(Path(a.input_dir).rglob('asset_*.csv'))
 if len(scope)!=EXPECTED or len(files)!=EXPECTED:raise SystemExit(f'scope/files mismatch {len(scope)}/{len(files)}')
 rows=[];seen=[]
 for p in files:
  rr=list(csv.DictReader(p.open(encoding='utf-8')))
  if not rr:raise SystemExit(f'empty shard {p}')
  ks={r['viewer_key'] for r in rr};vs={r['audit_version'] for r in rr}
  if len(ks)!=1 or vs!={VERSION}:raise SystemExit(f'invalid shard {p}')
  key=next(iter(ks));seen.append(key)
  if key not in decl or len(rr)!=decl[key]:raise SystemExit(f'cardinality mismatch {key}: {len(rr)} vs {decl.get(key)}')
  if any(r['probe_state']=='probe_error' or r['asset_status']=='probe_error' for r in rr):raise SystemExit(f'probe error persisted {key}')
  rows+=rr
 if set(seen)!=set(scope) or len(seen)!=len(set(seen)):raise SystemExit('viewer coverage/duplicate mismatch')
 rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key'],int(r['viewer_page'])));OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summaries=[];gen=defaultdict(Counter)
 for key in sorted(scope,key=lambda k:(int(scope[k]['catalog_generation']),int(scope[k]['grade_code']),k)):
  rr=[r for r in rows if r['viewer_key']==key];c=Counter(r['asset_status'] for r in rr);served=[r for r in rr if r['asset_status']=='source_jpeg'];terminal=c['terminal_synthetic_candidate'];internal=c['internal_unserved'];ready=int(internal==0 and c['probe_error']==0 and len(served)>0);summaries.append({'audit_version':VERSION,'viewer_key':key,'book_id':scope[key]['book_id'],'catalog_generation':scope[key]['catalog_generation'],'grade_code':scope[key]['grade_code'],'declared_positions':len(rr),'source_jpegs':len(served),'terminal_synthetic_candidates':terminal,'internal_unserved':internal,'probe_errors':c['probe_error'],'source_bytes':sum(int(r['byte_size']) for r in served),'unique_source_hashes':len({r['sha256'] for r in served}),'direct_asset_ready':ready});g=gen[scope[key]['catalog_generation']];g['viewers']+=1;g['ready']+=ready;g['declared']+=len(rr);g['served']+=len(served);g['internal']+=internal
 with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
 ready=sum(int(r['direct_asset_ready']) for r in summaries);internal=sum(int(r['internal_unserved']) for r in summaries);served=sum(int(r['source_jpegs']) for r in summaries);terminal=sum(int(r['terminal_synthetic_candidates']) for r in summaries)
 lines=['# LTMD-U1 W2 — auditoría de activos de Matemáticas','',f'Versión: `{VERSION}`.','',f'- Visores auditados: **{len(summaries)}/{EXPECTED}**.\n- Posiciones declaradas: **{len(rows):,}**.\n- JPEG servidos y hasheados: **{served:,}**.\n- Candidatos terminales sintéticos (404 sólo en posición final): **{terminal}**.\n- Posiciones internas no servidas: **{internal}**.\n- Visores `direct_asset_ready`: **{ready}/{EXPECTED}**.','', '## Por generación','', '| generación | visores | ready | declaradas | JPEG | internos no servidos |','|---:|---:|---:|---:|---:|---:|']
 for g in sorted(gen,key=int):lines.append(f"| {g} | {gen[g]['viewers']} | {gen[g]['ready']} | {gen[g]['declared']:,} | {gen[g]['served']:,} | {gen[g]['internal']} |")
 bad=[r for r in summaries if not int(r['direct_asset_ready'])]
 if bad:lines+=['','## Visores que requieren resolución adicional']+[f"- `{r['viewer_key']}` ({r['catalog_generation']}, grado {r['grade_code']}): internos no servidos={r['internal_unserved']}; terminales={r['terminal_synthetic_candidates']}; JPEG={r['source_jpegs']}/{r['declared_positions']}." for r in bad]
 lines+=['','## Regla','Cada posición declarada se prueba empíricamente y los bytes servidos se recorren sólo para SHA-256. Un 404 final se registra como candidato a terminal sintético; un 404 interno permanece como anomalía y requiere resolución/alias. Ningún JPEG se persiste en Git.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
