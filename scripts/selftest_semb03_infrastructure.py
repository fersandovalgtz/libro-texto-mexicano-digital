#!/usr/bin/env python3
"""Self-tests for SEMB 0.3 stage gates using temporary fake data only.

No fake annotation, private holdout, commitment, lock, prediction, reference, or
validation result is persisted as scientific evidence. The tests exercise schema
validation and the final one-shot private-holdout gate end to end.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MASTER=Path('data/validation/semb03_human_reference_sample.csv')
CRIT=Path('data/validation/semb03_acceptance_criteria.json')
GRID=Path('data/validation/semb03_candidate_grid.json')
LOCK_SCRIPT=Path('scripts/lock_semb03_model.py')
VAL_SCRIPT=Path('scripts/evaluate_semb03_locked_validation.py')
ANN_SCRIPT=Path('scripts/validate_semb03_annotations.py')
VERSION='SEMB03_SELFTEST_0.2'
GENERATIONS=('1972','1988','1993','2014')


def run(cmd,expect=0):
    cp=subprocess.run(cmd,text=True,capture_output=True)
    if cp.returncode!=expect:
        raise AssertionError(f'expected rc={expect}, got {cp.returncode}\nSTDOUT={cp.stdout}\nSTDERR={cp.stderr}')
    return cp


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path,fields,rows):
    with Path(path).open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(rows)


def main():
    master=list(csv.DictReader(MASTER.open(encoding='utf-8')));assert len(master)==480
    crit=json.load(CRIT.open(encoding='utf-8'));grid=json.load(GRID.open(encoding='utf-8'))
    assert crit['frozen_before_human_reference'] is True
    assert grid['frozen_before_human_reference'] is True
    assert grid['development_cv']=={'method':'GroupKFold','n_splits':5,'group':'page_id'}
    assert crit['locked_validation']['coverage']['certain_output_rate_min']==0.70
    assert crit['locked_validation']['coverage']['max_generation_uncertainty_gap_pp']==20.0

    # Validate two deliberately fake but schema-correct development annotations in temp only.
    ids=[master[0]['sample_id'],master[1]['sample_id']]
    fields=['sample_id','annotator_id','annotation_round','actionable','action_labels','position_labels','annotation_confidence','ambiguity_note']
    with tempfile.TemporaryDirectory(prefix='ltmd-selftest-') as td_name:
        td=Path(td_name)
        good=td/'good.csv';bad=td/'bad.csv'
        write_csv(good,fields,[
            {'sample_id':ids[0],'annotator_id':'FAKE_TEST','annotation_round':'0','actionable':'1','action_labels':'observe','position_labels':'observer','annotation_confidence':'3','ambiguity_note':''},
            {'sample_id':ids[1],'annotator_id':'FAKE_TEST','annotation_round':'0','actionable':'0','action_labels':'','position_labels':'receiver','annotation_confidence':'2','ambiguity_note':''},
        ])
        run([sys.executable,str(ANN_SCRIPT),str(good)],0)
        write_csv(bad,fields,[
            {'sample_id':ids[0],'annotator_id':'FAKE_TEST','annotation_round':'0','actionable':'0','action_labels':'observe','position_labels':'receiver','annotation_confidence':'3','ambiguity_note':''},
        ])
        cp=subprocess.run([sys.executable,str(ANN_SCRIPT),str(bad)],text=True,capture_output=True)
        assert cp.returncode!=0 and 'actionable=0 requires empty action_labels' in (cp.stdout+cp.stderr)

        # Build a completely fake private holdout and cryptographic gate in temp only.
        holdout=td/'holdout.csv';pred=td/'predictions.csv';ref=td/'reference.csv'
        commitment=td/'commitment.json';lock=td/'lock.json';result=td/'result.json'
        holdout_rows=[];pred_rows=[];ref_rows=[]
        counter=0
        for generation in GENERATIONS:
            for j in range(40):
                sid=f'FAKE-H-{counter:03d}'
                fid=f'FAKE-FRAGMENT-{generation}-{j:03d}'
                holdout_rows.append({'holdout_version':'SEMB03_PRIVATE_HOLDOUT_0.1','private_sample_id':sid,'fragment_id':fid,'catalog_generation':generation})
                actionable='1' if counter%2==0 else '0'
                actions='observe' if actionable=='1' else ''
                position='observer' if actionable=='1' else 'receiver'
                pred_rows.append({'private_sample_id':sid,'actionable':actionable,'action_labels':actions,'position_labels':position,'uncertain':'0','truncation_risk':'0'})
                ref_rows.append({'private_sample_id':sid,'actionable':actionable,'action_labels':actions,'position_labels':position})
                counter+=1
        write_csv(holdout,['holdout_version','private_sample_id','fragment_id','catalog_generation'],holdout_rows)
        write_csv(pred,['private_sample_id','actionable','action_labels','position_labels','uncertain','truncation_risk'],pred_rows)
        write_csv(ref,['private_sample_id','actionable','action_labels','position_labels'],ref_rows)
        manifest_sha=sha(holdout)
        commitment_obj={
            'commitment_version':'SEMB03_PRIVATE_HOLDOUT_COMMITMENT_0.1',
            'holdout_n':160,
            'per_generation':{'1972':40,'1988':40,'1993':40,'2014':40},
            'legacy_sample_excluded':True,
            'ids_public':False,
            'private_manifest_sha256':manifest_sha,
            'source_manifest_sha256':'a'*64,
            'source_manifest_git_blob_sha':'b'*40,
        }
        commitment.write_text(json.dumps(commitment_obj,sort_keys=True)+'\n',encoding='utf-8')
        lock_obj={
            'lock_version':'SEMB03_MODEL_LOCK_0.2',
            'git_head':'FAKE',
            'private_holdout_commitment_sha256':sha(commitment),
            'private_holdout_manifest_sha256':manifest_sha,
            'source_fragment_manifest_sha256':'a'*64,
            'source_fragment_manifest_git_blob_sha':'b'*40,
            'legacy_public_holdout_admissible':False,
            'locked_validation_accessed_before_lock':False,
        }
        lock.write_text(json.dumps(lock_obj,sort_keys=True)+'\n',encoding='utf-8')
        run([
            sys.executable,str(VAL_SCRIPT),
            '--predictions',str(pred),'--reference',str(ref),'--holdout-manifest',str(holdout),
            '--commitment',str(commitment),'--lock',str(lock),'--output',str(result),
        ],0)
        evaluated=json.loads(result.read_text(encoding='utf-8'))
        assert evaluated['passed'] is True
        assert evaluated['locked_n']==160
        assert evaluated['holdout_protocol']=='replacement_private_committed'
        assert evaluated['legacy_public_holdout_used'] is False
        rendered=result.read_text(encoding='utf-8')
        assert 'private_sample_id' not in rendered and 'fragment_id' not in rendered
        second=subprocess.run([
            sys.executable,str(VAL_SCRIPT),
            '--predictions',str(pred),'--reference',str(ref),'--holdout-manifest',str(holdout),
            '--commitment',str(commitment),'--lock',str(lock),'--output',str(result),
        ],text=True,capture_output=True)
        assert second.returncode!=0 and 'refusing a second look' in (second.stdout+second.stderr)

    lock_text=LOCK_SCRIPT.read_text(encoding='utf-8');val_text=VAL_SCRIPT.read_text(encoding='utf-8')
    assert 'legacy_public_holdout_admissible' in lock_text
    assert 'private_holdout_commitment_sha256' in lock_text
    assert 'private holdout manifest does not match the public commitment' in val_text
    assert 'legacy public fragment IDs' in val_text

    print(json.dumps({
        'selftest_version':VERSION,
        'passed':True,
        'fake_artifacts_persisted':False,
        'legacy_master_n':len(master),
        'private_holdout_gate_tested_n':160,
    },ensure_ascii=False))


if __name__=='__main__':main()
