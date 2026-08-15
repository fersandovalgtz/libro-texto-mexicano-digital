#!/usr/bin/env python3
"""Evaluate agreement between two blinded SEMB 0.3 human annotation files.

Intended for local/private annotation CSVs. Does not read classifier outputs or
historical comparison files.
"""
from __future__ import annotations
import argparse, csv
from collections import Counter


def load(path): return {r['sample_id']:r for r in csv.DictReader(open(path,encoding='utf-8'))}
def labs(s): return {x.strip() for x in (s or '').split(';') if x.strip()}
def jacc(a,b):
    u=a|b
    return 1.0 if not u else len(a&b)/len(u)
def f1(a,b):
    if not a and not b:return 1.0
    if not a or not b:return 0.0
    p=len(a&b)/len(a); r=len(a&b)/len(b)
    return 0.0 if p+r==0 else 2*p*r/(p+r)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('annotator_a');ap.add_argument('annotator_b');args=ap.parse_args()
    a=load(args.annotator_a);b=load(args.annotator_b);ids=sorted(set(a)&set(b))
    if not ids:raise SystemExit('No overlapping sample IDs')
    actionable=sum(a[i]['actionable']==b[i]['actionable'] for i in ids)/len(ids)
    aj=[jacc(labs(a[i]['action_labels']),labs(b[i]['action_labels'])) for i in ids]
    af=[f1(labs(a[i]['action_labels']),labs(b[i]['action_labels'])) for i in ids]
    pj=[jacc(labs(a[i]['position_labels']),labs(b[i]['position_labels'])) for i in ids]
    pf=[f1(labs(a[i]['position_labels']),labs(b[i]['position_labels'])) for i in ids]
    print('n_overlap',len(ids))
    print('actionable_exact_agreement',round(actionable,4))
    print('action_jaccard_mean',round(sum(aj)/len(aj),4))
    print('action_f1_mean',round(sum(af)/len(af),4))
    print('position_jaccard_mean',round(sum(pj)/len(pj),4))
    print('position_f1_mean',round(sum(pf)/len(pf),4))
    for field in ('action_labels','position_labels'):
        cats=sorted(set().union(*(labs(a[i][field])|labs(b[i][field]) for i in ids)))
        print('\n'+field)
        for c in cats:
            aa=[c in labs(a[i][field]) for i in ids];bb=[c in labs(b[i][field]) for i in ids]
            exact=sum(x==y for x,y in zip(aa,bb))/len(ids)
            tp=sum(x and y for x,y in zip(aa,bb));fp=sum(x and not y for x,y in zip(aa,bb));fn=sum((not x) and y for x,y in zip(aa,bb))
            f=0.0 if 2*tp+fp+fn==0 else 2*tp/(2*tp+fp+fn)
            print(c,'agreement',round(exact,4),'f1',round(f,4),'positive_union',tp+fp+fn)

if __name__=='__main__':main()
