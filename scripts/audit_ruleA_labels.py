#!/usr/bin/env python3
"""Audit RULEA_0.1 labels without reading fragment/source text."""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path

SRC=Path('data/derived/fragment_labels_A.csv')
MAN=Path('data/derived/fragment_manifest.csv')
OUT=Path('data/derived/fragment_labels_A_audit.csv')
VERSION='RULEA_AUDIT_0.1'

ACTIONS=['observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment']
POSITIONS=['receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent']


def main():
    labels=list(csv.DictReader(SRC.open(encoding='utf-8')))
    man=list(csv.DictReader(MAN.open(encoding='utf-8')))
    assert len(labels)==9594==len(man)
    assert {r['fragment_id'] for r in labels}=={r['fragment_id'] for r in man}
    mh={r['fragment_id']:r['text_sha256'] for r in man}
    assert all(r['text_sha256']==mh[r['fragment_id']] for r in labels)
    assert all(r['ruleset_version']=='RULEA_0.1' for r in labels)
    mm={r['fragment_id']:r for r in man}

    out=[]
    for gen in ['1972','1988','1993','2014','ALL']:
        rs=labels if gen=='ALL' else [r for r in labels if r['catalog_generation']==gen]
        zero_actions=sum(all(int(r[f'action_{a}'])==0 for a in ACTIONS) for r in rs)
        zero_positions=sum(all(int(r[f'position_{p}'])==0 for p in POSITIONS) for r in rs)
        multi_actions=sum(sum(int(r[f'action_{a}']) for a in ACTIONS)>1 for r in rs)
        multi_positions=sum(sum(int(r[f'position_{p}']) for p in POSITIONS)>1 for r in rs)
        uncertain=sum(int(r['uncertain_A']) for r in rs)
        # Suspicious logical co-occurrences. These are diagnostics, not automatic corrections.
        receiver_plus_rich=sum(
            int(r['position_receiver']) and any(int(r[f'position_{p}']) for p in POSITIONS if p!='receiver')
            for r in rs
        )
        follower_plus_rich=sum(
            int(r['position_instruction_follower']) and any(int(r[f'position_{p}']) for p in POSITIONS if p!='instruction_follower')
            for r in rs
        )
        experiment_without_experimenter=sum(int(r['action_experiment']) and not int(r['position_experimenter']) for r in rs)
        investigate_without_investigator=sum(int(r['action_investigate']) and not int(r['position_investigator']) for r in rs)
        decide_without_decision=sum(int(r['action_decide']) and not int(r['position_decision_maker']) for r in rs)
        community_without_agent=sum(int(r['action_act_on_environment']) and not int(r['position_community_agent']) for r in rs)
        row={
            'catalog_generation':gen,'fragment_count':len(rs),
            'zero_action_count':zero_actions,'zero_action_rate':round(zero_actions/len(rs),6),
            'zero_position_count':zero_positions,'zero_position_rate':round(zero_positions/len(rs),6),
            'multi_action_count':multi_actions,'multi_action_rate':round(multi_actions/len(rs),6),
            'multi_position_count':multi_positions,'multi_position_rate':round(multi_positions/len(rs),6),
            'uncertain_A':uncertain,'uncertain_rate_A':round(uncertain/len(rs),6),
            'receiver_plus_rich_position':receiver_plus_rich,
            'instruction_follower_plus_rich_position':follower_plus_rich,
            'experiment_without_experimenter':experiment_without_experimenter,
            'investigate_without_investigator':investigate_without_investigator,
            'decide_without_decision_maker':decide_without_decision,
            'community_action_without_agent':community_without_agent,
            'audit_version':VERSION,
        }
        for a in ACTIONS:
            n=sum(int(r[f'action_{a}']) for r in rs); row[f'action_{a}']=n; row[f'action_{a}_rate']=round(n/len(rs),6)
        for p in POSITIONS:
            n=sum(int(r[f'position_{p}']) for r in rs); row[f'position_{p}']=n; row[f'position_{p}_rate']=round(n/len(rs),6)
        out.append(row)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0].keys()));w.writeheader();w.writerows(out)
    allrow=out[-1]
    print(allrow)
    assert allrow['receiver_plus_rich_position']==0
    assert allrow['instruction_follower_plus_rich_position']==0
    assert allrow['experiment_without_experimenter']==0
    assert allrow['investigate_without_investigator']==0
    assert allrow['decide_without_decision_maker']==0
    assert allrow['community_action_without_agent']==0

if __name__=='__main__':main()
