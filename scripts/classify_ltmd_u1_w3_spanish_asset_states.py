#!/usr/bin/env python3
"""Classify W3 Spanish/Language viewers after the full source-asset audit.

Operational routing only: no bibliographic identity, OCR, semantic or historical
inference is made here.
"""
from __future__ import annotations
import csv
from pathlib import Path

IN=Path('data/catalog/ltmd_u1_w3_spanish_asset_summary.csv')
OUT=Path('data/catalog/ltmd_u1_w3_spanish_asset_states.csv')
REPORT=Path('data/catalog/ltmd_u1_w3_spanish_asset_states.md')
VERSION='LTMD_U1_W3_SPANISH_ASSET_STATES_0.1'
EXPECTED=130

def main():
 rows=list(csv.DictReader(IN.open(encoding='utf-8')))
 if len(rows)!=EXPECTED or len({r['viewer_key'] for r in rows})!=EXPECTED:
  raise SystemExit(f'expected {EXPECTED} unique W3 viewer summaries, got {len(rows)}')
 out=[]
 for r in rows:
  declared=int(r['declared_positions']);served=int(r['source_jpegs']);internal=int(r['internal_unserved']);terminal=int(r['terminal_synthetic_candidates']);errors=int(r['probe_errors']);direct=int(r['direct_asset_ready'])
  if errors:
   state,action='probe_failure','rerun_or_diagnose_transport'
  elif direct:
   state,action='full_direct','eligible_for_exact_alias_audit_then_reconciliation'
  elif served==0 and internal>=max(1,declared-terminal-1):
   state,action='routing_anomaly_all_or_near_all','resolve_alternate_asset_route'
  elif served>0 and internal>0:
   state,action='partial_internal_unserved','cryptographic_recovery_or_exception'
  else:
   state,action='other_nonready','technical_diagnosis'
  out.append({'state_version':VERSION,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'viewer_ui':r['viewer_ui'],'ag_clave':r['ag_clave'],'declared_positions':declared,'source_jpegs':served,'terminal_synthetic_candidates':terminal,'internal_unserved':internal,'probe_errors':errors,'asset_state':state,'next_action':action})
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 states=sorted({r['asset_state'] for r in out});counts={s:sum(r['asset_state']==s for r in out) for s in states}
 lines=['# LTMD-U1 W3 — estados de activos Español/Lengua','',f'Versión: `{VERSION}`.','',f'- Visores clasificados: **{len(out)}/{EXPECTED}**.']
 for s in states:lines.append(f'- `{s}`: **{counts[s]}**.')
 lines+=['','## Casos no directos']
 bad=[r for r in out if r['asset_state']!='full_direct']
 if not bad:lines.append('- Ninguno.')
 else:
  for r in bad:lines.append(f"- `{r['viewer_key']}` ({r['catalog_generation']}, grado {r['grade_code']}, UI={r['viewer_ui']}): `{r['asset_state']}`; JPEG={r['source_jpegs']}/{r['declared_positions']}; internos={r['internal_unserved']}; terminales={r['terminal_synthetic_candidates']}; siguiente acción=`{r['next_action']}`.")
 lines+=['','## Interpretación','Esta clasificación sólo enruta trabajo técnico. No deduce identidad bibliográfica ni convierte una anomalía en alias. Sólo los objetos `full_direct`, o los posteriormente reconciliados con evidencia documental o criptográfica suficiente, podrán entrar a OCR.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
