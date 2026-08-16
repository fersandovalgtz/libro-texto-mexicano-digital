#!/usr/bin/env python3
"""Build reconciled W1 2008 page manifests without erasing the original anomalies."""
from __future__ import annotations
import csv
from pathlib import Path

BASE=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
REC=Path('data/catalog/ltmd_u1_w1_2008_recovered_positions.csv')
OUT=Path('data/catalog/ltmd_u1_w1_2008_page_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w1_2008_page_manifest_summary.csv')
REPORT=Path('data/catalog/ltmd_u1_w1_2008_page_manifest.md')
VERSION='LTMD_U1_W1_2008_PAGE_MANIFEST_0.1'
BOOKS={'LTMD-CN3-G2008','LTMD-CN4-G2008'}

def main():
    base=[r for r in csv.DictReader(BASE.open(encoding='utf-8')) if r['book_id'] in BOOKS]
    rec={(r['source_book_id'],int(r['source_target_page'])):r for r in csv.DictReader(REC.open(encoding='utf-8'))}
    expected_missing={(r['book_id'],int(r['viewer_page'])) for r in base if r['asset_status']=='internal_missing'}
    if set(rec)!=expected_missing:raise SystemExit(f'recovery set mismatch recovered={sorted(rec)} expected={sorted(expected_missing)}')
    out=[]
    for r in base:
        key=(r['book_id'],int(r['viewer_page']));rr=rec.get(key)
        if r['asset_status']=='source_jpeg':
            effective_status='source_jpeg';eff_url=r['source_asset_url'];sha=r['sha256'];size=r['byte_size'];recovery='';rv='';rg='';off='';mapped='';anchors='';mismatches=''
        elif r['asset_status']=='internal_missing' and rr:
            if rr['recovery_state']!='recovered_by_cryptographic_alignment' or int(rr['anchor_hash_matches'])<4 or int(rr['anchor_hash_mismatches'])!=0:raise SystemExit(f'weak recovery {key}')
            effective_status='source_jpeg_recovered_crypto';eff_url=rr['recovered_asset_url'];sha=rr['recovered_sha256'];size=rr['recovered_byte_size'];recovery=rr['recovery_state'];rv=rr['recovery_viewer_key'];rg=rr['recovery_generation'];off=rr['fixed_offset'];mapped=rr['mapped_target_page'];anchors=rr['anchor_hash_matches'];mismatches=rr['anchor_hash_mismatches']
        elif r['asset_status']=='terminal_synthetic':
            effective_status='terminal_synthetic';eff_url='';sha='';size='';recovery='';rv='';rg='';off='';mapped='';anchors='';mismatches=''
        else:raise SystemExit(f'unresolved base state {key}: {r["asset_status"]}')
        out.append({'manifest_version':VERSION,'page_id':r['page_id'],'book_id':r['book_id'],'viewer_key':r['viewer_key'],'catalog_generation':r['catalog_generation'],'grade':r['grade'],'viewer_page':r['viewer_page'],'declared_page_count':r['declared_page_count'],'source_image_index':r['source_image_index'],'is_final_declared_position':r['is_final_declared_position'],'position_ratio':r['position_ratio'],'position_quartile':r['position_quartile'],'original_source_asset_url':r['source_asset_url'],'original_asset_status':r['asset_status'],'original_http_status':r['http_status'],'effective_source_asset_url':eff_url,'effective_asset_status':effective_status,'byte_size':size,'sha256':sha,'recovery_state':recovery,'recovery_viewer_key':rv,'recovery_generation':rg,'fixed_offset':off,'mapped_target_page':mapped,'anchor_hash_matches':anchors,'anchor_hash_mismatches':mismatches})
    if len(out)!=len(base):raise SystemExit('row count drift')
    active=[r for r in out if r['effective_asset_status'].startswith('source_jpeg')]
    if any(not r['sha256'] or not r['effective_source_asset_url'] for r in active):raise SystemExit('effective source missing SHA/URL')
    if any(r['effective_asset_status'] not in {'source_jpeg','source_jpeg_recovered_crypto','terminal_synthetic'} for r in out):raise SystemExit('unresolved effective state remains')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    summary=[]
    for b in sorted(BOOKS):
        z=[r for r in out if r['book_id']==b];src=[r for r in z if r['effective_asset_status'].startswith('source_jpeg')];reco=[r for r in z if r['effective_asset_status']=='source_jpeg_recovered_crypto'];term=[r for r in z if r['effective_asset_status']=='terminal_synthetic']
        summary.append({'manifest_version':VERSION,'book_id':b,'viewer_key':z[0]['viewer_key'],'catalog_generation':z[0]['catalog_generation'],'grade':z[0]['grade'],'viewer_positions':len(z),'effective_source_jpegs':len(src),'cryptographically_recovered_positions':len(reco),'terminal_synthetic':len(term),'unresolved_effective_positions':0,'unique_effective_hashes':len({r['sha256'] for r in src}),'asset_layer_ready':1})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    reco=[r for r in out if r['effective_asset_status']=='source_jpeg_recovered_crypto']
    lines=['# LTMD-U1 W1 — manifiesto reconciliado 2008','',f'Versión: `{VERSION}`.','',f'- Libros: **2**.\n- Posiciones declaradas: **{len(out)}**.\n- Fuentes efectivas con SHA: **{len(active)}**.\n- Posiciones recuperadas criptográficamente: **{len(reco)}**.\n- Posiciones efectivas unresolved: **0**.','', '## Preservación de procedencia']
    for r in reco:lines.append(f"- `{r['book_id']}` VP{r['viewer_page']}: la URL original de `{r['viewer_key']}` permanece registrada como `{r['original_asset_status']}`; la fuente efectiva proviene de `{r['recovery_viewer_key']}` VP{r['mapped_target_page']} con offset {r['fixed_offset']}, {r['anchor_hash_matches']} anchors idénticos y {r['anchor_hash_mismatches']} discrepancias.")
    lines+=['','La recuperación técnica no se interpreta como prueba de identidad bibliográfica completa entre ediciones. Permite reconstruir un activo puntual mediante continuidad criptográficamente demostrada, conservando la anomalía original como parte de la trazabilidad.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
