#!/usr/bin/env python3
"""Observe the W11 downstream GitHub Actions chain without mutating it."""
from __future__ import annotations
import json,os,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

VERSION='LTMD_U1_W11_PIPELINE_STATUS_0.2'
API='https://api.github.com'
WORKFLOWS=[
 ('G5 OCR','build-ltmd-u1-w11-ocr.yml'),
 ('G6 PAGESTRUCT','build-ltmd-u1-w11-pagestruct.yml'),
 ('G6 FRAGSEG','build-ltmd-u1-w11-fragseg.yml'),
 ('G6 exact reuse','build-ltmd-u1-w11-exact-reuse.yml'),
 ('G7 completion','build-ltmd-u1-w11-completion.yml'),
]
REPORT=Path('docs/LTMD_U1_W11_PIPELINE_STATUS.md')
JSON_OUT=Path('data/catalog/ltmd_u1_w11_pipeline_status.json')

def api(path,token,params=None,attempts=3):
    url=API+path+('?' + urlencode(params) if params else '');last=''
    for attempt in range(1,attempts+1):
        try:
            req=Request(url,headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'LTMD-W11-pipeline-observer/0.2'})
            with urlopen(req,timeout=30) as r:return json.loads(r.read().decode())
        except (HTTPError,URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:
            last=f'{type(exc).__name__}: {exc}'
            if attempt<attempts:time.sleep(attempt)
    raise RuntimeError(f'GitHub API failed for {path}: {last}')

def jobs(repo,run_id,token):
    out=[];page=1
    while True:
        batch=api(f'/repos/{repo}/actions/runs/{run_id}/jobs',token,{'per_page':100,'page':page}).get('jobs',[]);out+=batch
        if len(batch)<100:break
        page+=1
        if page>20:raise RuntimeError('unexpected workflow job pagination >2000')
    return out

def main():
    repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GITHUB_TOKEN'];observed=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    observer_run=os.environ.get('GITHUB_RUN_ID','');observer_job=os.environ.get('OBSERVER_JOB_ID','')
    rows=[]
    for gate,wf in WORKFLOWS:
        data=api(f'/repos/{repo}/actions/workflows/{wf}/runs',token,{'per_page':10})
        runs=data.get('workflow_runs',[])
        if not runs:
            rows.append({'gate':gate,'workflow':wf,'run_id':'','event':'','status':'not_started','conclusion':'','head_sha':'','jobs':0,'jobs_completed':0,'jobs_success':0,'jobs_in_progress':0,'jobs_queued':0,'job_failures':0,'job_cancelled':0,'updated_at':''});continue
        # Prefer an active/materialized run over a newer no-op or queued shell.
        candidates=[]
        for r in runs[:5]:
            jj=jobs(repo,int(r['id']),token)
            active_weight=sum(j.get('status') in {'queued','in_progress'} for j in jj)
            work_weight=max(0,len(jj)-2)
            candidates.append((active_weight>0,work_weight,len(jj),int(r['id']),r,jj))
        _,_,_,_,r,jj=max(candidates,key=lambda x:(x[0],x[1],x[2],x[3]))
        status=Counter(j.get('status') or 'unknown' for j in jj);concl=Counter(j.get('conclusion') or 'pending' for j in jj)
        rows.append({'gate':gate,'workflow':wf,'run_id':r['id'],'event':r.get('event',''),'status':r.get('status',''),'conclusion':r.get('conclusion') or '','head_sha':r.get('head_sha',''),'jobs':len(jj),'jobs_completed':status['completed'],'jobs_success':concl['success'],'jobs_in_progress':status['in_progress'],'jobs_queued':status['queued'],'job_failures':concl['failure'],'job_cancelled':concl['cancelled'],'updated_at':r.get('updated_at','')})
    payload={'report_version':VERSION,'observed_at_utc':observed,'repository':repo,'observer_run_id':observer_run,'observer_job_id':observer_job,'stages':rows}
    JSON_OUT.parent.mkdir(parents=True,exist_ok=True);JSON_OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# LTMD-U1 W11 — estado operativo de la cadena downstream','',f'Versión: `{VERSION}`. Observado: **{observed}**.','',
      '> Observación operativa; no sustituye los reportes científicos de cada compuerta.','',
      f'- Run observador: **{observer_run or "—"}**; job observador: **{observer_job or "—"}**.','',
      '| etapa | run | estado API | conclusión | jobs | éxito | en curso | cola | fallos |','|---|---:|---|---|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['gate']} | {r['run_id'] or '—'} | `{r['status']}` | `{r['conclusion'] or 'pendiente'}` | {r['jobs']} | {r['jobs_success']} | {r['jobs_in_progress']} | {r['jobs_queued']} | {r['job_failures']} |")
    lines += ['','## Regla','',
      'El observador selecciona el run con trabajo materializado cuando coexist(en) shells/no-op más nuevos. Un estado `success` sólo indica que Actions terminó el workflow. El cierre científico requiere que el artefacto final de la etapa exista y pase verificaciones de cardinalidad, procedencia, hashes y estados.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
