#!/usr/bin/env python3
"""Build the technical completion report for LTMD-U1 W4 Social Sciences."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
PROC=Path('data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv');MAN=Path('data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv');OCR=Path('data/catalog/ltmd_u1_w4_social_sciences_ocr_metrics.csv');STRUCT=Path('data/catalog/ltmd_u1_w4_social_sciences_page_structure.csv');FRAGS=Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest.csv');FRAG_SUM=Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest_summary.csv');FRAG_GAPS=Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_sequence_gaps.csv');UNITS=Path('data/catalog/ltmd_u1_w4_social_sciences_exact_content_units.csv');OVERLAP=Path('data/catalog/ltmd_u1_w4_social_sciences_exact_viewer_overlap.csv');OUT=Path('docs/LTMD_U1_W4_COMPLETION.md');VERSION='LTMD_U1_W4_COMPLETION_0.1';EXPECTED=14;EXPECTED_PAGES=2414

def read(p):
 if not p.exists():raise SystemExit(f'missing finalized W4 artifact: {p}')
 return list(csv.DictReader(p.open(encoding='utf-8',newline='')))
def main():
 proc=read(PROC);man=read(MAN);ocr=read(OCR);struct=read(STRUCT);frags=read(FRAGS);frag_sum=read(FRAG_SUM);gap_rows=read(FRAG_GAPS);units=read(UNITS);overlap=read(OVERLAP)
 if len(proc)!=EXPECTED or len({r['viewer_key'] for r in proc})!=EXPECTED:raise SystemExit('W4 processing inventory failure')
 if any(r['processing_mode']!='direct_canonical' or r['is_canonical_processing_object']!='1' or r['ocr_identity_eligible']!='1' for r in proc):raise SystemExit('W4 topology not 14 direct canonicals')
 if len(man)!=EXPECTED_PAGES or len({(r['viewer_key'],r['viewer_page']) for r in man})!=EXPECTED_PAGES:raise SystemExit('W4 page manifest failure')
 if len(ocr)!=EXPECTED_PAGES or {r['ocr_version'] for r in ocr}!={'LTMD_U1_W4_SOCIAL_SCIENCES_OCR_0.1'}:raise SystemExit('W4 OCR cardinality/version failure')
 if any(r['source_sha256_verified']!='1' or r['ocr_status']!='ok' or r['ocr_class']=='unresolved' for r in ocr):raise SystemExit('W4 OCR provenance/execution failure')
 text=sum(r['ocr_class']=='text_detected' for r in ocr);no_text=sum(r['ocr_class']=='no_text_detected' for r in ocr)
 if text+no_text!=EXPECTED_PAGES:raise SystemExit('W4 OCR accounting failure')
 if len(struct)!=EXPECTED_PAGES or {r['classifier_version'] for r in struct}!={'PAGESTRUCT_LTMD_U1_W4_SOCIAL_SCIENCES_0.1'}:raise SystemExit('W4 PAGESTRUCT failure')
 sc=Counter(r['primary_structure'] for r in struct);eligible=sc['textual']+sc['mixed_text_image']
 if not frags or {r['segmenter_version'] for r in frags}!={'FRAGSEG_LTMD_U1_W4_SOCIAL_SCIENCES_0.1'} or len({r['viewer_key'] for r in frags})!=EXPECTED:raise SystemExit('W4 FRAGSEG failure')
 ids=[r['fragment_id'] for r in frags]
 if len(ids)!=len(set(ids)):raise SystemExit('duplicate W4 fragment IDs')
 allsum=[r for r in frag_sum if r['viewer_key']=='ALL']
 if len(allsum)!=1 or int(allsum[0]['fragment_count'])!=len(frags):raise SystemExit('W4 FRAGSEG summary mismatch')
 segmented=int(allsum[0]['segmented_page_count']);empty=eligible-segmented;slots=sum(int(r.get('missing_slot_count') or 0) for r in gap_rows)
 hashes={r['text_sha256'] for r in frags}
 if len(units)!=len(hashes) or {r['text_sha256'] for r in units}!=hashes:raise SystemExit('W4 exact content-unit mismatch')
 repeated=sum(int(r['occurrence_count'])>1 for r in units);cross=sum(int(r['viewer_count'])>1 for r in units);crossgen=sum(int(r['catalog_generation_count'])>1 for r in units);types=Counter(r['candidate_type'] for r in frags);classes=['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown']
 lines=['# LTMD-U1 W4 — cierre técnico Ciencias Sociales','',f'Versión: `{VERSION}`.','','## Resultado ejecutivo',f'- Identidades/canónicos técnicos: **{EXPECTED}/{EXPECTED}**.', '- Aliases de libro completo byte-exacto: **0**.','- Huecos internos de fuente: **0**.',f'- Páginas canónicas: **{EXPECTED_PAGES:,}**.','','## OCR 0.1',f'- SHA-256 verificados: **{EXPECTED_PAGES:,}/{EXPECTED_PAGES:,}**.',f'- Texto detectado: **{text:,} ({100*text/EXPECTED_PAGES:.2f}%)**.',f'- `no_text_detected`: **{no_text:,}**.','- `unresolved`: **0**.','','## PAGESTRUCT 0.1']
 for c in classes:lines.append(f'- `{c}`: **{sc[c]:,}**.')
 lines+=['',f'- Páginas elegibles para FRAGSEG: **{eligible:,}**.','','## FRAGSEG 0.1',f'- Páginas con ≥1 fragmento: **{segmented:,}**.',f'- Páginas elegibles sin fragmentos: **{empty:,}**.',f'- Fragmentos técnicos: **{len(frags):,}**.',f'- IDs únicos: **{len(set(ids)):,}**.',f'- Páginas con huecos legítimos de secuencia: **{len(gap_rows):,}**.',f'- Slots omitidos: **{slots:,}**.','','### Tipos candidatos']
 for t in sorted(types):lines.append(f'- `{t}`: **{types[t]:,}**.')
 lines+=['','## Reutilización textual exacta',f'- Unidades exactas únicas: **{len(units):,}**.',f'- Unidades repetidas: **{repeated:,}**.',f'- Unidades presentes en ≥2 visores: **{cross:,}**.',f'- Unidades presentes en ≥2 generaciones: **{crossgen:,}**.',f'- Pares de visores con ≥1 unidad exacta compartida: **{len(overlap):,}**.','','## Límite epistemológico','Este cierre es técnico. El proyecto opera temporalmente sin referencia humana: no se afirma CER/WER validado, desempeño semántico contra gold standard ni equivalencia curricular/pedagógica a partir de las categorías automáticas. PAGESTRUCT, FRAGSEG y `text_sha256` se usan como infraestructura y evidencia de estructura/dependencia documental, no como sustituto de validación humana.']
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(OUT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
