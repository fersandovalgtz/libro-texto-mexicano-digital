#!/usr/bin/env python3
"""Audit SEMB 0.3 sample coverage using FRAGSEG metadata only.

Computes post-stratification weights by generation x candidate_type and reports
small locked-validation strata. Reads no human annotations or semantic outputs.
"""
from __future__ import annotations
import csv
from collections import Counter,defaultdict
from pathlib import Path

MANIFEST=Path('data/derived/fragment_manifest.csv')
SAMPLE=Path('data/validation/semb03_human_reference_sample.csv')
OUT=Path('data/derived/semb03_sample_coverage.csv')
REPORT=Path('data/derived/semb03_sample_coverage.md')
VERSION='SEMB03_SAMPLE_COVERAGE_0.1'
GENS=('1972','1988','1993','2014')

def eligible(r):return r['candidate_type']!='heading_candidate' and int(r['token_count'])>=4

def main():
    pop=[r for r in csv.DictReader(MANIFEST.open(encoding='utf-8')) if eligible(r)]
    sample=list(csv.DictReader(SAMPLE.open(encoding='utf-8')))
    byfid={r['fragment_id']:r for r in pop}
    assert len(pop)==5037 and len(sample)==480
    rows=[]
    types=sorted({r['candidate_type'] for r in pop})
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
    sample_types=Counter(r['candidate_type'] for r in sample);pop_types=Counter(r['candidate_type'] for r in pop)
    locked_types=Counter(r['candidate_type'] for r in sample if r['analysis_role']=='locked_validation')
    lines=['# Cobertura de la muestra humana SEMB 0.3','',f'Versión: `{VERSION}`. Universo elegible FRAGSEG: **{len(pop)}** fragmentos; muestra: **{len(sample)}**; desarrollo: 320; validación bloqueada: 160.','',
           'La muestra es deliberadamente estratificada y no es una muestra autoponderada del corpus. Por ello se publican pesos de postestratificación `N_h/n_h` por generación × tipo de candidato. Las métricas primarias preregistradas permanecen sin ponderar para respetar el diseño de validación; las métricas ponderadas podrán reportarse como análisis de transportabilidad al corpus.','',
           '## Distribución por tipo']
    for typ in types:
        lines.append(f"- `{typ}`: población={pop_types[typ]}, muestra={sample_types[typ]}, locked={locked_types[typ]}.")
    small=[r for r in rows if r['locked_small_stratum']]
    lines += ['', '## Estratos pequeños en validación bloqueada', f'Se detectan **{len(small)}** combinaciones generación × tipo con población >0 y menos de 5 casos locked. Esto no invalida la validación global, pero limita inferencias finas por estrato.']
    for r in small:lines.append(f"- {r['catalog_generation']} `{r['candidate_type']}`: población={r['eligible_population_n']}, locked={r['locked_validation_n']}.")
    lines += ['', '## Regla de uso', 'Los pesos se fijan antes de ver anotaciones humanas. No deben recalcularse en función del desempeño del modelo ni de las diferencias históricas.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('eligible',len(pop),'sample',len(sample),'small_locked_strata',len(small))

if __name__=='__main__':main()
