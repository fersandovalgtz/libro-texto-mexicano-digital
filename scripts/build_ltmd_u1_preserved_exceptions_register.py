#!/usr/bin/env python3
"""Build a cross-wave register of preserved U1 technical exceptions.

The register is derived from wave-level technical artifacts, not from prose or
semantic inference. It covers unresolved routing/source exceptions only; an
active downstream wave may still contribute zero coverage for reasons unrelated
to these exceptions until its technical completion report is published.
"""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

OUT=Path('data/catalog/ltmd_u1_preserved_exceptions.csv')
REPORT=Path('docs/LTMD_U1_PRESERVED_EXCEPTIONS.md')
COVERAGE=Path('data/catalog/ltmd_u1_coverage_summary.csv')
VERSION='LTMD_U1_PRESERVED_EXCEPTIONS_0.1'
EXPECTED={'W2':4,'W7':5,'W8':4,'W10':1,'W11':4}

def read(path:str):
    p=Path(path)
    if not p.exists():raise SystemExit(f'missing exception source: {path}')
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def add(rows,wave,viewer,kind,state,detail,evidence,issue):
    rows.append({'register_version':VERSION,'wave':wave,'viewer_key':viewer,'exception_kind':kind,'technical_state':state,'detail':detail,'evidence':evidence,'tracking_issue':issue,'semantic_state':'WAITING_HUMAN_REFERENCE'})

def main():
    out=[]

    # W2: zero served JPEGs in the audited mathematical routing state.
    p='data/catalog/ltmd_u1_w2_math_asset_states.csv';w2=read(p)
    unresolved=[r for r in w2 if int(r['declared_positions'])>0 and int(r['source_jpegs'])==0]
    if len(unresolved)!=EXPECTED['W2']:raise SystemExit(f'W2 exception drift: {len(unresolved)}')
    for r in unresolved:
        add(out,'W2',r['viewer_key'],'routing_unresolved',r['asset_state'],f"declared={r['declared_positions']}; source_jpegs={r['source_jpegs']}; next={r['next_action']}",p,'#4')

    # W7: explicit source gate retentions.
    p='data/catalog/ltmd_u1_w7_source_admissibility.csv';w7=read(p)
    retained=[r for r in w7 if r['ocr_source_admitted']=='0']
    if len(retained)!=EXPECTED['W7']:raise SystemExit(f'W7 exception drift: {len(retained)}')
    for r in retained:
        add(out,'W7',r['viewer_key'],'source_retained',r['reason_code'],f"declared={r['declared_positions']}; source_jpegs={r['source_jpegs']}; internal_unserved={r['internal_unserved']}",p,'#5')

    # W8: closed topology declares SOURCE_RETAINED identities explicitly.
    p='data/catalog/ltmd_u1_w8_processing_inventory.csv';w8=read(p)
    retained=[r for r in w8 if r['source_status']=='SOURCE_RETAINED']
    if len(retained)!=EXPECTED['W8']:raise SystemExit(f'W8 exception drift: {len(retained)}')
    for r in retained:
        add(out,'W8',r['viewer_key'],'source_retained',r['processing_mode'],f"declared={r['declared_positions']}; source_pages={r['source_page_count']}; persistent_gaps={r['persistent_internal_source_gaps']}",p,'#9')

    # W10 and W11: strict source-admissibility gates.
    for wave,path,issue_default in [
        ('W10','data/catalog/ltmd_u1_w10_source_admissibility.csv','#11'),
        ('W11','data/catalog/ltmd_u1_w11_source_admissibility.csv','')]:
        rr=read(path);retained=[r for r in rr if r['ocr_source_admitted']=='0']
        if len(retained)!=EXPECTED[wave]:raise SystemExit(f'{wave} exception drift: {len(retained)}')
        for r in retained:
            issue=issue_default
            if wave=='W11':issue='#13' if r['viewer_key'] in {'H2014P1EAM','H2014P2EAM'} else '#14'
            add(out,wave,r['viewer_key'],'source_retained',r['source_state'],f"declared={r['declared_positions']}; source_jpegs={r['source_jpegs']}; internal_unserved={r['internal_unserved']}; probe_errors={r['probe_errors']}",path,issue)

    if len(out)!=sum(EXPECTED.values()):raise SystemExit(f'exception total drift: {len(out)}')
    keys=[(r['wave'],r['viewer_key']) for r in out]
    if len(keys)!=len(set(keys)):raise SystemExit('duplicate wave/viewer exceptions')
    order={'W2':2,'W7':7,'W8':8,'W10':10,'W11':11}
    out.sort(key=lambda r:(order[r['wave']],r['viewer_key']))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)

    # When W11 is technically closed, the total U1 remaining count must reduce
    # exactly to this register. Before that, W11 downstream work legitimately
    # contributes additional remaining_to_effective rows and is not compared.
    completion=Path('docs/LTMD_U1_W11_COMPLETION.md').exists()
    coverage_remaining=None
    if completion and COVERAGE.exists():
        cov=read(str(COVERAGE));coverage_remaining=sum(int(r['remaining_to_effective']) for r in cov)
        if coverage_remaining!=len(out):raise SystemExit(f'post-W11 coverage/exception mismatch: remaining={coverage_remaining}, register={len(out)}')

    counts=Counter(r['wave'] for r in out);kinds=Counter(r['exception_kind'] for r in out)
    lines=['# LTMD-U1 — registro de excepciones técnicas preservadas','',f'Versión: `{VERSION}`.','',
           'Este registro se deriva de artefactos técnicos de las olas y reúne únicamente excepciones de routing/fuente que permanecen explícitamente sin imputación. No representa pendientes semánticos ni convierte una excepción en evidencia histórica.','',
           f'- Excepciones técnicas preservadas: **{len(out)}**.',f'- Olas con excepciones: **{len(counts)}**.']
    if coverage_remaining is not None:lines.append(f'- Remanente total del tablero después del cierre W11: **{coverage_remaining}**, reconciliado 1:1 con este registro.')
    else:lines.append('- Reconciliación contra `remaining_to_effective`: **pendiente del cierre técnico W11**; la ola activa aún no debe contarse como cubierta.')
    lines+=['','## Por ola','','| Ola | Excepciones | seguimiento |','|---|---:|---|']
    issue_by={'W2':'#4','W7':'#5','W8':'#9','W10':'#11','W11':'#13 y #14'}
    for wave in sorted(counts,key=lambda w:order[w]):lines.append(f'| {wave} | {counts[wave]} | {issue_by[wave]} |')
    lines+=['','## Identidades','','| Ola | viewer_key | tipo | estado técnico | issue |','|---|---|---|---|---|']
    for r in out:lines.append(f"| {r['wave']} | `{r['viewer_key']}` | `{r['exception_kind']}` | `{r['technical_state']}` | {r['tracking_issue']} |")
    lines+=['','## Regla','Resolver una fila requiere actualizar primero la evidencia de su ola y recomputar únicamente las capas afectadas. El registro debe regenerarse después; no se elimina una excepción manualmente ni por semejanza con otra edición. `WAITING_HUMAN_REFERENCE` continúa separado de esta deuda técnica.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
