#!/usr/bin/env python3
"""Audit SEMB 0.3 sample coverage using FRAGSEG metadata only.

Computes post-stratification weights by generation x candidate_type, reports
small locked-validation strata, page clustering, and token-length transportability.
Reads no human annotations or semantic outputs.
"""
from __future__ import annotations
import csv,statistics
from collections import Counter
from pathlib import Path

MANIFEST=Path('data/derived/fragment_manifest.csv')
SAMPLE=Path('data/validation/semb03_human_reference_sample.csv')
OUT=Path('data/derived/semb03_sample_coverage.csv')
TOKEN_OUT=Path('data/derived/semb03_sample_token_coverage.csv')
REPORT=Path('data/derived/semb03_sample_coverage.md')
VERSION='SEMB03_SAMPLE_COVERAGE_0.2'
GENS=('1972','1988','1993','2014')
BINS=(('4-12',4,12),('13-30',13,30),('31-60',31,60),('61-120',61,120),('>120',121,10**9))

def eligible(r):return r['candidate_type']!='heading_candidate' and int(r['token_count'])>=4

def tbin(n):
    for name,lo,hi in BINS:
        if lo<=n<=hi:return name
    raise ValueError(n)

def main():
    pop=[r for r in csv.DictReader(MANIFEST.open(encoding='utf-8')) if eligible(r)]
    sample=list(csv.DictReader(SAMPLE.open(encoding='utf-8')))
    byfid={r['fragment_id']:r for r in pop}
    assert len(pop)==5037 and len(sample)==480
    assert all(r['fragment_id'] in byfid for r in sample)
    types=sorted({r['candidate_type'] for r in pop})
    rows=[]
    for g in GENS:
        for typ in types:
            N=sum(r['catalog_generation']==g and r['candidate_type']==typ for r in pop)
            ss=[r for r in sample if r['catalog_generation']==g and r['candidate_type']==typ]
            n=len(ss);dev=sum(r['analysis_role']=='development' for r in ss);locked=sum(r['analysis_role']=='locked_validation' for r in ss)
            rows.append({'coverage_version':VERSION,'catalog_generation':g,'candidate_type':typ,'eligible_population_n':N,'sample_n':n,
                         'development_n':dev,'locked_validation_n':locked,'sample_fraction':round(n/N,6) if N else '',
                         'poststrat_weight':round(N/n,6) if n else '', 'locked_small_stratum':int(N>0 and locked<5)})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

    token_rows=[]
    for g in GENS:
        for name,lo,hi in BINS:
            N=sum(r['catalog_generation']==g and lo<=int(r['token_count'])<=hi for r in pop)
            ss=[r for r in sample if r['catalog_generation']==g and lo<=int(r['token_count'])<=hi]
            token_rows.append({'coverage_version':VERSION,'catalog_generation':g,'token_bin':name,'eligible_population_n':N,'sample_n':len(ss),
                               'locked_validation_n':sum(r['analysis_role']=='locked_validation' for r in ss),
                               'poststrat_weight':round(N/len(ss),6) if ss else ''})
    with TOKEN_OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(token_rows[0]));w.writeheader();w.writerows(token_rows)

    sample_types=Counter(r['candidate_type'] for r in sample);pop_types=Counter(r['candidate_type'] for r in pop)
    locked_types=Counter(r['candidate_type'] for r in sample if r['analysis_role']=='locked_validation')
    lines=['# Cobertura de la muestra humana SEMB 0.3','',f'Versión: `{VERSION}`. Universo elegible FRAGSEG: **{len(pop)}** fragmentos; muestra: **{len(sample)}**; desarrollo: 320; validación bloqueada: 160.','',
           'La muestra es deliberadamente estratificada y no es autoponderada. Se congelan pesos descriptivos `N_h/n_h` por generación × tipo y generación × longitud. Las métricas primarias preregistradas permanecen sin ponderar; los pesos sólo sirven para análisis de transportabilidad al corpus.','',
           '## Distribución por tipo']
    for typ in types:lines.append(f"- `{typ}`: población={pop_types[typ]}, muestra={sample_types[typ]}, locked={locked_types[typ]}.")
    small=[r for r in rows if r['locked_small_stratum']]
    lines += ['', '## Estratos pequeños en validación bloqueada', f'Se detectan **{len(small)}** combinaciones generación × tipo con población >0 y menos de 5 casos locked. Esto no invalida la validación global, pero limita inferencias finas por estrato.']
    for r in small:lines.append(f"- {r['catalog_generation']} `{r['candidate_type']}`: población={r['eligible_population_n']}, locked={r['locked_validation_n']}.")

    lines += ['', '## Diversidad de páginas']
    for g in GENS:
        sp=[r for r in sample if r['catalog_generation']==g];lp=[r for r in sp if r['analysis_role']=='locked_validation']
        cp=Counter(r['page_id'] for r in sp);cl=Counter(r['page_id'] for r in lp)
        pop_pages=len({r['page_id'] for r in pop if r['catalog_generation']==g})
        lines.append(f"- {g}: muestra 120 fragmentos en **{len(cp)} páginas** de {pop_pages} elegibles; máximo {max(cp.values())} fragmentos de una misma página; locked 40 fragmentos en **{len(cl)} páginas**, máximo {max(cl.values())} por página.")
    allc=Counter(r['page_id'] for r in sample);lockedc=Counter(r['page_id'] for r in sample if r['analysis_role']=='locked_validation')
    lines.append(f"- Total: 480 fragmentos abarcan **{len(allc)} páginas**; los 160 locked abarcan **{len(lockedc)} páginas**.")

    lines += ['', '## Longitud']
    for name,_,_ in BINS:
        N=sum(tbin(int(r['token_count']))==name for r in pop);n=sum(tbin(int(r['token_count']))==name for r in sample);lk=sum(tbin(int(r['token_count']))==name and r['analysis_role']=='locked_validation' for r in sample)
        lines.append(f'- `{name}` tokens: población={N}, muestra={n}, locked={lk}.')
    pop_med=statistics.median(int(r['token_count']) for r in pop);sample_med=statistics.median(int(r['token_count']) for r in sample)
    lines.append(f'- Mediana de longitud: universo={pop_med} tokens; muestra={sample_med} tokens.')

    lines += ['', '## Regla de uso', 'Los pesos y diagnósticos de diversidad se fijan antes de ver anotaciones humanas. No deben recalcularse en función del desempeño del modelo ni de las diferencias históricas. La dependencia entre fragmentos de una misma página deberá respetarse en análisis de incertidumbre posteriores.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('eligible',len(pop),'sample',len(sample),'unique_pages',len(allc),'locked_pages',len(lockedc),'small_locked_strata',len(small))

if __name__=='__main__':main()
