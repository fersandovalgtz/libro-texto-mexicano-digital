#!/usr/bin/env python3
"""Static preflight for LTMD-U1 W10 FRAGSEG.

This gate validates the exact structural/source topology that FRAGSEG is allowed
to consume. It does not perform OCR or segmentation and therefore cannot replace
FRAGSEG execution; it isolates corpus/topology defects before expensive work.
"""
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path

PROC=Path('data/catalog/ltmd_u1_w10_processing_inventory.csv')
MAN=Path('data/catalog/ltmd_u1_w10_canonical_page_manifest.csv')
STRUCT=Path('data/catalog/ltmd_u1_w10_integrados_page_structure.csv')
OUT=Path('data/control/ltmd_u1_w10_fragseg_preflight.json')
VERSION='LTMD_U1_W10_FRAGSEG_PREFLIGHT_0.1'
EXPECTED_IDENTITIES=69
EXPECTED_CANONICAL=68
EXPECTED_SOURCE_PAGES=11937
EXPECTED_ELIGIBLE=10366
ELIGIBLE={'textual','mixed_text_image'}
ALLOWED_PSM={'','3','6','11'}

def rows(path):
    return list(csv.DictReader(path.open(encoding='utf-8',newline='')))

def main():
    proc=rows(PROC);man=rows(MAN);struct=rows(STRUCT)
    failures=[]
    if len(proc)!=EXPECTED_IDENTITIES or len({r['viewer_key'] for r in proc})!=EXPECTED_IDENTITIES:
        failures.append(f'processing_inventory={len(proc)} identities={len({r["viewer_key"] for r in proc})}')
    canonical={r['viewer_key'] for r in proc if r['source_admitted']=='1' and r['is_canonical_processing_object']=='1'}
    retained={r['viewer_key'] for r in proc if r['source_admitted']!='1'}
    if len(canonical)!=EXPECTED_CANONICAL:failures.append(f'canonical={len(canonical)} expected={EXPECTED_CANONICAL}')
    if len(retained)!=1:failures.append(f'retained={len(retained)} expected=1')
    if len(man)!=EXPECTED_SOURCE_PAGES:failures.append(f'manifest_pages={len(man)} expected={EXPECTED_SOURCE_PAGES}')
    man_ids=[r['page_id'] for r in man]
    if len(man_ids)!=len(set(man_ids)):failures.append('duplicate canonical page_id')
    if {r['viewer_key'] for r in man}!=canonical:failures.append('canonical manifest viewer set mismatch')
    if any(r['asset_status']!='source_jpeg' or len(r['sha256'])!=64 or int(r['byte_size'])<=0 for r in man):
        failures.append('invalid source provenance row in canonical manifest')
    if len(struct)!=EXPECTED_SOURCE_PAGES:failures.append(f'pagestruct_pages={len(struct)} expected={EXPECTED_SOURCE_PAGES}')
    struct_ids=[r['page_id'] for r in struct]
    if len(struct_ids)!=len(set(struct_ids)):failures.append('duplicate PAGESTRUCT page_id')
    if set(struct_ids)!=set(man_ids):failures.append('PAGESTRUCT/source manifest page universe mismatch')
    if {r['viewer_key'] for r in struct}!=canonical:failures.append('PAGESTRUCT viewer set mismatch')
    if any(r.get('selected_psm','') not in ALLOWED_PSM for r in struct):failures.append('unexpected selected_psm')
    eligible=[r for r in struct if r['primary_structure'] in ELIGIBLE]
    if len(eligible)!=EXPECTED_ELIGIBLE:failures.append(f'eligible_pages={len(eligible)} expected={EXPECTED_ELIGIBLE}')
    eligible_by=Counter(r['viewer_key'] for r in eligible)
    no_eligible=sorted(canonical-set(eligible_by))
    if no_eligible:failures.append('canonical viewers without eligible pages: '+','.join(no_eligible))
    man_map={(r['viewer_key'],r['viewer_page']):r for r in man}
    missing=[r['page_id'] for r in eligible if (r['viewer_key'],r['viewer_page']) not in man_map]
    if missing:failures.append(f'eligible pages without source mapping={len(missing)}')
    result={
        'preflight_version':VERSION,
        'status':'PASS' if not failures else 'FAIL',
        'historical_identities':len(proc),
        'canonical_objects':len(canonical),
        'retained_identities':len(retained),
        'canonical_source_pages':len(man),
        'pagestruct_pages':len(struct),
        'fragseg_eligible_pages':len(eligible),
        'canonical_viewers_with_eligible_pages':len(eligible_by),
        'failures':failures,
        'epistemic_limit':'Static topology/source validation only; not OCR, FRAGSEG or semantic validation.',
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:raise SystemExit('W10 FRAGSEG preflight failed')

if __name__=='__main__':main()
