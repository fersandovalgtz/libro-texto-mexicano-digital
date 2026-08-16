#!/usr/bin/env python3
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

SRC=Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv')
REC=Path('data/catalog/ltmd_u1_w2_math_internal_recoveries.csv')
OUT=Path('data/catalog/ltmd_u1_w2_math_reconciled_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w2_math_reconciled_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w2_math_reconciled_manifest.md')
VERSION='LTMD_U1_W2_MATH_RECONCILED_0.1'
EXPECTED_VIEWERS=64
EXPECTED_RECOVERIES=2


def main():
    with REC.open(encoding='utf-8',newline='') as f:
        recs=list(csv.DictReader(f))
    if len(recs)!=EXPECTED_RECOVERIES:
        raise SystemExit(f'expected {EXPECTED_RECOVERIES} recoveries, got {len(recs)}')
    rmap={(r['source_viewer_key'],int(r['source_target_page'])):r for r in recs}

    with SRC.open(encoding='utf-8',newline='') as f:
        rd=csv.DictReader(f); fields=list(rd.fieldnames or []); rows=list(rd)
    viewers=sorted({r['viewer_key'] for r in rows})
    if len(viewers)!=EXPECTED_VIEWERS:
        raise SystemExit(f'expected {EXPECTED_VIEWERS} viewers, got {len(viewers)}')

    extra=['reconcile_version','effective_asset_status','effective_asset_url','effective_sha256','effective_byte_size','effective_source_viewer_key','resolution_method','original_anomaly_preserved']
    out=[]; used=set()
    for r in rows:
        x=dict(r); key=(r['viewer_key'],int(r['viewer_page']))
        status=r.get('asset_status','')
        if status=='source_jpeg':
            eff='source_jpeg'; url=r.get('source_asset_url',''); sha=r.get('sha256',''); bs=r.get('byte_size',''); ev=r['viewer_key']; method='direct_source'; anomaly='0'
        elif key in rmap:
            q=rmap[key]; used.add(key)
            eff='source_jpeg_recovered'; url=q['recovered_asset_url']; sha=q['recovered_sha256']; bs=q['recovered_byte_size']; ev=q['recovery_viewer_key']; method='hash_anchored_fixed_offset_recovery'; anomaly='1'
        elif r.get('is_final_declared_position')=='1' and status!='source_jpeg':
            eff='terminal_synthetic'; url=''; sha=''; bs=''; ev=r['viewer_key']; method='preserved_terminal_non_jpeg'; anomaly='0'
        else:
            eff='unresolved'; url=''; sha=''; bs=''; ev=''; method='unresolved_original_route'; anomaly='1'
        x.update({'reconcile_version':VERSION,'effective_asset_status':eff,'effective_asset_url':url,'effective_sha256':sha,'effective_byte_size':bs,'effective_source_viewer_key':ev,'resolution_method':method,'original_anomaly_preserved':anomaly})
        out.append(x)
    if used!=set(rmap): raise SystemExit(f'unused recoveries: {set(rmap)-used}')

    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields+extra);w.writeheader();w.writerows(out)

    by={v:Counter() for v in viewers}; meta={}
    for r in out:
        v=r['viewer_key'];by[v][r['effective_asset_status']]+=1;meta[v]=r
    summary=[]
    for v in viewers:
        c=by[v]; unresolved=c['unresolved']; real=c['source_jpeg']+c['source_jpeg_recovered']; terminal=c['terminal_synthetic']
        summary.append({'reconcile_version':VERSION,'viewer_key':v,'book_id':meta[v]['book_id'],'catalog_generation':meta[v]['catalog_generation'],'grade_code':meta[v]['grade_code'],'title_core':meta[v]['title_core'],'declared_rows':sum(c.values()),'effective_real_jpeg':real,'recovered_jpeg':c['source_jpeg_recovered'],'terminal_synthetic':terminal,'effective_unresolved':unresolved,'effective_asset_ready':int(unresolved==0 and real>0)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)

    ready=sum(int(r['effective_asset_ready']) for r in summary); unresolved=sum(int(r['effective_unresolved']) for r in summary); recovered=sum(int(r['recovered_jpeg']) for r in summary)
    problem=[r for r in summary if not int(r['effective_asset_ready'])]
    lines=['# LTMD-U1 W2 — manifiesto reconciliado de activos de Matemáticas','',f'Versión: `{VERSION}`.','',f'- Visores: **{len(summary)}**.',f'- Visores con resolución efectiva completa: **{ready}/{len(summary)}**.',f'- JPEG recuperados criptográficamente: **{recovered}**.',f'- Posiciones aún no resueltas: **{unresolved}**.','', '## Casos todavía no resueltos','']
    for r in problem: lines.append(f"- `{r['viewer_key']}`: {r['effective_unresolved']} posiciones no resueltas.")
    lines += ['','El manifiesto conserva las URLs/estados originales y añade campos `effective_*`; una recuperación técnica no se interpreta como identidad bibliográfica. Los cuatro visores DMA 2018 permanecen sin promover mientras no exista una prueba documental o criptográfica suficiente.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text())
if __name__=='__main__':main()
