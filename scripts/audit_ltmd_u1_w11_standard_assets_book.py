#!/usr/bin/env python3
"""Audit one architecture-standard W11 viewer, hashing official images without persisting them."""
from __future__ import annotations
import argparse,csv,hashlib,time
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

INV=Path('data/catalog/ltmd_u1_w11_standard_declared_inventory.csv')
VERSION='LTMD_U1_W11_STANDARD_ASSET_AUDIT_0.1'
BASE='https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg'
UA='LibroTextoMexicanoDigital/U1-W11 standard asset audit 0.1'
EXPECTED=100

def fetch_hash(url:str,attempts:int=3)->dict[str,object]:
    last=''
    for attempt in range(1,attempts+1):
        try:
            h=hashlib.sha256();size=0
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r:
                status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    h.update(b);size+=len(b)
            if status==200 and 'image' in ctype.lower() and size>0:return {'probe_state':'served_image','http_status':status,'content_type':ctype,'byte_size':size,'sha256':h.hexdigest(),'attempts':attempt,'error':''}
            last=f'unexpected status={status} type={ctype} size={size}'
        except HTTPError as e:
            if e.code==404:return {'probe_state':'http_404','http_status':404,'content_type':e.headers.get('Content-Type','') if e.headers else '','byte_size':'','sha256':'','attempts':attempt,'error':'HTTP 404'}
            last=f'HTTPError {e.code}'
        except (URLError,TimeoutError,OSError) as e:last=f'{type(e).__name__}: {e}'
        if attempt<attempts:time.sleep(attempt)
    return {'probe_state':'probe_error','http_status':'','content_type':'','byte_size':'','sha256':'','attempts':attempts,'error':last}

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--viewer-key',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w11_standard_assets');a=ap.parse_args()
    inv={r['viewer_key']:r for r in csv.DictReader(INV.open(encoding='utf-8'))}
    if len(inv)!=EXPECTED:raise SystemExit(f'W11 standard inventory cardinality mismatch: {len(inv)}')
    if a.viewer_key not in inv:raise SystemExit(f'viewer not in W11 standard route: {a.viewer_key}')
    m=inv[a.viewer_key]
    if m['technical_route']!='standard_dynamic_claves':raise SystemExit(f'wrong W11 technical route: {a.viewer_key}')
    n=int(m['declared_positions']);key=m['ag_clave']
    if n<=0 or not key:raise SystemExit(f'invalid inventory for {a.viewer_key}')
    records=[]
    for page in range(1,n+1):
        idx=0 if page==1 else page
        url=BASE.format(key=key,idx=idx);p=fetch_hash(url)
        records.append({'audit_version':VERSION,'viewer_key':a.viewer_key,'catalog_generation':m['catalog_generation'],'grade_code':m['grade_code'],'title_core':m['title_core'],'technical_route':m['technical_route'],'ag_clave':key,'viewer_page':page,'declared_positions':n,'source_image_index':idx,'source_asset_url':url,'is_final_declared_position':int(page==n),**p})
    prior_sequence_complete=bool(records[:-1]) and all(r['probe_state']=='served_image' for r in records[:-1])
    for r in records:
        if r['probe_state']=='served_image':status='source_jpeg'
        elif r['probe_state']=='http_404' and int(r['viewer_page'])==n and prior_sequence_complete:status='terminal_synthetic_candidate'
        elif r['probe_state']=='http_404':status='internal_unserved'
        else:status='probe_error'
        r['asset_status']=status
    d=Path(a.output_dir);d.mkdir(parents=True,exist_ok=True);out=d/f'asset_{a.viewer_key.lower()}.csv'
    with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    c={s:sum(r['asset_status']==s for r in records) for s in ('source_jpeg','terminal_synthetic_candidate','internal_unserved','probe_error')}
    print(f"{a.viewer_key}: declared={n} served={c['source_jpeg']} terminal404={c['terminal_synthetic_candidate']} internal404={c['internal_unserved']} probe_error={c['probe_error']}")
    if c['probe_error']:raise SystemExit(f"{a.viewer_key}: probe errors={c['probe_error']}")

if __name__=='__main__':main()
