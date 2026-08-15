#!/usr/bin/env python3
"""Strict schema/content validator for blinded SEMB 0.3 annotation CSVs."""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

MASTER=Path('data/validation/semb03_human_reference_sample.csv')
ACTIONS={'observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment'}
POSITIONS={'receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent'}
REQ=('sample_id','annotator_id','annotation_round','actionable','action_labels','position_labels','annotation_confidence','ambiguity_note')
VERSION='SEMB03_ANNOTATION_VALIDATOR_0.1'


def labs(s):return [x.strip() for x in (s or '').split(';') if x.strip()]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('annotations');ap.add_argument('--subset');ap.add_argument('--require-complete',action='store_true');ap.add_argument('--json-out');args=ap.parse_args()
    master={r['sample_id']:r for r in csv.DictReader(MASTER.open(encoding='utf-8'))}
    rows=list(csv.DictReader(open(args.annotations,encoding='utf-8')))
    if not rows:raise SystemExit('annotation file has no rows')
    missing=[f for f in REQ if f not in rows[0]]
    if missing:raise SystemExit('missing columns: '+','.join(missing))
    ids=[r['sample_id'] for r in rows]
    errors=[]
    if len(ids)!=len(set(ids)):errors.append('duplicate sample_id rows')
    for i,r in enumerate(rows,2):
        sid=r['sample_id'];pre=f'line {i} {sid}: '
        if sid not in master:errors.append(pre+'unknown sample_id')
        if not re.fullmatch(r'S03-[0-9A-F]{16}',sid or ''):errors.append(pre+'non-opaque sample_id format')
        if not r['annotator_id'].strip():errors.append(pre+'annotator_id empty')
        if not r['annotation_round'].strip():errors.append(pre+'annotation_round empty')
        if r['actionable'] not in {'0','1','u'}:errors.append(pre+'actionable must be 0/1/u')
        aa=labs(r['action_labels']);pp=labs(r['position_labels'])
        if len(aa)!=len(set(aa)):errors.append(pre+'duplicate action label')
        if len(pp)!=len(set(pp)):errors.append(pre+'duplicate position label')
        bad=[x for x in aa if x not in ACTIONS]
        if bad:errors.append(pre+'invalid action labels '+','.join(bad))
        bad=[x for x in pp if x not in POSITIONS]
        if bad:errors.append(pre+'invalid position labels '+','.join(bad))
        if r['actionable']=='0' and aa:errors.append(pre+'actionable=0 requires empty action_labels')
        if r['annotation_confidence'] not in {'1','2','3'}:errors.append(pre+'annotation_confidence must be 1/2/3')
        if r['actionable']=='u' and not r['ambiguity_note'].strip():errors.append(pre+'ambiguous actionable requires ambiguity_note')
    expected=set(master)
    if args.subset:
        subset={r['sample_id'] for r in csv.DictReader(open(args.subset,encoding='utf-8'))};expected=subset
        extra=set(ids)-subset
        if extra:errors.append(f'{len(extra)} rows outside requested subset')
    if args.require_complete:
        absent=expected-set(ids)
        if absent:errors.append(f'incomplete annotations: {len(absent)} expected IDs absent')
    report={'validator_version':VERSION,'file':args.annotations,'n_rows':len(rows),'n_unique':len(set(ids)),'require_complete':args.require_complete,'errors':errors,'passed':not errors}
    if args.json_out:
        p=Path(args.json_out);p.parent.mkdir(parents=True,exist_ok=True);json.dump(report,p.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(2)

if __name__=='__main__':main()
