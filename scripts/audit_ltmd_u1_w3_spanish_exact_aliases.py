#!/usr/bin/env python3
"""Detect exact aligned byte aliases among direct-ready W3 Spanish viewers.

An alias is asserted only from the complete served source-JPEG sequence with
identical viewer_page, SHA-256 and byte size. No title/year/OCR similarity is used.
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

MAN=Path('data/catalog/ltmd_u1_w3_spanish_asset_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w3_spanish_asset_summary.csv')
OUT=Path('data/catalog/ltmd_u1_w3_spanish_exact_aliases.csv')
REPORT=Path('data/catalog/ltmd_u1_w3_spanish_exact_aliases.md')
VERSION='LTMD_U1_W3_SPANISH_EXACT_ALIASES_0.1'
EXPECTED=130

def rows(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
 manifest=rows(MAN);summary=rows(SUMMARY)
 if len(summary)!=EXPECTED or len({r['viewer_key'] for r in summary})!=EXPECTED:raise SystemExit('W3 summary coverage mismatch')
 ready={r['viewer_key']:r for r in summary if int(r['direct_asset_ready'])==1}
 by=defaultdict(list)
 for r in manifest:
  if r['viewer_key'] in ready and r['asset_status']=='source_jpeg':by[r['viewer_key']].append(r)
 sigs=defaultdict(list)
 for viewer,rr in by.items():
  rr.sort(key=lambda r:int(r['viewer_page']))
  sig=tuple((int(r['viewer_page']),r['sha256'],int(r['byte_size'])) for r in rr)
  expected=int(ready[viewer]['source_jpegs'])
  if len(sig)!=expected or any(not sha for _,sha,_ in sig):raise SystemExit(f'incomplete direct-ready signature for {viewer}')
  sigs[sig].append(viewer)
 aliases=[];group_no=0
 for sig,viewers in sorted(sigs.items(),key=lambda item:item[1]):
  if len(viewers)<2:continue
  group_no+=1;viewers=sorted(viewers);canonical=viewers[0]
  for viewer in viewers[1:]:
   aliases.append({'alias_version':VERSION,'alias_group':f'SPANISH-ALIAS-{group_no:03d}','viewer_key':viewer,'canonical_viewer_key':canonical,'source_jpeg_count':len(sig),'all_pages_byte_identical_aligned':1,'interpretive_limit':'Operational byte alias only; catalog and bibliographic identities remain distinct.'})
 OUT.parent.mkdir(parents=True,exist_ok=True)
 fields=['alias_version','alias_group','viewer_key','canonical_viewer_key','source_jpeg_count','all_pages_byte_identical_aligned','interpretive_limit']
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(aliases)
 groups=len({r['alias_group'] for r in aliases})
 lines=['# LTMD-U1 W3 — aliases exactos Español/Lengua','',f'Versión: `{VERSION}`.','',f'- Visores `direct_asset_ready`: **{len(ready)}**.',f'- Grupos con ≥2 objetos byte-idénticos alineados: **{groups}**.',f'- Visores alias reutilizables operacionalmente: **{len(aliases)}**.','','## Criterio','','Un alias sólo se registra si la secuencia completa de páginas fuente servidas coincide en `viewer_page`, tamaño y SHA-256. No se usa similitud de título, año, grado, OCR ni resultados semánticos.','','El canónico es una decisión operacional para evitar cómputo duplicado; no implica prioridad bibliográfica ni identidad histórica de registros.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
