#!/usr/bin/env python3
"""Publish an observational status report for W11 OCR GitHub Actions runs.

The reporter never dispatches, cancels, or reruns OCR. When several runs exist
because of the concurrency queue, it selects the active run with the largest
materialized job set, rather than merely the newest pending run.
"""
from __future__ import annotations
import json,os,time
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

REPORT=Path('docs/LTMD_U1_W11_OCR_RUN_STATUS.md')
JSON_OUT=Path('data/catalog/ltmd_u1_w11_ocr_run_status.json')
VERSION='LTMD_U1_W11_OCR_RUN_STATUS_0.2'
WORKFLOW='build-ltmd-u1-w11-ocr.yml'
API='https://api.github.com'

def api(path:str,token:str,params:dict|None=None,attempts:int=3):
    url=API+path
    if params:url+='?'+urlencode(params)
    last=''
    for attempt in range(1,attempts+1):
        try:
            req=Request(url,headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'LTMD-W11-status-reporter/0.2'})
            with urlopen(req,timeout=30) as r:return json.loads(r.read().decode('utf-8'))
        except (HTTPError,URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:
            last=f'{type(exc).__name__}: {exc}'
            if attempt<attempts:time.sleep(attempt)
    raise RuntimeError(f'GitHub API failed for {path}: {last}')

def jobs_for_run(repo:str,run_id:int,token:str):
    jobs=[];page=1
    while True:
        data=api(f'/repos/{repo}/actions/runs/{run_id}/jobs',token,{'per_page':100,'page':page})
        batch=data.get('jobs',[]);jobs.extend(batch)
        if len(batch)<100:break
        page+=1
        if page>10:raise RuntimeError('unexpected W11 OCR job pagination > 1000 jobs')
    return jobs

def matrix_jobs(jobs):
    direct=[j for j in jobs if j.get('name','').startswith('ocr (') or j.get('name','').startswith('ocr /') or j.get('name','')=='ocr']
    if direct:return direct
    return [j for j in jobs if j.get('name') not in {'matrix','combine'}]

def main():
    repo=os.environ.get('GITHUB_REPOSITORY','').strip();token=os.environ.get('GITHUB_TOKEN','').strip()
    if not repo or not token:raise SystemExit('GITHUB_REPOSITORY/GITHUB_TOKEN required')
    data=api(f'/repos/{repo}/actions/workflows/{WORKFLOW}/runs',token,{'per_page':10})
    runs=data.get('workflow_runs',[])
    if not runs:raise SystemExit('no W11 OCR workflow runs found')
    active=[r for r in runs if r.get('status')!='completed']
    inspected=[]
    for r in active[:5]:
        jj=jobs_for_run(repo,int(r['id']),token);inspected.append((r,jj,len(matrix_jobs(jj))))
    if inspected:
        selected,jobs,_=max(inspected,key=lambda x:(x[2],len(x[1]),-int(x[0]['id'])))
    else:
        selected=runs[0];jobs=jobs_for_run(repo,int(selected['id']),token)
    status=Counter((j.get('status') or 'unknown') for j in jobs)
    conclusion=Counter((j.get('conclusion') or 'pending') for j in jobs)
    matrix=matrix_jobs(jobs);matrix_status=Counter((j.get('status') or 'unknown') for j in matrix);matrix_conclusion=Counter((j.get('conclusion') or 'pending') for j in matrix)
    succeeded=sum(j.get('conclusion')=='success' for j in matrix);failed=sum(j.get('conclusion')=='failure' for j in matrix);cancelled=sum(j.get('conclusion')=='cancelled' for j in matrix);active_matrix=sum(j.get('status')!='completed' for j in matrix)
    summary={'report_version':VERSION,'repository':repo,'workflow':WORKFLOW,'selected_run_id':selected['id'],'html_url':selected.get('html_url',''),'event':selected.get('event',''),'status':selected.get('status',''),'conclusion':selected.get('conclusion'),'head_sha':selected.get('head_sha',''),'created_at':selected.get('created_at',''),'updated_at':selected.get('updated_at',''),'jobs_total':len(jobs),'job_status_counts':dict(status),'job_conclusion_counts':dict(conclusion),'matrix_jobs_detected':len(matrix),'matrix_success':succeeded,'matrix_failure':failed,'matrix_cancelled':cancelled,'matrix_active':active_matrix,'matrix_status_counts':dict(matrix_status),'matrix_conclusion_counts':dict(matrix_conclusion),'active_runs_inspected':[{'id':r['id'],'status':r.get('status',''),'jobs':len(jj),'matrix_jobs':m} for r,jj,m in inspected],'recent_runs':[{'id':r['id'],'event':r.get('event',''),'status':r.get('status',''),'conclusion':r.get('conclusion'),'head_sha':r.get('head_sha',''),'created_at':r.get('created_at',''),'updated_at':r.get('updated_at',''),'html_url':r.get('html_url','')} for r in runs[:5]]}
    JSON_OUT.parent.mkdir(parents=True,exist_ok=True);JSON_OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# LTMD-U1 W11 — estado operativo del OCR','',f'Versión del reporte: `{VERSION}`.','', '> Este documento observa GitHub Actions. **No es evidencia de cierre científico**; G5 sólo cierra con `docs/LTMD_U1_W11_OCR.md` validado.','', '## Run con matriz materializada','',f'- Run ID: **{selected["id"]}**.',f'- Evento: `{selected.get("event","")}`.',f'- Estado reportado por Actions: `{selected.get("status","")}`.',f'- Conclusión: `{selected.get("conclusion") or "pendiente"}`.',f'- Head SHA: `{selected.get("head_sha","")}`.',f'- Jobs observados: **{len(jobs)}**.',f'- Jobs de matriz OCR detectados: **{len(matrix)}**.',f'- OCR exitosos: **{succeeded}**.',f'- OCR fallidos: **{failed}**.',f'- OCR cancelados: **{cancelled}**.',f'- OCR aún no completados: **{active_matrix}**.','','### Estados de jobs']
    for k,n in sorted(status.items()):lines.append(f'- `{k}`: **{n}**.')
    lines+=['','### Conclusiones de la matriz OCR']
    for k,n in sorted(matrix_conclusion.items()):lines.append(f'- `{k}`: **{n}**.')
    if inspected:
        lines+=['','## Runs activos inspeccionados','','| run | estado API | jobs | jobs OCR |','|---:|---|---:|---:|']
        for r,jj,m in inspected:lines.append(f"| {r['id']} | `{r.get('status','')}` | {len(jj)} | {m} |")
    lines+=['','## Runs recientes','','| run | evento | estado | conclusión | head | creado |','|---:|---|---|---|---|---|']
    for r in runs[:5]:lines.append(f"| {r['id']} | `{r.get('event','')}` | `{r.get('status','')}` | `{r.get('conclusion') or 'pendiente'}` | `{r.get('head_sha','')[:12]}` | {r.get('created_at','')} |")
    lines+=['','## Regla','Los artefactos de jobs exitosos permanecen subordinados al combine del mismo run. No se mezclan shards de runs diferentes. Un run `success` sólo promueve G5 después de que el combiner demuestre cobertura exacta de los 106 canónicos/19,862 páginas, SHA-256 verificado y cero `unresolved`.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
