#!/usr/bin/env python3
"""Build the preregistered LTMD historical comparison from derived A/B data.

Requires validated/audited SEMB_0.2 and A/B agreement. No source or fragment text
is read or emitted.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

BASE=Path('data/derived')
MAN=BASE/'fragment_manifest.csv'
A=BASE/'fragment_labels_A.csv'
B=BASE/'fragment_labels_B.csv'
AGR=BASE/'classifier_AB_fragment_agreement.csv'
OUT_DATA=BASE/'fragment_analysis_dataset.csv'
OUT_ACTION=BASE/'historical_action_prevalence.csv'
OUT_POSITION=BASE/'historical_position_prevalence.csv'
OUT_ACOMP=BASE/'historical_action_composition.csv'
OUT_PCOMP=BASE/'historical_position_composition.csv'
OUT_TRANS=BASE/'historical_transitions.csv'
OUT_FAMILY=BASE/'historical_family_prevalence.csv'
OUT_MD=BASE/'historical_comparison_summary.md'
VERSION='HISTCOMP_0.1'

GENERATIONS=['1972','1988','1993','2014']
ACTIONS=['observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment']
POSITIONS=['receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent']
ACTION_FAMILIES={
    'reception_retrieval':['recall','describe'],
    'observation_measurement':['observe','measure'],
    'reasoning':['explain','compare','classify','predict','infer','solve'],
    'experimental_inquiry':['experiment','investigate'],
    'production_interaction':['discuss','create'],
    'agency_action':['decide','act_on_environment'],
}
POSITION_FAMILIES={
    'reception_execution':['receiver','instruction_follower'],
    'inquiry_reasoning':['observer','experimenter','investigator','reasoner'],
    'social_agency':['collaborator','decision_maker','community_agent'],
}
TRANSITIONS=[('1972','1988'),('1988','1993'),('1993','2014'),('1972','2014')]


def load_by_id(path):
    rows=list(csv.DictReader(path.open(encoding='utf-8')))
    return rows,{r['fragment_id']:r for r in rows}


def yes(v): return int(v)==1

def rate(n,d): return 0.0 if d==0 else n/d

def strata(row):
    vals=['all_body_fragments']
    if row['candidate_type']!='heading_candidate':
        vals.append('nonheading')
        if not yes(row['uncertain_A']) and not yes(row['uncertain_B']):
            vals.append('certain_nonheading')
            if row['source_structure_class']=='textual': vals.append('textual_only_certain_nonheading')
            if row['source_structure_class']=='mixed_text_image': vals.append('mixed_text_image_certain_nonheading')
    return vals


def dir_from_delta(d):
    if d>0: return 'increase'
    if d<0: return 'decrease'
    return 'no_change'


def main():
    mrows,m=load_by_id(MAN); arows,a=load_by_id(A); brows,b=load_by_id(B); grows,g=load_by_id(AGR)
    ids=set(m)
    assert len(ids)==9594 and set(a)==ids==set(b)==set(g)
    assert all(m[i]['segmenter_version']=='FRAGSEG_0.2' for i in ids)
    assert all(a[i]['ruleset_version']=='RULEA_0.1' for i in ids)
    assert all(b[i]['semantic_rules_version']=='SEMB_0.2' for i in ids)
    assert all(g[i]['agreement_version']=='AGREE_AB_0.1' for i in ids)
    assert all(a[i]['text_sha256']==m[i]['text_sha256']==b[i]['text_sha256'] for i in ids)

    integrated=[]
    for r in mrows:
        fid=r['fragment_id']; ar=a[fid]; br=b[fid]; gr=g[fid]
        row={
            'fragment_id':fid,'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],
            'viewer_page':r['viewer_page'],'fragment_sequence':r['fragment_sequence'],'candidate_type':r['candidate_type'],
            'token_count':r['token_count'],'char_count':r['char_count'],'source_structure_class':r['source_structure_class'],
            'classification_certainty':r['classification_certainty'],'text_sha256':r['text_sha256'],
            'uncertain_A':ar['uncertain_A'],'uncertain_B':br['uncertain_B'],
            'action_jaccard':gr['action_jaccard'],'position_jaccard':gr['position_jaccard'],
            'action_exact_set':gr['action_exact_set'],'position_exact_set':gr['position_exact_set'],
            'stability_stratum':gr['stability_stratum'],'analysis_version':VERSION,
        }
        for c in ACTIONS:
            av=int(ar[f'action_{c}']); bv=int(br[f'action_{c}_B'])
            row[f'action_{c}_A']=av; row[f'action_{c}_B']=bv; row[f'action_{c}_consensus']=int(av and bv); row[f'action_{c}_disagree']=int(av!=bv)
        for c in POSITIONS:
            av=int(ar[f'position_{c}']); bv=int(br[f'position_{c}_B'])
            row[f'position_{c}_A']=av; row[f'position_{c}_B']=bv; row[f'position_{c}_consensus']=int(av and bv); row[f'position_{c}_disagree']=int(av!=bv)
        integrated.append(row)
    with OUT_DATA.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(integrated[0].keys())); w.writeheader(); w.writerows(integrated)

    strata_names=['all_body_fragments','nonheading','certain_nonheading','textual_only_certain_nonheading','mixed_text_image_certain_nonheading']
    prevalence={}
    def build_prevalence(family,cats,outpath):
        rows=[]
        prefix='action' if family=='action' else 'position'
        for gen in GENERATIONS:
            genrows=[r for r in integrated if r['catalog_generation']==gen]
            for st in strata_names:
                rs=[r for r in genrows if st in strata(r)]
                n=len(rs)
                for c in cats:
                    ca=sum(r[f'{prefix}_{c}_A'] for r in rs); cb=sum(r[f'{prefix}_{c}_B'] for r in rs); cc=sum(r[f'{prefix}_{c}_consensus'] for r in rs); cd=sum(r[f'{prefix}_{c}_disagree'] for r in rs)
                    key=(family,c,gen,st)
                    prevalence[key]=(rate(ca,n),rate(cb,n),rate(cc,n),n)
                    rows.append({
                        'family':family,'category':c,'catalog_generation':gen,'stratum':st,'n_fragments':n,
                        'A_count':ca,'A_rate':round(rate(ca,n),8),'A_per_100':round(rate(ca,n)*100,4),
                        'B_count':cb,'B_rate':round(rate(cb,n),8),'B_per_100':round(rate(cb,n)*100,4),
                        'consensus_positive_count':cc,'consensus_positive_rate':round(rate(cc,n),8),'consensus_positive_per_100':round(rate(cc,n)*100,4),
                        'method_sensitive_count':cd,'method_sensitive_rate':round(rate(cd,n),8),
                        'consensus_negative_count':n-ca-cb+cc,'consensus_negative_rate':round(rate(n-ca-cb+cc,n),8),
                        'comparison_version':VERSION,
                    })
        with outpath.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
        return rows
    action_prev=build_prevalence('action',ACTIONS,OUT_ACTION)
    position_prev=build_prevalence('position',POSITIONS,OUT_POSITION)

    def composition(family,cats,outpath):
        prefix='action' if family=='action' else 'position'; rows=[]
        for gen in GENERATIONS:
            rs=[r for r in integrated if r['catalog_generation']==gen and 'certain_nonheading' in strata(r)]
            denom=sum(any(r[f'{prefix}_{c}_consensus'] for c in cats) for r in rs)
            for c in cats:
                num=sum(r[f'{prefix}_{c}_consensus'] for r in rs)
                rows.append({'family':family,'category':c,'catalog_generation':gen,'denominator_consensus_positive_fragments':denom,'consensus_positive_count':num,'composition_rate':round(rate(num,denom),8),'composition_percent':round(rate(num,denom)*100,4),'comparison_version':VERSION})
        with outpath.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    composition('action',ACTIONS,OUT_ACOMP); composition('position',POSITIONS,OUT_PCOMP)

    # Family prevalence using OR within each family.
    famrows=[]
    for domain,mapping in [('action',ACTION_FAMILIES),('position',POSITION_FAMILIES)]:
        for gen in GENERATIONS:
            genrows=[r for r in integrated if r['catalog_generation']==gen]
            for st in strata_names:
                rs=[r for r in genrows if st in strata(r)]; n=len(rs)
                for fam,cats in mapping.items():
                    ca=sum(any(r[f'{domain}_{c}_A'] for c in cats) for r in rs)
                    cb=sum(any(r[f'{domain}_{c}_B'] for c in cats) for r in rs)
                    cc=sum(any(r[f'{domain}_{c}_consensus'] for c in cats) for r in rs)
                    famrows.append({'domain':domain,'aggregate_family':fam,'catalog_generation':gen,'stratum':st,'n_fragments':n,'A_count':ca,'A_rate':round(rate(ca,n),8),'B_count':cb,'B_rate':round(rate(cb,n),8),'consensus_positive_count':cc,'consensus_positive_rate':round(rate(cc,n),8),'comparison_version':VERSION})
    with OUT_FAMILY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(famrows[0].keys()));w.writeheader();w.writerows(famrows)

    trans=[]
    def add_trans(domain,category,initial,final,vals_i,vals_f,n_i,n_f):
        dirs=[]; names=['A','B','consensus']
        local=[]
        for name,vi,vf in zip(names,vals_i,vals_f):
            delta=vf-vi; direction=dir_from_delta(delta); dirs.append(direction)
            local.append((name,vi,vf,delta,direction))
        robust=int(dirs[0]==dirs[1]==dirs[2] and dirs[0]!='no_change')
        sensitive=int((dirs[0]=='increase' and dirs[1]=='decrease') or (dirs[0]=='decrease' and dirs[1]=='increase'))
        for name,vi,vf,delta,direction in local:
            trans.append({'domain':domain,'category':category,'initial_generation':initial,'final_generation':final,'stratum':'certain_nonheading','specification':name,'n_initial':n_i,'n_final':n_f,'initial_rate':round(vi,8),'final_rate':round(vf,8),'difference_pp':round(delta*100,4),'prevalence_ratio':'' if vi==0 else round(vf/vi,6),'direction':direction,'directionally_robust':robust,'method_sensitive_direction':sensitive,'comparison_version':VERSION})
    for domain,cats in [('action',ACTIONS),('position',POSITIONS)]:
        for c in cats:
            for initial,final in TRANSITIONS:
                vi=prevalence[(domain,c,initial,'certain_nonheading')]; vf=prevalence[(domain,c,final,'certain_nonheading')]
                add_trans(domain,c,initial,final,vi[:3],vf[:3],vi[3],vf[3])
    # Families in transitions.
    fmap={(r['domain'],r['aggregate_family'],r['catalog_generation'],r['stratum']):(float(r['A_rate']),float(r['B_rate']),float(r['consensus_positive_rate']),int(r['n_fragments'])) for r in famrows}
    for domain,mapping in [('action_family',ACTION_FAMILIES),('position_family',POSITION_FAMILIES)]:
        rawdomain='action' if domain=='action_family' else 'position'
        for fam in mapping:
            for initial,final in TRANSITIONS:
                vi=fmap[(rawdomain,fam,initial,'certain_nonheading')];vf=fmap[(rawdomain,fam,final,'certain_nonheading')]
                add_trans(domain,fam,initial,final,vi[:3],vf[:3],vi[3],vf[3])
    with OUT_TRANS.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(trans[0].keys()));w.writeheader();w.writerows(trans)

    # Deterministic summary: counts + robust transition counts only; no hand-picked narrative.
    robust_groups=defaultdict(int); sensitive_groups=defaultdict(int)
    seen=set()
    for r in trans:
        key=(r['domain'],r['category'],r['initial_generation'],r['final_generation'])
        if key in seen: continue
        seen.add(key); robust_groups[(r['initial_generation'],r['final_generation'])]+=int(r['directionally_robust']); sensitive_groups[(r['initial_generation'],r['final_generation'])]+=int(r['method_sensitive_direction'])
    certain={g:next(int(x['n_fragments']) for x in action_prev if x['catalog_generation']==g and x['stratum']=='certain_nonheading') for g in GENERATIONS}
    md=['# Historical comparison 0.1 — computational derived summary','',f'Version: `{VERSION}`. No source/fragment text is included.','','## Certain non-heading denominators']
    md += [f'- {g}: {certain[g]:,} fragments' for g in GENERATIONS]
    md += ['', '## Preregistered transition stability counts']
    for tr in TRANSITIONS:
        md.append(f'- {tr[0]} → {tr[1]}: {robust_groups[tr]} category/family transitions directionally robust; {sensitive_groups[tr]} method-sensitive directions.')
    md += ['', 'Interpretation must use the detailed prevalence/transition CSVs and the rules in `docs/HISTORICAL_COMPARISON_SPEC_0_1.md`. This summary deliberately avoids selecting favorable categories after seeing results.','']
    OUT_MD.write_text('\n'.join(md),encoding='utf-8')
    print('integrated',len(integrated),'transition rows',len(trans))

if __name__=='__main__':main()
