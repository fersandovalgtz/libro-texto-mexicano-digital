#!/usr/bin/env python3
"""Recover the two internal source gaps of H2008P4GE273 conservatively.

Evidence contract:
1) the 2008 audit must contain exactly two internal gaps at viewer pages 70 and 117;
2) every source JPEG served by H2008P4GE273 must have a same-position source JPEG
   in H1993P4GE196 with identical persisted SHA-256 and byte size;
3) recovery candidates are only H1993P4GE196 pages 70 and 117;
4) candidate pages plus ten same-position neighbor anchors around each gap are
   re-fetched live; every anchor is fetched from both 1993 and 2008 routes and
   must remain byte-identical, while each recovery candidate must match its
   persisted 1993 hash and size.

This proves page-level source recovery, not book identity, bibliographic equality,
or curricular/semantic equivalence. Original 2008 404 provenance is preserved.
"""
from __future__ import annotations
import csv,hashlib,time
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/catalog/ltmd_u1_w6_geography_atlas_asset_manifest.csv')
OUT=Path('data/catalog/ltmd_u1_w6_h2008p4ge273_gap_recovery.csv')
ANCHORS=Path('data/catalog/ltmd_u1_w6_h2008p4ge273_gap_recovery_anchors.csv')
REPORT=Path('data/catalog/ltmd_u1_w6_h2008p4ge273_gap_recovery.md')
VERSION='LTMD_U1_W6_H2008P4GE273_GAP_RECOVERY_0.1'
TARGET='H2008P4GE273';REFERENCE='H1993P4GE196';EXPECTED_GAPS={70,117}
UA='LibroTextoMexicanoDigital/U1-W6 H2008P4GE273 cryptographic gap recovery'

def fetch(url,attempts=3):
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
            if status==200 and 'image' in ctype.lower() and size>0:return h.hexdigest(),size,attempt,''
            last=f'unexpected status={status} type={ctype} size={size}'
        except Exception as exc:last=f'{type(exc).__name__}: {exc}'
        if attempt<attempts:time.sleep(attempt)
    return '',0,attempts,last

def main():
    rows=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    by={}
    for r in rows:
        if r['viewer_key'] in {TARGET,REFERENCE}:by.setdefault(r['viewer_key'],{})[int(r['viewer_page'])]=r
    if set(by)!={TARGET,REFERENCE}:raise SystemExit('target/reference viewer missing from W6 asset manifest')
    target=by[TARGET];ref=by[REFERENCE]
    gaps={p for p,r in target.items() if r['asset_status']=='internal_unserved'}
    if gaps!=EXPECTED_GAPS:raise SystemExit(f'unexpected target gap set: {sorted(gaps)}')
    if any(target[p]['asset_status']!='internal_unserved' for p in EXPECTED_GAPS):raise SystemExit('target gaps not preserved as internal_unserved')
    if any(ref.get(p,{}).get('asset_status')!='source_jpeg' for p in EXPECTED_GAPS):raise SystemExit('reference does not serve both recovery candidate pages')

    target_served=[r for r in target.values() if r['asset_status']=='source_jpeg']
    paired=[]
    for t in target_served:
        p=int(t['viewer_page']);rr=ref.get(p)
        if not rr or rr['asset_status']!='source_jpeg':raise SystemExit(f'reference missing same-position source page {p}')
        sha_ok=t['sha256']==rr['sha256'];size_ok=t['byte_size']==rr['byte_size']
        paired.append((p,sha_ok,size_ok))
    bad=[x for x in paired if not (x[1] and x[2])]
    if bad:raise SystemExit(f'same-position persisted identity fails for {len(bad)} served target pages; first={bad[:3]}')
    if len(paired)<150:raise SystemExit(f'insufficient whole-book same-position anchors: {len(paired)}')

    live_anchor_pages=sorted(({p for g in EXPECTED_GAPS for p in range(g-5,g+6)}-EXPECTED_GAPS))
    anchor_rows=[]
    for p in live_anchor_pages:
        t=target.get(p);r=ref.get(p)
        if not t or not r or t['asset_status']!='source_jpeg' or r['asset_status']!='source_jpeg':raise SystemExit(f'live anchor page unavailable: {p}')
        tsha,tsize,ta,te=fetch(t['source_asset_url']);rsha,rsize,ra,re=fetch(r['source_asset_url'])
        ok=(tsha==t['sha256']==r['sha256']==rsha and str(tsize)==t['byte_size']==r['byte_size']==str(rsize))
        anchor_rows.append({'recovery_version':VERSION,'viewer_page':p,'target_url':t['source_asset_url'],'reference_url':r['source_asset_url'],'persisted_sha256':t['sha256'],'target_live_sha256':tsha,'reference_live_sha256':rsha,'persisted_byte_size':t['byte_size'],'target_live_byte_size':tsize,'reference_live_byte_size':rsize,'target_attempts':ta,'reference_attempts':ra,'target_error':te,'reference_error':re,'live_anchor_exact':int(ok)})
    if not all(int(r['live_anchor_exact']) for r in anchor_rows):raise SystemExit('one or more live neighbor anchors failed exact identity')

    recovery=[]
    for p in sorted(EXPECTED_GAPS):
        t=target[p];r=ref[p];sha,size,attempts,error=fetch(r['source_asset_url']);ok=(sha==r['sha256'] and str(size)==r['byte_size'])
        recovery.append({'recovery_version':VERSION,'viewer_key':TARGET,'viewer_page':p,'original_source_asset_url':t['source_asset_url'],'original_asset_status':t['asset_status'],'original_http_status':t['http_status'],'recovery_reference_viewer_key':REFERENCE,'effective_source_asset_url':r['source_asset_url'],'effective_sha256':r['sha256'],'effective_byte_size':r['byte_size'],'live_sha256':sha,'live_byte_size':size,'fetch_attempts':attempts,'error':error,'candidate_live_verified':int(ok),'same_position_served_target_pages_exact':len(paired),'live_neighbor_anchor_count':len(anchor_rows),'recovery_status':'cryptographically_recovered_same_position_reference' if ok else 'unresolved'})
    if not all(int(r['candidate_live_verified']) for r in recovery):raise SystemExit('gap candidate live verification failed')

    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(recovery[0]));w.writeheader();w.writerows(recovery)
    with ANCHORS.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(anchor_rows[0]));w.writeheader();w.writerows(anchor_rows)
    lines=['# LTMD-U1 W6 — recuperación criptográfica de huecos `H2008P4GE273`','',f'Versión: `{VERSION}`.','',f'- Huecos internos originales preservados: **{len(EXPECTED_GAPS)}** (páginas {", ".join(map(str,sorted(EXPECTED_GAPS)))}).',f'- Páginas JPEG servidas por 2008 con contraparte 1993 en la misma posición: **{len(paired)}**.',f'- Coincidencias SHA-256 + tamaño en esas páginas servidas: **{len(paired)}/{len(paired)}**.',f'- Anclas vecinas rehasheadas en vivo por ambas rutas: **{len(anchor_rows)}**, todas exactas.',f'- Páginas candidatas recuperadas y rehasheadas en vivo desde `{REFERENCE}`: **{sum(int(r["candidate_live_verified"]) for r in recovery)}/{len(recovery)}**.','','## Recuperaciones']
    for r in recovery:lines.append(f"- página de visor **{r['viewer_page']}**: URL 2008 original preservada como 404; fuente efectiva `{REFERENCE}` misma posición; SHA-256 `{r['effective_sha256']}`; estado=`{r['recovery_status']}`.")
    lines+=['','## Límite epistemológico','Esta evidencia demuestra una recuperación puntual de dos activos digitales ausentes en la ruta 2008 mediante una secuencia de misma posición extensamente byte-idéntica con el visor 1993 y revalidación viva de candidatos/anclas. **No convierte `H1993P4GE196` y `H2008P4GE273` en aliases de libro**: sus cardinalidades documentales difieren y las identidades de catálogo permanecen separadas. Tampoco se infiere edición, continuidad curricular o equivalencia semántica.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))
if __name__=='__main__':main()
