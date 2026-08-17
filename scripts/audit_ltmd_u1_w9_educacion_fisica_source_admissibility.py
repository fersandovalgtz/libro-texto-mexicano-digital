#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

VERSION='LTMD_U1_W9_EDUCACION_FISICA_SOURCE_ADMISSIBILITY_0.1';EXPECTED=4
SCOPE=Path('data/catalog/ltmd_u1_w9_scope.csv');ARCH=Path('data/catalog/ltmd_u1_w9_viewer_architecture.csv');INV=Path('data/catalog/ltmd_u1_w9_declared_inventory.csv');ASSETS=Path('data/catalog/ltmd_u1_w9_educacion_fisica_asset_summary.csv')
OUT=Path('data/catalog/ltmd_u1_w9_educacion_fisica_source_admissibility.csv');REPORT=Path('docs/LTMD_U1_W9_EDUCACION_FISICA_SOURCE_ADMISSIBILITY.md')
FIELDS=['admissibility_version','book_id','viewer_key','catalog_generation','grade_code','title_core','identity_reconciliation_state','source_admissible','source_status','source_reason','declared_positions','source_jpegs','terminal_synthetic_candidates','internal_unserved','probe_errors','direct_asset_ready','semantic_state','alias_state','source_url']

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def keyed(rows,label):
 out={}
 for r in rows:
  k=r['viewer_key']
  if k in out:raise SystemExit(f'W9 admissibility duplicate {label} key {k}')
  out[k]=r
 return out
def asint(v):return int(v or 0)
def asbool(v):return str(v).lower() in {'1','true','yes'}
def main():
 scope=keyed(read(SCOPE),'scope');arch=keyed(read(ARCH),'architecture');inv=keyed(read(INV),'inventory');assets=keyed(read(ASSETS),'assets')
 sets=[set(scope),set(arch),set(inv),set(assets)]
 if any(s!=sets[0] for s in sets[1:]) or len(sets[0])!=EXPECTED:raise SystemExit('W9 admissibility identity-set drift')
 rows=[]
 for k in sorted(scope,key=lambda x:(int(scope[x]['grade_code']),x)):
  s,a,i,z=scope[k],arch[k],inv[k],assets[k]
  exact=(s['viewer_key']==a['viewer_key']==i['viewer_key']==z['viewer_key']==k and i['ag_clave']==z['ag_clave'])
  if not exact:raise SystemExit(f'W9 non-1:1 reconciliation {k}')
  if asint(i['declared_positions'])!=asint(z['declared_positions']):raise SystemExit(f'W9 declared-position drift {k}')
  standard=asbool(a['standard_dynamic_architecture']) and asbool(i['standard_dynamic_architecture']);served=asint(z['source_jpegs']);terminal=asint(z['terminal_synthetic_candidates']);internal=asint(z['internal_unserved']);errors=asint(z['probe_errors']);ready=asbool(z['direct_asset_ready'])
  ok=exact and standard and ready and served>0 and internal==0 and errors==0 and terminal<=1
  if ok:status='SOURCE_ADMISSIBLE';reason='exact_1_to_1; standard architecture; served source JPEG sequence has no internal gaps or probe errors'
  else:
   status='SOURCE_RETAINED';parts=[]
   if not standard:parts.append('nonstandard_or_unverified_architecture')
   if served==0:parts.append('no_source_jpegs_served')
   if internal:parts.append(f'internal_unserved={internal}')
   if errors:parts.append(f'probe_errors={errors}')
   if terminal>1:parts.append(f'terminal_synthetic_candidates={terminal}')
   if not ready:parts.append('direct_asset_ready=0')
   reason='; '.join(parts) or 'source gate not satisfied'
  rows.append({'admissibility_version':VERSION,'book_id':k,'viewer_key':k,'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'identity_reconciliation_state':'exact_1_to_1','source_admissible':int(ok),'source_status':status,'source_reason':reason,'declared_positions':z['declared_positions'],'source_jpegs':served,'terminal_synthetic_candidates':terminal,'internal_unserved':internal,'probe_errors':errors,'direct_asset_ready':int(ready),'semantic_state':'WAITING_HUMAN_REFERENCE','alias_state':'no_alias','source_url':s['source_url']})
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
 admitted=[r for r in rows if r['source_status']=='SOURCE_ADMISSIBLE'];retained=[r for r in rows if r['source_status']=='SOURCE_RETAINED']
 if len(admitted)+len(retained)!=EXPECTED:raise SystemExit('W9 admissibility partition failure')
 lines=['# LTMD-U1 W9 Educación Física — compuerta de admisibilidad de fuente','',f'Versión: `{VERSION}`.','',f'- Identidades reconciliadas 1:1: **{EXPECTED}/{EXPECTED}**.',f'- `SOURCE_ADMISSIBLE`: **{len(admitted)}/{EXPECTED}**.',f'- `SOURCE_RETAINED`: **{len(retained)}/{EXPECTED}**.','- Alias creados: **0**.','- Estado semántico: `WAITING_HUMAN_REFERENCE`.','','## Regla','Una identidad sólo es admisible con reconciliación exacta 1:1, arquitectura estándar, al menos un JPEG servido, cero huecos internos, cero errores de sondeo, máximo un terminal sintético estricto y `direct_asset_ready=1`.','','La partición admisible/retenida se deriva de la evidencia observada; **no está hardcodeada antes de la auditoría de activos**.','','OCR sólo podrá abrirse para las identidades `SOURCE_ADMISSIBLE`. Las retenidas no se imputan ni se reconstruyen.']
 if retained:lines+=['','## Retenidas']+[f"- `{r['viewer_key']}`: {r['source_reason']}." for r in retained]
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
