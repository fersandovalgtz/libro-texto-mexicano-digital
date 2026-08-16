#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
IN=Path('data/catalog/ltmd_u1_w2_viewer_architecture.json');OUT=Path('data/catalog/ltmd_u1_w2_viewer_architecture_summary.csv');REPORT=Path('data/catalog/ltmd_u1_w2_viewer_architecture.md');VERSION='LTMD_U1_W2_ARCHITECTURE_0.1';EXPECTED=64
def main():
 data=json.loads(IN.read_text(encoding='utf-8'))
 if len(data)!=EXPECTED or len({r['viewer_url'] for r in data})!=EXPECTED:raise SystemExit(f'expected {EXPECTED} unique probes, got {len(data)}')
 rows=[]
 for r in data:
  scripts=r.get('same_origin_script_assets',[]);urls=[x.get('url','') for x in scripts];xjs=any(u.endswith('/x.js') for u in urls);xsignal=any(any('ag_pages' in line for line in x.get('signal_lines',[])) for x in scripts if x.get('url','').endswith('/x.js'));html_ok=r.get('html',{}).get('http_status')==200;status=r.get('status','')
  rows.append({'architecture_version':VERSION,'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'viewer_url':r['viewer_url'],'probe_status':status,'html_200':int(html_ok),'x_js_present':int(xjs),'x_js_ag_pages_signal':int(xsignal),'same_origin_script_count':len(scripts),'standard_dynamic_architecture':int(status=='ok' and html_ok and xjs and xsignal)})
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 gen=defaultdict(lambda:Counter())
 for r in rows:
  g=gen[r['catalog_generation']];g['n']+=1;g['standard']+=r['standard_dynamic_architecture'];g['html200']+=r['html_200'];g['xjs']+=r['x_js_present']
 total=sum(r['standard_dynamic_architecture'] for r in rows);bad=[r for r in rows if not r['standard_dynamic_architecture']]
 lines=['# LTMD-U1 W2 — arquitectura de visores de Matemáticas','',f'Versión: `{VERSION}`.','',f'- Visores congelados: **{len(rows)}**.\n- HTML 200: **{sum(r["html_200"] for r in rows)}/{len(rows)}**.\n- `x.js` presente: **{sum(r["x_js_present"] for r in rows)}/{len(rows)}**.\n- Señal `ag_pages` en `x.js`: **{sum(r["x_js_ag_pages_signal"] for r in rows)}/{len(rows)}**.\n- Arquitectura dinámica estándar completa: **{total}/{len(rows)}**.\n- Casos no estándar: **{len(bad)}**.','', '## Por generación','', '| generación | visores | HTML 200 | x.js | estándar |','|---:|---:|---:|---:|---:|']
 for g in sorted(gen,key=int):lines.append(f"| {g} | {gen[g]['n']} | {gen[g]['html200']} | {gen[g]['xjs']} | {gen[g]['standard']} |")
 if bad:
  lines+=['','## Casos no estándar']+[f"- `{r['book_id']}` ({r['catalog_generation']}): status={r['probe_status']}; html200={r['html_200']}; xjs={r['x_js_present']}; ag_pages_signal={r['x_js_ag_pages_signal']}." for r in bad]
 lines+=['','## Interpretación','Este probe no descarga páginas ni prueba que todos los activos estén servidos. Sólo determina si el visor comparte la arquitectura pública que permite pasar a `claves.json` y a una auditoría empírica de activos. La promoción de W2 a ingestión requiere todavía manifiesto SHA-256 por objeto.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
