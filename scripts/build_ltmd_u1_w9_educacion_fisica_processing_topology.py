#!/usr/bin/env python3
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

VERSION='LTMD_U1_W9_EDUCACION_FISICA_PROCESSING_TOPOLOGY_0.1'
EXPECTED_IDENTITIES=4;EXPECTED_ADMITTED=4;EXPECTED_RETAINED=0;EXPECTED_SOURCE_PAGES=448
ADM=Path('data/catalog/ltmd_u1_w9_educacion_fisica_source_admissibility.csv')
ASSETS=Path('data/catalog/ltmd_u1_w9_educacion_fisica_asset_manifest.csv')
PROCESSING=Path('data/catalog/ltmd_u1_w9_processing_inventory.csv')
PAGES=Path('data/catalog/ltmd_u1_w9_canonical_page_manifest.csv')
REPORT=Path('docs/LTMD_U1_W9_EDUCACION_FISICA_PROCESSING_TOPOLOGY.md')
PROCESSING_FIELDS=['topology_version','book_id','viewer_key','catalog_generation','grade_code','title_core','source_status','processing_mode','is_canonical_processing_object','ocr_identity_eligible','source_page_count','declared_positions','persistent_internal_source_gaps','probe_errors','semantic_state','alias_state','source_url']
PAGE_FIELDS=['manifest_version','page_id','book_id','viewer_key','catalog_generation','grade_code','title_core','viewer_page','source_image_index','processing_mode','source_provenance','source_asset_url','byte_size','sha256','asset_status']

def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def page_id(k,p):return f'U1-{k}-P{int(p):03d}'
def main():
 adm=read(ADM);assets=read(ASSETS)
 if len(adm)!=EXPECTED_IDENTITIES or len({r['viewer_key'] for r in adm})!=EXPECTED_IDENTITIES:raise SystemExit('W9 topology admissibility cardinality mismatch')
 by={r['viewer_key']:r for r in adm};admitted={k for k,r in by.items() if r['source_status']=='SOURCE_ADMISSIBLE'};retained={k for k,r in by.items() if r['source_status']=='SOURCE_RETAINED'}
 if len(admitted)!=EXPECTED_ADMITTED or len(retained)!=EXPECTED_RETAINED:raise SystemExit(f'W9 observed source partition drift: {len(admitted)}/{len(retained)}')
 if {r['viewer_key'] for r in assets}!=set(by):raise SystemExit('W9 asset/admissibility identity drift')
 source=[r for r in assets if r['asset_status']=='source_jpeg']
 if len(source)!=EXPECTED_SOURCE_PAGES:raise SystemExit(f'W9 expected {EXPECTED_SOURCE_PAGES} source JPEGs, got {len(source)}')
 if any(r['viewer_key'] not in admitted for r in source):raise SystemExit('W9 retained viewer contributed source JPEG')
 if any(not r['sha256'] or len(r['sha256'])!=64 or int(r['byte_size'] or 0)<=0 for r in source):raise SystemExit('W9 source page provenance failure')
 counts=Counter(r['viewer_key'] for r in source);proc=[]
 for k in sorted(by,key=lambda x:(int(by[x]['grade_code']),x)):
  r=by[k];observed=counts.get(k,0);expected=int(r['source_jpegs'])
  if observed!=expected:raise SystemExit(f'W9 page-count drift {k}: {observed}/{expected}')
  if k in admitted:
   if r['source_admissible']!='1' or r['direct_asset_ready']!='1' or int(r['internal_unserved']) or int(r['probe_errors']):raise SystemExit(f'W9 admitted source flags invalid {k}')
   mode='direct_canonical'
  else:mode='withheld_source'
  proc.append({'topology_version':VERSION,'book_id':r['book_id'],'viewer_key':k,'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'source_status':r['source_status'],'processing_mode':mode,'is_canonical_processing_object':int(k in admitted),'ocr_identity_eligible':int(k in admitted),'source_page_count':observed,'declared_positions':r['declared_positions'],'persistent_internal_source_gaps':r['internal_unserved'],'probe_errors':r['probe_errors'],'semantic_state':r['semantic_state'],'alias_state':r['alias_state'],'source_url':r['source_url']})
 pages=[];seen=set()
 for r in sorted(source,key=lambda x:(x['viewer_key'],int(x['viewer_page']))):
  a=by[r['viewer_key']];pid=page_id(r['viewer_key'],r['viewer_page'])
  if pid in seen:raise SystemExit(f'duplicate W9 page_id {pid}')
  seen.add(pid);pages.append({'manifest_version':VERSION,'page_id':pid,'book_id':a['book_id'],'viewer_key':r['viewer_key'],'catalog_generation':a['catalog_generation'],'grade_code':a['grade_code'],'title_core':a['title_core'],'viewer_page':r['viewer_page'],'source_image_index':r['source_image_index'],'processing_mode':'direct_canonical','source_provenance':'official_conaliteg_source_jpeg_sha256_verified','source_asset_url':r['source_asset_url'],'byte_size':r['byte_size'],'sha256':r['sha256'],'asset_status':r['asset_status']})
 if len(pages)!=EXPECTED_SOURCE_PAGES or {r['viewer_key'] for r in pages}!=admitted:raise SystemExit('W9 canonical page manifest coverage mismatch')
 with PROCESSING.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=PROCESSING_FIELDS);w.writeheader();w.writerows(proc)
 with PAGES.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=PAGE_FIELDS);w.writeheader();w.writerows(pages)
 lines=['# LTMD-U1 W9 Educación Física — topología cerrada de procesamiento','',f'Versión: `{VERSION}`.','',f'- Identidades W9: **{EXPECTED_IDENTITIES}**.',f'- Objetos canónicos admitidos a OCR: **{EXPECTED_ADMITTED}**.',f'- Identidades retenidas por fuente: **{EXPECTED_RETAINED}**.',f'- JPEG fuente canónicos con SHA-256/tamaño: **{EXPECTED_SOURCE_PAGES}**.','- Alias creados: **0**.','','## Cobertura por visor','', '| visor | grado | páginas fuente |','|---|---:|---:|']
 for r in proc:lines.append(f"| `{r['viewer_key']}` | {r['grade_code']} | {r['source_page_count']} |")
 lines+=['','Cada fila del manifiesto canónico conserva URL oficial, índice, tamaño y SHA-256. Esta topología no descarga ni relicencia JPEG y no crea equivalencias históricas o semánticas.','','Este producto abre exclusivamente la fase OCR técnica de los cuatro objetos admitidos.']
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
