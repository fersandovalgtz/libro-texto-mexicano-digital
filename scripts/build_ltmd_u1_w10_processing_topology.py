#!/usr/bin/env python3
"""Build W10 canonical processing topology using only full-sequence byte identity."""
from __future__ import annotations
import csv,hashlib
from collections import defaultdict
from pathlib import Path

SCOPE=Path('data/catalog/ltmd_u1_w10_scope.csv')
ADM=Path('data/catalog/ltmd_u1_w10_source_admissibility.csv')
ASSET_MAN=Path('data/catalog/ltmd_u1_w10_asset_manifest.csv')
TOPO=Path('data/catalog/ltmd_u1_w10_processing_inventory.csv')
MAN=Path('data/catalog/ltmd_u1_w10_canonical_page_manifest.csv')
REPORT=Path('docs/LTMD_U1_W10_PROCESSING_TOPOLOGY.md')
VERSION='LTMD_U1_W10_PROCESSING_TOPOLOGY_0.1'
EXPECTED=69

def signature(rows,declared,terminal):
    h=hashlib.sha256();h.update(f'declared={declared}|terminal={terminal}\n'.encode())
    for r in sorted(rows,key=lambda x:int(x['viewer_page'])):
        h.update(f"{r['viewer_page']}|{r['source_image_index']}|{r['byte_size']}|{r['sha256']}\n".encode())
    return h.hexdigest()

def main():
    scope={r['viewer_key']:r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))}
    adm={r['viewer_key']:r for r in csv.DictReader(ADM.open(encoding='utf-8'))}
    assets=list(csv.DictReader(ASSET_MAN.open(encoding='utf-8')))
    if len(scope)!=EXPECTED or len(adm)!=EXPECTED or set(scope)!=set(adm):raise SystemExit('W10 topology scope/admissibility mismatch')
    by=defaultdict(list)
    for r in assets:by[r['viewer_key']].append(r)
    if set(by)!=set(scope):raise SystemExit('W10 topology asset viewer coverage mismatch')
    sigs={}
    for key in scope:
        a=adm[key]
        if a['ocr_source_admitted']=='1':
            source=[r for r in by[key] if r['asset_status']=='source_jpeg']
            if len(source)!=int(a['source_jpegs']):raise SystemExit(f'W10 source-page count mismatch {key}')
            if any(not r['sha256'] or not r['byte_size'] for r in source):raise SystemExit(f'W10 missing source hash/size {key}')
            sigs[key]=signature(source,a['declared_positions'],a['terminal_synthetic_candidates'])
    groups=defaultdict(list)
    for key,sig in sigs.items():groups[sig].append(key)
    canonical_for={}
    for sig,keys in groups.items():
        keys.sort(key=lambda k:(int(scope[k]['catalog_generation']),int(scope[k]['grade_code']),k));canon=keys[0]
        for k in keys:canonical_for[k]=canon
    topo=[]
    for key,s in sorted(scope.items(),key=lambda kv:(int(kv[1]['catalog_generation']),int(kv[1]['grade_code']),kv[0])):
        a=adm[key];admitted=int(a['ocr_source_admitted'])
        if not admitted:
            mode='withheld_source';canon='';iscan=0;sig=''
        else:
            canon=canonical_for[key];iscan=int(key==canon);mode='direct_canonical' if iscan else 'exact_source_alias';sig=sigs[key]
        topo.append({'topology_version':VERSION,'viewer_key':key,'catalog_generation':s['catalog_generation'],'grade_code':s['grade_code'],'title_core':s['title_core'],'source_admitted':admitted,'is_canonical_processing_object':iscan,'processing_mode':mode,'canonical_viewer_key':canon,'source_sequence_sha256':sig,'source_pages':a['source_jpegs'],'terminal_synthetic_candidates':a['terminal_synthetic_candidates'],'source_state':a['source_state']})
    with TOPO.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(topo[0]));w.writeheader();w.writerows(topo)
    canonical={r['viewer_key'] for r in topo if int(r['is_canonical_processing_object'])==1}
    aliases={r['viewer_key'] for r in topo if r['processing_mode']=='exact_source_alias'}
    rows=[]
    for key in sorted(canonical,key=lambda k:(int(scope[k]['catalog_generation']),int(scope[k]['grade_code']),k)):
        for r in sorted((x for x in by[key] if x['asset_status']=='source_jpeg'),key=lambda x:int(x['viewer_page'])):
            p=int(r['viewer_page'])
            rows.append({'manifest_version':VERSION,'page_id':f'U1-{key}-P{p:03d}','book_id':key,'viewer_key':key,'catalog_generation':scope[key]['catalog_generation'],'grade_code':scope[key]['grade_code'],'title_core':scope[key]['title_core'],'viewer_page':p,'source_image_index':r['source_image_index'],'processing_mode':'direct_canonical','source_provenance':'official_conaliteg_source_jpeg_sha256_verified','source_asset_url':r['source_asset_url'],'byte_size':r['byte_size'],'sha256':r['sha256'],'asset_status':'source_jpeg'})
    if rows:
        with MAN.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    else:raise SystemExit('W10 topology produced zero canonical pages')
    admitted=sum(int(r['source_admitted']) for r in topo);withheld=EXPECTED-admitted
    lines=['# LTMD-U1 W10 — topología canónica de procesamiento','',f'Versión: `{VERSION}`.','',f'- Identidades históricas preservadas: **{EXPECTED}/{EXPECTED}**.',f'- Identidades con fuente admitida: **{admitted}/{EXPECTED}**.',f'- Identidades retenidas: **{withheld}/{EXPECTED}**.',f'- Objetos canónicos directos: **{len(canonical)}**.',f'- Aliases por identidad byte-exacta de secuencia completa: **{len(aliases)}**.',f'- Páginas fuente en manifiesto canónico: **{len(rows):,}**.','','## Regla','Sólo se reutiliza procesamiento cuando dos identidades fuente-admitidas poseen la misma secuencia completa de páginas servidas, con idénticos índices, tamaños y SHA-256, además de la misma cardinalidad declarada/terminal. Título, grado, generación, OCR y similitud visual no participan en la decisión. Las identidades históricas permanecen separadas aunque compartan un objeto canónico.']
    if aliases:
        lines+=['','## Aliases exactos']
        for r in topo:
            if r['processing_mode']=='exact_source_alias':lines.append(f"- `{r['viewer_key']}` → `{r['canonical_viewer_key']}`.")
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
