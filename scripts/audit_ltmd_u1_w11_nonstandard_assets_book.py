#!/usr/bin/env python3
"""Audit one W11 nonstandard viewer using its official claves.json configuration, without persisting source images."""
from __future__ import annotations
import argparse,csv,hashlib,time
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

CONF=Path('data/catalog/ltmd_u1_w11_nonstandard_config.csv')
VERSION='LTMD_U1_W11_NONSTANDARD_ASSET_AUDIT_0.1'
BASE='https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg'
UA='LibroTextoMexicanoDigital/U1-W11 nonstandard official-config asset audit 0.1'
EXPECTED=11

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
    ap=argparse.ArgumentParser();ap.add_argument('--viewer-key',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w11_nonstandard_assets');a=ap.parse_args()
    conf={r['viewer_key']:r for r in csv.DictReader(CONF.open(encoding='utf-8'))}
    if len(conf)!=EXPECTED:raise SystemExit(f'W11 nonstandard config cardinality mismatch: {len(conf)}')
    if a.viewer_key not in conf:raise SystemExit(f'viewer not in W11 nonstandard cohort: {a.viewer_key}')
    m=conf[a.viewer_key]
    if m['official_config_ready']!='1':raise SystemExit(f'official config is not ready: {a.viewer_key}')
    n=int(m['ag_pages']);key=m['ag_clave']
    if n<=0 or not key:raise SystemExit(f'invalid official config for {a.viewer_key}')
    records=[]
    for page in range(1,n+1):
        idx=0 if page==1 else page
        url=BASE.format(key=key,idx=idx);p=fetch_hash(url)
        records.append({'audit_version':VERSION,'viewer_key':a.viewer_key,'catalog_generation':m['catalog_generation'],'grade_code':m['grade_code'],'title_core':m['title_core'],'technical_route':'nonstandard_html_official_config','ag_clave':key,'viewer_page':page,'declared_positions':n,'source_image_index':idx,'source_asset_url':url,'is_final_declared_position':int(page==n),**p})
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
