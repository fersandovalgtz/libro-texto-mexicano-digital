#!/usr/bin/env python3
"""Build a unified technical inventory for the 37 strict Ciencias Naturales viewers.

Uses the normalized family inventory plus public `claves.json` to obtain declared
viewer positions. No page images are downloaded. Existing CN5/CN4/CN6 processed
objects are mapped to their stable LTMD book IDs; unaudited objects receive the same
stable convention.
"""
from __future__ import annotations
import csv,json
from pathlib import Path
from urllib.request import Request,urlopen

FAMILY=Path('data/catalog/ciencias_naturales_family_inventory.csv')
OUT=Path('data/catalog/ciencias_naturales_technical_inventory.csv')
REPORT=Path('data/catalog/ciencias_naturales_technical_inventory.md')
VERSION='CN_TECH_INVENTORY_0.1'
UA='LibroTextoMexicanoDigital/0.1 full CN technical inventory'
BASE='https://historico.conaliteg.gob.mx/'

# Stable special ID retained because the same catalog-generation/grade cell also
# contains the historically related DH replacement object outside the strict title family.
SPECIAL={'H1993P6CI210':'LTMD-CN6-G1993-CN'}

def book_id(r):return SPECIAL.get(r['viewer_key'],f"LTMD-CN{r['grade_code']}-G{r['catalog_generation']}")

def main():
    fam=list(csv.DictReader(FAMILY.open(encoding='utf-8')))
    if len(fam)!=37:raise SystemExit(f'expected 37 strict CN viewers, found {len(fam)}')
    with urlopen(Request(BASE+'claves.json',headers={'User-Agent':UA}),timeout=45) as r:claves=json.loads(r.read().decode('utf-8-sig'))
    rows=[]
    for r in fam:
        key=r['viewer_key'];cfg=claves.get(key)
        if not isinstance(cfg,dict) or 'ag_pages' not in cfg:raise SystemExit(f'missing ag_pages for {key}')
        n=int(cfg['ag_pages']);covered=r['corpus_status']=='pilot_or_expansion_audited'
        rows.append({'inventory_version':VERSION,'book_id':book_id(r),'viewer_key':key,'catalog_generation':r['catalog_generation'],'grade':r['grade_code'],'title_core':r['title_core'],'viewer_positions_declared':n,'expected_source_assets_if_single_terminal':n-1,'source_url':BASE+key+'.htm','current_corpus_status':'audited_existing' if covered else 'catalog_only','next_required_stage':'reuse_existing_manifest' if covered else 'source_asset_hash_audit'})
    if len({r['book_id'] for r in rows})!=len(rows):raise SystemExit('book_id collision')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    total=sum(int(r['viewer_positions_declared']) for r in rows);covered=[r for r in rows if r['current_corpus_status']=='audited_existing'];pending=[r for r in rows if r['current_corpus_status']=='catalog_only'];pending_positions=sum(int(r['viewer_positions_declared']) for r in pending)
    lines=['# Inventario técnico unificado — familia estricta Ciencias Naturales','',f'Versión: `{VERSION}`.','',f'- Visores: **{len(rows)}**.\n- Posiciones declaradas acumuladas: **{total:,}**.\n- Objetos ya auditados en piloto/expansión: **{len(covered)}**.\n- Objetos pendientes de auditoría de activos: **{len(pending)}**.\n- Posiciones declaradas en los 25 pendientes: **{pending_positions:,}**.','', '## Pendientes por generación']
    for gen in sorted({r['catalog_generation'] for r in pending},key=int):
        g=[r for r in pending if r['catalog_generation']==gen]
        lines.append(f"- {gen}: {len(g)} objetos; {sum(int(r['viewer_positions_declared']) for r in g):,} posiciones declaradas; grados {', '.join(r['grade'] for r in g)}.")
    lines+=['','## Regla','`expected_source_assets_if_single_terminal` es sólo una expectativa derivada del patrón observado en los 13 objetos ya auditados (piloto CN5 + CN4/CN6 incluyendo DH). Cada objeto pendiente debe demostrar su propio patrón mediante auditoría/hash antes de adquirir `corpus_ready`.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
