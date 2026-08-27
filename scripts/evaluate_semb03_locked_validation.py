#!/usr/bin/env python3
"""One-shot evaluation of a locked SEMB 0.3 candidate against a private holdout.

The historical 160 rows labelled ``locked_validation`` in the public
SEMB03_SAMPLE_0.2 are explicitly inadmissible for final validation because their
identities were published before model lock. Final evaluation therefore requires
an explicit private holdout manifest whose SHA-256 matches the public commitment
bound into the model lock.

The script writes aggregate validation metrics only. It never modifies model
configuration and never writes private sample or fragment identifiers to the
result JSON.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

CRIT_DEFAULT = Path('data/validation/semb03_acceptance_criteria.json')
COMMITMENT_DEFAULT = Path('data/validation/semb03_private_holdout_commitment.json')
LOCK_DEFAULT = Path('data/validation/semb03_model_lock.json')
LEGACY = Path('data/validation/semb03_human_reference_sample.csv')
OUT_DEFAULT = Path('data/validation/semb03_locked_validation_result.json')
VERSION = 'SEMB03_LOCKED_VALIDATION_0.3'
HOLDOUT_VERSION = 'SEMB03_PRIVATE_HOLDOUT_0.1'
GENERATIONS = ('1972', '1988', '1993', '2014')
ACTIONS = ('observe','describe','recall','explain','compare','classify','measure','experiment','investigate','predict','infer','discuss','solve','create','decide','act_on_environment')
POSITIONS = ('receiver','instruction_follower','observer','experimenter','investigator','reasoner','collaborator','decision_maker','community_agent')
PRED_REQUIRED = {'private_sample_id','actionable','action_labels','position_labels','uncertain','truncation_risk'}
REF_REQUIRED = {'private_sample_id','actionable','action_labels','position_labels'}
HOLDOUT_REQUIRED = {'holdout_version','private_sample_id','fragment_id','catalog_generation'}


def labs(value):
    return {x.strip() for x in (value or '').split(';') if x.strip()}


def load_rows(path: Path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def keyed(rows, key):
    out = {r[key]: r for r in rows}
    if len(out) != len(rows):
        raise SystemExit(f'duplicate {key}')
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_hex(value, n):
    return isinstance(value, str) and len(value) == n and all(c in '0123456789abcdef' for c in value.lower())


def div(a,b):
    return a/b if b else None


def flag(value, name):
    if str(value) not in {'0','1'}:
        raise SystemExit(f'{name} must be 0/1, got {value!r}')
    return int(value)


def binary_metrics(y, yp):
    tp=sum(a==1 and b==1 for a,b in zip(y,yp));tn=sum(a==0 and b==0 for a,b in zip(y,yp));fp=sum(a==0 and b==1 for a,b in zip(y,yp));fn=sum(a==1 and b==0 for a,b in zip(y,yp))
    sens=div(tp,tp+fn);spec=div(tn,tn+fp)
    return {'tp':tp,'tn':tn,'fp':fp,'fn':fn,'sensitivity':sens,'specificity':spec,'balanced_accuracy':None if sens is None or spec is None else (sens+spec)/2}


def multilabel_metrics(rows, field, labels):
    total_tp=total_fp=total_fn=0; per={}
    for label in labels:
        tp=fp=fn=0
        for human,pred in rows:
            a=label in labs(human[field]);b=label in labs(pred[field])
            tp+=a and b;fp+=(not a) and b;fn+=a and (not b)
        denom=2*tp+fp+fn;f1=0.0 if denom==0 else 2*tp/denom
        human_pos=tp+fn
        per[label]={'tp':tp,'fp':fp,'fn':fn,'human_positives':human_pos,'f1':f1}
        total_tp+=tp;total_fp+=fp;total_fn+=fn
    micro=0.0 if 2*total_tp+total_fp+total_fn==0 else 2*total_tp/(2*total_tp+total_fp+total_fn)
    return {'micro_f1':micro,'per_category':per}


def require_columns(rows, required, label):
    if not rows:
        raise SystemExit(f'{label} file empty')
    missing=required-set(rows[0])
    if missing:
        raise SystemExit(f'{label} file missing required columns: '+','.join(sorted(missing)))


def validate_gate(holdout_path: Path, commitment_path: Path, lock_path: Path):
    if not holdout_path.exists():
        raise SystemExit('private holdout manifest is required for final validation')
    if not commitment_path.exists():
        raise SystemExit('private holdout commitment is required before final validation')
    if not lock_path.exists():
        raise SystemExit('model must be locked before final validation')

    commitment=json.loads(commitment_path.read_text(encoding='utf-8'))
    lock=json.loads(lock_path.read_text(encoding='utf-8'))
    if commitment.get('commitment_version')!='SEMB03_PRIVATE_HOLDOUT_COMMITMENT_0.1':
        raise SystemExit('unexpected private holdout commitment version')
    if commitment.get('ids_public') is not False or commitment.get('legacy_sample_excluded') is not True:
        raise SystemExit('commitment does not establish a private legacy-excluding holdout')
    if commitment.get('holdout_n')!=160 or commitment.get('per_generation')!={'1972':40,'1988':40,'1993':40,'2014':40}:
        raise SystemExit('commitment must document 160 cases = 40 per generation')

    manifest_digest=sha256(holdout_path)
    commitment_digest=sha256(commitment_path)
    if not valid_hex(commitment.get('private_manifest_sha256'),64) or commitment['private_manifest_sha256']!=manifest_digest:
        raise SystemExit('private holdout manifest does not match the public commitment')
    if lock.get('lock_version')!='SEMB03_MODEL_LOCK_0.2':
        raise SystemExit('final validation requires SEMB03_MODEL_LOCK_0.2')
    if lock.get('legacy_public_holdout_admissible') is not False:
        raise SystemExit('model lock does not explicitly reject the legacy public holdout')
    if lock.get('locked_validation_accessed_before_lock') is not False:
        raise SystemExit('model lock does not establish pre-access locking')
    if lock.get('private_holdout_commitment_sha256')!=commitment_digest:
        raise SystemExit('model lock is not bound to this private holdout commitment')
    if lock.get('private_holdout_manifest_sha256')!=manifest_digest:
        raise SystemExit('model lock is not bound to this private holdout manifest')
    if lock.get('source_fragment_manifest_sha256')!=commitment.get('source_manifest_sha256'):
        raise SystemExit('model lock/source-manifest SHA mismatch')
    if lock.get('source_fragment_manifest_git_blob_sha')!=commitment.get('source_manifest_git_blob_sha'):
        raise SystemExit('model lock/source-manifest Git blob mismatch')

    rows=load_rows(holdout_path)
    require_columns(rows,HOLDOUT_REQUIRED,'private holdout')
    if len(rows)!=160:
        raise SystemExit(f'expected 160 private holdout rows, found {len(rows)}')
    if any(r['holdout_version']!=HOLDOUT_VERSION for r in rows):
        raise SystemExit('unexpected private holdout row version')
    if len({r['private_sample_id'] for r in rows})!=160 or len({r['fragment_id'] for r in rows})!=160:
        raise SystemExit('private holdout IDs must be unique')
    counts=Counter(r['catalog_generation'] for r in rows)
    if counts!=Counter({'1972':40,'1988':40,'1993':40,'2014':40}):
        raise SystemExit(f'private holdout generation imbalance: {dict(counts)}')

    if LEGACY.exists():
        legacy_ids={r['fragment_id'] for r in load_rows(LEGACY)}
        overlap=legacy_ids & {r['fragment_id'] for r in rows}
        if overlap:
            raise SystemExit(f'private holdout overlaps {len(overlap)} legacy public fragment IDs')
    return rows, commitment, lock, manifest_digest, commitment_digest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--predictions',required=True,type=Path)
    parser.add_argument('--reference',required=True,type=Path)
    parser.add_argument('--holdout-manifest',required=True,type=Path,help='private 160-row manifest; never commit before evaluation closes')
    parser.add_argument('--commitment',type=Path,default=COMMITMENT_DEFAULT)
    parser.add_argument('--lock',type=Path,default=LOCK_DEFAULT)
    parser.add_argument('--criteria',type=Path,default=CRIT_DEFAULT)
    parser.add_argument('--output',type=Path,default=OUT_DEFAULT)
    args=parser.parse_args()

    if args.output.exists():
        raise SystemExit('Locked validation result already exists; refusing a second look')

    holdout_rows,commitment,lock,manifest_digest,commitment_digest=validate_gate(args.holdout_manifest,args.commitment,args.lock)
    criteria=json.loads(args.criteria.read_text(encoding='utf-8'))
    if criteria.get('criteria_version')!='SEMB03_ACCEPTANCE_0.1':
        raise SystemExit('unexpected acceptance criteria version')

    pred_rows=load_rows(args.predictions);ref_rows=load_rows(args.reference)
    require_columns(pred_rows,PRED_REQUIRED,'prediction');require_columns(ref_rows,REF_REQUIRED,'reference')
    pred=keyed(pred_rows,'private_sample_id');ref=keyed(ref_rows,'private_sample_id');holdout=keyed(holdout_rows,'private_sample_id')
    expected=set(holdout)
    if set(pred)!=expected:
        raise SystemExit(f'prediction IDs must exactly match private holdout: missing={len(expected-set(pred))}, extra={len(set(pred)-expected)}')
    if set(ref)!=expected:
        raise SystemExit(f'reference IDs must exactly match private holdout: missing={len(expected-set(ref))}, extra={len(set(ref)-expected)}')

    usable=[sid for sid in expected if ref[sid].get('actionable') in {'0','1'}]
    y=[int(ref[s]['actionable']) for s in usable]
    try:yp=[int(pred[s]['actionable']) for s in usable]
    except Exception as exc:raise SystemExit('predicted actionable must be 0/1') from exc
    if any(x not in {0,1} for x in yp):raise SystemExit('predicted actionable must be 0/1')
    actionable=binary_metrics(y,yp)
    pairs=[(ref[s],pred[s]) for s in usable]
    act=multilabel_metrics(pairs,'action_labels',ACTIONS);pos=multilabel_metrics(pairs,'position_labels',POSITIONS)
    ca=criteria['locked_validation']

    def macro_block(metrics,conf):
        vals=[v['f1'] for v in metrics['per_category'].values() if v['human_positives']>=conf['macro_min_human_positives']]
        metrics['macro_f1']=sum(vals)/len(vals) if vals else None
        floors=[(k,v) for k,v in metrics['per_category'].items() if v['human_positives']>=conf['category_floor_min_human_positives'] and v['f1']<conf['category_f1_floor']]
        metrics['category_floor_failures']=[k for k,_ in floors]
    macro_block(act,ca['actions']);macro_block(pos,ca['positions'])

    uncertain={sid:flag(pred[sid]['uncertain'],f'{sid}.uncertain') for sid in expected}
    trunc={sid:flag(pred[sid]['truncation_risk'],f'{sid}.truncation_risk') for sid in expected}
    certain_rate=sum(1-uncertain[s] for s in expected)/len(expected)
    by_generation={}
    for generation in GENERATIONS:
        ids=[sid for sid,row in holdout.items() if row['catalog_generation']==generation]
        rate=sum(uncertain[s] for s in ids)/len(ids)
        by_generation[generation]={'n':len(ids),'uncertain_n':sum(uncertain[s] for s in ids),'uncertain_rate':rate,'certain_rate':1-rate,'truncation_risk_n':sum(trunc[s] for s in ids)}
    rates=[x['uncertain_rate'] for x in by_generation.values()]
    uncertainty_gap_pp=100*(max(rates)-min(rates));total_trunc=sum(trunc.values())
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
    result={
      'validation_version':VERSION,
      'model_lock_version':lock.get('lock_version'),
      'model_lock_git_head':lock.get('git_head'),
      'criteria_version':criteria['criteria_version'],
      'holdout_protocol':'replacement_private_committed',
      'private_manifest_sha256':manifest_digest,
      'holdout_commitment_sha256':commitment_digest,
      'locked_n':160,
      'usable_nonambiguous_n':len(usable),
      'actionable':actionable,'actions':act,'positions':pos,'coverage':coverage,
      'checks':checks,'passed':all(checks.values()),
      'legacy_public_holdout_used':False,
      'model_modified_after_opening_validation':False,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
