#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.14 as an additive comparison perimeter over 0.13."""
from __future__ import annotations
import json
import build_research_integrity_manifest_v13 as v13

base=v13.base
base.VERSION='LTMD_INTEGRITY_0.14'
SCOPE=('LTMD v0.14: frozen v0.13 W8 technical-closure perimeter plus the closed, strictly descriptive LTMD-U1 W3-W4-W7-W8 technical comparison across PAGESTRUCT, FRAGSEG and exact-text reuse/dependence, including its reproducible script, explicit dispatch control and workflow')
SCOPE_ES=('perímetro v0.13 de cierre técnico W8 congelado + comparación técnica W3–W4–W7–W8 cerrada y estrictamente descriptiva sobre PAGESTRUCT, FRAGSEG y reutilización/dependencia textual exacta, incluido su script reproducible, control explícito de despacho y workflow')

V14_CRITICAL=[
 'data/derived/ltmd_u1_w3_w4_w7_w8_technical_comparison.csv',
 'docs/LTMD_U1_W3_W4_W7_W8_TECHNICAL_COMPARISON.md',
 'scripts/compare_ltmd_u1_w3_w4_w7_w8_technical_profiles.py',
 '.github/workflows/analyze-ltmd-u1-w3-w4-w7-w8-technical-comparison.yml',
 'data/control/ltmd_u1_w3_w4_w7_w8_comparison_trigger.txt',
 'scripts/build_research_integrity_manifest_v14.py',
]
for path in V14_CRITICAL:
    if path not in base.CRITICAL: base.CRITICAL.append(path)

def main():
    v13.main()
    data=json.loads(base.OUT.read_text(encoding='utf-8'));data['scope']=SCOPE;base.OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=base.REPORT.read_text(encoding='utf-8');old=f'Alcance: {v13.SCOPE_ES}.';new=f'Alcance: {SCOPE_ES}.'
    if old not in report: raise SystemExit('LTMD_INTEGRITY_0.14 scope postprocessor could not locate v0.13 scope line')
    base.REPORT.write_text(report.replace(old,new,1),encoding='utf-8')
if __name__=='__main__': main()
