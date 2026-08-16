#!/usr/bin/env python3
"""Classify canonical W7 Civics/Ethics pages with conservative PAGESTRUCT logic."""
from __future__ import annotations
import csv
from collections import Counter,defaultdict
from pathlib import Path
METRICS=Path('data/catalog/ltmd_u1_w7_civics_ethics_ocr_metrics.csv');FLAGS=Path('data/catalog/ltmd_u1_w7_civics_ethics_structural_keyword_flags.csv');OUT=Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure.csv');SUMMARY=Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure_summary.csv');REPORT=Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure.md');VERSION='PAGESTRUCT_LTMD_U1_W7_CIVICS_ETHICS_0.1';EXPECTED=25;EXPECTED_PAGES=3261

def fnum(v,d=None):
 try:return float(v)
 except (TypeError,ValueError):return d
def inum(v,d=0):
 try:return int(float(v))
 except (TypeError,ValueError):return d
def classify(row,kw):
 words=inum(row.get('recognized_words'));conf=fnum(row.get('mean_word_confidence'),0) or 0;low=fnum(row.get('low_confidence_word_rate'),1);psm=inum(row.get('selected_psm'));oc=row.get('ocr_class','');front=inum(kw.get('front_zone'));end=inum(kw.get('end_zone'));fs=inum(kw.get('front_matter_score'));ns=inum(kw.get('toc_navigation_score'));bs=inum(kw.get('bibliography_credits_score'));fallback=psm in (6,11);visual=oc=='no_text_detected' or (fallback and conf<50 and low>=.65) or (words<=3 and conf<50);strong=words>=120 and conf>=75 and low<=.25;moderate=words>=20 and conf>=60 and low<=.40;dense=end and words>=800 and conf<85;e=[]
 if front:e.append('front_zone')
 if end:e.append('end_zone')
 if fallback:e.append('fallback_psm')
 if visual:e.append('visual_noise')
 if strong:e.append('text_rich')
 elif moderate:e.append('text_present')
 if dense:e.append('dense_end_uncertain')
 if fs:e.append('front_kw')
 if ns:e.append('nav_kw')
 if bs:e.append('biblio_credit_kw')
 if bs>=2 or (bs>=1 and (front or end) and conf>=55):return 'bibliography_or_credits','high' if bs>=2 else 'medium','KW_BIBLIO_CREDITS',';'.join(e)
 if ns>=2 or (ns>=1 and front and conf>=65):return 'toc_or_navigation','high' if ns>=2 else 'medium','KW_NAVIGATION',';'.join(e)
 if fs>=1 and front and conf>=55:return 'front_matter','medium' if fs==1 else 'high','KW_FRONT_MATTER',';'.join(e)
 if visual:return 'visual_only','high' if (fallback and low>=.80) or oc=='no_text_detected' else 'medium','OCR_VISUAL_NOISE',';'.join(e)
 if dense:return 'unknown','medium','END_ZONE_DENSE_UNCERTAIN',';'.join(e)
 if strong:return 'textual','high','OCR_TEXT_RICH',';'.join(e)
 if moderate:return 'mixed_text_image','medium','OCR_MODERATE_TEXT',';'.join(e)
 if words>=4 and conf>=75 and low<=.30:return 'mixed_text_image','low','OCR_SPARSE_HIGH_CONF',';'.join(e)
 return 'unknown','low','CONSERVATIVE_UNKNOWN',';'.join(e)
def main():
 metrics=list(csv.DictReader(METRICS.open(encoding='utf-8',newline='')));flags={r['page_id']:r for r in csv.DictReader(FLAGS.open(encoding='utf-8',newline=''))}
 if len(metrics)!=EXPECTED_PAGES or len({r['viewer_key'] for r in metrics})!=EXPECTED:raise SystemExit('W7 PAGESTRUCT OCR coverage mismatch')
 if any(r['source_sha256_verified']!='1' or r['ocr_status']!='ok' for r in metrics):raise SystemExit('W7 PAGESTRUCT refuses unverified/unresolved OCR rows')
 out=[]
 for r in metrics:
  p,c,rule,e=classify(r,flags.get(r['page_id'],{}));kw=flags.get(r['page_id'],{})
  out.append({'page_id':r['page_id'],'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'title_core':r['title_core'],'viewer_page':r['viewer_page'],'selected_psm':r['selected_psm'],'recognized_words':r['recognized_words'],'mean_word_confidence':r['mean_word_confidence'],'low_confidence_word_rate':r['low_confidence_word_rate'],'ocr_class':r['ocr_class'],'front_matter_score':kw.get('front_matter_score',''),'toc_navigation_score':kw.get('toc_navigation_score',''),'bibliography_credits_score':kw.get('bibliography_credits_score',''),'primary_structure':p,'classification_certainty':c,'classification_rule':rule,'evidence_flags':e,'classifier_version':VERSION})
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 counts=defaultdict(Counter)
 for r in out:counts[r['viewer_key']][r['primary_structure']]+=1;counts['ALL'][r['primary_structure']]+=1
 classes=['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown'];summary=[]
 for k in sorted([x for x in counts if x!='ALL'])+['ALL']:
  c=counts[k];rec={'viewer_key':k,'n_pages':sum(c.values())};rec.update({cl:c[cl] for cl in classes});summary.append(rec)
 with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
 allc=counts['ALL'];eligible=allc['textual']+allc['mixed_text_image'];lines=['# PAGESTRUCT — LTMD-U1 W7 Cívica/Ética','',f'Versión: `{VERSION}`. Páginas clasificadas: **{len(out):,}**.','',f'Objetos canónicos: **{EXPECTED}**.','Identidades históricas retenidas por fuente y excluidas de PAGESTRUCT: **5**.','','## Total']
 for cl in classes:lines.append(f'- `{cl}`: {allc[cl]:,}.')
 lines+=['',f'Páginas elegibles para FRAGSEG (`textual` + `mixed_text_image`): **{eligible:,}**.','','## Regla','Se conserva la misma lógica PAGESTRUCT conservadora empleada en W4 para mantener comparabilidad técnica. Esta capa es estructural, no semántica. Las cinco identidades retenidas por fuente permanecen fuera de esta cohorte de procesamiento y no se imputan ni sustituyen. La ausencia de referencia humana no impide PAGESTRUCT/FRAGSEG, pero sí impide tratar clasificadores semánticos no validados como evidencia histórica primaria.']
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
