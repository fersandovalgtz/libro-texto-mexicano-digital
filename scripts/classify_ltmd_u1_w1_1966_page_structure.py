#!/usr/bin/env python3
"""Classify LTMD-U1 W1 1966 page structure with the same conservative CN logic."""
from __future__ import annotations
import csv
from collections import Counter,defaultdict
from pathlib import Path

METRICS=Path('data/catalog/ltmd_u1_w1_1966_ocr_metrics.csv')
FLAGS=Path('data/catalog/ltmd_u1_w1_1966_structural_keyword_flags.csv')
OUT=Path('data/catalog/ltmd_u1_w1_1966_page_structure.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w1_1966_page_structure_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w1_1966_page_structure.md')
VERSION='PAGESTRUCT_LTMD_U1_W1_1966_0.1'
EXPECTED_PAGES=340

def fnum(v,d=None):
    try:return float(v)
    except (TypeError,ValueError):return d

def inum(v,d=0):
    try:return int(float(v))
    except (TypeError,ValueError):return d

def classify(r,k):
    words=inum(r.get('recognized_words'));conf=fnum(r.get('mean_word_confidence'),0) or 0;low=fnum(r.get('low_confidence_word_rate'),1);psm=inum(r.get('selected_psm'));oc=r.get('ocr_class','')
    front=inum(k.get('front_zone'));end=inum(k.get('end_zone'));fs=inum(k.get('front_matter_score'));ns=inum(k.get('toc_navigation_score'));bs=inum(k.get('bibliography_credits_score'))
    fallback=psm in (6,11);visual=oc=='no_text_detected' or (fallback and conf<50 and low>=.65) or (words<=3 and conf<50);strong=words>=120 and conf>=75 and low<=.25;moderate=words>=20 and conf>=60 and low<=.40;dense_end=end and words>=800 and conf<85
    flags=[]
    if front:flags.append('front_zone')
    if end:flags.append('end_zone')
    if fallback:flags.append('fallback_psm')
    if visual:flags.append('visual_noise')
    if strong:flags.append('text_rich')
    elif moderate:flags.append('text_present')
    if dense_end:flags.append('dense_end_uncertain')
    if fs:flags.append('front_kw')
    if ns:flags.append('nav_kw')
    if bs:flags.append('biblio_credit_kw')
    if bs>=2 or (bs>=1 and (front or end) and conf>=55):primary,certainty,rule='bibliography_or_credits',('high' if bs>=2 else 'medium'),'KW_BIBLIO_CREDITS'
    elif ns>=2 or (ns>=1 and front and conf>=65):primary,certainty,rule='toc_or_navigation',('high' if ns>=2 else 'medium'),'KW_NAVIGATION'
    elif fs>=1 and front and conf>=55:primary,certainty,rule='front_matter',('medium' if fs==1 else 'high'),'KW_FRONT_MATTER'
    elif visual:primary,certainty,rule='visual_only',('high' if (fallback and low>=.80) or oc=='no_text_detected' else 'medium'),'OCR_VISUAL_NOISE'
    elif dense_end:primary,certainty,rule='unknown','medium','END_ZONE_DENSE_UNCERTAIN'
    elif strong:primary,certainty,rule='textual','high','OCR_TEXT_RICH'
    elif moderate:primary,certainty,rule='mixed_text_image','medium','OCR_MODERATE_TEXT'
    elif words>=4 and conf>=75 and low<=.30:primary,certainty,rule='mixed_text_image','low','OCR_SPARSE_HIGH_CONF'
    else:primary,certainty,rule='unknown','low','CONSERVATIVE_UNKNOWN'
    return primary,certainty,rule,';'.join(flags)

def main():
    metrics=list(csv.DictReader(METRICS.open(encoding='utf-8')));flags={r['page_id']:r for r in csv.DictReader(FLAGS.open(encoding='utf-8'))}
    if len(metrics)!=EXPECTED_PAGES:raise SystemExit(f'expected {EXPECTED_PAGES} W1 1966 source pages, found {len(metrics)}')
    out=[]
    for r in metrics:
        k=flags.get(r['page_id'],{});primary,certainty,rule,evidence=classify(r,k)
        out.append({'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':r['viewer_page'],'selected_psm':r['selected_psm'],'recognized_words':r['recognized_words'],'mean_word_confidence':r['mean_word_confidence'],'low_confidence_word_rate':r['low_confidence_word_rate'],'ocr_class':r['ocr_class'],'front_matter_score':k.get('front_matter_score',''),'toc_navigation_score':k.get('toc_navigation_score',''),'bibliography_credits_score':k.get('bibliography_credits_score',''),'primary_structure':primary,'classification_certainty':certainty,'classification_rule':rule,'evidence_flags':evidence,'classifier_version':VERSION})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    counts=defaultdict(Counter)
    for r in out:counts[r['book_id']][r['primary_structure']]+=1;counts['ALL'][r['primary_structure']]+=1
    classes=['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown'];summary=[]
    for bid in sorted([x for x in counts if x!='ALL'])+['ALL']:
        c=counts[bid];row={'book_id':bid,'n_pages':sum(c.values())};row.update({cl:c[cl] for cl in classes});summary.append(row)
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    allc=counts['ALL'];eligible=allc['textual']+allc['mixed_text_image']
    lines=['# PAGESTRUCT — LTMD-U1 W1 1966','',f'Versión: `{VERSION}`. Páginas clasificadas: **{len(out):,}**.','', '## Total']
    for cl in classes:lines.append(f'- `{cl}`: {allc[cl]:,}.')
    lines+=['',f'Páginas elegibles para FRAGSEG (`textual` + `mixed_text_image`): **{eligible:,}**.','', '## Regla','Se conserva la lógica conservadora usada en CN4/CN6 y Ola 2. La clasificación estructural no constituye clasificación pedagógica ni `semantic_ready`.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
