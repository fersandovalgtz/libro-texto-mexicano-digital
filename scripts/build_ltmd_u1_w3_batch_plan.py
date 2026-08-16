#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

INV=Path('data/catalog/ltmd_u1_w3_declared_inventory.csv')
OUT=Path('data/catalog/ltmd_u1_w3_batch_plan.csv')
REPORT=Path('data/catalog/ltmd_u1_w3_batch_plan.md')
VERSION='LTMD_U1_W3_BATCH_PLAN_0.1'
MAX_POSITIONS=2500
EXPECTED_VIEWERS=130

def main():
    rows=list(csv.DictReader(INV.open(encoding='utf-8',newline='')))
    if len(rows)!=EXPECTED_VIEWERS:raise SystemExit(f'expected {EXPECTED_VIEWERS} W3 viewers, got {len(rows)}')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    out=[];batch_no=0
    for gen in sorted({r['catalog_generation'] for r in rows},key=int):
        group=[r for r in rows if r['catalog_generation']==gen]
        cur=[];cur_n=0;gen_batch=0
        def flush():
            nonlocal batch_no,gen_batch,cur,cur_n
            if not cur:return
            batch_no+=1;gen_batch+=1;bid=f'W3-G{gen}-B{gen_batch:02d}'
            for seq,r in enumerate(cur,1):
                out.append({'batch_plan_version':VERSION,'batch_id':bid,'batch_global_order':batch_no,'catalog_generation':gen,'batch_sequence':seq,'viewer_key':r['viewer_key'],'grade_code':r['grade_code'],'title_core':r['title_core'],'declared_positions':r['declared_positions'],'batch_declared_positions':cur_n,'source_url':r['source_url']})
            cur=[];cur_n=0
        for r in group:
            n=int(r['declared_positions'])
            if cur and cur_n+n>MAX_POSITIONS:flush()
            cur.append(r);cur_n+=n
        flush()
    if len(out)!=EXPECTED_VIEWERS or len({r['viewer_key'] for r in out})!=EXPECTED_VIEWERS:raise SystemExit('batch plan coverage mismatch')
    fields=list(out[0])
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    batches=[]
    for bid in dict.fromkeys(r['batch_id'] for r in out):
        rr=[r for r in out if r['batch_id']==bid]
        batches.append((bid,rr[0]['catalog_generation'],len(rr),int(rr[0]['batch_declared_positions'])))
    lines=['# LTMD-U1 W3 — plan determinista de batches','',f'Versión: `{VERSION}`.','',f'- Visores: **{EXPECTED_VIEWERS}**.',f'- Techo operativo por batch: **{MAX_POSITIONS:,} posiciones declaradas**.',f'- Batches: **{len(batches)}**.','','| batch | generación | visores | posiciones declaradas |','|---|---:|---:|---:|']
    for bid,g,n,p in batches:lines.append(f'| {bid} | {g} | {n} | {p:,} |')
    lines+=['','Los batches no mezclan generaciones. La partición es logística y reproducible; no modifica el denominador W3 ni implica independencia histórica entre visores. Las auditorías de alias/dependencia deberán realizarse antes de OCR productivo.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
