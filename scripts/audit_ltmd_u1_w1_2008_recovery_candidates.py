#!/usr/bin/env python3
"""Search for defensible public-route recovery candidates for the three W1 2008 gaps.

A later/other viewer is never accepted because its title matches. A candidate can
only be promoted when a fixed positional offset is cryptographically anchored by
at least four served neighbouring 2008 pages, all compared neighbour hashes match,
and the mapped target image itself is publicly served. The recovered target bytes
are hashed but not persisted.
"""
from __future__ import annotations
import csv,hashlib,time
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

SRC=Path('data/catalog/ciencias_naturales_pending_page_manifest.csv')
COVERAGE=Path('data/catalog/ltmd_u1_coverage.csv')
OUT=Path('data/catalog/ltmd_u1_w1_2008_recovery_audit.csv')
RECOVERED=Path('data/catalog/ltmd_u1_w1_2008_recovered_positions.csv')
REPORT=Path('data/catalog/ltmd_u1_w1_2008_recovery_audit.md')
VERSION='LTMD_U1_W1_2008_RECOVERY_0.1'
UA='LibroTextoMexicanoDigital/U1-W1 2008 recovery audit'
BASE='https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg'
TARGETS=(('LTMD-CN3-G2008',94),('LTMD-CN4-G2008',76),('LTMD-CN4-G2008',96))
OFFSETS=range(-3,4)
MIN_ANCHORS=4

def fetch(key,page,attempts=2):
    idx=0 if page==1 else page;url=BASE.format(key=key,idx=idx);last=''
    for a in range(1,attempts+1):
        try:
            h=hashlib.sha256();size=0
            with urlopen(Request(url,headers={'User-Agent':UA}),timeout=30) as r:
                status=getattr(r,'status',None);ctype=r.headers.get('Content-Type','')
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    h.update(b);size+=len(b)
            if status==200 and 'image' in ctype.lower() and size:
                return {'ok':1,'url':url,'sha256':h.hexdigest(),'byte_size':size,'attempts':a,'error':''}
            last=f'status={status} type={ctype} size={size}'
        except HTTPError as e:
            if e.code==404:return {'ok':0,'url':url,'sha256':'','byte_size':'','attempts':a,'error':'HTTP404'}
            last=f'HTTP{e.code}'
        except (URLError,TimeoutError,OSError) as e:last=f'{type(e).__name__}:{e}'
        if a<attempts:time.sleep(.3*a)
    return {'ok':0,'url':url,'sha256':'','byte_size':'','attempts':attempts,'error':last}

def main():
    src=list(csv.DictReader(SRC.open(encoding='utf-8')));idx={(r['book_id'],int(r['viewer_page'])):r for r in src}
    cov=list(csv.DictReader(COVERAGE.open(encoding='utf-8')));cov_by_viewer={r['viewer_key']:r for r in cov}
    source_viewer_to_book={r['viewer_key']:r['book_id'] for r in src if r['catalog_generation']=='2008'}
    source_book_to_viewer={b:v for v,b in source_viewer_to_book.items()}
    results=[];recoveries=[]
    for book,p in TARGETS:
        target=idx[(book,p)]
        if target['asset_status']!='internal_missing':raise SystemExit(f'{book} VP{p}: source status drift')
        source_viewer=target['viewer_key'];source_cov=cov_by_viewer[source_viewer]
        grade=source_cov['grade_code'];core=source_cov['title_core_normalized']
        candidates=[r for r in cov if r['viewer_key']!=source_viewer and r['grade_code']==grade and r['title_core_normalized']==core]
        # Strong source anchors within +-3, excluding the unserved target.
        source_anchors=[]
        for q in range(p-3,p+4):
            if q==p:continue
            r=idx.get((book,q))
            if r and r['asset_status']=='source_jpeg' and r['sha256']:
                source_anchors.append((q,r['sha256'],int(r['byte_size'])))
        if len(source_anchors)<MIN_ANCHORS:raise SystemExit(f'{book} VP{p}: insufficient source anchors')
        accepted=[]
        for cand in candidates:
            key=cand['viewer_key']
            for offset in OFFSETS:
                mapped=[(q,q+offset,sha,size) for q,sha,size in source_anchors if q+offset>=1]
                if len(mapped)<MIN_ANCHORS:continue
                # Cheap two-anchor screen: closest neighbours first.
                mapped.sort(key=lambda x:abs(x[0]-p))
                first=mapped[:2];screen=[]
                for sq,cq,sha,size in first:
                    got=fetch(key,cq,1);screen.append(got['ok'] and got['sha256']==sha and int(got['byte_size'])==size)
                if not all(screen):
                    results.append({'audit_version':VERSION,'source_book_id':book,'source_viewer_key':source_viewer,'source_target_page':p,'candidate_viewer_key':key,'candidate_generation':cand['catalog_generation'],'candidate_offset':offset,'anchor_count_available':len(mapped),'anchor_count_compared':2,'anchor_hash_matches':sum(screen),'anchor_hash_mismatches':2-sum(screen),'candidate_target_page':p+offset,'candidate_target_reachable':0,'candidate_target_sha256':'','candidate_target_byte_size':'','decision':'rejected_anchor_screen'})
                    continue
                matches=0;mismatches=0;compared=0
                # Compare all source anchors under the same fixed offset.
                for sq,cq,sha,size in mapped:
                    got=fetch(key,cq,2);compared+=1
                    if got['ok'] and got['sha256']==sha and int(got['byte_size'])==size:matches+=1
                    else:mismatches+=1
                mapped_target=p+offset;tg=fetch(key,mapped_target,3) if mapped_target>=1 else {'ok':0,'sha256':'','byte_size':''}
                decision='accepted_cryptographic_alignment' if matches>=MIN_ANCHORS and mismatches==0 and tg['ok'] else 'rejected_full_alignment'
                row={'audit_version':VERSION,'source_book_id':book,'source_viewer_key':source_viewer,'source_target_page':p,'candidate_viewer_key':key,'candidate_generation':cand['catalog_generation'],'candidate_offset':offset,'anchor_count_available':len(mapped),'anchor_count_compared':compared,'anchor_hash_matches':matches,'anchor_hash_mismatches':mismatches,'candidate_target_page':mapped_target,'candidate_target_reachable':int(tg['ok']),'candidate_target_sha256':tg.get('sha256',''),'candidate_target_byte_size':tg.get('byte_size',''),'decision':decision}
                results.append(row)
                if decision=='accepted_cryptographic_alignment':accepted.append(row)
        if len(accepted)>1:
            # Multiple candidates are not automatically equivalent; preserve ambiguity.
            final='ambiguous_multiple_cryptographic_candidates'
        elif len(accepted)==1:
            a=accepted[0];final='recovered_by_cryptographic_alignment';recoveries.append({'recovery_version':VERSION,'source_book_id':book,'source_viewer_key':source_viewer,'source_target_page':p,'recovery_viewer_key':a['candidate_viewer_key'],'recovery_generation':a['candidate_generation'],'fixed_offset':a['candidate_offset'],'mapped_target_page':a['candidate_target_page'],'recovered_asset_url':BASE.format(key=a['candidate_viewer_key'],idx=(0 if int(a['candidate_target_page'])==1 else int(a['candidate_target_page']))),'recovered_sha256':a['candidate_target_sha256'],'recovered_byte_size':a['candidate_target_byte_size'],'anchor_hash_matches':a['anchor_hash_matches'],'anchor_hash_mismatches':a['anchor_hash_mismatches'],'recovery_state':final,'interpretive_limit':'Technical recovery of a byte-aligned asset through another public viewer; does not by itself establish bibliographic identity beyond the demonstrated alignment.'})
        else:final='no_cryptographic_recovery_found'
        results.append({'audit_version':VERSION,'source_book_id':book,'source_viewer_key':source_viewer,'source_target_page':p,'candidate_viewer_key':'FINAL','candidate_generation':'','candidate_offset':'','anchor_count_available':len(source_anchors),'anchor_count_compared':'','anchor_hash_matches':'','anchor_hash_mismatches':'','candidate_target_page':'','candidate_target_reachable':'','candidate_target_sha256':'','candidate_target_byte_size':'','decision':final})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['audit_version','source_book_id','source_viewer_key','source_target_page','candidate_viewer_key','candidate_generation','candidate_offset','anchor_count_available','anchor_count_compared','anchor_hash_matches','anchor_hash_mismatches','candidate_target_page','candidate_target_reachable','candidate_target_sha256','candidate_target_byte_size','decision']
    with OUT.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(results)
    rfields=['recovery_version','source_book_id','source_viewer_key','source_target_page','recovery_viewer_key','recovery_generation','fixed_offset','mapped_target_page','recovered_asset_url','recovered_sha256','recovered_byte_size','anchor_hash_matches','anchor_hash_mismatches','recovery_state','interpretive_limit']
    with RECOVERED.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=rfields);w.writeheader();w.writerows(recoveries)
    finals=[r for r in results if r['candidate_viewer_key']=='FINAL'];counts={d:sum(r['decision']==d for r in finals) for d in {r['decision'] for r in finals}}
    lines=['# LTMD-U1 W1 — auditoría de recuperación criptográfica 2008','',f'Versión: `{VERSION}`.','',f'- Posiciones objetivo: **{len(TARGETS)}**.\n- Recuperaciones criptográficas unívocas: **{sum(r["decision"]=="recovered_by_cryptographic_alignment" for r in finals)}**.\n- Sin recuperación criptográfica: **{sum(r["decision"]=="no_cryptographic_recovery_found" for r in finals)}**.\n- Ambiguas por múltiples candidatos: **{sum(r["decision"]=="ambiguous_multiple_cryptographic_candidates" for r in finals)}**.','', '## Resultado por posición']
    for r in finals:lines.append(f"- `{r['source_book_id']}` VP{r['source_target_page']}: `{r['decision']}`.")
    lines+=['','## Criterio','No se acepta una imagen por coincidencia de título, grado o generación. Se exige un único candidato con offset fijo, al menos cuatro páginas vecinas conocidas de 2008 byte-idénticas bajo ese offset, cero discrepancias entre los anchors comparados y disponibilidad pública de la posición objetivo mapeada. Si no se satisface, el estado 2008 previo permanece como `internal_unserved_position_observed`.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(REPORT.read_text(encoding='utf-8'))

if __name__=='__main__':main()
