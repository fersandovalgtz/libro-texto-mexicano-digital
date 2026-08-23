#!/usr/bin/env python3
"""Build the declared W10 asset inventory from official claves.json after G1 architecture audit."""
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen

SCOPE=Path('data/catalog/ltmd_u1_w10_scope.csv')
ARCH=Path('data/catalog/ltmd_u1_w10_viewer_architecture.csv')
OUT=Path('data/catalog/ltmd_u1_w10_declared_inventory.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w10_declared_inventory_summary.csv')
REPORT=Path('docs/LTMD_U1_W10_DECLARED_INVENTORY.md')
VERSION='LTMD_U1_W10_DECLARED_INVENTORY_0.1'
EXPECTED=69
UA='LibroTextoMexicanoDigital/U1-W10 integrated-multiarea declared inventory 0.1'

def main():
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')))
    arch={r['viewer_key']:r for r in csv.DictReader(ARCH.open(encoding='utf-8',newline=''))}
    if len(scope)!=EXPECTED or len({r['viewer_key'] for r in scope})!=EXPECTED or len(arch)!=EXPECTED:
        raise SystemExit(f'W10 scope/architecture mismatch {len(scope)}/{len(arch)}')
    if any(arch[s['viewer_key']]['standard_dynamic_architecture']!='1' for s in scope):
        raise SystemExit('W10 declared inventory requires resolved G1 architecture for all 69 viewers')
    with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=60) as r:
        cfg=json.loads(r.read().decode('utf-8-sig'))
    rows=[]
    for s in scope:
        d=cfg.get(s['viewer_key'])
        if not isinstance(d,dict):raise SystemExit(f'missing claves config {s["viewer_key"]}')
        try:n=int(d.get('ag_pages'))
        except Exception:raise SystemExit(f'invalid ag_pages {s["viewer_key"]}: {d.get("ag_pages")!r}')
        if n<=0:raise SystemExit(f'nonpositive ag_pages {s["viewer_key"]}: {n}')
        ag=str(d.get('ag_clave','')).strip()
        if not ag:raise SystemExit(f'missing ag_clave {s["viewer_key"]}')
        rows.append({'inventory_version':VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'ag_clave':ag,'declared_positions':n,'standard_dynamic_architecture':'1','source_url':s['source_url']})
    rows.sort(key=lambda x:(int(x['catalog_generation']),int(x['grade_code']),x['viewer_key']))
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    bygen=Counter();posgen=Counter()
    for r in rows:
        bygen[r['catalog_generation']]+=1;posgen[r['catalog_generation']]+=int(r['declared_positions'])
    total=sum(int(r['declared_positions']) for r in rows)
    sr=[]
    for g in sorted(bygen,key=int):sr.append({'inventory_version':VERSION,'catalog_generation':g,'viewer_count':bygen[g],'declared_positions':posgen[g]})
    sr.append({'inventory_version':VERSION,'catalog_generation':'ALL','viewer_count':EXPECTED,'declared_positions':total})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(sr[0]));w.writeheader();w.writerows(sr)
    lines=['# LTMD-U1 W10 — inventario declarado Integrados/Multiarea','',f'Versión: `{VERSION}`.','',f'- Visores con configuración oficial: **{EXPECTED}/{EXPECTED}**.',f'- Posiciones declaradas por `claves.json`: **{total:,}**.','- Arquitectura dinámica estándar: **69/69**.','','## Por generación de catálogo','', '| generación | visores | posiciones declaradas |','|---:|---:|---:|']
    for r in sr[:-1]:lines.append(f"| {r['catalog_generation']} | {r['viewer_count']} | {int(r['declared_positions']):,} |")
    lines+=['','## Límite de la compuerta','`claves.json` se trata únicamente como inventario declarado. La existencia de `ag_clave` y `ag_pages` no demuestra que cada posición esté servida, no autoriza completar huecos por analogía y no abre OCR. La siguiente fase debe auditar activos oficiales posición por posición, conservar estado HTTP, tamaño y SHA-256, y separar explícitamente fuentes admitidas de retenciones.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':
    main()
