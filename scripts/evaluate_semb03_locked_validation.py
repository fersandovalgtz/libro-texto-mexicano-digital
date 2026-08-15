#!/usr/bin/env python3
"""One-shot evaluation of a locked SEMB 0.3 candidate against human reference.

Requires an existing model lock. Uses only sample IDs assigned to locked_validation.
It writes the validation result but never modifies model configuration.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

MASTER=Path('data/validation/semb03_human_reference_sample.csv')
CRIT=Path('data/validation/semb03_acceptance_criteria.json')
LOCK=Path('data/validation/semb03_model_lock.json')
OUT=Path('data/validation/semb03_locked_validation_result.json')
VERSION='SEMB03_LOCKED_VALIDATION_0.1'
ACTIONS=('observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment')
POSITIONS=('receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent')

def labs(s):return {x.strip() for x in (s or '').split(';') if x.strip()}
def load(p):return {r['sample_id']:r for r in csv.DictReader(open(p,encoding='utf-8'))}
def div(a,b):return a/b if b else None

def binary_metrics(y,yp):
    tp=sum(a==1 and b==1 for a,b in zip(y,yp));tn=sum(a==0 and b==0 for a,b in zip(y,yp));fp=sum(a==0 and b==1 for a,b in zip(y,yp));fn=sum(a==1 and b==0 for a,b in zip(y,yp))
    sens=div(tp,tp+fn);spec=div(tn,tn+fp)
    return {'tp':tp,'tn':tn,'fp':fp,'fn':fn,'sensitivity':sens,'specificity':spec,'balanced_accuracy':None if sens is None or spec is None else (sens+spec)/2}

def multilabel_metrics(rows,field,labels):
    total_tp=total_fp=total_fn=0; per={}
    for lab in labels:
        tp=fp=fn=0
        for h,p in rows:
            a=lab in labs(h[field]);b=lab in labs(p[field])
            tp+=a and b;fp+=(not a) and b;fn+=a and (not b)
        denom=2*tp+fp+fn;f1=0.0 if denom==0 else 2*tp/denom
        human_pos=tp+fn
        per[lab]={'tp':tp,'fp':fp,'fn':fn,'human_positives':human_pos,'f1':f1}
        total_tp+=tp;total_fp+=fp;total_fn+=fn
    micro=0.0 if 2*total_tp+total_fp+total_fn==0 else 2*total_tp/(2*total_tp+total_fp+total_fn)
    return {'micro_f1':micro,'per_category':per}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--predictions',required=True);ap.add_argument('--reference',required=True);args=ap.parse_args()
    if OUT.exists():raise SystemExit('Locked validation result already exists; refusing a second look')
    if not LOCK.exists():raise SystemExit('Model must be locked before validation')
    lock=json.load(LOCK.open(encoding='utf-8'));crit=json.load(CRIT.open(encoding='utf-8'))
    master=load(MASTER);pred=load(args.predictions);ref=load(args.reference)
    locked=[sid for sid,r in master.items() if r['analysis_role']=='locked_validation']
    if len(locked)!=160:raise SystemExit(f'expected 160 locked IDs, found {len(locked)}')
    missing_pred=[x for x in locked if x not in pred];missing_ref=[x for x in locked if x not in ref]
    if missing_pred or missing_ref:raise SystemExit(f'incomplete locked data: predictions missing={len(missing_pred)}, reference missing={len(missing_ref)}')
    usable=[sid for sid in locked if ref[sid].get('actionable') in {'0','1'}]
    y=[int(ref[s]['actionable']) for s in usable];yp=[int(pred[s]['actionable']) for s in usable]
    actionable=binary_metrics(y,yp)
    pairs=[(ref[s],pred[s]) for s in usable]
    act=multilabel_metrics(pairs,'action_labels',ACTIONS);pos=multilabel_metrics(pairs,'position_labels',POSITIONS)
    ca=crit['locked_validation'];
    def macro_block(m,conf):
        vals=[v['f1'] for v in m['per_category'].values() if v['human_positives']>=conf['macro_min_human_positives']]
        m['macro_f1']=sum(vals)/len(vals) if vals else None
        floors=[(k,v) for k,v in m['per_category'].items() if v['human_positives']>=conf['category_floor_min_human_positives'] and v['f1']<conf['category_f1_floor']]
        m['category_floor_failures']=[k for k,_ in floors]
    macro_block(act,ca['actions']);macro_block(pos,ca['positions'])
    checks={
      'actionable_balanced_accuracy':actionable['balanced_accuracy']>=ca['actionable']['balanced_accuracy_min'],
      'actionable_sensitivity':actionable['sensitivity']>=ca['actionable']['sensitivity_min'],
      'actionable_specificity':actionable['specificity']>=ca['actionable']['specificity_min'],
      'actions_micro_f1':act['micro_f1']>=ca['actions']['micro_f1_min'],
      'actions_macro_f1':act['macro_f1'] is not None and act['macro_f1']>=ca['actions']['macro_f1_min'],
      'actions_category_floors':not act['category_floor_failures'],
      'positions_micro_f1':pos['micro_f1']>=ca['positions']['micro_f1_min'],
      'positions_macro_f1':pos['macro_f1'] is not None and pos['macro_f1']>=ca['positions']['macro_f1_min'],
      'positions_category_floors':not pos['category_floor_failures'],
    }
    result={'validation_version':VERSION,'model_lock_version':lock.get('lock_version'),'model_lock_git_head':lock.get('git_head'),'criteria_version':crit['criteria_version'],'locked_n':160,'usable_nonambiguous_n':len(usable),'actionable':actionable,'actions':act,'positions':pos,'checks':checks,'passed':all(checks.values()),'model_modified_after_opening_validation':False}
    OUT.parent.mkdir(parents=True,exist_ok=True);json.dump(result,OUT.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
