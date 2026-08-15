#!/usr/bin/env python3
"""Lightweight self-tests for SEMB 0.3 infrastructure using fake temporary data.

No fake annotation is persisted or treated as scientific reference. The tests
exercise schema validation and static stage-gate invariants only.
"""
from __future__ import annotations
import csv,json,subprocess,sys,tempfile
from pathlib import Path

MASTER=Path('data/validation/semb03_human_reference_sample.csv')
CRIT=Path('data/validation/semb03_acceptance_criteria.json')
GRID=Path('data/validation/semb03_candidate_grid.json')
LOCK_SCRIPT=Path('scripts/lock_semb03_model.py')
VAL_SCRIPT=Path('scripts/evaluate_semb03_locked_validation.py')
ANN_SCRIPT=Path('scripts/validate_semb03_annotations.py')
VERSION='SEMB03_SELFTEST_0.1'

def run(cmd,expect=0):
    cp=subprocess.run(cmd,text=True,capture_output=True)
    if cp.returncode!=expect:
        raise AssertionError(f'expected rc={expect}, got {cp.returncode}\nSTDOUT={cp.stdout}\nSTDERR={cp.stderr}')
    return cp

def main():
    master=list(csv.DictReader(MASTER.open(encoding='utf-8')));assert len(master)==480
    crit=json.load(CRIT.open(encoding='utf-8'));grid=json.load(GRID.open(encoding='utf-8'))
    assert crit['frozen_before_human_reference'] is True
    assert grid['frozen_before_human_reference'] is True
    assert grid['development_cv']=={'method':'GroupKFold','n_splits':5,'group':'page_id'}
    assert crit['locked_validation']['coverage']['certain_output_rate_min']==0.70
    assert crit['locked_validation']['coverage']['max_generation_uncertainty_gap_pp']==20.0

    # Validate two deliberately fake but schema-correct annotations in temp only.
    ids=[master[0]['sample_id'],master[1]['sample_id']]
    fields=['sample_id','annotator_id','annotation_round','actionable','action_labels','position_labels','annotation_confidence','ambiguity_note']
    with tempfile.TemporaryDirectory(prefix='ltmd-selftest-') as td:
        good=Path(td)/'good.csv';bad=Path(td)/'bad.csv'
        with good.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();
            w.writerow({'sample_id':ids[0],'annotator_id':'FAKE_TEST','annotation_round':'0','actionable':'1','action_labels':'observe','position_labels':'observer','annotation_confidence':'3','ambiguity_note':''})
            w.writerow({'sample_id':ids[1],'annotator_id':'FAKE_TEST','annotation_round':'0','actionable':'0','action_labels':'','position_labels':'receiver','annotation_confidence':'2','ambiguity_note':''})
        run([sys.executable,str(ANN_SCRIPT),str(good)],0)
        with bad.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();
            w.writerow({'sample_id':ids[0],'annotator_id':'FAKE_TEST','annotation_round':'0','actionable':'0','action_labels':'observe','position_labels':'receiver','annotation_confidence':'3','ambiguity_note':''})
        cp=subprocess.run([sys.executable,str(ANN_SCRIPT),str(bad)],text=True,capture_output=True)
        assert cp.returncode!=0 and 'actionable=0 requires empty action_labels' in (cp.stdout+cp.stderr)

    lock_text=LOCK_SCRIPT.read_text(encoding='utf-8');val_text=VAL_SCRIPT.read_text(encoding='utf-8')
    assert 'refusing overwrite' in lock_text and 'locked_validation_accessed' in lock_text
    assert 'refusing a second look' in val_text
    assert "'uncertain'" in val_text and "'truncation_risk'" in val_text
    assert 'generation_uncertainty_gap' in val_text and 'certain_output_rate' in val_text

    print(json.dumps({'selftest_version':VERSION,'passed':True,'fake_annotations_persisted':False,'master_n':len(master)},ensure_ascii=False))

if __name__=='__main__':main()
