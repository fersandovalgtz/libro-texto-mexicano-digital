#!/usr/bin/env python3
"""Combine W11 FRAGSEG shards with exact topology/page coverage checks."""
from __future__ import annotations
import argparse,csv
from collections import Counter,defaultdict
from pathlib import Path
STRUCT=Path('data/catalog/ltmd_u1_w11_page_structure.csv');PROC=Path('data/catalog/ltmd_u1_w11_processing_inventory.csv');OUT=Path('data/catalog/ltmd_u1_w11_fragment_manifest.csv');SUMMARY=Path('data/catalog/ltmd_u1_w11_fragment_manifest_summary.csv');GAPS=Path('data/catalog/ltmd_u1_w11_fragment_sequence_gaps.csv');REPORT=Path('docs/LTMD_U1_W11_FRAGSEG.md');VERSION='FRAGSEG_LTMD_U1_W11_0.1';STRUCT_VERSION='PAGESTRUCT_LTMD_U1_W11_0.1';ELIGIBLE={'textual','mixed_text_image'};EXPECTED_IDENTITIES=111

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='data/work/ltmd_u1_w11_fragments');a=ap.parse_args();structure=list(csv.DictReader(STRUCT.open(encoding='utf-8',newline='')));proc=list(csv.DictReader(PROC.open(encoding='utf-8',newline='')))
    if len(proc)!=EXPECTED_IDENTITIES or len({r['viewer_key'] for r in proc})!=EXPECTED_IDENTITIES:raise SystemExit('W11 FRAGSEG topology cardinality mismatch')
    canonical={r['viewer_key'] for r in proc if r['source_admitted']=='1' and r['is_canonical_processing_object']=='1'};admitted={r['viewer_key'] for r in proc if r['source_admitted']=='1'};withheld={r['viewer_key'] for r in proc if r['source_admitted']=='0'};aliases={r['viewer_key'] for r in proc if r['processing_mode']=='exact_source_alias'}
    viewers={r['viewer_key'] for r in structure};eligible={(r['viewer_key'],r['page_id']) for r in structure if r['primary_structure'] in ELIGIBLE}
    if not structure or viewers!=canonical or {r['classifier_version'] for r in structure}!={STRUCT_VERSION}:raise SystemExit('W11 FRAGSEG PAGESTRUCT coverage/version mismatch')
    per={k:0 for k in canonical}
    for k,_ in eligible:per[k]+=1
    bad=[k for k,n in per.items() if n==0]
    if bad:raise SystemExit(f'W11 canonical viewers without FRAGSEG-eligible pages: {bad}')
    files=sorted(p for p in Path(a.input_dir).rglob('fragment_*.csv') if not p.name.endswith('_failures.csv'));failfiles=sorted(Path(a.input_dir).rglob('fragment_*_failures.csv'))
    if len(files)!=len(canonical) or len(failfiles)!=len(canonical):raise SystemExit(f'expected {len(canonical)} fragment/failure shards, got {len(files)}/{len(failfiles)}')
    rows=[];seen=[];empty=[];failure_by={}
    for p in failfiles:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')));failure_by[p.name.replace('_failures.csv','.csv')]=rr
        for r in rr:
            if r['status']!='ok':raise SystemExit(f'fatal W11 FRAGSEG failure persisted: {r}')
            empty.append((r['viewer_key'],r['page_id']))
    if len(empty)!=len(set(empty)):raise SystemExit('duplicate W11 FRAGSEG empty-page records')
    empty_set=set(empty)
    if not empty_set<=eligible:raise SystemExit(f'W11 FRAGSEG empty page outside eligible set: {sorted(empty_set-eligible)[:5]}')
    for p in files:
        rr=list(csv.DictReader(p.open(encoding='utf-8',newline='')));fr=failure_by.get(p.name,[]);keys={r['viewer_key'] for r in rr}|{r['viewer_key'] for r in fr}
        if len(keys)!=1:raise SystemExit(f'cannot identify exactly one W11 viewer for shard {p}')
        key=next(iter(keys));seen.append(key)
        if rr and {r['segmenter_version'] for r in rr}!={VERSION}:raise SystemExit(f'invalid W11 segmenter version {p}')
        rows+=rr
    if set(seen)!=canonical or len(seen)!=len(canonical) or len(seen)!=len(set(seen)):raise SystemExit('W11 FRAGSEG viewer coverage mismatch')
    ids=[r['fragment_id'] for r in rows]
    if len(ids)!=len(set(ids)):raise SystemExit('duplicate W11 fragment IDs')
    fragment_pages={(r['viewer_key'],r['page_id']) for r in rows}
    if fragment_pages&empty_set:raise SystemExit(f'W11 FRAGSEG page recorded both fragmented and empty: {sorted(fragment_pages&empty_set)[:5]}')
    pagekeys=fragment_pages|empty_set
    if pagekeys!=eligible:raise SystemExit(f'W11 eligible coverage mismatch missing={len(eligible-pagekeys)} extra={len(pagekeys-eligible)}')
    bypage=defaultdict(list)
    for r in rows:bypage[(r['viewer_key'],r['page_id'])].append(int(r['fragment_sequence']))
    gaprows=[]
    for (k,pid),vals in sorted(bypage.items()):
        seq=sorted(vals)
        if any(v<=0 for v in seq) or len(seq)!=len(set(seq)):raise SystemExit(f'invalid W11 fragment sequence {k} {pid}')
        missing=[x for x in range(1,max(seq)+1) if x not in set(seq)] if seq else []
        if missing:gaprows.append({'viewer_key':k,'page_id':pid,'observed_fragment_count':len(seq),'max_sequence':max(seq),'missing_sequence_slots':' '.join(map(str,missing)),'missing_slot_count':len(missing)})
    if not rows:raise SystemExit('W11 FRAGSEG produced zero fragments')
    rows.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade']),r['viewer_key'],int(r['viewer_page']),int(r['fragment_sequence'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    fields=['viewer_key','page_id','observed_fragment_count','max_sequence','missing_sequence_slots','missing_slot_count']
    with GAPS.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(gaprows)
    types=sorted({r['candidate_type'] for r in rows});counts=defaultdict(Counter);pages=defaultdict(set)
    for r in rows:counts[r['viewer_key']][r['candidate_type']]+=1;counts['ALL'][r['candidate_type']]+=1;pages[r['viewer_key']].add(r['page_id']);pages['ALL'].add(r['page_id'])
    summary=[]
    for k in sorted(canonical)+['ALL']:
        c=counts[k];rec={'segmenter_version':VERSION,'viewer_key':k,'fragment_count':sum(c.values()),'segmented_page_count':len(pages[k])};rec.update({t:c[t] for t in types});summary.append(rec)
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    allc=summary[-1];slots=sum(int(r['missing_slot_count']) for r in gaprows);lines=['# FRAGSEG — LTMD-U1 W11','',f'Versión: `{VERSION}`.','',f'- Identidades históricas preservadas: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}**.',f'- Identidades con fuente admitida: **{len(admitted)}**.',f'- Identidades retenidas: **{len(withheld)}**.',f'- Objetos canónicos: **{len(canonical)}**.',f'- Aliases byte-exactos: **{len(aliases)}**.',f'- Páginas elegibles PAGESTRUCT: **{len(eligible):,}**.',f'- Páginas con ≥1 fragmento: **{allc["segmented_page_count"]:,}**.',f'- Páginas elegibles sin fragmentos: **{len(empty_set)}**.',f'- Fragmentos: **{allc["fragment_count"]:,}**.',f'- IDs únicos: **{len(set(ids)):,}**.',f'- Páginas con huecos legítimos de secuencia: **{len(gaprows)}**.',f'- Slots omitidos: **{slots}**.','','## Tipos candidatos']
    for t in types:lines.append(f'- `{t}`: {allc[t]:,}.')
    lines+=['','## Regla','Se reutiliza sin cambios el motor FRAGSEG W3 para comparabilidad técnica. Los tipos son candidatos, no categorías semánticas validadas. El texto completo no se persiste; cualquier fallo de fuente/SHA/OCR hace fallar el shard. Una página elegible no puede aparecer simultáneamente como fragmentada y vacía. Las identidades retenidas no se imputan ni se sustituyen.']
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
