#!/usr/bin/env python3
"""Extend the live U1 dashboard with finalized W2 Mathematics evidence, stage by stage."""
from __future__ import annotations
import csv,subprocess
from collections import defaultdict
from pathlib import Path

BASE='scripts/build_ltmd_u1_coverage_current.py'
COVERAGE=Path('data/catalog/ltmd_u1_coverage.csv');SUMMARY=Path('data/catalog/ltmd_u1_coverage_summary.csv');DOMAIN=Path('data/catalog/ltmd_u1_domain_summary.csv');QUEUE=Path('data/catalog/ltmd_u1_wave_queue.csv');REPORT=Path('data/catalog/ltmd_u1_coverage.md')
REC=Path('data/catalog/ltmd_u1_w2_math_reconciled_summary.csv');ALIASES=Path('data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv');OCR=Path('data/catalog/ltmd_u1_w2_math_ocr_summary.csv');PS=Path('data/catalog/ltmd_u1_w2_math_page_structure_summary.csv');FRAG=Path('data/catalog/ltmd_u1_w2_math_fragment_manifest_summary.csv')
VERSION='LTMD_U1_COVERAGE_0.5';U=542

def rows(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(p,rr):
 with p.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)

def main():
 subprocess.run(['python3',BASE],check=True)
 cov=rows(COVERAGE);by={r['viewer_key']:r for r in cov}
 if len(cov)!=U:raise SystemExit(f'coverage cardinality={len(cov)}')
 if not REC.exists() or not ALIASES.exists():raise SystemExit('W2 reconciled asset evidence missing')
 rec=rows(REC);aliases=rows(ALIASES)
 if len(rec)!=64:raise SystemExit(f'W2 reconciled summary={len(rec)} expected=64')
 ready={r['viewer_key'] for r in rec if r['effective_asset_ready']=='1'}
 if len(ready)!=60:raise SystemExit(f'W2 effective-ready={len(ready)} expected=60')
 alias_map={r['viewer_key']:r['canonical_viewer_key'] for r in aliases if r['all_effective_pages_byte_identical_aligned']=='1'}
 if len(alias_map)!=3 or not set(alias_map)<=ready:raise SystemExit(f'W2 alias topology invalid: {alias_map}')
 for r in rec:
  v=r['viewer_key'];c=by[v]
  if v in ready:
   c['asset_resolved_full']='1';c['asset_resolved_partial']='0';c['page_manifest_ready']='1';c['asset_status']='full_effective_w2_math_reconciled'
  elif int(r['effective_unresolved'])>0:
   c['asset_status']='unresolved_w2_math_routing'

 if OCR.exists():
  oo=rows(OCR)
  if len(oo)!=57 or {r['ocr_version'] for r in oo}!={'LTMD_U1_W2_MATH_OCR_0.2'}:raise SystemExit('invalid W2 OCR 0.2 summary')
  for s in oo:
   if int(s['pages'])==int(s['sha_verified']) and int(s['unresolved'])==0:by[s['viewer_key']]['ocr_ready']='1'

 if PS.exists():
  pp=rows(PS);pkeys={r['viewer_key'] for r in pp if r['viewer_key']!='ALL'}
  if len(pkeys)!=57:raise SystemExit(f'W2 PAGESTRUCT canonical viewers={len(pkeys)}')
  for v in pkeys:by[v]['pagestruct_ready']='1'

 if FRAG.exists():
  ff=rows(FRAG);frows=[r for r in ff if r['viewer_key']!='ALL']
  if len(frows)!=57 or {r['segmenter_version'] for r in frows}!={'FRAGSEG_LTMD_U1_W2_MATH_0.2'}:raise SystemExit('invalid W2 FRAGSEG 0.2 summary')
  for s in frows:
   if int(s['fragment_count'])<=0 or int(s['segmented_page_count'])<=0:raise SystemExit(f'empty W2 FRAGSEG viewer {s["viewer_key"]}')
   c=by[s['viewer_key']];c['fragseg_materialized']='1';c['effective_fragseg_coverage']='1';c['fragment_count_materialized']=s['fragment_count'];c['wave_priority']='0';c['wave_label']='U1-W0-materializado';c['queue_status']='materialized_direct'
  for alias,canonical in alias_map.items():
   if by[canonical]['fragseg_materialized']!='1':raise SystemExit(f'alias canonical not materialized: {canonical}')
   c=by[alias];c['effective_fragseg_coverage']='1';c['coverage_inherited_from_viewer']=canonical;c['wave_priority']='0';c['wave_label']='U1-W0-alias-cubierto';c['queue_status']='covered_alias'

 for r in cov:r['coverage_version']=VERSION
 write(COVERAGE,cov)
 def count(k):return sum(int(r[k]) for r in cov)
 stages=[('cataloged',count('cataloged'),'All viewers in frozen U1 catalog snapshot.'),('title_normalized',count('title_normalized'),'Normalized title-core families.'),('asset_resolved_full',count('asset_resolved_full'),'Full source-asset resolution demonstrated, direct or cryptographically reconciled.'),('asset_resolved_partial',count('asset_resolved_partial'),'Known partial source resolution; separate from full coverage.'),('page_manifest_ready_direct',count('page_manifest_ready'),'Page/source manifest materialized; may include explicitly reconciled source positions.'),('ocr_ready_direct',count('ocr_ready'),'Technical OCR layer directly materialized on canonical content.'),('pagestruct_ready_direct',count('pagestruct_ready'),'PAGESTRUCT directly materialized on canonical content.'),('fragseg_materialized_direct',count('fragseg_materialized'),'FRAGSEG directly materialized on canonical content.'),('effective_fragseg_coverage',count('effective_fragseg_coverage'),'Direct FRAGSEG plus verified byte-identical aliases.'),('dependence_audited',count('dependence_audited'),'Viewer participates in registered documentary dependence.'),('semantic_ready_validated',0,'SEMB 0.3 remains WAITING_HUMAN_REFERENCE.')]
 sr=[{'coverage_version':VERSION,'stage':s,'viewer_count':n,'universe_viewers':U,'percent':f'{100*n/U:.2f}','notes':note} for s,n,note in stages];write(SUMMARY,sr)
 grouped=defaultdict(list)
 for r in cov:grouped[r['operational_domain']].append(r)
 old={r['operational_domain']:r for r in rows(DOMAIN)} if DOMAIN.exists() else {};dr=[]
 for domain,rr in grouped.items():
  total=len(rr);direct=sum(int(r['fragseg_materialized']) for r in rr);effective=sum(int(r['effective_fragseg_coverage']) for r in rr);full=sum(int(r['asset_resolved_full']) for r in rr);prior=old.get(domain,{});queued=[r for r in rr if r['queue_status']=='queued']
  if queued:wave=prior.get('next_wave_label') or queued[0]['wave_label'];priority=prior.get('next_wave_priority') or queued[0]['wave_priority']
  else:wave='completed_domain';priority='0'
  dr.append({'coverage_version':VERSION,'operational_domain':domain,'viewer_count':total,'percent_of_u1':f'{100*total/U:.2f}','asset_resolved_full':full,'fragseg_materialized_direct':direct,'effective_fragseg_coverage':effective,'remaining_effective':total-effective,'next_wave_priority':priority,'next_wave_label':wave})
 dr.sort(key=lambda r:(int(r['next_wave_priority']) if str(r['next_wave_priority']).isdigit() else 999,r['operational_domain']));write(DOMAIN,dr)
 qf=['coverage_version','wave_priority','wave_label','queue_status','operational_domain','viewer_key','catalog_generation','grade_code','title_core','asset_status','effective_fragseg_coverage','coverage_inherited_from_viewer','source_url'];qr=sorted(cov,key=lambda r:(int(r['wave_priority']),int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
 with QUEUE.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=qf);w.writeheader();w.writerows([{k:r[k] for k in qf} for r in qr])
 sm={s:n for s,n,_ in stages};lines=['# LTMD-U1 — tablero maestro de cobertura','',f'Versión: **{VERSION}**  ',f'Universo operativo U1: **{U} visores**.','', '## Estado ejecutivo','',f"- Activos completamente resueltos: **{sm['asset_resolved_full']}/{U} ({100*sm['asset_resolved_full']/U:.2f}%)**.",f"- Manifiesto de fuente listo: **{sm['page_manifest_ready_direct']}/{U} ({100*sm['page_manifest_ready_direct']/U:.2f}%)**.",f"- OCR directo canónico: **{sm['ocr_ready_direct']}/{U} ({100*sm['ocr_ready_direct']/U:.2f}%)**.",f"- PAGESTRUCT directo canónico: **{sm['pagestruct_ready_direct']}/{U} ({100*sm['pagestruct_ready_direct']/U:.2f}%)**.",f"- FRAGSEG directo: **{sm['fragseg_materialized_direct']}/{U} ({100*sm['fragseg_materialized_direct']/U:.2f}%)**.",f"- Cobertura FRAGSEG efectiva: **{sm['effective_fragseg_coverage']}/{U} ({100*sm['effective_fragseg_coverage']/U:.2f}%)**.",'- Semántica humana validada: **0/542**.','', 'W2 Matemáticas conserva 4 DMA 2018 como excepciones de routing no resueltas; no reciben crédito por similitud nominal. Los aliases exactos sólo heredan cobertura efectiva después de que su contenido canónico llegue a FRAGSEG.','', '## Cobertura por dominio operativo','', '| dominio | visores | activos full | FRAGSEG directo | efectiva | restantes | próxima ola |','|---|---:|---:|---:|---:|---:|---|']
 for r in dr:lines.append(f"| {r['operational_domain']} | {r['viewer_count']} | {r['asset_resolved_full']} | {r['fragseg_materialized_direct']} | {r['effective_fragseg_coverage']} | {r['remaining_effective']} | {r['next_wave_label']} |")
 lines+=['','## Regla','Cada KPI se promueve sólo con el artefacto final correspondiente. Resolución de activos, OCR, PAGESTRUCT, FRAGSEG y semántica son capas separadas.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(f"{VERSION}: assets={sm['asset_resolved_full']} manifest={sm['page_manifest_ready_direct']} ocr={sm['ocr_ready_direct']} pagestruct={sm['pagestruct_ready_direct']} fragseg={sm['fragseg_materialized_direct']} effective={sm['effective_fragseg_coverage']}")
if __name__=='__main__':main()
