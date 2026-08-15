#!/usr/bin/env python3
"""Freeze a SEMB 0.3 candidate before locked validation is opened.

The lock records cryptographic hashes of the development result, configuration,
executable code and preregistered acceptance criteria. It refuses to overwrite a
lock or to run after a locked-validation result exists.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path

OUT=Path('data/validation/semb03_model_lock.json')
CRIT=Path('data/validation/semb03_acceptance_criteria.json')
LOCKED_RESULT=Path('data/validation/semb03_locked_validation_result.json')
VERSION='SEMB03_MODEL_LOCK_0.1'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def git_head():
    try:return subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    except Exception:return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--development-result',required=True);ap.add_argument('--config',required=True);ap.add_argument('--code',nargs='+',required=True);ap.add_argument('--model-name',required=True);ap.add_argument('--model-revision',required=True);args=ap.parse_args()
    if OUT.exists():raise SystemExit('Model lock already exists; refusing overwrite')
    if LOCKED_RESULT.exists():raise SystemExit('Locked validation result already exists; cannot create a retroactive lock')
    dev=Path(args.development_result);cfg=Path(args.config)
    for p in [dev,cfg,CRIT,*map(Path,args.code)]:
        if not p.exists():raise SystemExit(f'missing lock input: {p}')
    d=json.load(dev.open(encoding='utf-8'))
    if int(d.get('development_n',-1))!=320:raise SystemExit('development_result must document development_n=320')
    if d.get('locked_validation_accessed') is not False:raise SystemExit('development_result must assert locked_validation_accessed=false')
    criteria=json.load(CRIT.open(encoding='utf-8'))
    if criteria.get('criteria_version')!='SEMB03_ACCEPTANCE_0.1':raise SystemExit('unexpected acceptance criteria version')
    lock={
      'lock_version':VERSION,
      'created_utc':datetime.now(timezone.utc).isoformat(),
      'git_head':git_head(),
      'model_name':args.model_name,'model_revision':args.model_revision,
      'development_result':str(dev),'development_result_sha256':sha(dev),
      'config':str(cfg),'config_sha256':sha(cfg),
      'code_files':[{'path':str(Path(p)),'sha256':sha(p)} for p in args.code],
      'acceptance_criteria':str(CRIT),'acceptance_criteria_sha256':sha(CRIT),
      'acceptance_criteria_version':criteria['criteria_version'],
      'locked_validation_accessed_before_lock':False,
      'historical_outputs_used_for_selection':False,
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    json.dump(lock,OUT.open('w',encoding='utf-8'),ensure_ascii=False,indent=2)
    print(json.dumps(lock,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
