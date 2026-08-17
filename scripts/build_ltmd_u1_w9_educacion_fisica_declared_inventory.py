#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
from urllib.request import Request,urlopen

SCOPE=Path('data/catalog/ltmd_u1_w9_scope.csv')
ARCH=Path('data/catalog/ltmd_u1_w9_viewer_architecture.csv')
OUT=Path('data/catalog/ltmd_u1_w9_declared_inventory.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w9_declared_inventory_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w9_declared_inventory.md')
VERSION='LTMD_U1_W9_DECLARED_INVENTORY_0.1'
EXPECTED=4
UA='LibroTextoMexicanoDigital/U1-W9 Physical Education declared inventory'

def main():
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')));arch={r['viewer_key']:r for r in csv.DictReader(ARCH.open(encoding='utf-8',newline=''))}
    if len(scope)!=EXPECTED or len(arch)!=EXPECTED:raise SystemExit(f'W9 scope/architecture mismatch {len(scope)}/{len(arch)}')
    with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=45) as r:cfg=json.loads(r.read().decode('utf-8-sig'))
    rows=[]
    for s in scope:
        d=cfg.get(s['viewer_key'])
        if not isinstance(d,dict):raise SystemExit(f'missing claves config {s["viewer_key"]}')
        try:n=int(d.get('ag_pages'))
        except Exception:raise SystemExit(f'invalid ag_pages {s["viewer_key"]}: {d.get("ag_pages")!r}')
        if n<=0:raise SystemExit(f'nonpositive ag_pages {s["viewer_key"]}: {n}')
        rows.append({'inventory_version':VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'ag_clave':str(d.get('ag_clave','')),'declared_positions':n,'standard_dynamic_architecture':arch[s['viewer_key']]['standard_dynamic_architecture'],'source_url':s['source_url']})
    rows.sort(key=lambda x:(int(x['grade_code']),x['viewer_key']))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    total=sum(int(r['declared_positions']) for r in rows);standard=sum(int(r['standard_dynamic_architecture']) for r in rows)
    sr=[{'inventory_version':VERSION,'catalog_generation':'2008','viewer_count':len(rows),'declared_positions':total,'standard_architecture_count':standard}]
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(sr[0]));w.writeheader();w.writerows(sr)
    lines=['# LTMD-U1 W9 — inventario declarado Educación Física','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.',f'- Posiciones declaradas por `claves.json`: **{total:,}**.',f'- Arquitectura HTML estándar: **{standard}/{EXPECTED}**.','','## Por visor','', '| visor | grado | posiciones declaradas | estándar HTML |','|---|---:|---:|---:|']
    for r in rows:lines.append(f"| `{r['viewer_key']}` | {r['grade_code']} | {int(r['declared_positions']):,} | {r['standard_dynamic_architecture']} |")
    lines+=['','`claves.json` se usa sólo como inventario declarado. No prueba que las posiciones estén servidas y no abre OCR. La siguiente capa debe auditar los activos posición por posición y conservar SHA-256, tamaño, huecos y errores.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
