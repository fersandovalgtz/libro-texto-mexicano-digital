#!/usr/bin/env python3
"""Build a non-destructive functional retyping of frozen FRAGSEG 0.2 fragments.

No boundaries, IDs, hashes, token counts or source metadata change. The residual
label `heading_candidate` is renamed `short_residual_candidate` because the
original rule contains no typographic heading evidence. Units >=4 tokens become
semantically eligible in the shadow layer; units <4 remain ineligible.
"""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

IN=Path('data/derived/fragment_manifest.csv')
OUT=Path('data/derived/fragment_manifest_fragtype03_shadow.csv')
REPORT=Path('data/derived/fragtype03_shadow_summary.md')
VERSION='FRAGTYPE_0.3_SHADOW'
GENS=('1972','1988','1993','2014')

def main():
    rows=list(csv.DictReader(IN.open(encoding='utf-8')));assert len(rows)==9594
    out=[]
    for r in rows:
        old=r['candidate_type'];n=int(r['token_count'])
        new='short_residual_candidate' if old=='heading_candidate' else old
        eligible=int(n>=4)  # semantic eligibility separated from residual functional label
        out.append({**r,'candidate_type_original':old,'candidate_type_03':new,'semantic_eligible_03':eligible,'functional_retyping_version':VERSION})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=list(out[0])
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    lines=['# FRAGTYPE 0.3 — re-tipificación shadow','',f'Versión: `{VERSION}`. Esta capa no modifica ningún límite de fragmento, ID ni hash.','',
           '`heading_candidate` se interpreta como categoría residual de longitud y se renombra `short_residual_candidate`. La elegibilidad semántica se separa de esa etiqueta: cualquier fragmento de ≥4 tokens es elegible para futura validación, sin afirmar que deba ser clasificado correctamente por SEMB 0.2.','',
           '## Impacto potencial de cobertura']
    for g in GENS:
        rr=[r for r in out if r['catalog_generation']==g]
        old_eligible=sum(r['candidate_type_original']!='heading_candidate' and int(r['token_count'])>=4 for r in rr)
        new_eligible=sum(int(r['semantic_eligible_03']) for r in rr)
        residual=sum(r['candidate_type_03']=='short_residual_candidate' for r in rr)
        recovered=sum(r['candidate_type_03']=='short_residual_candidate' and int(r['token_count'])>=4 for r in rr)
        lines.append(f'- {g}: elegibles SEMB 0.2={old_eligible}; elegibles shadow={new_eligible}; +{recovered} unidades breves recuperables; residual total={residual}.')
    old=sum(r['candidate_type_original']!='heading_candidate' and int(r['token_count'])>=4 for r in out);new=sum(int(r['semantic_eligible_03']) for r in out);rec=new-old
    lines += ['',f'**Total:** elegibilidad pasa de **{old}** a **{new}** fragmentos (+{rec}, {100*rec/old:.1f}% respecto al universo anterior).','',
              '## Restricción','Esta capa sólo demuestra que la exclusión anterior dependía de una etiqueta residual mal nombrada. La inclusión de estas unidades en SEMB 0.3 requerirá validación humana suplementaria; no se incorporan retroactivamente a los resultados históricos SEMB 0.2.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('old_eligible',old,'shadow_eligible',new,'recoverable',rec)

if __name__=='__main__':main()
