#!/usr/bin/env python3
"""Verify headline quantitative claims in METHODS_ARTICLE_DRAFT_0_2.md.

The manuscript must not silently drift from frozen derived data. This script
recomputes headline infrastructure/methodological quantities from versioned
artifacts and asserts that the corresponding representations remain present in
the article. It does not validate prose interpretation or historical semantic
claims.
"""
from __future__ import annotations
import csv,json
from pathlib import Path

ARTICLE=Path('docs/METHODS_ARTICLE_DRAFT_0_2.md')
OUT=Path('data/derived/methods_article_claim_check.json')
VERSION='METHODS_ARTICLE_CLAIMS_0.2'

def rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))

def present(article, variants):
    return any(v in article for v in variants)

def truthy(v):
    return str(v).strip().lower() in {'1','true','yes'}

def main():
    article=ARTICLE.read_text(encoding='utf-8')

    pilot_pages=rows('data/derived/page_structure.csv')
    pilot_frag=rows('data/derived/fragment_manifest.csv')
    shadow=rows('data/derived/fragment_manifest_fragtype03_shadow.csv')
    sample=rows('data/validation/semb03_human_reference_sample.csv')
    rel=rows('data/validation/semb03_reliability_subset.csv')
    bsum=rows('data/derived/fragment_labels_B_summary.csv')
    stress=json.load(open('data/derived/semb02_synthetic_stress_result.json',encoding='utf-8'))

    cn46_positions=rows('data/expansion/cn46_page_manifest.csv')
    cn46_ocr=rows('data/expansion/cn46_ocr_page_metrics.csv')
    cn46_frag=rows('data/expansion/cn46_fragment_manifest.csv')
    wave2_pages=rows('data/expansion/cn_wave2_page_manifest.csv')
    wave2_ocr=rows('data/expansion/cn_wave2_ocr_page_metrics.csv')
    wave2_struct=rows('data/expansion/cn_wave2_page_structure.csv')
    wave2_frag=rows('data/expansion/cn_wave2_fragment_manifest.csv')
    readiness=rows('data/catalog/ciencias_naturales_family_asset_readiness.csv')
    alias_identity=rows('data/catalog/cn2018_2019_asset_identity.csv')

    allb=next(r for r in bsum if r['catalog_generation']=='ALL')
    old_eligible=sum(r['candidate_type']!='heading_candidate' and int(r['token_count'])>=4 for r in pilot_frag)
    if shadow and 'semantic_eligible_shadow' in shadow[0]:
        new_eligible=sum(truthy(r['semantic_eligible_shadow']) for r in shadow)
    else:
        new_eligible=sum(int(r['token_count'])>=4 for r in shadow)

    dev=sum(r['analysis_role']=='development' for r in sample)
    locked=sum(r['analysis_role']=='locked_validation' for r in sample)
    sample_pages=len({r['page_id'] for r in sample})
    locked_pages=len({r['page_id'] for r in sample if r['analysis_role']=='locked_validation'})

    cn46_real_manifest=sum(r['asset_status']=='source_jpeg' for r in cn46_positions)
    wave2_text=sum(r['ocr_class']=='text_detected' for r in wave2_ocr)
    wave2_unresolved=sum(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in wave2_ocr)
    wave2_sha=sum(truthy(r['source_sha256_verified']) for r in wave2_ocr)
    wave2_eligible=sum(r['primary_structure'] in {'textual','mixed_text_image'} for r in wave2_struct)
    total_frag=len(pilot_frag)+len(cn46_frag)+len(wave2_frag)

    readiness_counts={k:sum(r['asset_readiness']==k for r in readiness) for k in {
        'full_direct','full_alias_same_bytes','partial_internal_unserved','not_resolved'
    }}
    full_resolved=readiness_counts['full_direct']+readiness_counts['full_alias_same_bytes']
    internal_unserved=sum(int(r['internal_unserved_positions']) for r in readiness)
    alias_sha_ok=sum(truthy(r['sha256_identity']) for r in alias_identity)
    alias_bytes_ok=sum(truthy(r['byte_size_identity']) for r in alias_identity)

    values={
      'pilot_pages':len(pilot_pages),
      'pilot_fragments':len(pilot_frag),
      'cn46_declared_positions':len(cn46_positions),
      'cn46_real_jpegs_manifest':cn46_real_manifest,
      'cn46_ocr_rows':len(cn46_ocr),
      'cn46_fragments':len(cn46_frag),
      'wave2_pages':len(wave2_pages),
      'wave2_ocr_rows':len(wave2_ocr),
      'wave2_sha_verified':wave2_sha,
      'wave2_text_detected':wave2_text,
      'wave2_unresolved':wave2_unresolved,
      'wave2_struct_rows':len(wave2_struct),
      'wave2_eligible_pages':wave2_eligible,
      'wave2_fragments':len(wave2_frag),
      'technical_fragment_occurrences':total_frag,
      'family_viewers':len(readiness),
      'family_full_resolved':full_resolved,
      'family_full_direct':readiness_counts['full_direct'],
      'family_alias':readiness_counts['full_alias_same_bytes'],
      'family_partial':readiness_counts['partial_internal_unserved'],
      'family_not_resolved':readiness_counts['not_resolved'],
      'family_internal_unserved_positions':internal_unserved,
      'alias_asset_pairs':len(alias_identity),
      'alias_sha_identity':alias_sha_ok,
      'alias_byte_identity':alias_bytes_ok,
      'old_eligible':old_eligible,
      'shadow_eligible':new_eligible,
      'shadow_gain':new_eligible-old_eligible,
      'sample_n':len(sample),
      'development_n':dev,
      'locked_n':locked,
      'reliability_n':len(rel),
      'sample_pages':sample_pages,
      'locked_pages':locked_pages,
      'semb02_uncertainty_rate':float(allb['uncertain_rate_B']),
      'stress_n':int(stress['n_cases']),
      'stress_gate_balanced_accuracy':float(stress['gate']['balanced_accuracy']),
      'stress_gate_sensitivity':float(stress['gate']['sensitivity']),
      'stress_gate_specificity':float(stress['gate']['specificity']),
    }

    expected={
      'pilot_pages':759,'pilot_fragments':9594,
      'cn46_declared_positions':1897,'cn46_real_jpegs_manifest':1888,
      'cn46_ocr_rows':1888,'cn46_fragments':19067,
      'wave2_pages':3177,'wave2_ocr_rows':3177,'wave2_sha_verified':3177,
      'wave2_text_detected':3164,'wave2_unresolved':0,'wave2_struct_rows':3177,
      'wave2_eligible_pages':2528,'wave2_fragments':36195,
      'technical_fragment_occurrences':64856,
      'family_viewers':37,'family_full_resolved':35,'family_full_direct':31,
      'family_alias':4,'family_partial':2,'family_not_resolved':0,
      'family_internal_unserved_positions':3,
      'alias_asset_pairs':652,'alias_sha_identity':652,'alias_byte_identity':652,
      'old_eligible':5037,'shadow_eligible':7429,'shadow_gain':2392,
      'sample_n':480,'development_n':320,'locked_n':160,'reliability_n':120,
      'sample_pages':312,'locked_pages':138,
    }

    required_text={
      'pilot_pages':['759 imágenes','759 páginas'],
      'pilot_fragments':['9,594 fragmentos'],
      'cn46_declared_positions':['1,897 posiciones declaradas'],
      'cn46_real_jpegs_manifest':['1,888 JPEG reales','1,888 páginas'],
      'cn46_fragments':['19,067'],
      'wave2_pages':['3,177 páginas','3,177 JPEG'],
      'wave2_text_detected':['3,164'],
      'wave2_eligible_pages':['2,528'],
      'wave2_fragments':['36,195 fragmentos'],
      'technical_fragment_occurrences':['64,856'],
      'family_viewers':['37 visores'],
      'family_full_resolved':['35/37'],
      'family_full_direct':['Treinta y un visores','31 resuelven'],
      'family_alias':['cuatro entradas de 2018','Cuatro visores asociados a 2018'],
      'family_internal_unserved_positions':['tres posiciones internas'],
      'alias_asset_pairs':['652 pares','652 activos'],
      'old_eligible':['5,037'],
      'shadow_eligible':['7,429'],
      'shadow_gain':['2,392'],
      'sample_n':['480 fragmentos','480 casos'],
      'development_n':['320 casos de desarrollo'],
      'locked_n':['160 casos de validación'],
      'reliability_n':['120 casos'],
      'sample_pages':['312 páginas'],
      'locked_pages':['138'],
      'semb02_uncertainty_rate':['99.49%'],
      'stress_n':['105 casos'],
      'stress_gate_balanced_accuracy':['0.526'],
      'stress_gate_sensitivity':['0.597'],
      'stress_gate_specificity':['0.455'],
    }

    failures=[]
    for k,v in expected.items():
        if values[k]!=v:
            failures.append(f'{k}: data={values[k]}, expected={v}')
    if values['cn46_real_jpegs_manifest'] != values['cn46_ocr_rows']:
        failures.append('CN46 real-JPEG manifest count and OCR-row count diverge')
    if round(values['semb02_uncertainty_rate'],6)!=0.994893:
        failures.append('SEMB 0.2 uncertainty changed')
    if round(values['stress_gate_balanced_accuracy'],3)!=0.526:
        failures.append('synthetic gate BA changed')
    if round(values['stress_gate_sensitivity'],3)!=0.597:
        failures.append('synthetic gate sensitivity changed')
    if round(values['stress_gate_specificity'],3)!=0.455:
        failures.append('synthetic gate specificity changed')
    for name,variants in required_text.items():
        if not present(article,variants):
            failures.append(f'article missing headline representation for {name}: {variants}')

    result={
      'claim_check_version':VERSION,
      'article':str(ARTICLE),
      'passed':not failures,
      'failures':failures,
      'values':values,
      'note':'Checks quantitative infrastructure claims only; does not validate historiographic interpretation.'
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if failures:
        raise SystemExit('claim verification failed')

if __name__=='__main__':
    main()
