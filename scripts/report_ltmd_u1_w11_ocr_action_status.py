#!/usr/bin/env python3
"""Publish an observational status report for W11 OCR GitHub Actions runs."""
from __future__ import annotations
import json,os,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

REPORT=Path('docs/LTMD_U1_W11_OCR_RUN_STATUS.md');JSON_OUT=Path('data/catalog/ltmd_u1_w11_ocr_run_status.json')
VERSION='LTMD_U1_W11_OCR_RUN_STATUS_0.3';WORKFLOW='build-ltmd-u1-w11-ocr.yml';API='https://api.github.com';EXPECTED_MATRIX=106

def api(path,token,params=None,attempts=3):
    url=API+path+('?' + urlencode(params) if params else '');last=''
    for attempt in range(1,attempts+1):
        try:
            req=Request(url,headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'LTMD-W11-status-reporter/0.3'})
            with urlopen(req,timeout=30) as r:return json.loads(r.read().decode())
        except (HTTPError,URLError,TimeoutError,OSError,json.JSONDecodeError) as exc:
            last=f'{type(exc).__name__}: {exc}'
            if attempt<attempts:time.sleep(attempt)
    raise RuntimeError(f'GitHub API failed for {path}: {last}')

def jobs_for_run(repo,run_id,token):
    jobs=[];page=1
    while True:
        batch=api(f'/repos/{repo}/actions/runs/{run_id}/jobs',token,{'per_page':100,'page':page}).get('jobs',[]);jobs+=batch
        if len(batch)<100:break
        page+=1
    return jobs

def matrix_jobs(jobs):
    direct=[j for j in jobs if j.get('name','').startswith('ocr (') or j.get('name','').startswith('ocr /') or j.get('name','')=='ocr']
    return direct or [j for j in jobs if j.get('name') not in {'matrix','combine'}]

def main():
    repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GITHUB_TOKEN'];observed=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    runs=api(f'/repos/{repo}/actions/workflows/{WORKFLOW}/runs',token,{'per_page':10}).get('workflow_runs',[])
    if not runs:raise SystemExit('no W11 OCR workflow runs found')
    active=[r for r in runs if r.get('status')!='completed'];inspected=[]
    for r in active[:5]:
        jj=jobs_for_run(repo,int(r['id']),token);inspected.append((r,jj,len(matrix_jobs(jj))))
    selected,jobs,_=max(inspected,key=lambda x:(x[2],len(x[1]),-int(x[0]['id']))) if inspected else (runs[0],jobs_for_run(repo,int(runs[0]['id']),token),0)
    matrix=matrix_jobs(jobs);status=Counter(j.get('status') or 'unknown' for j in jobs);conclusion=Counter(j.get('conclusion') or 'pending' for j in jobs);mc=Counter(j.get('conclusion') or 'pending' for j in matrix)
    success=[j for j in matrix if j.get('conclusion')=='success'];failed=[j for j in matrix if j.get('conclusion')=='failure'];cancelled=[j for j in matrix if j.get('conclusion')=='cancelled'];active_matrix=[j for j in matrix if j.get('status')!='completed']
    if len(matrix) not in {0,EXPECTED_MATRIX}:raise SystemExit(f'unexpected materialized matrix cardinality {len(matrix)}')
    pct=100*len(success)/EXPECTED_MATRIX
    summary={'report_version':VERSION,'observed_at_utc':observed,'repository':repo,'workflow':WORKFLOW,'selected_run_id':selected['id'],'status':selected.get('status',''),'conclusion':selected.get('conclusion'),'head_sha':selected.get('head_sha',''),'matrix_expected':EXPECTED_MATRIX,'matrix_jobs_detected':len(matrix),'matrix_success':len(success),'matrix_failure':len(failed),'matrix_cancelled':len(cancelled),'matrix_active':len(active_matrix),'progress_percent':round(pct,2),'failed_jobs':[j.get('name','') for j in failed],'cancelled_jobs':[j.get('name','') for j in cancelled],'job_status_counts':dict(status),'matrix_conclusion_counts':dict(mc),'active_runs_inspected':[{'id':r['id'],'status':r.get('status',''),'jobs':len(jj),'matrix_jobs':m} for r,jj,m in inspected],'recent_runs':[{'id':r['id'],'event':r.get('event',''),'status':r.get('status',''),'conclusion':r.get('conclusion'),'head_sha':r.get('head_sha',''),'created_at':r.get('created_at','')} for r in runs[:5]]}
    JSON_OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# LTMD-U1 W11 — estado operativo del OCR','',f'Versión: `{VERSION}`. Observado: **{observed}**.','', '> Estado operativo solamente; G5 cierra únicamente con el OCR consolidado validado.','',f'- Run con matriz: **{selected["id"]}**.',f'- Matriz: **{len(matrix)}/{EXPECTED_MATRIX}** jobs.',f'- Exitosos: **{len(success)}/{EXPECTED_MATRIX} ({pct:.2f}%)**.',f'- Fallidos: **{len(failed)}**.',f'- Cancelados: **{len(cancelled)}**.',f'- Aún no completados: **{len(active_matrix)}**.','','## Estado global de jobs']
    for k,n in sorted(status.items()):lines.append(f'- `{k}`: **{n}**.')
    if failed:
        lines+=['','## Jobs fallidos'];lines += [f'- `{j.get("name","")}`.' for j in failed]
    lines+=['','## Runs activos inspeccionados','','| run | estado API | jobs | OCR |','|---:|---|---:|---:|']
    for r,jj,m in inspected:lines.append(f"| {r['id']} | `{r.get('status','')}` | {len(jj)} | {m} |")
    lines+=['','## Regla','No se mezclan shards entre runs. El porcentaje indica jobs terminados con éxito, no páginas ni cobertura científica. Sólo el combine del mismo run puede demostrar 19,862/19,862 páginas, SHA verificado y cero `unresolved`.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
