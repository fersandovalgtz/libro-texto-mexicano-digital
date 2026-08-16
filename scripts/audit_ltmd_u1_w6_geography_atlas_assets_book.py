#!/usr/bin/env python3
"""Audit one LTMD-U1 W6 Geography/Atlas viewer from institutional ag_clave.

Source JPEG bytes are streamed only for SHA-256 and size; they are not persisted.
This is a source-integrity layer, not a historical or semantic interpretation.
"""
from __future__ import annotations
import argparse,csv,hashlib,time
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

INV=Path('data/catalog/ltmd_u1_w6_declared_inventory.csv')
ARCH=Path('data/catalog/ltmd_u1_w6_viewer_architecture.csv')
VERSION='LTMD_U1_W6_GEOGRAPHY_ATLAS_ASSET_AUDIT_0.1'
BASE='https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg'
UA='LibroTextoMexicanoDigital/U1-W6 Geography Atlas asset audit'
EXPECTED=42

def fetch_hash(url,attempts=3):
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
            if status==200 and 'image' in ctype.lower() and size>0:
                return {'probe_state':'served_image','http_status':status,'content_type':ctype,'byte_size':size,'sha256':h.hexdigest(),'attempts':attempt,'error':''}
            last=f'unexpected status={status} type={ctype} size={size}'
        except HTTPError as e:
            if e.code==404:return {'probe_state':'http_404','http_status':404,'content_type':e.headers.get('Content-Type','') if e.headers else '','byte_size':'','sha256':'','attempts':attempt,'error':'HTTP 404'}
            last=f'HTTPError {e.code}'
        except (URLError,TimeoutError,OSError) as e:last=f'{type(e).__name__}: {e}'
        if attempt<attempts:time.sleep(attempt)
    return {'probe_state':'probe_error','http_status':'','content_type':'','byte_size':'','sha256':'','attempts':attempts,'error':last}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--viewer-key',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w6_geography_atlas_assets');a=ap.parse_args()
    inv={r['viewer_key']:r for r in csv.DictReader(INV.open(encoding='utf-8'))};arch={r['viewer_key']:r for r in csv.DictReader(ARCH.open(encoding='utf-8'))}
    if len(inv)!=EXPECTED or len(arch)!=EXPECTED:raise SystemExit('W6 inventory/architecture cardinality mismatch')
    if a.viewer_key not in inv:raise SystemExit(f'viewer not in W6: {a.viewer_key}')
    m=inv[a.viewer_key];ar=arch[a.viewer_key];n=int(m['declared_positions']);key=m['ag_clave']
    if not key:raise SystemExit(f'missing ag_clave for {a.viewer_key}')
    ui='standard_x_js' if ar['standard_dynamic_architecture']=='1' else 'nonstandard_viewer_architecture'
    records=[]
    for page in range(1,n+1):
        idx=0 if page==1 else page;url=BASE.format(key=key,idx=idx);p=fetch_hash(url)
        if p['probe_state']=='served_image':status='source_jpeg'
        elif p['probe_state']=='http_404' and page==n:status='terminal_synthetic_candidate'
        elif p['probe_state']=='http_404':status='internal_unserved'
        else:status='probe_error'
        records.append({'audit_version':VERSION,'viewer_key':a.viewer_key,'catalog_generation':m['catalog_generation'],'grade_code':m['grade_code'],'title_core':m['title_core'],'viewer_ui':ui,'ag_clave':key,'viewer_page':page,'declared_positions':n,'source_image_index':idx,'source_asset_url':url,'is_final_declared_position':int(page==n),'asset_status':status,**p})
    d=Path(a.output_dir);d.mkdir(parents=True,exist_ok=True);out=d/f'asset_{a.viewer_key.lower()}.csv'
    with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    c={s:sum(r['asset_status']==s for r in records) for s in ('source_jpeg','terminal_synthetic_candidate','internal_unserved','probe_error')}
    print(f"{a.viewer_key}: ui={ui} declared={n} served={c['source_jpeg']} terminal404={c['terminal_synthetic_candidate']} internal404={c['internal_unserved']} probe_error={c['probe_error']}")
    if c['probe_error']:raise SystemExit(f"{a.viewer_key}: probe errors={c['probe_error']}")
if __name__=='__main__':main()
