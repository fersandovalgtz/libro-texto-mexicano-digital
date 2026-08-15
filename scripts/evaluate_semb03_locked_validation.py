#!/usr/bin/env python3
"""One-shot evaluation of a locked SEMB 0.3 candidate against human reference.

Requires an existing model lock. Uses only sample IDs assigned to locked_validation.
It writes the validation result but never modifies model configuration. Prediction
files must expose uncertainty and truncation flags so coverage cannot be ignored.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

MASTER=Path('data/validation/semb03_human_reference_sample.csv')
CRIT=Path('data/validation/semb03_acceptance_criteria.json')
LOCK=Path('data/validation/semb03_model_lock.json')
OUT=Path('data/validation/semb03_locked_validation_result.json')
VERSION='SEMB03_LOCKED_VALIDATION_0.2'
ACTIONS=('observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment')
POSITIONS=('receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent')
PRED_REQUIRED={'sample_id','actionable','action_labels','position_labels','uncertain','truncation_risk'}

def labs(s):return {x.strip() for x in (s or '').split(';') if x.strip()}
def load_rows(p):return list(csv.DictReader(open(p,encoding='utf-8')))
def load(p):return {r['sample_id']:r for r in load_rows(p)}
def div(a,b):return a/b if b else None

def flag(v,name):
    if str(v) not in {'0','1'}:raise SystemExit(f'{name} must be 0/1, got {v!r}')
    return int(v)

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
    pred_rows=load_rows(args.predictions)
    if not pred_rows:raise SystemExit('prediction file empty')
    missing_cols=PRED_REQUIRED-set(pred_rows[0])
    if missing_cols:raise SystemExit('prediction file missing required columns: '+','.join(sorted(missing_cols)))
    master=load(MASTER);pred={r['sample_id']:r for r in pred_rows};ref=load(args.reference)
    if len(pred)!=len(pred_rows):raise SystemExit('duplicate sample_id in predictions')
    locked=[sid for sid,r in master.items() if r['analysis_role']=='locked_validation']
    if len(locked)!=160:raise SystemExit(f'expected 160 locked IDs, found {len(locked)}')
    missing_pred=[x for x in locked if x not in pred];missing_ref=[x for x in locked if x not in ref]
    if missing_pred or missing_ref:raise SystemExit(f'incomplete locked data: predictions missing={len(missing_pred)}, reference missing={len(missing_ref)}')
    extra_locked=set(pred)-set(locked)
    if extra_locked:raise SystemExit(f'prediction file contains {len(extra_locked)} non-locked sample IDs; refuse mixed evaluation file')

    usable=[sid for sid in locked if ref[sid].get('actionable') in {'0','1'}]
    y=[int(ref[s]['actionable']) for s in usable]
    try:yp=[int(pred[s]['actionable']) for s in usable]
    except Exception:raise SystemExit('predicted actionable must be 0/1')
    if any(x not in {0,1} for x in yp):raise SystemExit('predicted actionable must be 0/1')
    actionable=binary_metrics(y,yp)
    pairs=[(ref[s],pred[s]) for s in usable]
    act=multilabel_metrics(pairs,'action_labels',ACTIONS);pos=multilabel_metrics(pairs,'position_labels',POSITIONS)
    ca=crit['locked_validation']
    def macro_block(m,conf):
        vals=[v['f1'] for v in m['per_category'].values() if v['human_positives']>=conf['macro_min_human_positives']]
        m['macro_f1']=sum(vals)/len(vals) if vals else None
        floors=[(k,v) for k,v in m['per_category'].items() if v['human_positives']>=conf['category_floor_min_human_positives'] and v['f1']<conf['category_f1_floor']]
        m['category_floor_failures']=[k for k,_ in floors]
    macro_block(act,ca['actions']);macro_block(pos,ca['positions'])

    uncertain={sid:flag(pred[sid]['uncertain'],f'{sid}.uncertain') for sid in locked}
    trunc={sid:flag(pred[sid]['truncation_risk'],f'{sid}.truncation_risk') for sid in locked}
    certain_rate=sum(1-uncertain[s] for s in locked)/len(locked)
    by_generation={}
    for g in ('1972','1988','1993','2014'):
        ids=[s for s in locked if master[s]['catalog_generation']==g]
        if not ids:raise SystemExit(f'no locked cases for generation {g}')
        rate=sum(uncertain[s] for s in ids)/len(ids)
        by_generation[g]={'n':len(ids),'uncertain_n':sum(uncertain[s] for s in ids),'uncertain_rate':rate,'certain_rate':1-rate,'truncation_risk_n':sum(trunc[s] for s in ids)}
    rates=[x['uncertain_rate'] for x in by_generation.values()]
    uncertainty_gap_pp=100*(max(rates)-min(rates))
    total_trunc=sum(trunc.values())
    coverage={'certain_output_rate':certain_rate,'uncertain_rate':1-certain_rate,'by_generation':by_generation,'max_generation_uncertainty_gap_pp':uncertainty_gap_pp,'truncation_risk_n':total_trunc}

    checks={
      'actionable_balanced_accuracy':actionable['balanced_accuracy'] is not None and actionable['balanced_accuracy']>=ca['actionable']['balanced_accuracy_min'],
      'actionable_sensitivity':actionable['sensitivity'] is not None and actionable['sensitivity']>=ca['actionable']['sensitivity_min'],
      'actionable_specificity':actionable['specificity'] is not None and actionable['specificity']>=ca['actionable']['specificity_min'],
      'actions_micro_f1':act['micro_f1']>=ca['actions']['micro_f1_min'],
      'actions_macro_f1':act['macro_f1'] is not None and act['macro_f1']>=ca['actions']['macro_f1_min'],
      'actions_category_floors':not act['category_floor_failures'],
      'positions_micro_f1':pos['micro_f1']>=ca['positions']['micro_f1_min'],
      'positions_macro_f1':pos['macro_f1'] is not None and pos['macro_f1']>=ca['positions']['macro_f1_min'],
      'positions_category_floors':not pos['category_floor_failures'],
      'certain_output_rate':certain_rate>=ca['coverage']['certain_output_rate_min'],
      'generation_uncertainty_gap':uncertainty_gap_pp<=ca['coverage']['max_generation_uncertainty_gap_pp'],
      'no_silent_truncation':(total_trunc==0) if ca['coverage']['silent_truncation_allowed'] is False else True,
    }
    result={'validation_version':VERSION,'model_lock_version':lock.get('lock_version'),'model_lock_git_head':lock.get('git_head'),'criteria_version':crit['criteria_version'],'locked_n':160,'usable_nonambiguous_n':len(usable),'actionable':actionable,'actions':act,'positions':pos,'coverage':coverage,'checks':checks,'passed':all(checks.values()),'model_modified_after_opening_validation':False}
    OUT.parent.mkdir(parents=True,exist_ok=True);json.dump(result,OUT.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
