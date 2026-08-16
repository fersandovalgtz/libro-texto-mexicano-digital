#!/usr/bin/env python3
"""Build reconciled processing topology and canonical page manifest for LTMD-U1 W6."""
from __future__ import annotations
import csv
from collections import Counter,defaultdict
from pathlib import Path

SCOPE=Path('data/catalog/ltmd_u1_w6_scope.csv')
MAN=Path('data/catalog/ltmd_u1_w6_geography_atlas_asset_manifest.csv')
READINESS=Path('data/catalog/ltmd_u1_w6_geography_atlas_source_readiness.csv')
ROUTES=Path('data/catalog/ltmd_u1_w6_geography_atlas_2018_2019_route_relationships.csv')
RECOVERY=Path('data/catalog/ltmd_u1_w6_h2008p4ge273_gap_recovery.csv')
OUT=Path('data/catalog/ltmd_u1_w6_geography_atlas_processing_inventory.csv')
PAGES=Path('data/catalog/ltmd_u1_w6_geography_atlas_canonical_page_manifest.csv')
REPORT=Path('data/catalog/ltmd_u1_w6_geography_atlas_processing_topology.md')
VERSION='LTMD_U1_W6_GEOGRAPHY_ATLAS_TOPOLOGY_0.1'
EXPECTED_IDENTITIES=42;EXPECTED_CANONICAL=37;EXPECTED_ALIASES=5;EXPECTED_RECOVERED=2;EXPECTED_CANONICAL_PAGES=5258

def main():
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8',newline='')));meta={r['viewer_key']:r for r in scope}
    man=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')));readiness={r['viewer_key']:r for r in csv.DictReader(READINESS.open(encoding='utf-8',newline=''))}
    routes=list(csv.DictReader(ROUTES.open(encoding='utf-8',newline='')));recovery=list(csv.DictReader(RECOVERY.open(encoding='utf-8',newline='')))
    if len(meta)!=EXPECTED_IDENTITIES or len(readiness)!=EXPECTED_IDENTITIES:raise SystemExit('W6 topology identity cardinality mismatch')
    if len(routes)!=EXPECTED_ALIASES or any(r['complete_route_resolution']!='1' or not r['canonical_processing_viewer_key'] for r in routes):raise SystemExit('W6 route aliases not fully proven')
    alias={r['viewer_key_2018']:r['canonical_processing_viewer_key'] for r in routes}
    if len(alias)!=EXPECTED_ALIASES or any(meta[k]['catalog_generation']!='2018' or meta[v]['catalog_generation']!='2019' for k,v in alias.items()):raise SystemExit('W6 route generation contract failed')
    if len(recovery)!=EXPECTED_RECOVERED or {int(r['viewer_page']) for r in recovery}!={70,117}:raise SystemExit('W6 2008 recovery cardinality/page contract failed')
    if any(r['viewer_key']!='H2008P4GE273' or r['candidate_live_verified']!='1' or r['recovery_status']!='cryptographically_recovered_same_position_reference' for r in recovery):raise SystemExit('W6 2008 recovery not fully proven')

    by=defaultdict(list)
    for r in man:by[r['viewer_key']].append(r)
    inventory=[];canonical=set(meta)-set(alias)
    if len(canonical)!=EXPECTED_CANONICAL:raise SystemExit(f'expected {EXPECTED_CANONICAL} W6 canonical viewers, got {len(canonical)}')
    rec_by_page={int(r['viewer_page']):r for r in recovery}
    for key in sorted(meta,key=lambda k:(int(meta[k]['catalog_generation']),int(meta[k]['grade_code']),k)):
        rr=by[key];statuses=Counter(r['asset_status'] for r in rr);is_can=key in canonical
        if key in alias:
            mode='route_alias_to_2019';canon=alias[key];direct_pages=0;recovered_pages=0;persistent=0;technical=1
        else:
            canon=key;direct_pages=statuses['source_jpeg'];recovered_pages=EXPECTED_RECOVERED if key=='H2008P4GE273' else 0;persistent=statuses['internal_unserved']-recovered_pages
            mode='direct_canonical_reconciled_gap' if recovered_pages else 'direct_canonical';technical=int(persistent==0 and direct_pages+recovered_pages>0)
        inventory.append({'topology_version':VERSION,'viewer_key':key,'catalog_generation':meta[key]['catalog_generation'],'grade_code':meta[key]['grade_code'],'title_core':meta[key]['title_core'],'technical_identity_covered':technical,'is_canonical_processing_object':int(is_can),'canonical_processing_viewer_key':canon,'processing_mode':mode,'declared_positions':len(rr),'direct_source_pages_for_processing':direct_pages,'recovered_source_pages_for_processing':recovered_pages,'terminal_synthetic_candidates':statuses['terminal_synthetic_candidate'],'original_internal_unserved':statuses['internal_unserved'],'persistent_source_gaps':persistent})
    if sum(int(r['technical_identity_covered']) for r in inventory)!=EXPECTED_IDENTITIES:raise SystemExit('W6 topology does not cover all 42 identities')
    if sum(int(r['is_canonical_processing_object']) for r in inventory)!=EXPECTED_CANONICAL:raise SystemExit('W6 canonical count mismatch')
    if sum(r['processing_mode']=='route_alias_to_2019' for r in inventory)!=EXPECTED_ALIASES:raise SystemExit('W6 alias count mismatch')
    if any(int(r['persistent_source_gaps']) for r in inventory):raise SystemExit('W6 topology still has persistent source gaps')

    page_rows=[]
    for key in sorted(canonical,key=lambda k:(int(meta[k]['catalog_generation']),int(meta[k]['grade_code']),k)):
        for r in by[key]:
            p=int(r['viewer_page'])
            if r['asset_status']=='source_jpeg':
                page_rows.append({'topology_version':VERSION,'page_id':f'{key}:p{p:04d}','viewer_key':key,'catalog_generation':meta[key]['catalog_generation'],'grade_code':meta[key]['grade_code'],'title_core':meta[key]['title_core'],'viewer_page':p,'source_kind':'direct_source_jpeg','source_asset_url':r['source_asset_url'],'sha256':r['sha256'],'byte_size':r['byte_size'],'original_source_asset_url':r['source_asset_url'],'original_asset_status':r['asset_status'],'recovery_reference_viewer_key':''})
            elif key=='H2008P4GE273' and p in rec_by_page:
                rec=rec_by_page[p]
                page_rows.append({'topology_version':VERSION,'page_id':f'{key}:p{p:04d}','viewer_key':key,'catalog_generation':meta[key]['catalog_generation'],'grade_code':meta[key]['grade_code'],'title_core':meta[key]['title_core'],'viewer_page':p,'source_kind':'cryptographically_recovered_same_position_reference','source_asset_url':rec['effective_source_asset_url'],'sha256':rec['effective_sha256'],'byte_size':rec['effective_byte_size'],'original_source_asset_url':rec['original_source_asset_url'],'original_asset_status':rec['original_asset_status'],'recovery_reference_viewer_key':rec['recovery_reference_viewer_key']})
    ids=[r['page_id'] for r in page_rows]
    if len(ids)!=len(set(ids)):raise SystemExit('duplicate W6 canonical page IDs')
    expected_pages=sum(int(r['direct_source_pages_for_processing'])+int(r['recovered_source_pages_for_processing']) for r in inventory if int(r['is_canonical_processing_object'])==1)
    if len(page_rows)!=expected_pages:raise SystemExit(f'W6 canonical page manifest mismatch {len(page_rows)} vs {expected_pages}')
    if len(page_rows)!=EXPECTED_CANONICAL_PAGES:raise SystemExit(f'W6 canonical source page invariant changed: {len(page_rows)} != {EXPECTED_CANONICAL_PAGES}')
    if sum(r['source_kind']=='cryptographically_recovered_same_position_reference' for r in page_rows)!=EXPECTED_RECOVERED:raise SystemExit('W6 recovered page manifest count mismatch')

    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(inventory[0]));w.writeheader();w.writerows(inventory)
    page_rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key'],int(r['viewer_page'])))
    with PAGES.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(page_rows[0]));w.writeheader();w.writerows(page_rows)
    gens=defaultdict(Counter)
    for r in inventory:
        g=gens[r['catalog_generation']];g['identities']+=1;g['canonical']+=int(r['is_canonical_processing_object']);g['aliases']+=r['processing_mode']=='route_alias_to_2019';g['pages']+=(int(r['direct_source_pages_for_processing'])+int(r['recovered_source_pages_for_processing'])) if int(r['is_canonical_processing_object'])==1 else 0
    terminals=sum(int(r['terminal_synthetic_candidates']) for r in inventory if int(r['is_canonical_processing_object'])==1)
    lines=['# LTMD-U1 W6 — topología de procesamiento Geografía/Atlas','',f'Versión: `{VERSION}`.','',f'- Identidades técnicas cubiertas: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}**.',f'- Objetos canónicos de procesamiento: **{EXPECTED_CANONICAL}**.',f'- Aliases operacionales de ruta 2018→2019: **{EXPECTED_ALIASES}**.',f'- Páginas recuperadas criptográficamente en `H2008P4GE273`: **{EXPECTED_RECOVERED}**.',f'- Huecos de fuente persistentes después de reconciliación: **0**.',f'- Páginas fuente canónicas autorizadas para OCR: **{len(page_rows):,}**.',f'- Terminales sintéticos de objetos canónicos excluidos de OCR: **{terminals}**.',f'- Renumeración de páginas: **0**.','','## Por generación','', '| generación | identidades | canónicos | aliases | páginas canónicas |','|---:|---:|---:|---:|---:|']
    for g in sorted(gens,key=int):lines.append(f"| {g} | {gens[g]['identities']} | {gens[g]['canonical']} | {gens[g]['aliases']} | {gens[g]['pages']:,} |")
    lines+=['','## Contrato downstream','OCR W6 sólo puede consumir `ltmd_u1_w6_geography_atlas_canonical_page_manifest.csv` y debe revalidar en vivo SHA-256 + tamaño antes de reconocer texto. Los cinco visores 2018 no duplican OCR; heredan cobertura técnica de sus rutas 2019 demostradas. Las dos páginas 2008 recuperadas mantienen la URL original 404 y la referencia 1993 como provenance.','','La topología es infraestructura de fuente. No fusiona identidades de catálogo ni autoriza equivalencias bibliográficas, históricas, curriculares o semánticas. `WAITING_HUMAN_REFERENCE` permanece vigente.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
