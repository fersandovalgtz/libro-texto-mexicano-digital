#!/usr/bin/env python3
"""Compare RULEA_0.1 and SEMB_0.1 labels without text or human adjudication."""
from __future__ import annotations
import csv, statistics
from collections import Counter, defaultdict
from pathlib import Path

MAN=Path('data/derived/fragment_manifest.csv')
A=Path('data/derived/fragment_labels_A.csv')
B=Path('data/derived/fragment_labels_B.csv')
OUT_CAT=Path('data/derived/classifier_AB_category_agreement.csv')
OUT_FRAG=Path('data/derived/classifier_AB_fragment_agreement.csv')
OUT_SUM=Path('data/derived/classifier_AB_agreement_summary.csv')
VERSION='AGREE_AB_0.1'
ACTIONS=['observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment']
POSITIONS=['receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent']


def jacc(a,b):
    u=a|b
    return 1.0 if not u else len(a&b)/len(u)

def safe(num,den):
    return '' if den==0 else round(num/den,6)

def main():
    man=list(csv.DictReader(MAN.open(encoding='utf-8')))
    aa={r['fragment_id']:r for r in csv.DictReader(A.open(encoding='utf-8'))}
    bb={r['fragment_id']:r for r in csv.DictReader(B.open(encoding='utf-8'))}
    ids={r['fragment_id'] for r in man}
    assert len(man)==9594 and set(aa)==ids==set(bb)
    mh={r['fragment_id']:r['text_sha256'] for r in man}
    assert all(aa[i]['text_sha256']==mh[i] and bb[i]['text_sha256']==mh[i] for i in ids)
    mm={r['fragment_id']:r for r in man}

    frag=[]
    for fid in sorted(ids):
        ar={x for x in ACTIONS if int(aa[fid][f'action_{x}'])}
        br={x for x in ACTIONS if int(bb[fid][f'action_{x}_B'])}
        ap={x for x in POSITIONS if int(aa[fid][f'position_{x}'])}
        bp={x for x in POSITIONS if int(bb[fid][f'position_{x}_B'])}
        ja=jacc(ar,br); jp=jacc(ap,bp)
        exacta=int(ar==br); exactp=int(ap==bp)
        uncertain=int(aa[fid]['uncertain_A']) or int(bb[fid]['uncertain_B'])
        minj=min(ja,jp)
        if uncertain: stability='uncertain'
        elif exacta and exactp: stability='stable_exact'
        elif minj>=.5: stability='stable_partial'
        else: stability='method_sensitive'
        frag.append({
            'fragment_id':fid,'page_id':mm[fid]['page_id'],'catalog_generation':mm[fid]['catalog_generation'],
            'candidate_type':mm[fid]['candidate_type'],'source_structure_class':mm[fid]['source_structure_class'],
            'action_jaccard':round(ja,6),'position_jaccard':round(jp,6),
            'action_exact_set':exacta,'position_exact_set':exactp,
            'action_empty_both':int(not ar and not br),'position_empty_both':int(not ap and not bp),
            'action_size_A':len(ar),'action_size_B':len(br),'position_size_A':len(ap),'position_size_B':len(bp),
            'uncertain_A':aa[fid]['uncertain_A'],'uncertain_B':bb[fid]['uncertain_B'],'stability_stratum':stability,
            'agreement_version':VERSION,
        })
    with OUT_FRAG.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(frag[0].keys()));w.writeheader();w.writerows(frag)

    catrows=[]
    for family,cats in [('action',ACTIONS),('position',POSITIONS)]:
        for gen in ['1972','1988','1993','2014','ALL']:
            sel=ids if gen=='ALL' else {i for i in ids if mm[i]['catalog_generation']==gen}
            for c in cats:
                vals=[]
                for i in sel:
                    av=int(aa[i][f'{family}_{c}']); bv=int(bb[i][f'{family}_{c}_B']); vals.append((av,bv))
                n11=sum(a==1 and b==1 for a,b in vals);n10=sum(a==1 and b==0 for a,b in vals);n01=sum(a==0 and b==1 for a,b in vals);n00=sum(a==0 and b==0 for a,b in vals);n=len(vals)
                catrows.append({
                    'family':family,'category':c,'catalog_generation':gen,'n':n,
                    'n11':n11,'n10':n10,'n01':n01,'n00':n00,
                    'binary_agreement':safe(n11+n00,n),'positive_jaccard':safe(n11,n11+n10+n01),
                    'B_precision_vs_A_descriptor':safe(n11,n11+n01),'B_recall_vs_A_descriptor':safe(n11,n11+n10),
                    'prevalence_A':safe(n11+n10,n),'prevalence_B':safe(n11+n01,n),
                    'absolute_prevalence_difference':round(abs((n11+n10)/n-(n11+n01)/n),6),
                    'agreement_version':VERSION,
                })
    with OUT_CAT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(catrows[0].keys()));w.writeheader();w.writerows(catrows)

    def aggregate(rs,label):
        ajs=[float(r['action_jaccard']) for r in rs];pjs=[float(r['position_jaccard']) for r in rs]
        c=Counter(r['stability_stratum'] for r in rs)
        return {
            'stratum':label,'n':len(rs),
            'action_jaccard_mean':round(sum(ajs)/len(ajs),6),'action_jaccard_median':round(statistics.median(ajs),6),
            'position_jaccard_mean':round(sum(pjs)/len(pjs),6),'position_jaccard_median':round(statistics.median(pjs),6),
            'action_exact_rate':round(sum(int(r['action_exact_set']) for r in rs)/len(rs),6),
            'position_exact_rate':round(sum(int(r['position_exact_set']) for r in rs)/len(rs),6),
            'action_empty_both_rate':round(sum(int(r['action_empty_both']) for r in rs)/len(rs),6),
            'position_empty_both_rate':round(sum(int(r['position_empty_both']) for r in rs)/len(rs),6),
            'stable_exact':c['stable_exact'],'stable_partial':c['stable_partial'],'method_sensitive':c['method_sensitive'],'uncertain':c['uncertain'],
            'agreement_version':VERSION,
        }
    sums=[]
    for gen in ['1972','1988','1993','2014','ALL']:
        base=frag if gen=='ALL' else [r for r in frag if r['catalog_generation']==gen]
        sums.append(aggregate(base,f'{gen}:all'))
        nh=[r for r in base if r['candidate_type']!='heading_candidate'];sums.append(aggregate(nh,f'{gen}:nonheading'))
        certain=[r for r in base if not int(r['uncertain_A']) and not int(r['uncertain_B'])];sums.append(aggregate(certain,f'{gen}:certain_only'))
        for st in ['textual','mixed_text_image']:
            xs=[r for r in base if r['source_structure_class']==st]
            if xs:sums.append(aggregate(xs,f'{gen}:structure={st}'))
    with OUT_SUM.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(sums[0].keys()));w.writeheader();w.writerows(sums)
    print('fragment rows',len(frag),'category rows',len(catrows),'summary rows',len(sums))

if __name__=='__main__':main()
