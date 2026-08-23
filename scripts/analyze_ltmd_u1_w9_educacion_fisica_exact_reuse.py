#!/usr/bin/env python3
"""Build exact-text reuse/document-dependence views for LTMD-U1 W9 Educación Física."""
from __future__ import annotations
import csv
from collections import defaultdict
from itertools import combinations
from pathlib import Path

FRAGS=Path('data/catalog/ltmd_u1_w9_educacion_fisica_fragment_manifest.csv')
PROC=Path('data/catalog/ltmd_u1_w9_processing_inventory.csv')
UNITS=Path('data/catalog/ltmd_u1_w9_educacion_fisica_exact_content_units.csv')
OVERLAP=Path('data/catalog/ltmd_u1_w9_educacion_fisica_exact_viewer_overlap.csv')
REPORT=Path('data/catalog/ltmd_u1_w9_educacion_fisica_exact_reuse.md')
VERSION='LTMD_U1_W9_EDUCACION_FISICA_EXACT_REUSE_0.1'
EXPECTED_TOTAL=4
EXPECTED_CANONICAL=4

def fmt(x):return f'{x:.6f}'

def main():
    frags=list(csv.DictReader(FRAGS.open(encoding='utf-8',newline='')))
    proc_rows=list(csv.DictReader(PROC.open(encoding='utf-8',newline='')))
    proc={r['viewer_key']:r for r in proc_rows}
    if not frags or len(proc_rows)!=EXPECTED_TOTAL or len(proc)!=EXPECTED_TOTAL:
        raise SystemExit('W9 exact-reuse input cardinality failure')
    canonical={r['viewer_key'] for r in proc_rows if r['is_canonical_processing_object']=='1' and r['ocr_identity_eligible']=='1'}
    withheld={r['viewer_key'] for r in proc_rows if r['ocr_identity_eligible']=='0'}
    if len(canonical)!=EXPECTED_CANONICAL or withheld:
        raise SystemExit('W9 exact-reuse topology mismatch')
    if any(proc[k]['processing_mode']!='direct_canonical' for k in canonical):
        raise SystemExit('W9 exact-reuse requires direct canonicals')
    if {r['viewer_key'] for r in frags}!=canonical:
        raise SystemExit('W9 FRAGSEG canonical viewer coverage mismatch')
    if {r['segmenter_version'] for r in frags}!={'FRAGSEG_LTMD_U1_W9_EDUCACION_FISICA_0.1'}:
        raise SystemExit('W9 FRAGSEG version mismatch')
    ids=[r['fragment_id'] for r in frags]
    if len(ids)!=len(set(ids)):
        raise SystemExit('duplicate W9 fragment IDs')
    by_hash=defaultdict(list);by_viewer_hashes=defaultdict(set)
    for r in frags:
        h=r['text_sha256']
        if not h:
            raise SystemExit(f'missing hash {r["fragment_id"]}')
        by_hash[h].append(r);by_viewer_hashes[r['viewer_key']].add(h)
    unit_rows=[]
    for h,rr in by_hash.items():
        viewers={r['viewer_key'] for r in rr};gens={proc[v]['catalog_generation'] for v in viewers};grades={proc[v]['grade_code'] for v in viewers};tokens={r['token_count'] for r in rr};chars={r['char_count'] for r in rr}
        if len(tokens)!=1 or len(chars)!=1:
            raise SystemExit(f'hash length mismatch {h}')
        unit_rows.append({'analysis_version':VERSION,'text_sha256':h,'token_count':next(iter(tokens)),'char_count':next(iter(chars)),'occurrence_count':len(rr),'viewer_count':len(viewers),'catalog_generation_count':len(gens),'grade_count':len(grades),'first_fragment_id':min(r['fragment_id'] for r in rr)})
    unit_rows.sort(key=lambda r:(-int(r['occurrence_count']),r['text_sha256']))
    with UNITS.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(unit_rows[0]));w.writeheader();w.writerows(unit_rows)
    overlap=[];keys=sorted(canonical,key=lambda k:(int(proc[k]['catalog_generation']),int(proc[k]['grade_code']),k))
    for a,b in combinations(keys,2):
        sa,sb=by_viewer_hashes[a],by_viewer_hashes[b];shared=len(sa&sb)
        if not shared:continue
        union=len(sa|sb)
        overlap.append({'analysis_version':VERSION,'viewer_a':a,'viewer_b':b,'generation_a':proc[a]['catalog_generation'],'generation_b':proc[b]['catalog_generation'],'grade_a':proc[a]['grade_code'],'grade_b':proc[b]['grade_code'],'same_generation':int(proc[a]['catalog_generation']==proc[b]['catalog_generation']),'same_grade':int(proc[a]['grade_code']==proc[b]['grade_code']),'unique_units_a':len(sa),'unique_units_b':len(sb),'shared_unique_units':shared,'jaccard':fmt(shared/union),'containment_a_in_b':fmt(shared/len(sa)),'containment_b_in_a':fmt(shared/len(sb))})
    overlap.sort(key=lambda r:(-int(r['shared_unique_units']),-float(r['jaccard']),r['viewer_a'],r['viewer_b']))
    fields=['analysis_version','viewer_a','viewer_b','generation_a','generation_b','grade_a','grade_b','same_generation','same_grade','unique_units_a','unique_units_b','shared_unique_units','jaccard','containment_a_in_b','containment_b_in_a']
    with OVERLAP.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(overlap)
    repeated=sum(int(r['occurrence_count'])>1 for r in unit_rows);cross=sum(int(r['viewer_count'])>1 for r in unit_rows);crossgen=sum(int(r['catalog_generation_count'])>1 for r in unit_rows)
    lines=['# LTMD-U1 W9 Educación Física — reutilización textual exacta','',f'Versión: `{VERSION}`.','',f'- Identidades históricas W9 preservadas: **{EXPECTED_TOTAL}**.',f'- Objetos canónicos analizados: **{EXPECTED_CANONICAL}**.','- Identidades retenidas por fuente: **0**.',f'- Fragmentos canónicos (ocurrencias): **{len(frags):,}**.',f'- Unidades textuales exactas únicas: **{len(unit_rows):,}**.',f'- Unidades repetidas en ≥2 ocurrencias: **{repeated:,}**.',f'- Unidades presentes en ≥2 visores: **{cross:,}**.',f'- Unidades presentes en ≥2 generaciones: **{crossgen:,}**.',f'- Pares de visores con ≥1 unidad exacta compartida: **{len(overlap):,}**.','','## Pares con mayor reutilización exacta','','| Visor A | Visor B | Compartidas | Jaccard | Contención A→B | Contención B→A |','|---|---|---:|---:|---:|---:|']
    for r in overlap[:20]:
        lines.append(f"| `{r['viewer_a']}` | `{r['viewer_b']}` | {r['shared_unique_units']} | {r['jaccard']} | {r['containment_a_in_b']} | {r['containment_b_in_a']} |")
    lines+=['','## Límite','La igualdad de `text_sha256` documenta reutilización textual exacta dentro de la representación OCR+FRAGSEG fijada. No demuestra identidad bibliográfica ni equivalencia curricular, pedagógica o semántica. W9 no contiene identidades retenidas por fuente. Este análisis se limita a dependencia documental técnica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':
    main()
