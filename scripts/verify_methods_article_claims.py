#!/usr/bin/env python3
"""Verify headline quantitative claims in METHODS_ARTICLE_DRAFT_0_1.md.

The manuscript must not silently drift from frozen derived data. This script
recomputes or reads only headline infrastructure/methodological quantities and
asserts that the corresponding statements remain present in the article.
It does not validate prose interpretation or historical semantic claims.
"""
from __future__ import annotations
import csv,json,re
from pathlib import Path

ARTICLE=Path('docs/METHODS_ARTICLE_DRAFT_0_1.md')
OUT=Path('data/derived/methods_article_claim_check.json')
VERSION='METHODS_ARTICLE_CLAIMS_0.1'

def rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def fmt_pct(x,d=2):return f'{100*x:.{d}f}%'

def main():
    article=ARTICLE.read_text(encoding='utf-8')
    page=rows('data/derived/page_structure.csv')
    frag=rows('data/derived/fragment_manifest.csv')
    shadow=rows('data/derived/fragment_manifest_fragtype03_shadow.csv')
    sample=rows('data/validation/semb03_human_reference_sample.csv')
    rel=rows('data/validation/semb03_reliability_subset.csv')
    bsum=rows('data/derived/fragment_labels_B_summary.csv')
    stress=json.load(open('data/derived/semb02_synthetic_stress_result.json',encoding='utf-8'))

    allb=next(r for r in bsum if r['catalog_generation']=='ALL')
    old_eligible=sum(r['candidate_type']!='heading_candidate' and int(r['token_count'])>=4 for r in frag)
    # Shadow manifest has an explicit semantic eligibility column produced by FRAGTYPE 0.3.
    if shadow and 'semantic_eligible_shadow' in shadow[0]:
        new_eligible=sum(str(r['semantic_eligible_shadow']).strip().lower() in {'1','true','yes'} for r in shadow)
    else:
        new_eligible=sum(int(r['token_count'])>=4 for r in shadow)
    dev=sum(r['analysis_role']=='development' for r in sample)
    locked=sum(r['analysis_role']=='locked_validation' for r in sample)
    sample_pages=len({r['page_id'] for r in sample})
    locked_pages=len({r['page_id'] for r in sample if r['analysis_role']=='locked_validation'})

    claims={
      'page_structure_n':{'value':len(page),'required_text':['759 páginas','759 imágenes']},
      'fragment_n':{'value':len(frag),'required_text':['9,594 fragmentos']},
      'old_eligible_n':{'value':old_eligible,'required_text':['5,037']},
      'shadow_eligible_n':{'value':new_eligible,'required_text':['7,429']},
      'shadow_gain_n':{'value':new_eligible-old_eligible,'required_text':['2,392']},
      'sample_n':{'value':len(sample),'required_text':['480 fragmentos','480 casos']},
      'development_n':{'value':dev,'required_text':['320 casos de desarrollo','320 casos']},
      'locked_n':{'value':locked,'required_text':['160 casos de validación','160 casos']},
      'reliability_n':{'value':len(rel),'required_text':['120 casos']},
      'sample_pages':{'value':sample_pages,'required_text':['312 páginas']},
      'locked_pages':{'value':locked_pages,'required_text':['138']},
      'semb02_uncertainty_rate':{'value':float(allb['uncertain_rate_B']),'required_text':['99.49%']},
      'stress_n':{'value':int(stress['n_cases']),'required_text':['105 casos']},
      'stress_gate_balanced_accuracy':{'value':float(stress['gate']['balanced_accuracy']),'required_text':['0.526']},
      'stress_gate_sensitivity':{'value':float(stress['gate']['sensitivity']),'required_text':['0.597']},
      'stress_gate_specificity':{'value':float(stress['gate']['specificity']),'required_text':['0.455']},
    }
    expected={'page_structure_n':759,'fragment_n':9594,'old_eligible_n':5037,'shadow_eligible_n':7429,'shadow_gain_n':2392,'sample_n':480,'development_n':320,'locked_n':160,'reliability_n':120,'sample_pages':312,'locked_pages':138}
    failures=[]
    for k,v in expected.items():
        if claims[k]['value']!=v:failures.append(f'{k}: data={claims[k]["value"]}, expected={v}')
    if round(claims['semb02_uncertainty_rate']['value'],6)!=0.994893:failures.append('SEMB 0.2 uncertainty changed')
    if round(claims['stress_gate_balanced_accuracy']['value'],3)!=0.526:failures.append('synthetic gate BA changed')
    for name,c in claims.items():
        if not any(t in article for t in c['required_text']):failures.append(f'article missing headline representation for {name}: {c["required_text"]}')
    result={'claim_check_version':VERSION,'article':str(ARTICLE),'passed':not failures,'failures':failures,'claims':claims}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:raise SystemExit('claim verification failed')

if __name__=='__main__':main()
