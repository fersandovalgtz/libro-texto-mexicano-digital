#!/usr/bin/env python3
"""Resolve asset-routing anomalies found in the pending Ciencias Naturales manifest.

The first family-wide audit intentionally assumed the pilot asset route only as a
hypothesis and flagged internal 404s. This script investigates those cases without
changing the original manifest:
- records exact missing viewer positions;
- extracts viewer-key-like references from each HTML landing page;
- probes plausible alias content keys (especially paired 2018/2019 CNA viewers);
- tests whether an unresolved position is available under an alias route.

Only routing metadata is persisted; page bytes are not stored.
"""
from __future__ import annotations
import csv,re
from collections import defaultdict
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen

MAN=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
OUT=Path('data/catalog/ciencias_naturales_asset_routing_anomalies.csv')
REPORT=Path('data/catalog/ciencias_naturales_asset_routing_anomalies.md')
VERSION='CN_ASSET_ROUTING_AUDIT_0.1'
BASE='https://historico.conaliteg.gob.mx/'
UA='LibroTextoMexicanoDigital/0.1 CN asset routing anomaly audit'
KEY_RE=re.compile(r'\bH(?:19|20)\d{2}P\d{1,2}[A-Z][A-Z0-9_-]{1,20}\b',re.I)

def fetch_text(url):
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:return r.read().decode('utf-8',errors='replace'),r.geturl()

def probe(key,p):
    idx=0 if p==1 else p;url=f'{BASE}c/{key}/{idx:03d}.jpg'
    try:
        with urlopen(Request(url,headers={'User-Agent':UA,'Range':'bytes=0-0'}),timeout=20) as r:
            status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','');r.read(1)
        return int(status in (200,206) and 'image' in ctype.lower()),status,ctype,url
    except HTTPError as e:return 0,e.code,e.headers.get('Content-Type','') if e.headers else '',url
    except Exception:return 0,'','',url

def aliases(viewer_key,gen,grade,html):
    cand={viewer_key}
    cand.update(k.upper() for k in KEY_RE.findall(html))
    # 2018/2019 are title-identical parallel catalog entries in the strict CN family;
    # test the paired key, but do not assume equivalence unless bytes/routes resolve.
    if gen=='2018':cand.add(re.sub(r'^H2018', 'H2019', viewer_key, flags=re.I).upper())
    if gen=='2019':cand.add(re.sub(r'^H2019', 'H2018', viewer_key, flags=re.I).upper())
    return sorted(cand)

def main():
    rows=list(csv.DictReader(MAN.open(encoding='utf-8')))
    missing=[r for r in rows if r['asset_status']=='internal_missing']
    if not missing:raise SystemExit('no internal missing rows to audit')
    bybook=defaultdict(list)
    for r in missing:bybook[r['book_id']].append(r)
    out=[]
    for bid,rr in sorted(bybook.items()):
        first=rr[0];key=first['viewer_key'];gen=first['catalog_generation'];grade=first['grade'];html='';final='';htmlerr=''
        try:html,final=fetch_text(BASE+key+'.htm')
        except Exception as e:htmlerr=f'{type(e).__name__}: {e}'
        cand=aliases(key,gen,grade,html)
        # Limit exact-position probing to every missing page; for all-pages-missing 2018,
        # candidate aliases are naturally tested across the complete sequence.
        for r in rr:
            p=int(r['viewer_page'])
            for ck in cand:
                ok,status,ctype,url=probe(ck,p)
                out.append({'audit_version':VERSION,'book_id':bid,'catalog_generation':gen,'grade':grade,'viewer_key':key,'viewer_page':p,'original_http_status':r['http_status'],'html_final_url':final,'html_key_references':';'.join(sorted(set(k.upper() for k in KEY_RE.findall(html)))),'candidate_content_key':ck,'candidate_is_original':int(ck.upper()==key.upper()),'candidate_asset_url':url,'candidate_reachable_image':ok,'candidate_http_status':status,'candidate_content_type':ctype,'html_error':htmlerr})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=list(out[0])
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
    lines=['# Auditoría de enrutamiento de activos — anomalías Ciencias Naturales','',f'Versión: `{VERSION}`. Huecos internos originales: **{len(missing)}** en **{len(bybook)}** objetos.','', '## Resolución por objeto']
    for bid,rr in sorted(bybook.items()):
        pages={int(r['viewer_page']) for r in rr};candrows=[x for x in out if x['book_id']==bid and int(x['candidate_reachable_image'])]
        resolved_pages={int(x['viewer_page']) for x in candrows}
        alias_keys=sorted({x['candidate_content_key'] for x in candrows if not int(x['candidate_is_original'])})
        unresolved=sorted(pages-resolved_pages)
        lines.append(f"- `{bid}`: huecos={len(pages)}; posiciones resueltas por algún candidato={len(resolved_pages)}; aliases funcionales={'; '.join(alias_keys) if alias_keys else 'ninguno'}; no resueltas={len(unresolved)}"+(f" ({','.join(map(str,unresolved[:30]))}{'…' if len(unresolved)>30 else ''})" if unresolved else '.'))
    lines+=['','## Regla','Una ruta alias sólo demuestra que los bytes de una posición son servidos bajo otra clave de contenido. Antes de fusionar objetos se requiere comparar hashes y metadatos bibliográficos. Los huecos 2008 que no resuelvan por alias se conservan como ausencias reales del activo público observado.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
