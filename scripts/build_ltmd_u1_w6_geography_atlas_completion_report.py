#!/usr/bin/env python3
"""Build the technical completion report for LTMD-U1 W6 Geography/Atlas."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
PROC=Path('data/catalog/ltmd_u1_w6_geography_atlas_processing_inventory.csv');MAN=Path('data/catalog/ltmd_u1_w6_geography_atlas_canonical_page_manifest.csv');OCR=Path('data/catalog/ltmd_u1_w6_geography_atlas_ocr_metrics.csv');STRUCT=Path('data/catalog/ltmd_u1_w6_geography_atlas_page_structure.csv');FRAGS=Path('data/catalog/ltmd_u1_w6_geography_atlas_fragment_manifest.csv');FRAG_SUM=Path('data/catalog/ltmd_u1_w6_geography_atlas_fragment_manifest_summary.csv');FRAG_GAPS=Path('data/catalog/ltmd_u1_w6_geography_atlas_fragment_sequence_gaps.csv');UNITS=Path('data/catalog/ltmd_u1_w6_geography_atlas_exact_content_units.csv');OVERLAP=Path('data/catalog/ltmd_u1_w6_geography_atlas_exact_viewer_overlap.csv');ROUTES=Path('data/catalog/ltmd_u1_w6_geography_atlas_2018_2019_route_relationships.csv');RECOVERY=Path('data/catalog/ltmd_u1_w6_h2008p4ge273_gap_recovery.csv');OUT=Path('docs/LTMD_U1_W6_COMPLETION.md');VERSION='LTMD_U1_W6_COMPLETION_0.1';EXPECTED_IDENTITIES=42;EXPECTED_CANONICAL=37;EXPECTED_ALIASES=5;EXPECTED_PAGES=5258

def read(p):
 if not p.exists():raise SystemExit(f'missing finalized W6 artifact: {p}')
 return list(csv.DictReader(p.open(encoding='utf-8',newline='')))
def main():
 proc=read(PROC);man=read(MAN);ocr=read(OCR);struct=read(STRUCT);frags=read(FRAGS);frag_sum=read(FRAG_SUM);gap_rows=read(FRAG_GAPS);units=read(UNITS);overlap=read(OVERLAP);routes=read(ROUTES);recovery=read(RECOVERY)
 if len(proc)!=EXPECTED_IDENTITIES or len({r['viewer_key'] for r in proc})!=EXPECTED_IDENTITIES:raise SystemExit('W6 processing inventory failure')
 canonical={r['viewer_key'] for r in proc if r['is_canonical_processing_object']=='1'};aliases=[r for r in proc if r['processing_mode']=='route_alias_to_2019']
 if len(canonical)!=EXPECTED_CANONICAL or len(aliases)!=EXPECTED_ALIASES:raise SystemExit('W6 topology cardinality failure')
 modes=Counter(r['processing_mode'] for r in proc if r['viewer_key'] in canonical)
 if modes['direct_canonical']!=36 or modes['direct_canonical_reconciled_gap']!=1 or proc[[i for i,r in enumerate(proc) if r['viewer_key']=='H2008P4GE273'][0]]['processing_mode']!='direct_canonical_reconciled_gap':raise SystemExit('W6 canonical topology mode failure')
 if any(int(r['persistent_source_gaps'])!=0 for r in proc):raise SystemExit('W6 persistent source gap')
 if len(routes)!=EXPECTED_ALIASES or any(r['complete_route_resolution']!='1' for r in routes):raise SystemExit('W6 route resolution evidence failure')
 if len(recovery)!=2 or {int(r['viewer_page']) for r in recovery}!={70,117} or any(r['candidate_live_verified']!='1' for r in recovery):raise SystemExit('W6 gap recovery evidence failure')
 if len(man)!=EXPECTED_PAGES or len({(r['viewer_key'],r['viewer_page']) for r in man})!=EXPECTED_PAGES or {r['viewer_key'] for r in man}!=canonical:raise SystemExit('W6 page manifest failure')
 if sum(r['source_kind']=='cryptographically_recovered_same_position_reference' for r in man)!=2:raise SystemExit('W6 recovered page manifest failure')
 if len(ocr)!=EXPECTED_PAGES or {r['ocr_version'] for r in ocr}!={'LTMD_U1_W6_GEOGRAPHY_ATLAS_OCR_0.1'}:raise SystemExit('W6 OCR cardinality/version failure')
 if any(r['source_sha256_verified']!='1' or r['ocr_status']!='ok' or r['ocr_class']=='unresolved' for r in ocr):raise SystemExit('W6 OCR provenance/execution failure')
 text=sum(r['ocr_class']=='text_detected' for r in ocr);no_text=sum(r['ocr_class']=='no_text_detected' for r in ocr)
 if text+no_text!=EXPECTED_PAGES:raise SystemExit('W6 OCR accounting failure')
 if len(struct)!=EXPECTED_PAGES or {r['classifier_version'] for r in struct}!={'PAGESTRUCT_LTMD_U1_W6_GEOGRAPHY_ATLAS_0.1'} or {r['viewer_key'] for r in struct}!=canonical:raise SystemExit('W6 PAGESTRUCT failure')
 sc=Counter(r['primary_structure'] for r in struct);eligible=sc['textual']+sc['mixed_text_image']
 if not frags or {r['segmenter_version'] for r in frags}!={'FRAGSEG_LTMD_U1_W6_GEOGRAPHY_ATLAS_0.1'} or {r['viewer_key'] for r in frags}!=canonical:raise SystemExit('W6 FRAGSEG failure')
 ids=[r['fragment_id'] for r in frags]
 if len(ids)!=len(set(ids)):raise SystemExit('duplicate W6 fragment IDs')
 allsum=[r for r in frag_sum if r['viewer_key']=='ALL']
 if len(allsum)!=1 or int(allsum[0]['fragment_count'])!=len(frags):raise SystemExit('W6 FRAGSEG summary mismatch')
 segmented=int(allsum[0]['segmented_page_count']);empty=eligible-segmented;slots=sum(int(r.get('missing_slot_count') or 0) for r in gap_rows)
 hashes={r['text_sha256'] for r in frags}
 if len(units)!=len(hashes) or {r['text_sha256'] for r in units}!=hashes:raise SystemExit('W6 exact content-unit mismatch')
 repeated=sum(int(r['occurrence_count'])>1 for r in units);cross=sum(int(r['viewer_count'])>1 for r in units);crossgen=sum(int(r['catalog_generation_count'])>1 for r in units);types=Counter(r['candidate_type'] for r in frags);classes=['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown']
 lines=['# LTMD-U1 W6 — cierre técnico Geografía/Atlas','',f'Versión: `{VERSION}`.','','## Resultado ejecutivo',f'- Identidades históricas técnicamente cubiertas: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}**.',f'- Objetos canónicos de procesamiento: **{EXPECTED_CANONICAL}**.',f'- Aliases operacionales de ruta 2018→2019: **{EXPECTED_ALIASES}**.','- Aliases de libro completo byte-exacto entre fuentes directas: **0**.','- Páginas internas recuperadas criptográficamente: **2** (`H2008P4GE273`, páginas 70 y 117).','- Huecos internos de fuente después de reconciliación: **0**.',f'- Páginas canónicas: **{EXPECTED_PAGES:,}**.','','## OCR 0.1',f'- SHA-256 verificados: **{EXPECTED_PAGES:,}/{EXPECTED_PAGES:,}**.',f'- Texto detectado: **{text:,} ({100*text/EXPECTED_PAGES:.2f}%)**.',f'- `no_text_detected`: **{no_text:,}**.','- `unresolved`: **0**.','','## PAGESTRUCT 0.1']
 for c in classes:lines.append(f'- `{c}`: **{sc[c]:,}**.')
 lines+=['',f'- Páginas elegibles para FRAGSEG: **{eligible:,}**.','','## FRAGSEG 0.1',f'- Páginas con ≥1 fragmento: **{segmented:,}**.',f'- Páginas elegibles sin fragmentos: **{empty:,}**.',f'- Fragmentos técnicos: **{len(frags):,}**.',f'- IDs únicos: **{len(set(ids)):,}**.',f'- Páginas con huecos legítimos de secuencia: **{len(gap_rows):,}**.',f'- Slots omitidos: **{slots:,}**.','','### Tipos candidatos']
 for t in sorted(types):lines.append(f'- `{t}`: **{types[t]:,}**.')
 lines+=['','## Reutilización textual exacta',f'- Unidades exactas únicas: **{len(units):,}**.',f'- Unidades repetidas: **{repeated:,}**.',f'- Unidades presentes en ≥2 visores canónicos: **{cross:,}**.',f'- Unidades presentes en ≥2 generaciones canónicas: **{crossgen:,}**.',f'- Pares de visores canónicos con ≥1 unidad exacta compartida: **{len(overlap):,}**.','','## Límite epistemológico','Este cierre es técnico. Los cinco visores 2018 conservan identidad institucional independiente aunque su contenido operativo se resuelva mediante rutas 2019 demostradas. `H2008P4GE273` conserva identidad canónica propia; sus dos activos recuperados documentan únicamente continuidad byte-exacta de misma posición con la fuente 1993. Sin referencia humana no se afirma CER/WER validado, desempeño semántico contra gold standard ni equivalencia curricular/pedagógica. PAGESTRUCT, FRAGSEG y `text_sha256` son infraestructura y evidencia de estructura/dependencia documental, no sustitutos de validación humana. `WAITING_HUMAN_REFERENCE` permanece vigente.']
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(OUT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
