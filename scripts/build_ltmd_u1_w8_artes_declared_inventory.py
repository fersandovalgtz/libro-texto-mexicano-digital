#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

SCOPE=Path('data/catalog/ltmd_u1_w8_scope.csv')
ARCH=Path('data/catalog/ltmd_u1_w8_viewer_architecture.csv')
OUT=Path('data/catalog/ltmd_u1_w8_declared_inventory.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w8_declared_inventory_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w8_declared_inventory.md')
VERSION='LTMD_U1_W8_DECLARED_INVENTORY_0.1'
EXPECTED=20
UA='LibroTextoMexicanoDigital/U1-W8 Arts declared inventory'

def main():
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    arch={r['viewer_key']:r for r in csv.DictReader(ARCH.open(encoding='utf-8',newline=''))}
    if len(scope)!=EXPECTED or len(arch)!=EXPECTED:raise SystemExit(f'W8 scope/architecture mismatch {len(scope)}/{len(arch)}')
    with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=45) as r:cfg=json.loads(r.read().decode('utf-8-sig'))
    rows=[]
    for s in scope:
        d=cfg.get(s['viewer_key'])
        if not isinstance(d,dict):raise SystemExit(f'missing claves config {s["viewer_key"]}')
        try:n=int(d.get('ag_pages'))
        except Exception:raise SystemExit(f'invalid ag_pages {s["viewer_key"]}: {d.get("ag_pages")!r}')
        if n<=0:raise SystemExit(f'nonpositive ag_pages {s["viewer_key"]}: {n}')
        rows.append({'inventory_version':VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'ag_clave':str(d.get('ag_clave','')),'declared_positions':n,'standard_dynamic_architecture':arch[s['viewer_key']]['standard_dynamic_architecture'],'source_url':s['source_url']})
    rows.sort(key=lambda x:(int(x['catalog_generation']),int(x['grade_code']),x['viewer_key']))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    by=defaultdict(lambda:[0,0,0])
    for r in rows:
        g=r['catalog_generation'];by[g][0]+=1;by[g][1]+=int(r['declared_positions']);by[g][2]+=int(r['standard_dynamic_architecture'])
    sr=[{'inventory_version':VERSION,'catalog_generation':g,'viewer_count':n,'declared_positions':p,'standard_architecture_count':st} for g,(n,p,st) in sorted(by.items(),key=lambda x:int(x[0]))]
    sr.append({'inventory_version':VERSION,'catalog_generation':'ALL','viewer_count':len(rows),'declared_positions':sum(int(r['declared_positions']) for r in rows),'standard_architecture_count':sum(int(r['standard_dynamic_architecture']) for r in rows)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(sr[0]));w.writeheader();w.writerows(sr)
    total=int(sr[-1]['declared_positions']);nonstandard=[r['viewer_key'] for r in rows if r['standard_dynamic_architecture']!='1']
    lines=['# LTMD-U1 W8 — inventario declarado Artes','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.',f'- Posiciones declaradas por `claves.json`: **{total:,}**.',f'- Arquitectura HTML estándar: **{EXPECTED-len(nonstandard)}/{EXPECTED}**.',f'- Excepciones HTML conservadas: **{len(nonstandard)}**' + (f" (`{', '.join(nonstandard)}`)" if nonstandard else '') + '.','','## Por generación','', '| generación | visores | posiciones declaradas | estándar HTML |','|---:|---:|---:|---:|']
    for r in sr[:-1]:lines.append(f"| {r['catalog_generation']} | {r['viewer_count']} | {int(r['declared_positions']):,} | {r['standard_architecture_count']} |")
    lines += ['', 'El registro central `claves.json` se usa únicamente como inventario declarado. No prueba que las posiciones estén servidas ni convierte una configuración en fuente suficiente.', '', 'La siguiente capa audita posición por posición, hashea cada activo servido y conserva terminales sintéticos, huecos internos, rutas alternativas y errores. OCR sigue cerrado.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
