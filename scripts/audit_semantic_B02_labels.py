#!/usr/bin/env python3
"""Audit validated SEMB_0.2 labels using derived metadata only.

No source/fragment text, embeddings, RULEA patterns, or human labels are read.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

MAN=Path('data/derived/fragment_manifest.csv')
SRC=Path('data/derived/fragment_labels_B.csv')
OUT=Path('data/derived/fragment_labels_B_audit.csv')
VERSION='SEMB_AUDIT_0.1'
MODEL='intfloat/multilingual-e5-small'
REV='fd1525a9fd15316a2d503bf26ab031a61d056e98'

ACTIONS=['observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment']
POSITIONS=['receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent']


def main():
    man=list(csv.DictReader(MAN.open(encoding='utf-8')))
    rows=list(csv.DictReader(SRC.open(encoding='utf-8')))
    assert len(man)==9594==len(rows), (len(man),len(rows))
    assert all(r['segmenter_version']=='FRAGSEG_0.2' for r in man)
    assert len({r['fragment_id'] for r in rows})==9594
    assert {r['fragment_id'] for r in rows}=={r['fragment_id'] for r in man}
    mh={r['fragment_id']:r['text_sha256'] for r in man}
    assert all(r['text_sha256']==mh[r['fragment_id']] for r in rows)
    assert all(r['semantic_rules_version']=='SEMB_0.2' for r in rows)
    assert all(r['semantic_model']==MODEL and r['semantic_model_revision']==REV for r in rows)
    assert len({r['semantic_method'] for r in rows})==1

    out=[]
    for gen in ['1972','1988','1993','2014','ALL']:
        rs=rows if gen=='ALL' else [r for r in rows if r['catalog_generation']==gen]
        action_sizes=[int(r['action_label_count_B']) for r in rs]
        pos_sizes=[int(r['position_label_count_B']) for r in rs]
        uncertain=sum(int(r['uncertain_B']) for r in rs)
        trunc=sum(int(r['truncation_risk_B']) for r in rs)
        bad_action=sum(x>3 for x in action_sizes)
        bad_pos=sum(x>2 for x in pos_sizes)
        zero_a=sum(x==0 for x in action_sizes)
        zero_p=sum(x==0 for x in pos_sizes)
        gate_below=sum(
            (r['action_gate_margin_B']!='' and float(r['action_gate_margin_B']) < float(r['action_gate_threshold_B']))
            for r in rs
        )
        labeled_below=sum(
            int(r['action_label_count_B'])>0 and r['action_gate_margin_B']!='' and float(r['action_gate_margin_B']) < float(r['action_gate_threshold_B'])
            for r in rs
        )
        d={
            'catalog_generation':gen,'fragment_count':len(rs),
            'zero_action_B':zero_a,'zero_action_rate_B':round(zero_a/len(rs),6),
            'zero_position_B':zero_p,'zero_position_rate_B':round(zero_p/len(rs),6),
            'uncertain_B':uncertain,'uncertain_rate_B':round(uncertain/len(rs),6),
            'truncation_risk_B':trunc,'truncation_rate_B':round(trunc/len(rs),6),
            'max_action_labels_observed':max(action_sizes),'max_position_labels_observed':max(pos_sizes),
            'action_label_limit_violations':bad_action,'position_label_limit_violations':bad_pos,
            'gate_below_threshold_count':gate_below,'labeled_action_below_gate_count':labeled_below,
            'semantic_method':rs[0]['semantic_method'],'audit_version':VERSION,
        }
        for a in ACTIONS:
            n=sum(int(r[f'action_{a}_B']) for r in rs); d[f'action_{a}_B']=n; d[f'action_{a}_B_rate']=round(n/len(rs),6)
        for p in POSITIONS:
            n=sum(int(r[f'position_{p}_B']) for r in rs); d[f'position_{p}_B']=n; d[f'position_{p}_B_rate']=round(n/len(rs),6)
        out.append(d)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0].keys()));w.writeheader();w.writerows(out)
    allrow=out[-1]
    print(allrow)
    assert allrow['action_label_limit_violations']==0
    assert allrow['position_label_limit_violations']==0
    assert allrow['labeled_action_below_gate_count']==0
    assert allrow['truncation_rate_B'] <= .02, allrow

if __name__=='__main__':main()
