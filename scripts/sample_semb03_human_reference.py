#!/usr/bin/env python3
"""Create the preregistered SEMB 0.3 human-reference sample from FRAGSEG metadata only.

Scientific invariant: this script must never read semantic classifier outputs or
historical comparison files. Selection is deterministic from manifest metadata
and fragment_id hashes. Annotator-facing IDs are opaque: they disclose neither
generation nor development/validation role.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

MANIFEST=Path('data/derived/fragment_manifest.csv')
OUT=Path('data/validation/semb03_human_reference_sample.csv')
ANNOT=Path('data/validation/semb03_human_reference_annotation_template.csv')
VERSION='SEMB03_SAMPLE_0.2'
GENERATIONS=('1972','1988','1993','2014')
RARE={'activity_candidate','experiment_candidate','project_candidate','assessment_candidate'}


def h(fid,salt):
    return hashlib.sha256(f'{salt}|{fid}'.encode()).hexdigest()


def eligible(r):
    return r['candidate_type']!='heading_candidate' and int(r['token_count'])>=4


def pick(rows,n,salt,used):
    pool=[r for r in rows if r['fragment_id'] not in used]
    pool=sorted(pool,key=lambda r:h(r['fragment_id'],salt))
    if len(pool)<n:
        raise RuntimeError(f'Insufficient pool: requested {n}, have {len(pool)}')
    out=pool[:n]
    used.update(r['fragment_id'] for r in out)
    return out


def opaque_sample_id(fragment_id):
    # 16 hex chars are ample for 480 deterministic IDs and reveal no generation.
    return 'S03-'+h(fragment_id,VERSION+':opaque')[:16].upper()


def main():
    rows=list(csv.DictReader(MANIFEST.open(encoding='utf-8')))
    assert len(rows)==9594
    sample=[]
    for gen in GENERATIONS:
        g=[r for r in rows if r['catalog_generation']==gen and eligible(r)]
        used=set(); chosen=[]
        chosen += pick([r for r in g if r['candidate_type']=='expository_candidate'],25,f'{VERSION}:{gen}:expository',used)
        chosen += pick([r for r in g if r['candidate_type']=='instruction_candidate'],25,f'{VERSION}:{gen}:instruction',used)
        chosen += pick([r for r in g if r['candidate_type']=='question_candidate'],25,f'{VERSION}:{gen}:question',used)
        chosen += pick([r for r in g if r['candidate_type'] in RARE],20,f'{VERSION}:{gen}:rare',used)
        chosen += pick(g,25,f'{VERSION}:{gen}:remainder',used)
        assert len(chosen)==120 and len(used)==120
        ranked=sorted(chosen,key=lambda r:h(r['fragment_id'],f'{VERSION}:{gen}:role'))
        roles={r['fragment_id']:('development' if i<80 else 'locked_validation') for i,r in enumerate(ranked)}
        for r in chosen:
            sample.append({
                'sample_version':VERSION,
                'sample_id':opaque_sample_id(r['fragment_id']),
                'fragment_id':r['fragment_id'],'page_id':r['page_id'],'catalog_generation':gen,
                'candidate_type':r['candidate_type'],'token_count':r['token_count'],'char_count':r['char_count'],
                'text_sha256':r['text_sha256'],'analysis_role':roles[r['fragment_id']],
            })
    assert len(sample)==480 and len({r['fragment_id'] for r in sample})==480
    assert len({r['sample_id'] for r in sample})==480
    for gen in GENERATIONS:
        rr=[r for r in sample if r['catalog_generation']==gen]
        assert sum(r['analysis_role']=='development' for r in rr)==80
        assert sum(r['analysis_role']=='locked_validation' for r in rr)==40

    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=list(sample[0].keys())
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(sample)

    # Annotator-facing template deliberately omits generation, page, candidate type,
    # token/character counts and development/validation role.
    afields=['sample_id','annotator_id','annotation_round','actionable','action_labels',
             'position_labels','annotation_confidence','ambiguity_note']
    with ANNOT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=afields);w.writeheader()
        for r in sorted(sample,key=lambda x:h(x['sample_id'],VERSION+':annotator-order')):
            w.writerow({'sample_id':r['sample_id'],'annotator_id':'','annotation_round':'',
                        'actionable':'','action_labels':'','position_labels':'',
                        'annotation_confidence':'','ambiguity_note':''})
    print('sample',len(sample),'development',sum(r['analysis_role']=='development' for r in sample),
          'locked_validation',sum(r['analysis_role']=='locked_validation' for r in sample))

if __name__=='__main__': main()
