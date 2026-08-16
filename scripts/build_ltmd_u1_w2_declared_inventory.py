#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen
SCOPE=Path('data/catalog/ltmd_u1_w2_scope.csv');OUT=Path('data/catalog/ltmd_u1_w2_declared_inventory.csv');SUMMARY=Path('data/catalog/ltmd_u1_w2_declared_inventory_summary.csv');REPORT=Path('data/catalog/ltmd_u1_w2_declared_inventory.md');VERSION='LTMD_U1_W2_DECLARED_INVENTORY_0.1';UA='LibroTextoMexicanoDigital/U1-W2 declared inventory';EXPECTED=64
def main():
 scope=list(csv.DictReader(SCOPE.open(encoding='utf-8')))
 if len(scope)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} W2 viewers got {len(scope)}')
 with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=45) as r:cfg=json.loads(r.read().decode('utf-8-sig'))
 out=[]
 for r in scope:
  c=cfg.get(r['viewer_key'])
  if not isinstance(c,dict) or 'ag_pages' not in c:raise SystemExit(f"missing ag_pages {r['viewer_key']}")
  n=int(c['ag_pages'])
  if n<=0:raise SystemExit(f"invalid ag_pages {r['viewer_key']}={n}")
  out.append({'inventory_version':VERSION,'viewer_key':r['viewer_key'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade_code':r['grade_code'],'title_core':r['title_core'],'declared_positions':n,'source_url':r['source_url']})
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 gen=Counter();books=Counter()
 for r in out:gen[r['catalog_generation']]+=int(r['declared_positions']);books[r['catalog_generation']]+=1
 summary=[]
 for g in sorted(books,key=int):summary.append({'inventory_version':VERSION,'catalog_generation':g,'viewer_count':books[g],'declared_positions':gen[g]})
 summary.append({'inventory_version':VERSION,'catalog_generation':'ALL','viewer_count':len(out),'declared_positions':sum(int(r['declared_positions']) for r in out)})
 with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
 total=summary[-1]['declared_positions'];lines=['# LTMD-U1 W2 — inventario declarado de Matemáticas','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.\n- Posiciones declaradas por `claves.json`: **{total:,}**.','', '## Por generación','', '| generación | visores | posiciones declaradas |','|---:|---:|---:|']+[f"| {r['catalog_generation']} | {r['viewer_count']} | {int(r['declared_positions']):,} |" for r in summary if r['catalog_generation']!='ALL']+['','Este inventario no presupone que cada posición tenga un JPEG real ni que el último folio sea sintético. La siguiente capa deberá probar empíricamente los activos y sus hashes.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
