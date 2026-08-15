#!/usr/bin/env python3
"""Verify that strict Ciencias Naturales 2018 catalog entries alias 2019 bytes.

The prior routing audit established reachability under paired 2019 content keys.
This audit strengthens that claim by comparing every 2018-resolved asset against
the persisted SHA-256/size of the corresponding 2019 source asset, while also
re-fetching the aliased URL and hashing its current bytes. Source bytes are never
persisted.
"""
from __future__ import annotations
import csv, hashlib, time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

ANOM=Path('data/catalog/ciencias_naturales_asset_routing_anomalies.csv')
MAN=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
OUT=Path('data/catalog/cn2018_2019_asset_identity.csv')
REL=Path('data/catalog/cn2018_2019_catalog_alias_relationships.csv')
REPORT=Path('data/catalog/cn2018_2019_asset_identity.md')
VERSION='CN2018_2019_ASSET_IDENTITY_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN 2018-2019 byte identity audit'
EXPECTED_BY_GRADE={3:153,4:161,5:161,6:177}

def fetch_hash(url,max_attempts=3):
    last=''
    for attempt in range(1,max_attempts+1):
        try:
            h=hashlib.sha256();size=0
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
                ctype=r.headers.get('Content-Type','');status=getattr(r,'status',None)
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    h.update(b);size+=len(b)
            if status==200 and 'image' in ctype.lower() and size:
                return h.hexdigest(),size,status,ctype,attempt,''
            last=f'unexpected status={status} type={ctype} size={size}'
        except Exception as e:last=f'{type(e).__name__}: {e}'
        if attempt<max_attempts:time.sleep(attempt)
    return '',0,'','',max_attempts,last

def main():
    anom=list(csv.DictReader(ANOM.open(encoding='utf-8')))
    man=list(csv.DictReader(MAN.open(encoding='utf-8')))
    refs={(int(r['grade']),int(r['viewer_page'])):r for r in man
          if r['catalog_generation']=='2019' and r['asset_status']=='source_jpeg'}
    chosen={}
    for r in anom:
        if r['catalog_generation']!='2018' or r['candidate_reachable_image']!='1' or r['candidate_is_original']=='1':continue
        g=int(r['grade']);p=int(r['viewer_page']);expected_key=f'H2019P{g}CNA'
        if r['candidate_content_key'].upper()==expected_key:
            chosen[(g,p)]=r
    expected_total=sum(EXPECTED_BY_GRADE.values())
    if len(chosen)!=expected_total:raise SystemExit(f'expected {expected_total} paired 2018 alias positions, got {len(chosen)}')
    for g,n in EXPECTED_BY_GRADE.items():
        if sum(1 for gg,_ in chosen if gg==g)!=n:raise SystemExit(f'grade {g} paired count drift')
        if sum(1 for gg,_ in refs if gg==g)!=n:raise SystemExit(f'grade {g} 2019 reference count drift')
    rows=[];futs={}
    with ThreadPoolExecutor(max_workers=16) as ex:
        for (g,p),a in sorted(chosen.items()):
            ref=refs[(g,p)]
            row={'audit_version':VERSION,'grade':g,'viewer_page':p,
                 'book_2018':a['book_id'],'viewer_key_2018':a['viewer_key'],
                 'alias_content_key':a['candidate_content_key'],'alias_asset_url':a['candidate_asset_url'],
                 'book_2019':ref['book_id'],'viewer_key_2019':ref['viewer_key'],
                 'reference_asset_url':ref['source_asset_url'],'reference_sha256':ref['sha256'],
                 'reference_byte_size':ref['byte_size'],
                 'url_identity':int(a['candidate_asset_url']==ref['source_asset_url'])}
            rows.append(row);futs[ex.submit(fetch_hash,a['candidate_asset_url'])]=row
        for fut in as_completed(futs):
            sha,size,status,ctype,attempts,error=fut.result();r=futs[fut]
            r.update({'observed_sha256':sha,'observed_byte_size':size,'http_status':status,
                      'content_type':ctype,'fetch_attempts':attempts,'error':error,
                      'sha256_identity':int(bool(sha) and sha==r['reference_sha256']),
                      'byte_size_identity':int(str(size)==str(r['reference_byte_size']))})
    rows.sort(key=lambda r:(int(r['grade']),int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    relationships=[]
    for g,n in EXPECTED_BY_GRADE.items():
        rr=[r for r in rows if int(r['grade'])==g];ok=sum(int(r['sha256_identity']) for r in rr)
        relationships.append({'relationship_version':VERSION,'catalog_generation_a':2018,
            'book_a':rr[0]['book_2018'],'viewer_key_a':rr[0]['viewer_key_2018'],
            'relationship_type':'catalog_entry_aliases_same_asset_bytes' if ok==n else 'alias_identity_not_proven',
            'catalog_generation_b':2019,'book_b':rr[0]['book_2019'],'viewer_key_b':rr[0]['viewer_key_2019'],
            'compared_source_assets':n,'sha256_identical_assets':ok,'identity_rate':f'{ok/n:.6f}',
            'interpretive_limit':'Byte identity proves shared digital assets, not independent bibliographic dating.'})
    with REL.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(relationships[0]));w.writeheader();w.writerows(relationships)
    ok=sum(int(r['sha256_identity']) for r in rows);urls=sum(int(r['url_identity']) for r in rows)
    sizes=sum(int(r['byte_size_identity']) for r in rows)
    lines=['# Identidad de activos Ciencias Naturales 2018 ↔ 2019','',f'Versión: `{VERSION}`.','',
           f'- Pares de activos comparados: **{len(rows)}**.\n- URL alias 2018 = URL fuente 2019: **{urls}/{len(rows)}**.\n- SHA-256 idéntico: **{ok}/{len(rows)}**.\n- Tamaño idéntico: **{sizes}/{len(rows)}**.','', '## Por grado']
    for rel in relationships:lines.append(f"- {rel['book_a']} ↔ {rel['book_b']}: {rel['sha256_identical_assets']}/{rel['compared_source_assets']} SHA idénticos ({float(rel['identity_rate'])*100:.1f}%).")
    lines+=['','## Interpretación',
        'Si la identidad SHA es completa, las entradas de catálogo 2018 se conservan como registros institucionales distintos pero se modelan como alias de los mismos activos digitales servidos por las claves 2019. No se duplica el contenido en una vista de contenido único y no se infiere por ello que “2018” sea el año bibliográfico del ejemplar.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))
    if ok!=len(rows) or urls!=len(rows) or sizes!=len(rows):raise SystemExit('2018/2019 byte identity incomplete')

if __name__=='__main__':main()
