#!/usr/bin/env python3
"""Combine W9 Educación Física FRAGSEG shards with exact coverage checks."""
from __future__ import annotations
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path

STRUCT=Path('data/catalog/ltmd_u1_w9_educacion_fisica_page_structure.csv')
OUT=Path('data/catalog/ltmd_u1_w9_educacion_fisica_fragment_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w9_educacion_fisica_fragment_manifest_summary.csv')
GAPS=Path('data/catalog/ltmd_u1_w9_educacion_fisica_fragment_sequence_gaps.csv')
REPORT=Path('data/catalog/ltmd_u1_w9_educacion_fisica_fragment_manifest.md')
VERSION='FRAGSEG_LTMD_U1_W9_EDUCACION_FISICA_0.1'
ELIGIBLE={'textual','mixed_text_image'}
EXPECTED=4
EXPECTED_PAGES=448

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w9_educacion_fisica_fragments');a=ap.parse_args()
    structure=list(csv.DictReader(STRUCT.open(encoding='utf-8',newline='')))
    viewers={r['viewer_key'] for r in structure}
    eligible={(r['viewer_key'],r['page_id']) for r in structure if r['primary_structure'] in ELIGIBLE}
    if len(structure)!=EXPECTED_PAGES or len(viewers)!=EXPECTED:
        raise SystemExit(f'expected {EXPECTED_PAGES} W9 PAGESTRUCT rows/{EXPECTED} viewers, found {len(structure)}/{len(viewers)}')
    if {r['classifier_version'] for r in structure}!={'PAGESTRUCT_LTMD_U1_W9_EDUCACION_FISICA_0.1'}:
        raise SystemExit('unexpected W9 PAGESTRUCT version')
    files=sorted(p for p in Path(a.input_dir).rglob('fragment_*.csv') if not p.name.endswith('_failures.csv'))
    failfiles=sorted(Path(a.input_dir).rglob('fragment_*_failures.csv'))
    if len(files)!=EXPECTED or len(failfiles)!=EXPECTED:
        raise SystemExit(f'expected {EXPECTED} fragment and failure shards, got {len(files)}/{len(failfiles)}')
    rows=[];seen=[];empty=[];failure_by={}
    for p in failfiles:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')));failure_by[p.name.replace('_failures.csv','.csv')]=rr
        for r in rr:
            if r['status']!='ok':
                raise SystemExit(f'fatal W9 FRAGSEG failure persisted: {r}')
            empty.append((r['viewer_key'],r['page_id']))
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')));fr=failure_by.get(p.name,[]);keys={r['viewer_key'] for r in rr}|{r['viewer_key'] for r in fr}
        if len(keys)!=1:
            raise SystemExit(f'cannot identify exactly one W9 viewer for shard {p}')
        key=next(iter(keys));seen.append(key)
        if rr and {r['segmenter_version'] for r in rr}!={VERSION}:
            raise SystemExit(f'invalid W9 segmenter version {p}')
        rows+=rr
    if set(seen)!=viewers or len(seen)!=EXPECTED or len(seen)!=len(set(seen)):
        raise SystemExit('W9 FRAGSEG viewer coverage mismatch')
    ids=[r['fragment_id'] for r in rows]
    if len(ids)!=len(set(ids)):
        raise SystemExit('duplicate W9 fragment IDs')
    pagekeys={(r['viewer_key'],r['page_id']) for r in rows}|set(empty)
    if pagekeys!=eligible:
        raise SystemExit(f'W9 eligible coverage mismatch missing={len(eligible-pagekeys)} extra={len(pagekeys-eligible)}')
    bypage=defaultdict(list)
    for r in rows:bypage[(r['viewer_key'],r['page_id'])].append(int(r['fragment_sequence']))
    gaprows=[]
    for (k,pid),vals in sorted(bypage.items()):
        seq=sorted(vals)
        if any(v<=0 for v in seq) or len(seq)!=len(set(seq)):
            raise SystemExit(f'invalid W9 fragment sequence {k} {pid}')
        missing=[x for x in range(1,max(seq)+1) if x not in set(seq)] if seq else []
        if missing:gaprows.append({'viewer_key':k,'page_id':pid,'observed_fragment_count':len(seq),'max_sequence':max(seq),'missing_sequence_slots':' '.join(map(str,missing)),'missing_slot_count':len(missing)})
    if not rows:
        raise SystemExit('W9 FRAGSEG produced zero fragments')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page']),int(r['fragment_sequence'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    fields=['viewer_key','page_id','observed_fragment_count','max_sequence','missing_sequence_slots','missing_slot_count']
    with GAPS.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(gaprows)
    types=sorted({r['candidate_type'] for r in rows});counts=defaultdict(Counter);pages=defaultdict(set)
    for r in rows:
        counts[r['viewer_key']][r['candidate_type']]+=1;counts['ALL'][r['candidate_type']]+=1;pages[r['viewer_key']].add(r['page_id']);pages['ALL'].add(r['page_id'])
    summary=[]
    for k in sorted(viewers)+['ALL']:
        c=counts[k];rec={'segmenter_version':VERSION,'viewer_key':k,'fragment_count':sum(c.values()),'segmented_page_count':len(pages[k])};rec.update({t:c[t] for t in types});summary.append(rec)
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    allc=summary[-1];slots=sum(int(r['missing_slot_count']) for r in gaprows)
    lines=['# FRAGSEG — LTMD-U1 W9 Educación Física','',f'Versión: `{VERSION}`.','',f'- Objetos canónicos: **{EXPECTED}**.','- Identidades retenidas por fuente: **0**.',f'- Páginas elegibles PAGESTRUCT: **{len(eligible):,}**.',f'- Páginas con ≥1 fragmento: **{allc["segmented_page_count"]:,}**.',f'- Páginas elegibles sin fragmentos: **{len(empty)}**.',f'- Fragmentos: **{allc["fragment_count"]:,}**.',f'- IDs únicos: **{len(set(ids)):,}**.',f'- Páginas con huecos legítimos de secuencia: **{len(gaprows)}**.',f'- Slots omitidos: **{slots}**.','','## Tipos candidatos']
    for t in types:lines.append(f'- `{t}`: {allc[t]:,}.')
    lines+=['','## Regla','Se reutiliza sin cambios el motor FRAGSEG W3 para comparabilidad técnica. Los tipos son candidatos; el texto completo no se persiste y cualquier fallo de fuente/SHA/OCR de ejecución hace fallar el shard. W9 no tiene identidades retenidas por fuente. Esta capa no es validación semántica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':
    main()
