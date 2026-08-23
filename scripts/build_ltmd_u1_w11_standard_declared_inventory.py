#!/usr/bin/env python3
"""Build W11 declared inventory only for the architecture-standard technical route."""
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path
from urllib.request import Request,urlopen

ROUTING=Path('data/catalog/ltmd_u1_w11_technical_routing.csv')
OUT=Path('data/catalog/ltmd_u1_w11_standard_declared_inventory.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w11_standard_declared_inventory_summary.csv')
REPORT=Path('docs/LTMD_U1_W11_STANDARD_DECLARED_INVENTORY.md')
ROUTING_VERSION='LTMD_U1_W11_TECHNICAL_ROUTING_0.1'
VERSION='LTMD_U1_W11_STANDARD_DECLARED_INVENTORY_0.1'
EXPECTED_TOTAL=111
EXPECTED_STANDARD=100
UA='LibroTextoMexicanoDigital/U1-W11 standard declared inventory 0.1'

def main()->None:
    routing=list(csv.DictReader(ROUTING.open(encoding='utf-8',newline='')))
    if len(routing)!=EXPECTED_TOTAL or len({r['viewer_key'] for r in routing})!=EXPECTED_TOTAL:raise SystemExit('W11 declared inventory routing cardinality drift')
    if {r['routing_version'] for r in routing}!={ROUTING_VERSION}:raise SystemExit('W11 declared inventory routing version drift')
    standard=[r for r in routing if r['technical_route']=='standard_dynamic_claves'];nonstandard=[r for r in routing if r['technical_route']=='nonstandard_html_diagnostics']
    if len(standard)!=EXPECTED_STANDARD or len(nonstandard)!=(EXPECTED_TOTAL-EXPECTED_STANDARD):raise SystemExit(f'W11 route count drift standard={len(standard)} nonstandard={len(nonstandard)}')
    with urlopen(Request('https://historico.conaliteg.gob.mx/claves.json',headers={'User-Agent':UA}),timeout=60) as r:cfg=json.loads(r.read().decode('utf-8-sig'))
    rows=[]
    for s in standard:
        d=cfg.get(s['viewer_key'])
        if not isinstance(d,dict):raise SystemExit(f'missing claves config {s["viewer_key"]}')
        try:n=int(d.get('ag_pages'))
        except Exception:raise SystemExit(f'invalid ag_pages {s["viewer_key"]}: {d.get("ag_pages")!r}')
        ag=str(d.get('ag_clave','')).strip()
        if n<=0 or not ag:raise SystemExit(f'invalid declared config {s["viewer_key"]}: ag_pages={n}, ag_clave={ag!r}')
        rows.append({'inventory_version':VERSION,'routing_version':ROUTING_VERSION,'viewer_key':s['viewer_key'],'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'ag_clave':ag,'declared_positions':n,'technical_route':s['technical_route'],'source_url':s['source_url']})
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    if len(rows)!=EXPECTED_STANDARD or len({r['viewer_key'] for r in rows})!=EXPECTED_STANDARD:raise SystemExit('W11 standard inventory output cardinality drift')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    bygen=Counter();posgen=Counter()
    for r in rows:bygen[r['catalog_generation']]+=1;posgen[r['catalog_generation']]+=int(r['declared_positions'])
    total=sum(int(r['declared_positions']) for r in rows);sr=[]
    for g in sorted(bygen,key=int):sr.append({'inventory_version':VERSION,'catalog_generation':g,'viewer_count':bygen[g],'declared_positions':posgen[g]})
    sr.append({'inventory_version':VERSION,'catalog_generation':'ALL','viewer_count':EXPECTED_STANDARD,'declared_positions':total})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(sr[0]));w.writeheader();w.writerows(sr)
    lines=['# LTMD-U1 W11 — inventario declarado de la ruta estándar','',f'Versión: `{VERSION}`.','',f'- Universo W11 preservado: **{EXPECTED_TOTAL}/{EXPECTED_TOTAL}**.','- Ruta auditada aquí: `standard_dynamic_claves`. ',f'- Visores estándar con configuración oficial: **{EXPECTED_STANDARD}/{EXPECTED_STANDARD}**.',f'- Visores no estándar excluidos de este inventario: **{len(nonstandard)}**.',f'- Posiciones declaradas por `claves.json` en la ruta estándar: **{total:,}**.','','## Por generación de catálogo','','| generación | visores | posiciones declaradas |','|---:|---:|---:|']
    for r in sr[:-1]:lines.append(f"| {r['catalog_generation']} | {r['viewer_count']} | {int(r['declared_positions']):,} |")
    lines+=['','## Límite de la compuerta','Este inventario no acredita que las posiciones declaradas estén servidas. Los 11 visores no estándar permanecen fuera de esta ruta y requieren diagnóstico HTML independiente. No se abre OCR hasta que cada ruta haya producido una decisión de fuente explícita y reproducible.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
