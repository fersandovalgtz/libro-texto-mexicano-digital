#!/usr/bin/env python3
"""Generate transparent exploratory findings from preregistered LTMD derivatives.

No source/fragment text is read. This script does not alter confirmatory tables.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

BASE=Path('data/derived')
TRANS=BASE/'historical_transitions.csv'
CAT=BASE/'classifier_AB_category_agreement.csv'
ROB=BASE/'exploratory_robust_transitions.csv'
SENS=BASE/'exploratory_method_sensitive_transitions.csv'
STAB=BASE/'exploratory_category_stability.csv'
MD=BASE/'exploratory_historical_findings.md'
VERSION='EXPLORE_FINDINGS_0.1'


def main():
    trans=list(csv.DictReader(TRANS.open(encoding='utf-8')))
    cats=list(csv.DictReader(CAT.open(encoding='utf-8')))
    assert trans and cats
    # Index transition specifications so consensus rows can carry A/B deltas.
    ti={(r['domain'],r['category'],r['initial_generation'],r['final_generation'],r['specification']):r for r in trans}
    robust=[]; sensitive=[]
    for r in trans:
        if r['specification']!='consensus':
            continue
        keybase=(r['domain'],r['category'],r['initial_generation'],r['final_generation'])
        ar=ti[keybase+('A',)]; br=ti[keybase+('B',)]
        row={
            'domain':r['domain'],'category':r['category'],'initial_generation':r['initial_generation'],'final_generation':r['final_generation'],
            'consensus_initial_rate':r['initial_rate'],'consensus_final_rate':r['final_rate'],'consensus_difference_pp':r['difference_pp'],'consensus_direction':r['direction'],
            'A_initial_rate':ar['initial_rate'],'A_final_rate':ar['final_rate'],'A_difference_pp':ar['difference_pp'],'A_direction':ar['direction'],
            'B_initial_rate':br['initial_rate'],'B_final_rate':br['final_rate'],'B_difference_pp':br['difference_pp'],'B_direction':br['direction'],
            'directionally_robust':r['directionally_robust'],'method_sensitive_direction':r['method_sensitive_direction'],'exploratory_version':VERSION,
        }
        if int(r['directionally_robust']): robust.append(row)
        if int(r['method_sensitive_direction']): sensitive.append(row)
    robust.sort(key=lambda x:(x['initial_generation'],x['final_generation'],-abs(float(x['consensus_difference_pp'])),x['domain'],x['category']))
    sensitive.sort(key=lambda x:(x['initial_generation'],x['final_generation'],x['domain'],x['category']))
    if robust:
        with ROB.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(robust[0].keys()));w.writeheader();w.writerows(robust)
    else:
        ROB.write_text('domain,category,initial_generation,final_generation\n',encoding='utf-8')
    if sensitive:
        with SENS.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(sensitive[0].keys()));w.writeheader();w.writerows(sensitive)
    else:
        SENS.write_text('domain,category,initial_generation,final_generation\n',encoding='utf-8')

    stability=[]
    for r in cats:
        stability.append({
            'family':r['family'],'category':r['category'],'catalog_generation':r['catalog_generation'],'n':r['n'],
            'n11':r['n11'],'n10':r['n10'],'n01':r['n01'],'n00':r['n00'],
            'binary_agreement':r['binary_agreement'],'positive_jaccard':r['positive_jaccard'],
            'prevalence_A':r['prevalence_A'],'prevalence_B':r['prevalence_B'],'absolute_prevalence_difference':r['absolute_prevalence_difference'],
            'exploratory_version':VERSION,
        })
    stability.sort(key=lambda x:(x['family'],x['category'],x['catalog_generation']))
    with STAB.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(stability[0].keys()));w.writeheader();w.writerows(stability)

    bytr=defaultdict(list)
    for r in robust: bytr[(r['initial_generation'],r['final_generation'])].append(r)
    sensby=defaultdict(list)
    for r in sensitive: sensby[(r['initial_generation'],r['final_generation'])].append(r)
    lines=[
        '# LTMD — hallazgos exploratorios computacionales 0.1','',
        'Esta capa es **exploratoria/post hoc** respecto de los resultados históricos ya calculados. No modifica las tablas preregistradas. El ranking usa únicamente |Δ pp| del consenso A∩B y publica además los CSV completos.','',
        f'- Hallazgos directionally robust totales: **{len(robust)}**.',
        f'- Hallazgos con dirección method-sensitive A/B: **{len(sensitive)}**.','',
    ]
    for tr in [('1972','1988'),('1988','1993'),('1993','2014'),('1972','2014')]:
        lines += [f'## {tr[0]} → {tr[1]}','',f'Robustos: {len(bytr[tr])}; method-sensitive: {len(sensby[tr])}.','', '### Diez robustos de mayor magnitud']
        xs=bytr[tr][:10]
        if not xs: lines.append('- Ninguno.')
        for r in xs:
            lines.append(
                f"- `{r['domain']} / {r['category']}`: consenso {float(r['consensus_initial_rate']):.3%} → {float(r['consensus_final_rate']):.3%} "
                f"({float(r['consensus_difference_pp']):+.2f} pp; {r['consensus_direction']}); "
                f"ΔA={float(r['A_difference_pp']):+.2f} pp; ΔB={float(r['B_difference_pp']):+.2f} pp."
            )
        lines += ['', '### Direcciones method-sensitive']
        ms=sensby[tr]
        if not ms: lines.append('- Ninguna.')
        for r in ms:
            lines.append(f"- `{r['domain']} / {r['category']}`: ΔA={float(r['A_difference_pp']):+.2f} pp ({r['A_direction']}), ΔB={float(r['B_difference_pp']):+.2f} pp ({r['B_direction']}).")
        lines.append('')
    lines += [
        '## Regla de lectura','',
        'Los robustos pueden convertirse en hipótesis historiográficas, pero la magnitud/ranking es exploratoria. Las categorías method-sensitive no sostienen por sí solas una afirmación histórica principal. Para estabilidad de positivos debe consultarse `exploratory_category_stability.csv`, especialmente `positive_jaccard`, no sólo el acuerdo binario dominado por ceros.','',
        f'Versión: `{VERSION}`.',''
    ]
    MD.write_text('\n'.join(lines),encoding='utf-8')
    print('robust',len(robust),'method_sensitive',len(sensitive),'stability_rows',len(stability))

if __name__=='__main__':main()
