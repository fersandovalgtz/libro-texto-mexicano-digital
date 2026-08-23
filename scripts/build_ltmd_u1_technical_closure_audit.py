#!/usr/bin/env python3
"""Certify the internally consistent LTMD-U1 technical cut after W11 closes.

This is a source-admitted technical audit, not a claim of semantic completion.
It requires all wave-level coverage accounting to reconcile exactly with the
cross-wave preserved-exceptions register.
"""
from __future__ import annotations
import csv,json,re
from collections import Counter
from pathlib import Path

COVERAGE=Path('data/catalog/ltmd_u1_coverage_summary.csv')
EXCEPTIONS=Path('data/catalog/ltmd_u1_preserved_exceptions.csv')
W11=Path('docs/LTMD_U1_W11_COMPLETION.md')
OUT=Path('docs/LTMD_U1_TECHNICAL_CLOSURE_AUDIT.md')
JSON_OUT=Path('data/catalog/ltmd_u1_technical_closure_audit.json')
VERSION='LTMD_U1_TECHNICAL_CLOSURE_AUDIT_0.1'
TOTAL=542
EXPECTED_WAVES={f'W{i}' for i in range(1,12)}

def read(path:Path):
    if not path.exists():raise SystemExit(f'missing U1 closure input: {path}')
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def req(cond,msg):
    if not cond:raise SystemExit(f'U1 technical closure audit failed: {msg}')

def main():
    req(W11.exists(),'W11 completion report not yet published; U1 closure audit remains gated')
    cov=read(COVERAGE);exc=read(EXCEPTIONS)
    req(len(cov)==11 and {r['wave'] for r in cov}==EXPECTED_WAVES,'coverage wave partition')
    req(sum(int(r['planned_identities']) for r in cov)==TOTAL,'planned universe != 542')
    req(len({(r['wave'],r['viewer_key']) for r in exc})==len(exc),'duplicate preserved exception')
    eff=sum(int(r['effective_technical_identities']) for r in cov);can=sum(int(r['canonical_processing_objects']) for r in cov);remaining=sum(int(r['remaining_to_effective']) for r in cov)
    req(eff+remaining==TOTAL,'effective + remaining != universe')
    req(can<=eff,'canonical total exceeds effective identities')
    req(remaining==len(exc),f'coverage remaining {remaining} != exception register {len(exc)}')
    exc_by=Counter(r['wave'] for r in exc);cov_by={r['wave']:r for r in cov}
    for wave,r in cov_by.items():
        req(int(r['remaining_to_effective'])==exc_by[wave],f'{wave} remaining != preserved exceptions')
        if exc_by[wave]==0:req(r['stage']=='closed',f'{wave} has no exception but is not closed')
        else:req(r['stage'] in {'partial_with_preserved_exceptions','source_admitted_cohort_closed_with_retentions'},f'{wave} exception-bearing stage unexpected: {r["stage"]}')
    # W11 completion itself must preserve the exact source-admitted cohort counts encoded by coverage.
    text=W11.read_text(encoding='utf-8')
    m_eff=re.search(r'Identidades técnicamente cubiertas por fuente admitida:\s*\*\*([\d,]+)/([\d,]+)\*\*',text,re.I)
    m_can=re.search(r'Objetos canónicos procesados:\s*\*\*([\d,]+)\*\*',text,re.I)
    m_ret=re.search(r'Identidades retenidas por fuente:\s*\*\*([\d,]+)\*\*',text,re.I)
    req(m_eff and m_can and m_ret,'could not parse W11 completion metrics')
    w11_eff,w11_total=(int(x.replace(',','')) for x in m_eff.groups());w11_can=int(m_can.group(1).replace(',',''));w11_ret=int(m_ret.group(1).replace(',',''))
    req(w11_total==int(cov_by['W11']['planned_identities']) and w11_eff==int(cov_by['W11']['effective_technical_identities']),'W11 completion/coverage effective drift')
    req(w11_can==int(cov_by['W11']['canonical_processing_objects']),'W11 completion/coverage canonical drift')
    req(w11_ret==int(cov_by['W11']['remaining_to_effective']),'W11 completion/coverage retention drift')
    summary={'audit_version':VERSION,'universe':TOTAL,'effective_technical_identities':eff,'effective_percent':round(100*eff/TOTAL,2),'canonical_processing_objects':can,'canonical_percent':round(100*can/TOTAL,2),'preserved_exceptions':len(exc),'remaining_to_effective':remaining,'semantic_human_validated':0,'wave_remaining':{w:int(cov_by[w]['remaining_to_effective']) for w in sorted(EXPECTED_WAVES,key=lambda x:int(x[1:]))},'status':'PASS'}
    JSON_OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# LTMD-U1 — auditoría de cierre técnico del universo congelado','',f'Versión: `{VERSION}`.','',
           'Este documento certifica la consistencia del corte técnico fuente-admitido de U1 después de cerrar W11. **No declara cierre semántico, curricular, pedagógico ni histórico.**','',
           '## Resultado',f'- Universo congelado: **{TOTAL}/{TOTAL}** identidades.',f'- Cobertura técnica efectiva: **{eff}/{TOTAL} ({100*eff/TOTAL:.2f}%)**.',f'- Objetos canónicos cerrados: **{can}/{TOTAL} ({100*can/TOTAL:.2f}%)**.',f'- Excepciones técnicas preservadas: **{len(exc)}**.',f'- Remanente del tablero: **{remaining}**, reconciliado 1:1 con el registro de excepciones.',f'- Cobertura semántica humana incorporada: **0/{TOTAL}**.','','## Reconciliación por ola','','| ola | plan | efectiva | canónicos | excepciones | estado |','|---|---:|---:|---:|---:|---|']
    for w in sorted(EXPECTED_WAVES,key=lambda x:int(x[1:])):
        r=cov_by[w];lines.append(f"| {w} | {r['planned_identities']} | {r['effective_technical_identities']} | {r['canonical_processing_objects']} | {exc_by[w]} | `{r['stage']}` |")
    lines+=['','## Contrato','Cada identidad no cubierta técnicamente debe aparecer exactamente una vez en `ltmd_u1_preserved_exceptions.csv`; ninguna identidad cubierta puede quedar contada como excepción. Las olas sin excepciones deben estar `closed`; las olas con excepciones sólo pueden usar estados parciales explícitos. Cualquier cambio en una fuente retenida exige recomputar su ola, tablero, registro de excepciones y esta auditoría.','','`WAITING_HUMAN_REFERENCE` continúa vigente. La alta cobertura técnica no debe interpretarse como validación humana de constructos ni como independencia histórica de las ocurrencias.','','**Estado: PASS**']
    OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(OUT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
