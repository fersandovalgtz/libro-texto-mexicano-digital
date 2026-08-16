#!/usr/bin/env python3
"""Audit W6 Geography/Atlas 2018 routing anomalies against paired 2019 routes.

The 2018 and 2019 viewer identities remain distinct catalog records. A pair is
accepted only when grade, normalized title, declared cardinality and the complete
page set agree, and every paired 2019 JPEG is re-fetched live and matches its
persisted 2019 SHA-256 and byte size. Source bytes are streamed and discarded.
"""
from __future__ import annotations
import csv,hashlib,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.request import Request,urlopen

READINESS=Path('data/catalog/ltmd_u1_w6_geography_atlas_source_readiness.csv')
MANIFEST=Path('data/catalog/ltmd_u1_w6_geography_atlas_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w6_geography_atlas_2018_2019_route_identity.csv')
REL=Path('data/catalog/ltmd_u1_w6_geography_atlas_2018_2019_route_relationships.csv')
REPORT=Path('data/catalog/ltmd_u1_w6_geography_atlas_2018_2019_route_identity.md')
VERSION='LTMD_U1_W6_GEOGRAPHY_ATLAS_2018_2019_ROUTE_IDENTITY_0.1'
UA='LibroTextoMexicanoDigital/U1-W6 Geography Atlas 2018-2019 route identity'
EXPECTED_ANOMALOUS_VIEWERS=5

def fetch_hash(url,max_attempts=3):
    last=''
    for attempt in range(1,max_attempts+1):
        try:
            h=hashlib.sha256();size=0
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
                status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
                while True:
                    block=r.read(1024*1024)
                    if not block:break
                    h.update(block);size+=len(block)
            if status==200 and 'image' in ctype.lower() and size:return h.hexdigest(),size,status,ctype,attempt,''
            last=f'unexpected status={status} type={ctype} size={size}'
        except Exception as exc:last=f'{type(exc).__name__}: {exc}'
        if attempt<max_attempts:time.sleep(attempt)
    return '',0,'','',max_attempts,last

def norm_title(value):return ' '.join(value.casefold().split())

def main():
    readiness=list(csv.DictReader(READINESS.open(encoding='utf-8')));manifest=list(csv.DictReader(MANIFEST.open(encoding='utf-8')))
    state={r['viewer_key']:r for r in readiness};man={}
    for row in manifest:man.setdefault(row['viewer_key'],[]).append(row)
    anomalies=[r for r in readiness if r['catalog_generation']=='2018' and r['source_state']=='no_source_jpegs']
    if len(anomalies)!=EXPECTED_ANOMALOUS_VIEWERS:raise SystemExit(f'expected {EXPECTED_ANOMALOUS_VIEWERS} W6 2018 routing anomalies, got {len(anomalies)}')
    pairs=[]
    for a in sorted(anomalies,key=lambda r:r['viewer_key']):
        k18=a['viewer_key'];k19=k18.replace('H2018','H2019',1)
        if k19==k18 or k19 not in state:raise SystemExit(f'paired 2019 viewer not found for {k18}: {k19}')
        b=state[k19]
        checks={'paired_generation_2019':b['catalog_generation']=='2019','paired_full_direct':b['source_state']=='full_direct_source','same_grade':a['grade_code']==b['grade_code'],'same_title_core':norm_title(a['title_core'])==norm_title(b['title_core']),'same_declared_positions':a['declared_positions']==b['declared_positions']}
        if not all(checks.values()):raise SystemExit(f'pair metadata/cardinality mismatch {k18}->{k19}: {checks}')
        refs={int(r['viewer_page']):r for r in man[k19] if r['asset_status']=='source_jpeg'}
        if len(refs)!=int(b['source_jpegs']):raise SystemExit(f'{k19}: reference JPEG mismatch')
        unresolved=sorted(int(r['viewer_page']) for r in man[k18] if r['asset_status']=='internal_unserved')
        if unresolved!=sorted(refs):raise SystemExit(f'{k18}->{k19}: unresolved-page set does not equal 2019 source-page set ({len(unresolved)} vs {len(refs)})')
        pairs.append((a,b,refs))
    rows=[];futures={}
    with ThreadPoolExecutor(max_workers=16) as pool:
        for a,b,refs in pairs:
            for page,ref in sorted(refs.items()):
                row={'audit_version':VERSION,'viewer_key_2018':a['viewer_key'],'viewer_key_2019':b['viewer_key'],'grade_code':a['grade_code'],'title_core':a['title_core'],'viewer_page':page,'declared_positions':a['declared_positions'],'alternate_route_url':ref['source_asset_url'],'reference_sha256_2019':ref['sha256'],'reference_byte_size_2019':ref['byte_size']};rows.append(row);futures[pool.submit(fetch_hash,ref['source_asset_url'])]=row
        for fut in as_completed(futures):
            sha,size,status,ctype,attempts,error=fut.result();row=futures[fut];row.update({'observed_sha256':sha,'observed_byte_size':size,'http_status':status,'content_type':ctype,'fetch_attempts':attempts,'error':error,'sha256_matches_2019_reference':int(bool(sha) and sha==row['reference_sha256_2019']),'byte_size_matches_2019_reference':int(str(size)==str(row['reference_byte_size_2019']))})
    rows.sort(key=lambda r:(r['viewer_key_2018'],int(r['viewer_page'])))
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    relationships=[]
    for a,b,refs in pairs:
        rr=[r for r in rows if r['viewer_key_2018']==a['viewer_key']];sha_ok=sum(int(r['sha256_matches_2019_reference']) for r in rr);size_ok=sum(int(r['byte_size_matches_2019_reference']) for r in rr);complete=sha_ok==len(rr)==len(refs) and size_ok==len(rr)
        relationships.append({'relationship_version':VERSION,'viewer_key_2018':a['viewer_key'],'viewer_key_2019':b['viewer_key'],'grade_code':a['grade_code'],'title_core':a['title_core'],'declared_positions':a['declared_positions'],'compared_source_assets':len(rr),'sha256_matches':sha_ok,'byte_size_matches':size_ok,'complete_route_resolution':int(complete),'relationship_type':'catalog_entry_resolves_through_paired_2019_asset_route' if complete else 'paired_route_identity_not_proven','canonical_processing_viewer_key':b['viewer_key'] if complete else '','interpretive_limit':'Operational route resolution only. Catalog identities remain distinct; no bibliographic edition year or curricular equivalence is inferred.'})
    with REL.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(relationships[0]));w.writeheader();w.writerows(relationships)
    total=len(rows);sha_ok=sum(int(r['sha256_matches_2019_reference']) for r in rows);size_ok=sum(int(r['byte_size_matches_2019_reference']) for r in rows);complete=sum(int(r['complete_route_resolution']) for r in relationships)
    lines=['# LTMD-U1 W6 — resolución de rutas Geografía/Atlas 2018 ↔ 2019','',f'Versión: `{VERSION}`.','',f'- Visores 2018 con anomalía auditados: **{len(relationships)}**.',f'- Activos emparejados y rehasheados: **{total}**.',f'- SHA-256 coincidente con referencia 2019: **{sha_ok}/{total}**.',f'- Tamaño coincidente con referencia 2019: **{size_ok}/{total}**.',f'- Visores con resolución completa por ruta 2019: **{complete}/{len(relationships)}**.','','## Por visor']
    for rel in relationships:lines.append(f"- `{rel['viewer_key_2018']}` → `{rel['viewer_key_2019']}`: {rel['sha256_matches']}/{rel['compared_source_assets']} SHA idénticos; estado=`{rel['relationship_type']}`.")
    lines+=['','## Interpretación','Una resolución completa habilita reutilización operacional del contenido canónico servido bajo la ruta 2019 sin duplicar procesamiento. Las identidades 2018 y 2019 permanecen separadas; esta evidencia es de routing y bytes digitales, no de identidad bibliográfica, fecha de edición, continuidad curricular o equivalencia semántica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
    if complete!=len(relationships) or sha_ok!=total or size_ok!=total:raise SystemExit('one or more W6 Geography/Atlas 2018/2019 route pairs remain unresolved')
if __name__=='__main__':main()
