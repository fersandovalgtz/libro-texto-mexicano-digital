#!/usr/bin/env python3
from __future__ import annotations
import csv
from collections import Counter,defaultdict
from pathlib import Path
from classify_ltmd_u1_w1_1966_page_structure import classify
MET=Path('data/catalog/ltmd_u1_w1_2008_ocr_metrics.csv');FLAGS=Path('data/catalog/ltmd_u1_w1_2008_structural_keyword_flags.csv');OUT=Path('data/catalog/ltmd_u1_w1_2008_page_structure.csv');SUMMARY=Path('data/catalog/ltmd_u1_w1_2008_page_structure_summary.csv');REPORT=Path('data/catalog/ltmd_u1_w1_2008_page_structure.md');VERSION='PAGESTRUCT_LTMD_U1_W1_2008_0.1';EXPECTED=355
def main():
 met=list(csv.DictReader(MET.open(encoding='utf-8')));flags={r['page_id']:r for r in csv.DictReader(FLAGS.open(encoding='utf-8'))}
 if len(met)!=EXPECTED:raise SystemExit(f'expected {EXPECTED} pages got {len(met)}')
 out=[]
 for r in met:
  k=flags.get(r['page_id'],{});primary,certainty,rule,evidence=classify(r,k);out.append({'page_id':r['page_id'],'book_id':r['book_id'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':r['viewer_page'],'selected_psm':r['selected_psm'],'recognized_words':r['recognized_words'],'mean_word_confidence':r['mean_word_confidence'],'low_confidence_word_rate':r['low_confidence_word_rate'],'ocr_class':r['ocr_class'],'front_matter_score':k.get('front_matter_score',''),'toc_navigation_score':k.get('toc_navigation_score',''),'bibliography_credits_score':k.get('bibliography_credits_score',''),'primary_structure':primary,'classification_certainty':certainty,'classification_rule':rule,'evidence_flags':evidence,'classifier_version':VERSION})
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 counts=defaultdict(Counter)
 for r in out:counts[r['book_id']][r['primary_structure']]+=1;counts['ALL'][r['primary_structure']]+=1
 classes=['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown'];s=[]
 for b in sorted([x for x in counts if x!='ALL'])+['ALL']:
  c=counts[b];row={'book_id':b,'n_pages':sum(c.values())};row.update({cl:c[cl] for cl in classes});s.append(row)
 with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(s[0]));w.writeheader();w.writerows(s)
 c=counts['ALL'];eligible=c['textual']+c['mixed_text_image'];lines=['# PAGESTRUCT — LTMD-U1 W1 2008','',f'Versión: `{VERSION}`. Páginas: **{len(out)}**.','']+[f'- `{cl}`: {c[cl]}.' for cl in classes]+['',f'Páginas elegibles para FRAGSEG: **{eligible}**.','','Se usa exactamente la lógica conservadora de W1 1966/CN previo; esta capa no es `semantic_ready`.'];REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text())
if __name__=='__main__':main()
