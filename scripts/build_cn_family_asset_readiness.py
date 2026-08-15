#!/usr/bin/env python3
"""Build one conservative asset-readiness table for all 37 strict CN viewers."""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path

INV=Path('data/catalog/ciencias_naturales_technical_inventory.csv')
PEND=Path('data/catalog/ciencias_naturales_pending_page_manifest_summary.csv')
ALIAS=Path('data/catalog/cn2018_2019_catalog_alias_relationships.csv')
AUD08=Path('data/catalog/cn2008_internal_unserved_audit.csv')
OUT=Path('data/catalog/ciencias_naturales_family_asset_readiness.csv')
REPORT=Path('data/catalog/ciencias_naturales_family_asset_readiness.md')
VERSION='CN_FAMILY_ASSET_READINESS_0.1'

def main():
    inv=list(csv.DictReader(INV.open(encoding='utf-8')))
    if len(inv)!=37:raise SystemExit(f'expected 37 strict CN viewers, got {len(inv)}')
    pend={r['book_id']:r for r in csv.DictReader(PEND.open(encoding='utf-8'))}
    aliases={r['book_a']:r for r in csv.DictReader(ALIAS.open(encoding='utf-8'))}
    aud08=list(csv.DictReader(AUD08.open(encoding='utf-8')))
    aud08_by_book=defaultdict(list)
    for r in aud08:aud08_by_book[r['book_id']].append(r)
    rows=[]
    for b in inv:
        bid=b['book_id'];status='not_resolved';strategy='';alias_to='';resolved='';internal='';terminal='';notes=''
        if b['current_corpus_status']=='audited_existing':
            status='full_direct';strategy='existing_pilot_or_cn46_manifest';resolved=b['expected_source_assets_if_single_terminal'];internal='0';terminal='1';notes='Existing audited corpus layer; source asset manifest already established.'
        elif bid in aliases:
            a=aliases[bid]
            if a['relationship_type']=='catalog_entry_aliases_same_asset_bytes' and float(a['identity_rate'])==1.0:
                status='full_alias_same_bytes';strategy='paired_2019_asset_alias_sha256_verified';alias_to=a['book_b'];resolved=a['compared_source_assets'];internal='0';terminal='1';notes='Distinct catalog entry; all served content bytes are identical to paired 2019 assets.'
            else:
                status='not_resolved';strategy='alias_identity_not_proven';notes='Routing alias observed but byte identity incomplete.'
        elif bid in pend:
            p=pend[bid];resolved=p['source_jpegs'];internal=p['internal_missing'];terminal=p['terminal_synthetic']
            if int(p['corpus_ready_asset_layer']):
                status='full_direct';strategy='direct_sha256_manifest';notes='All source assets directly verified; any final synthetic position explicitly recorded.'
            elif bid in aud08_by_book:
                rr=aud08_by_book[bid]
                if all(r['target_state']=='internal_unserved_position_observed' and int(r['neighbours_sha_verified'])==1 for r in rr) and len(rr)==int(p['internal_missing']):
                    status='partial_internal_unserved';strategy='direct_manifest_plus_focused_gap_audit';notes=f"{len(rr)} internal public asset position(s) repeatedly unserved while immediate neighbours reproduce persisted SHA-256."
                else:
                    status='not_resolved';strategy='focused_gap_audit_incomplete';notes='Internal gaps remain without complete focused verification.'
            else:
                status='not_resolved';strategy='pending_anomaly_resolution';notes='Manifest anomaly has not been fully resolved.'
        rows.append({'readiness_version':VERSION,'book_id':bid,'viewer_key':b['viewer_key'],'catalog_generation':b['catalog_generation'],'grade':b['grade'],'viewer_positions_declared':b['viewer_positions_declared'],'asset_readiness':status,'asset_strategy':strategy,'alias_to_book_id':alias_to,'resolved_source_assets':resolved,'terminal_synthetic':terminal,'internal_unserved_positions':internal,'source_url':b['source_url'],'notes':notes})
    counts=Counter(r['asset_readiness'] for r in rows)
    if counts['full_direct']!=31:raise SystemExit(f'expected 31 full_direct (12 existing + 19 new), got {counts}')
    if counts['full_alias_same_bytes']!=4:raise SystemExit(f'expected 4 full aliases, got {counts}')
    if counts['partial_internal_unserved']!=2:raise SystemExit(f'expected 2 partial 2008 objects, got {counts}')
    if counts['not_resolved']!=0:raise SystemExit(f'unexpected unresolved viewers: {counts}')
    if sum(int(r['internal_unserved_positions'] or 0) for r in rows)!=3:raise SystemExit('family internal-unserved total must be 3')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['book_id']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    full=counts['full_direct']+counts['full_alias_same_bytes']
    lines=['# Readiness de activos — familia estricta Ciencias Naturales','',f'Versión: `{VERSION}`.','',
           f'- Visores estrictos: **{len(rows)}**.\n- Resolución completa de activos: **{full}/{len(rows)} ({100*full/len(rows):.1f}%)**.\n- `full_direct`: **{counts["full_direct"]}**.\n- `full_alias_same_bytes`: **{counts["full_alias_same_bytes"]}**.\n- `partial_internal_unserved`: **{counts["partial_internal_unserved"]}**.\n- `not_resolved`: **{counts["not_resolved"]}**.\n- Posiciones internas no servidas persistentes: **3**.','',
           '## Interpretación',
           'Los cuatro visores 2018 se conservan como registros institucionales distintos pero no como contenido digital independiente: sus 652 activos son byte-idénticos a los pares 2019. Los dos objetos parciales de 2008 conservan tres huecos internos del servicio público; no se renumeran, rellenan ni interpretan automáticamente como páginas bibliográficas ausentes.','',
           '## Por generación']
    bygen=defaultdict(Counter)
    for r in rows:bygen[r['catalog_generation']][r['asset_readiness']]+=1
    for g in sorted(bygen,key=int):
        c=bygen[g];lines.append(f"- {g}: total={sum(c.values())}; full_direct={c['full_direct']}; full_alias_same_bytes={c['full_alias_same_bytes']}; partial_internal_unserved={c['partial_internal_unserved']}.")
    lines+=['','## Regla','`asset_readiness` describe demostración técnica de activos, no validez semántica, independencia histórica ni año bibliográfico. `semantic_ready` permanece separado y sujeto a validación humana SEMB 0.3.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
