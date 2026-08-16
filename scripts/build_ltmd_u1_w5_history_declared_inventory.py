#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

SCOPE=Path('data/catalog/ltmd_u1_w5_scope.csv')
OUT=Path('data/catalog/ltmd_u1_w5_declared_inventory.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w5_declared_inventory_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w5_declared_inventory.md')
VERSION='LTMD_U1_W5_DECLARED_INVENTORY_0.1'
EXPECTED=18
UA='LibroTextoMexicanoDigital/U1-W5 History declared inventory'

def main():
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    if len(scope)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} W5 viewers, got {len(scope)}')
    with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=45) as r:cfg=json.loads(r.read().decode('utf-8-sig'))
    rows=[]
    for s in scope:
        d=cfg.get(s['viewer_key'])
        if not isinstance(d,dict):raise SystemExit(f'missing claves config {s["viewer_key"]}')
        try:n=int(d.get('ag_pages'))
        except Exception:raise SystemExit(f'invalid ag_pages {s["viewer_key"]}: {d.get("ag_pages")!r}')
        rows.append({'inventory_version':VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'ag_clave':str(d.get('ag_clave','')),'declared_positions':n,'source_url':s['source_url']})
    rows.sort(key=lambda x:(int(x['catalog_generation']),int(x['grade_code']),x['viewer_key']))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    by=defaultdict(lambda:[0,0])
    for r in rows:g=r['catalog_generation'];by[g][0]+=1;by[g][1]+=int(r['declared_positions'])
    sr=[{'inventory_version':VERSION,'catalog_generation':g,'viewer_count':n,'declared_positions':p} for g,(n,p) in sorted(by.items(),key=lambda x:int(x[0]))]
    sr.append({'inventory_version':VERSION,'catalog_generation':'ALL','viewer_count':len(rows),'declared_positions':sum(int(r['declared_positions']) for r in rows)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(sr[0]));w.writeheader();w.writerows(sr)
    total=int(sr[-1]['declared_positions']);lines=['# LTMD-U1 W5 — inventario declarado Historia','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED}**.',f'- Posiciones declaradas por `claves.json`: **{total:,}**.','','## Por generación','', '| generación | visores | posiciones declaradas |','|---:|---:|---:|']
    for r in sr[:-1]:lines.append(f"| {r['catalog_generation']} | {r['viewer_count']} | {int(r['declared_positions']):,} |")
    lines += ['', 'Este inventario no acredita que cada posición declarada corresponda a un JPEG servido. La auditoría de activos debe probar cada posición y conservar explícitamente terminales sintéticos, huecos internos y errores de probe.', '', 'La similitud entre las entradas 2018 y 2019 no se considera evidencia de alias. Cualquier dependencia o identidad deberá demostrarse con activos y hashes.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
