#!/usr/bin/env python3
"""Analyze exact asset reuse and source readiness for LTMD-U1 W5 History.

This layer is source-only. It does not choose canonical documents, merge catalog
identities, infer historical/curricular continuity, or authorize semantic claims.
Exact relationships require equality of the full served-page sequence
(viewer page, source image index, byte size, SHA-256) after the source audit.
"""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path

MAN=Path('data/catalog/ltmd_u1_w5_history_asset_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w5_history_asset_summary.csv')
REL=Path('data/catalog/ltmd_u1_w5_history_exact_asset_relationships.csv')
READY=Path('data/catalog/ltmd_u1_w5_history_source_readiness.csv')
REPORT=Path('data/catalog/ltmd_u1_w5_history_asset_relationships.md')
VERSION='LTMD_U1_W5_HISTORY_ASSET_REL_0.1'
AUDIT_VERSION='LTMD_U1_W5_HISTORY_ASSET_AUDIT_0.1'
EXPECTED=18

def sequence_fingerprint(rows):
    served=[r for r in rows if r['asset_status']=='source_jpeg']
    payload=[[int(r['viewer_page']),int(r['source_image_index']),int(r['byte_size']),r['sha256']] for r in sorted(served,key=lambda x:int(x['viewer_page']))]
    raw=json.dumps(payload,separators=(',',':'),ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest(),payload

def main():
    manifest=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')));summaries=list(csv.DictReader(SUMMARY.open(encoding='utf-8',newline='')))
    if len(summaries)!=EXPECTED or len({r['viewer_key'] for r in summaries})!=EXPECTED:raise SystemExit(f'W5 source summary cardinality mismatch: {len(summaries)}')
    if {r['audit_version'] for r in summaries}!={AUDIT_VERSION}:raise SystemExit('unexpected W5 asset-audit version')
    if any(int(r['probe_errors']) for r in summaries):raise SystemExit('W5 source relationships refuse unresolved probe errors')
    expected_rows=sum(int(r['declared_positions']) for r in summaries)
    if len(manifest)!=expected_rows:raise SystemExit(f'W5 manifest cardinality mismatch {len(manifest)} vs {expected_rows}')
    if {r['audit_version'] for r in manifest}!={AUDIT_VERSION}:raise SystemExit('unexpected W5 manifest audit version')
    meta={r['viewer_key']:r for r in summaries};by_viewer=defaultdict(list)
    for row in manifest:by_viewer[row['viewer_key']].append(row)
    if set(by_viewer)!=set(meta):raise SystemExit('W5 manifest viewer coverage mismatch')
    fingerprints={};payloads={};readiness=[]
    for key,rows in by_viewer.items():
        if len(rows)!=int(meta[key]['declared_positions']):raise SystemExit(f'W5 per-viewer manifest mismatch: {key}')
        statuses=Counter(r['asset_status'] for r in rows)
        if statuses['probe_error']:raise SystemExit(f'probe_error persisted for {key}')
        fp,payload=sequence_fingerprint(rows);fingerprints[key]=fp;payloads[key]=payload
        source_jpegs=statuses['source_jpeg'];internal=statuses['internal_unserved'];terminal=statuses['terminal_synthetic_candidate']
        state='no_source_jpegs' if source_jpegs==0 else ('partial_internal_unserved' if internal else 'full_direct_source')
        readiness.append({'analysis_version':VERSION,'viewer_key':key,'catalog_generation':meta[key]['catalog_generation'],'grade_code':meta[key]['grade_code'],'title_core':meta[key]['title_core'],'declared_positions':meta[key]['declared_positions'],'source_jpegs':source_jpegs,'terminal_synthetic_candidates':terminal,'internal_unserved':internal,'source_state':state,'served_sequence_sha256':fp})
    exact_rows=[];keys=sorted(meta,key=lambda k:(int(meta[k]['catalog_generation']),int(meta[k]['grade_code']),k))
    for a,b in combinations(keys,2):
        if fingerprints[a]!=fingerprints[b]:continue
        if payloads[a]!=payloads[b]:raise SystemExit('fingerprint collision/inconsistency')
        if not payloads[a]:continue
        exact_rows.append({'analysis_version':VERSION,'viewer_a':a,'viewer_b':b,'generation_a':meta[a]['catalog_generation'],'generation_b':meta[b]['catalog_generation'],'grade_a':meta[a]['grade_code'],'grade_b':meta[b]['grade_code'],'same_grade':int(meta[a]['grade_code']==meta[b]['grade_code']),'served_page_count':len(payloads[a]),'served_sequence_sha256':fingerprints[a],'relationship':'full_served_asset_sequence_byte_exact'})
    readiness.sort(key=lambda r:(int(r['catalog_generation']),int(r['grade_code']),r['viewer_key']))
    with READY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(readiness[0]));w.writeheader();w.writerows(readiness)
    fields=['analysis_version','viewer_a','viewer_b','generation_a','generation_b','grade_a','grade_b','same_grade','served_page_count','served_sequence_sha256','relationship']
    with REL.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(exact_rows)
    states=Counter(r['source_state'] for r in readiness);cross=[r for r in exact_rows if r['generation_a']!=r['generation_b']];same_grade_cross=[r for r in cross if r['same_grade']==1]
    target_141819=[r for r in cross if {r['generation_a'],r['generation_b']} <= {'2014','2018','2019'}]
    lines=['# LTMD-U1 W5 — relaciones exactas de activos y readiness fuente Historia','',f'Versión: `{VERSION}`.','',f'- Visores analizados: **{len(readiness)}/{EXPECTED}**.',f'- `full_direct_source`: **{states["full_direct_source"]}**.',f'- `partial_internal_unserved`: **{states["partial_internal_unserved"]}**.',f'- `no_source_jpegs`: **{states["no_source_jpegs"]}**.',f'- Pares con secuencia completa de activos servidos byte-idéntica: **{len(exact_rows)}**.',f'- Pares byte-idénticos entre generaciones: **{len(cross)}**.',f'- Pares byte-idénticos entre generaciones y mismo grado: **{len(same_grade_cross)}**.',f'- Pares exactos restringidos a generaciones 2014/2018/2019: **{len(target_141819)}**.','','## Relaciones exactas','']
    if exact_rows:
        for row in exact_rows:lines.append(f"- `{row['viewer_a']}` ↔ `{row['viewer_b']}`: {row['served_page_count']} JPEG servidos en secuencia byte-idéntica; generaciones {row['generation_a']}→{row['generation_b']}; mismo grado={row['same_grade']}.")
    else:lines.append('- No se detectaron pares con secuencia completa byte-idéntica.')
    partial=[r for r in readiness if r['source_state']!='full_direct_source']
    if partial:
        lines+=['','## Excepciones que requieren reconciliación antes de OCR','']
        for row in partial:lines.append(f"- `{row['viewer_key']}`: estado `{row['source_state']}`, JPEG={row['source_jpegs']}/{row['declared_positions']}, internos no servidos={row['internal_unserved']}, terminales candidatos={row['terminal_synthetic_candidates']}.")
    lines += ['', '## Límite de interpretación', '', 'Una relación `full_served_asset_sequence_byte_exact` prueba igualdad byte a byte de la secuencia completa de JPEG servidos registrada por la auditoría, pero no fusiona identidades de catálogo ni demuestra identidad bibliográfica, continuidad histórica, equivalencia curricular, pedagógica o semántica. La elección posterior de un canónico operacional debe conservar provenance hacia cada identidad representada.', '', 'Este informe no autoriza por sí solo OCR W5. Antes debe existir una reconciliación explícita que resuelva parcialidad/routing y decida cómo representar pares exactos sin deduplicación destructiva.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
