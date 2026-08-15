#!/usr/bin/env python3
"""Build a SEMB 0.3 consensus draft without adjudicating disagreements automatically.

Exact matches are copied into a consensus draft. Any disagreement is written to a
separate adjudication queue. This script never chooses one annotator over another.
"""
from __future__ import annotations
import argparse,csv
from pathlib import Path

FIELDS=('sample_id','actionable','action_labels','position_labels','annotation_confidence','ambiguity_note','consensus_status')

def load(p):return {r['sample_id']:r for r in csv.DictReader(open(p,encoding='utf-8'))}
def canon_labels(s):return ';'.join(sorted({x.strip() for x in (s or '').split(';') if x.strip()}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('annotator_a');ap.add_argument('annotator_b');ap.add_argument('--subset');ap.add_argument('--out',default='private/semb03_consensus_draft.csv');ap.add_argument('--disagreements',default='private/semb03_disagreements.csv');args=ap.parse_args()
    a=load(args.annotator_a);b=load(args.annotator_b)
    ids=set(a)&set(b)
    if args.subset:
        ids &= {r['sample_id'] for r in csv.DictReader(open(args.subset,encoding='utf-8'))}
    ids=sorted(ids)
    if not ids:raise SystemExit('No overlapping sample IDs')
    cons=[];dis=[]
    for sid in ids:
        x,y=a[sid],b[sid]
        vals_a=(x['actionable'],canon_labels(x['action_labels']),canon_labels(x['position_labels']))
        vals_b=(y['actionable'],canon_labels(y['action_labels']),canon_labels(y['position_labels']))
        if vals_a==vals_b:
            conf=str(min(int(x['annotation_confidence']),int(y['annotation_confidence']))) if x['annotation_confidence'] and y['annotation_confidence'] else ''
            notes=' | '.join(z for z in (x.get('ambiguity_note','').strip(),y.get('ambiguity_note','').strip()) if z)
            cons.append({'sample_id':sid,'actionable':vals_a[0],'action_labels':vals_a[1],'position_labels':vals_a[2],
                         'annotation_confidence':conf,'ambiguity_note':notes,'consensus_status':'exact_agreement'})
        else:
            dis.append({'sample_id':sid,
                        'a_actionable':vals_a[0],'b_actionable':vals_b[0],
                        'a_action_labels':vals_a[1],'b_action_labels':vals_b[1],
                        'a_position_labels':vals_a[2],'b_position_labels':vals_b[2],
                        'a_confidence':x.get('annotation_confidence',''),'b_confidence':y.get('annotation_confidence',''),
                        'a_note':x.get('ambiguity_note',''),'b_note':y.get('ambiguity_note',''),
                        'adjudicated_actionable':'','adjudicated_action_labels':'','adjudicated_position_labels':'','adjudication_note':''})
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(cons)
    d=Path(args.disagreements);d.parent.mkdir(parents=True,exist_ok=True)
    dfields=['sample_id','a_actionable','b_actionable','a_action_labels','b_action_labels','a_position_labels','b_position_labels','a_confidence','b_confidence','a_note','b_note','adjudicated_actionable','adjudicated_action_labels','adjudicated_position_labels','adjudication_note']
    with d.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=dfields);w.writeheader();w.writerows(dis)
    print('overlap',len(ids),'exact_consensus',len(cons),'requires_human_adjudication',len(dis))

if __name__=='__main__':main()
