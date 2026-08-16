#!/usr/bin/env python3
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
INV=Path('data/catalog/ltmd_u1_w3_declared_inventory.csv');OUT=Path('data/catalog/ltmd_u1_w3_ag_clave_reuse.csv');REPORT=Path('data/catalog/ltmd_u1_w3_ag_clave_reuse.md');VERSION='LTMD_U1_W3_AG_CLAVE_REUSE_0.1'

def main():
 rows=list(csv.DictReader(INV.open(encoding='utf-8',newline='')));by=defaultdict(list)
 for r in rows:
  key=r['ag_clave'];
  if key:by[key].append(r)
 reused={k:v for k,v in by.items() if len(v)>1};out=[];g=0
 for key,rr in sorted(reused.items()):
  g+=1
  for r in sorted(rr,key=lambda x:(int(x['catalog_generation']),int(x['grade_code']),x['viewer_key'])):
   out.append({'audit_version':VERSION,'reuse_group':f'W3-AG-{g:03d}','ag_clave':key,'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'declared_positions':r['declared_positions'],'interpretive_limit':'Shared institutional ag_clave is a routing/dependence signal, not proof of byte-identical content.'})
 fields=['audit_version','reuse_group','ag_clave','viewer_key','catalog_generation','grade_code','title_core','declared_positions','interpretive_limit']
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
 lines=['# LTMD-U1 W3 — reutilización de `ag_clave`','',f'Versión: `{VERSION}`.','',f'- Visores: **{len(rows)}**.',f'- Claves institucionales reutilizadas por >1 visor: **{len(reused)}**.',f'- Visores implicados: **{len(out)}**.','']
 for key,rr in sorted(reused.items()):lines.append(f"- `{key}`: "+', '.join(f"{r['viewer_key']} (G{r['catalog_generation']}, {r['declared_positions']} pos.)" for r in rr))
 lines+=['','Compartir `ag_clave` se registra como señal de routing/dependencia. No se declara alias hasta comparar todos los activos con SHA-256 y byte-size.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
