#!/usr/bin/env python3
"""Validate and report technical closure of the source-admitted LTMD-U1 W7 cohort.

This report never upgrades the five source-withheld historical identities into
processed objects. It cross-validates finalized W7 artifacts and fails on any
coverage, provenance, version, topology or accounting inconsistency.
"""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

PROC=Path('data/catalog/ltmd_u1_w7_processing_inventory.csv')
MAN=Path('data/catalog/ltmd_u1_w7_canonical_page_manifest.csv')
OCR=Path('data/catalog/ltmd_u1_w7_civics_ethics_ocr_metrics.csv')
OCR_SUM=Path('data/catalog/ltmd_u1_w7_civics_ethics_ocr_summary.csv')
STRUCT=Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure.csv')
STRUCT_SUM=Path('data/catalog/ltmd_u1_w7_civics_ethics_page_structure_summary.csv')
FRAGS=Path('data/catalog/ltmd_u1_w7_civics_ethics_fragment_manifest.csv')
FRAG_SUM=Path('data/catalog/ltmd_u1_w7_civics_ethics_fragment_manifest_summary.csv')
FRAG_GAPS=Path('data/catalog/ltmd_u1_w7_civics_ethics_fragment_sequence_gaps.csv')
UNITS=Path('data/catalog/ltmd_u1_w7_civics_ethics_exact_content_units.csv')
OVERLAP=Path('data/catalog/ltmd_u1_w7_civics_ethics_exact_viewer_overlap.csv')
OUT=Path('docs/LTMD_U1_W7_COMPLETION.md')
VERSION='LTMD_U1_W7_COMPLETION_0.1'
PROC_VERSION='LTMD_U1_W7_PROCESSING_0.1'
MAN_VERSION='LTMD_U1_W7_CANONICAL_PAGE_MANIFEST_0.1'
OCR_VERSION='LTMD_U1_W7_CIVICS_ETHICS_OCR_0.1'
STRUCT_VERSION='PAGESTRUCT_LTMD_U1_W7_CIVICS_ETHICS_0.1'
FRAG_VERSION='FRAGSEG_LTMD_U1_W7_CIVICS_ETHICS_0.1'
REUSE_VERSION='LTMD_U1_W7_CIVICS_ETHICS_EXACT_REUSE_0.1'
EXPECTED_TOTAL=30;EXPECTED_CANONICAL=25;EXPECTED_WITHHELD=5;EXPECTED_PAGES=3261
STRUCT_CLASSES=['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown']

def read(path):
 if not path.exists():raise SystemExit(f'missing finalized W7 artifact: {path}')
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def req(cond,msg):
 if not cond:raise SystemExit(f'W7 completion: {msg}')
def main():
 proc=read(PROC);man=read(MAN);ocr=read(OCR);ocr_sum=read(OCR_SUM);struct=read(STRUCT);struct_sum=read(STRUCT_SUM);frags=read(FRAGS);frag_sum=read(FRAG_SUM);gaps=read(FRAG_GAPS);units=read(UNITS);overlap=read(OVERLAP)
 req(len(proc)==EXPECTED_TOTAL and len({r['viewer_key'] for r in proc})==EXPECTED_TOTAL,'processing inventory cardinality')
 req({r['processing_version'] for r in proc}=={PROC_VERSION},'processing version drift')
 canonical={r['viewer_key'] for r in proc if r['ocr_identity_eligible']=='1' and r['is_canonical_processing_object']=='1'};withheld={r['viewer_key'] for r in proc if r['ocr_identity_eligible']=='0'}
 req(len(canonical)==EXPECTED_CANONICAL and len(withheld)==EXPECTED_WITHHELD and not canonical&withheld,'canonical/withheld topology')
 req(all(next(x for x in proc if x['viewer_key']==k)['processing_mode']=='direct_canonical' for k in canonical),'canonical processing mode drift')
 req(len(man)==EXPECTED_PAGES and {r['viewer_key'] for r in man}==canonical,'canonical page coverage')
 req({r['manifest_version'] for r in man}=={MAN_VERSION},'canonical manifest version')
 req(all(r['asset_status']=='source_jpeg' and r['page_numbering_policy']=='preserve_original_viewer_page_no_renumbering' for r in man),'canonical source/page policy drift')
 req(len({(r['viewer_key'],r['viewer_page']) for r in man})==EXPECTED_PAGES,'duplicate canonical viewer/page')
 req(len(ocr)==EXPECTED_PAGES and len(ocr_sum)==EXPECTED_CANONICAL,'OCR cardinality')
 req({r['ocr_version'] for r in ocr}=={OCR_VERSION},'OCR version')
 req({r['viewer_key'] for r in ocr}==canonical,'OCR viewer coverage')
 req(all(r['source_sha256_verified']=='1' and r['ocr_status']=='ok' and r['ocr_class']!='unresolved' for r in ocr),'OCR provenance/execution')
 req(sum(int(r['pages']) for r in ocr_sum)==EXPECTED_PAGES and sum(int(r['sha_verified']) for r in ocr_sum)==EXPECTED_PAGES and sum(int(r['unresolved']) for r in ocr_sum)==0,'OCR summary accounting')
 text=sum(r['ocr_class']=='text_detected' for r in ocr);no_text=sum(r['ocr_class']=='no_text_detected' for r in ocr);req(text+no_text==EXPECTED_PAGES,'OCR class accounting')
 req(len(struct)==EXPECTED_PAGES and {r['viewer_key'] for r in struct}==canonical,'PAGESTRUCT coverage')
 req({r['classifier_version'] for r in struct}=={STRUCT_VERSION},'PAGESTRUCT version')
 sc=Counter(r['primary_structure'] for r in struct);req(set(sc)<=set(STRUCT_CLASSES),'unexpected PAGESTRUCT class')
 all_struct=[r for r in struct_sum if r['viewer_key']=='ALL'];req(len(all_struct)==1 and int(all_struct[0]['n_pages'])==EXPECTED_PAGES,'PAGESTRUCT ALL summary')
 for cls in STRUCT_CLASSES:req(int(all_struct[0][cls])==sc[cls],f'PAGESTRUCT summary {cls}')
 eligible=sc['textual']+sc['mixed_text_image'];req(eligible>0,'zero FRAGSEG-eligible pages')
 per={k:0 for k in canonical}
 for r in struct:
  if r['primary_structure'] in {'textual','mixed_text_image'}:per[r['viewer_key']]+=1
 req(all(per.values()),'one or more canonical viewers have zero FRAGSEG-eligible pages')
 req(bool(frags) and {r['viewer_key'] for r in frags}==canonical,'FRAGSEG viewer coverage')
 req({r['segmenter_version'] for r in frags}=={FRAG_VERSION},'FRAGSEG version')
 ids=[r['fragment_id'] for r in frags];req(len(ids)==len(set(ids)),'duplicate fragment IDs');req(all(r.get('text_sha256') for r in frags),'fragment missing text_sha256')
 all_frag=[r for r in frag_sum if r['viewer_key']=='ALL'];req(len(all_frag)==1 and all_frag[0]['segmenter_version']==FRAG_VERSION,'FRAGSEG ALL summary')
 req(int(all_frag[0]['fragment_count'])==len(frags),'FRAGSEG fragment summary mismatch')
 segmented_pages=len({r['page_id'] for r in frags});req(int(all_frag[0]['segmented_page_count'])==segmented_pages,'FRAGSEG page summary mismatch');req(segmented_pages<=eligible,'FRAGSEG pages exceed eligible pages')
 candidate=Counter(r['candidate_type'] for r in frags);req(sum(candidate.values())==len(frags),'candidate accounting')
 for field in [f for f in all_frag[0] if f.endswith('_candidate')]:req(int(all_frag[0][field])==candidate[field],f'candidate summary {field}')
 gap_slots=sum(int(r.get('missing_slot_count') or 0) for r in gaps)
 req(bool(units) and {r['analysis_version'] for r in units}=={REUSE_VERSION},'exact-reuse units/version')
 req(len({r['text_sha256'] for r in units})==len(units),'duplicate exact-content hashes')
 req({r['text_sha256'] for r in units}=={r['text_sha256'] for r in frags},'exact-content/hash coverage')
 if overlap:req({r['analysis_version'] for r in overlap}=={REUSE_VERSION},'exact-reuse overlap version')
 repeated=sum(int(r['occurrence_count'])>1 for r in units);cross=sum(int(r['viewer_count'])>1 for r in units);crossgen=sum(int(r['catalog_generation_count'])>1 for r in units)
 lines=['# LTMD-U1 W7 — cierre técnico de la cohorte admisible Cívica/Ética','',f'Versión: `{VERSION}`.','','## Alcance y fuente',f'- Identidades históricas preservadas: **{EXPECTED_TOTAL}/{EXPECTED_TOTAL}**.',f'- Canónicos procesados: **{EXPECTED_CANONICAL}**.',f'- Identidades retenidas por fuente: **{EXPECTED_WITHHELD}**.','- Imputaciones o aliases para identidades retenidas: **0**.',f'- Páginas fuente canónicas: **{EXPECTED_PAGES:,}**.','','## OCR',f'- SHA-256 verificados: **{EXPECTED_PAGES:,}/{EXPECTED_PAGES:,}**.',f'- Texto detectado: **{text:,} ({100*text/EXPECTED_PAGES:.2f}%)**.',f'- `no_text_detected`: **{no_text:,}**.','- `unresolved`: **0**.','','## PAGESTRUCT']
 for cls in STRUCT_CLASSES:lines.append(f'- `{cls}`: **{sc[cls]:,}**.')
 lines+=['',f'- Páginas elegibles para FRAGSEG: **{eligible:,}**.','','## FRAGSEG',f'- Páginas con ≥1 fragmento: **{segmented_pages:,}**.',f'- Páginas elegibles sin fragmentos: **{eligible-segmented_pages:,}**.',f'- Fragmentos técnicos: **{len(frags):,}**.',f'- IDs únicos: **{len(set(ids)):,}**.',f'- Páginas con huecos legítimos de secuencia: **{len(gaps):,}**.',f'- Slots omitidos: **{gap_slots:,}**.','','### Tipos candidatos']
 for typ in sorted(candidate):lines.append(f'- `{typ}`: **{candidate[typ]:,}**.')
 lines+=['','## Reutilización textual exacta',f'- Unidades exactas únicas: **{len(units):,}**.',f'- Unidades repetidas: **{repeated:,}**.',f'- Unidades presentes en ≥2 visores: **{cross:,}**.',f'- Unidades presentes en ≥2 generaciones: **{crossgen:,}**.',f'- Pares de visores con ≥1 unidad exacta compartida: **{len(overlap):,}**.','','## Estado científico','Este documento cierra técnicamente la cohorte con fuente admisible; **no declara completo el W7 histórico**. Las cinco identidades retenidas permanecen explícitamente fuera del procesamiento por limitaciones de fuente. OCR, PAGESTRUCT, FRAGSEG y reutilización exacta son capas técnicas reproducibles; no sustituyen una referencia humana ni validan categorías históricas o semánticas.']
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(OUT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
