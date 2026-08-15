#!/usr/bin/env python3
"""Create a blinded supplemental sample for validating short residual fragments.

Selection uses only frozen FRAGSEG metadata and deterministic hashes. This sample
is separate from the 480-case SEMB 0.3 semantic reference and exists to decide
whether formerly `heading_candidate` units >=4 tokens should be semantically eligible.
"""
from __future__ import annotations
import csv,hashlib
from pathlib import Path

MANIFEST=Path('data/derived/fragment_manifest.csv')
OUT=Path('data/validation/short_residual_validation_sample.csv')
TEMPLATE=Path('data/validation/short_residual_annotation_template.csv')
VERSION='SHORT_RESIDUAL_SAMPLE_0.1'
GENS=('1972','1988','1993','2014')

def h(fid,salt):return hashlib.sha256(f'{VERSION}|{salt}|{fid}'.encode()).hexdigest()
def opaque(fid):return 'SR03-'+hashlib.sha256(f'{VERSION}|opaque|{fid}'.encode()).hexdigest()[:16].upper()

def main():
    rows=list(csv.DictReader(MANIFEST.open(encoding='utf-8')))
    sample=[]
    for g in GENS:
        pool=[r for r in rows if r['catalog_generation']==g and r['candidate_type']=='heading_candidate' and int(r['token_count'])>=4]
        chosen=sorted(pool,key=lambda r:h(r['fragment_id'],f'{g}:sample'))[:40]
        assert len(chosen)==40
        ranked=sorted(chosen,key=lambda r:h(r['fragment_id'],f'{g}:role'))
        roles={r['fragment_id']:('development' if i<25 else 'locked_validation') for i,r in enumerate(ranked)}
        for r in chosen:
            sample.append({'sample_version':VERSION,'sample_id':opaque(r['fragment_id']),'fragment_id':r['fragment_id'],'page_id':r['page_id'],
                           'catalog_generation':g,'token_count':r['token_count'],'char_count':r['char_count'],'text_sha256':r['text_sha256'],
                           'analysis_role':roles[r['fragment_id']]})
    assert len(sample)==160 and len({r['sample_id'] for r in sample})==160 and len({r['fragment_id'] for r in sample})==160
    assert sum(r['analysis_role']=='development' for r in sample)==100
    assert sum(r['analysis_role']=='locked_validation' for r in sample)==60
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(sample[0]));w.writeheader();w.writerows(sample)
    fields=['sample_id','annotator_id','annotation_round','is_typographic_heading','is_semantic_unit','actionable','functional_class','confidence','note']
    order=sorted(sample,key=lambda r:h(r['fragment_id'],'annotator-order'))
    with TEMPLATE.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in order:w.writerow({'sample_id':r['sample_id'],'annotator_id':'','annotation_round':'','is_typographic_heading':'','is_semantic_unit':'','actionable':'','functional_class':'','confidence':'','note':''})
    print('short_residual_sample',len(sample),'development',100,'locked_validation',60)

if __name__=='__main__':main()
