#!/usr/bin/env python3
"""Publish an observational status report for the W11 OCR GitHub Actions runs.

This script queries GitHub Actions metadata only. It never dispatches, cancels,
reruns, or mutates OCR jobs. It is intended to make long matrix execution
observable without confusing run state with scientific completion.
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
VERSION='LTMD_U1_W11_OCR_RUN_STATUS_0.1'
WORKFLOW='build-ltmd-u1-w11-ocr.yml'
API='https://api.github.com'

def api(path:str,token:str,params:dict|None=None,attempts:int=3):
    url=API+path
    if params:url+='?'+urlencode(params)
    last=''
    for attempt in range(1,attempts+1):
        try:
            req=Request(url,headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'LTMD-W11-status-reporter/0.1'})
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

def main():
    repo=os.environ.get('GITHUB_REPOSITORY','').strip();token=os.environ.get('GITHUB_TOKEN','').strip()
    if not repo or not token:raise SystemExit('GITHUB_REPOSITORY/GITHUB_TOKEN required')
    data=api(f'/repos/{repo}/actions/workflows/{WORKFLOW}/runs',token,{'per_page':10})
    runs=data.get('workflow_runs',[])
    if not runs:raise SystemExit('no W11 OCR workflow runs found')
    # Prefer an active run; otherwise inspect the newest run.
    active=[r for r in runs if r.get('status')!='completed']
    selected=(active[0] if active else runs[0])
    jobs=jobs_for_run(repo,int(selected['id']),token)
    status=Counter((j.get('status') or 'unknown') for j in jobs)
    conclusion=Counter((j.get('conclusion') or 'pending') for j in jobs)
    matrix=[j for j in jobs if j.get('name','').startswith('ocr (') or j.get('name','').startswith('ocr /') or j.get('name','')=='ocr']
    # Matrix naming differs slightly by Actions UI/API versions, so if no direct
    # name match is available classify all jobs except known orchestration jobs.
    if not matrix:
        matrix=[j for j in jobs if j.get('name') not in {'matrix','combine'}]
    matrix_status=Counter((j.get('status') or 'unknown') for j in matrix)
    matrix_conclusion=Counter((j.get('conclusion') or 'pending') for j in matrix)
    summary={
        'report_version':VERSION,'repository':repo,'workflow':WORKFLOW,
        'selected_run_id':selected['id'],'html_url':selected.get('html_url',''),
        'event':selected.get('event',''),'status':selected.get('status',''),
        'conclusion':selected.get('conclusion'),'head_sha':selected.get('head_sha',''),
        'created_at':selected.get('created_at',''),'updated_at':selected.get('updated_at',''),
        'jobs_total':len(jobs),'job_status_counts':dict(status),'job_conclusion_counts':dict(conclusion),
        'matrix_jobs_detected':len(matrix),'matrix_status_counts':dict(matrix_status),'matrix_conclusion_counts':dict(matrix_conclusion),
        'recent_runs':[{'id':r['id'],'event':r.get('event',''),'status':r.get('status',''),'conclusion':r.get('conclusion'),'head_sha':r.get('head_sha',''),'created_at':r.get('created_at',''),'updated_at':r.get('updated_at',''),'html_url':r.get('html_url','')} for r in runs[:5]],
    }
    JSON_OUT.parent.mkdir(parents=True,exist_ok=True);JSON_OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# LTMD-U1 W11 — estado operativo del OCR','',f'Versión del reporte: `{VERSION}`.','',
           '> Este documento observa GitHub Actions. **No es evidencia de cierre científico**; el único gate de G5 sigue siendo `docs/LTMD_U1_W11_OCR.md` validado.','',
           '## Run seleccionado','',f'- Run ID: **{selected["id"]}**.',f'- Evento: `{selected.get("event","")}`.',f'- Estado: `{selected.get("status","")}`.',f'- Conclusión: `{selected.get("conclusion") or "pendiente"}`.',f'- Head SHA: `{selected.get("head_sha","")}`.',f'- Creado: `{selected.get("created_at","")}`.',f'- Actualizado: `{selected.get("updated_at","")}`.',f'- Jobs observados: **{len(jobs)}**.',f'- Jobs de matriz OCR detectados: **{len(matrix)}**.','','### Estados de jobs']
    for k,n in sorted(status.items()):lines.append(f'- `{k}`: **{n}**.')
    lines+=['','### Conclusiones de jobs']
    for k,n in sorted(conclusion.items()):lines.append(f'- `{k}`: **{n}**.')
    lines+=['','### Matriz OCR — estado']
    for k,n in sorted(matrix_status.items()):lines.append(f'- `{k}`: **{n}**.')
    lines+=['','### Matriz OCR — conclusión']
    for k,n in sorted(matrix_conclusion.items()):lines.append(f'- `{k}`: **{n}**.')
    lines+=['','## Runs recientes','','| run | evento | estado | conclusión | head | creado |','|---:|---|---|---|---|---|']
    for r in runs[:5]:lines.append(f"| {r['id']} | `{r.get('event','')}` | `{r.get('status','')}` | `{r.get('conclusion') or 'pendiente'}` | `{r.get('head_sha','')[:12]}` | {r.get('created_at','')} |")
    lines+=['','## Regla','Un run `completed/success` no promueve G5 por sí solo: debe existir el artefacto consolidado de OCR con cobertura exacta de los canónicos, SHA-256 verificado y cero `unresolved`. Un run fallido se diagnostica por job; no se reejecuta automáticamente desde este reporte.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
