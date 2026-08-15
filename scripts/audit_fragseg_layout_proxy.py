#!/usr/bin/env python3
"""Audit FRAGSEG short-unit labels using OCR layout proxies, without human labels.

Samples heading_candidate and expository_candidate fragments independently of
semantic labels. Reconstructs pages ephemerally, verifies fragment hashes, and
persists numeric layout features only (no OCR text).
"""
from __future__ import annotations
import csv,hashlib,math,statistics,tempfile
from collections import defaultdict
from pathlib import Path

from segment_fragments import SOURCE_CODES,download_with_retry,run_tesseract,norm,candidate_type,token_count,sentence_units

MANIFEST=Path('data/derived/fragment_manifest.csv')
STRUCTURE=Path('data/derived/page_structure.csv')
OUT=Path('data/derived/fragseg_layout_proxy_sample.csv')
SUMMARY=Path('data/derived/fragseg_layout_proxy_summary.csv')
REPORT=Path('data/derived/fragseg_layout_proxy_audit.md')
VERSION='FRAGSEG_LAYOUT_PROXY_0.1'
GENS=('1972','1988','1993','2014')
GROUPS=('heading_candidate','expository_candidate')
N_PER_GROUP_GEN=20

def h(x,salt):return hashlib.sha256(f'{VERSION}|{salt}|{x}'.encode()).hexdigest()
def med(xs):return statistics.median(xs) if xs else None
def mean(xs):return sum(xs)/len(xs) if xs else None

def parse_tsv(path):
    with path.open(encoding='utf-8',errors='replace',newline='') as f:
        rr=list(csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
    words=[];pw=ph=None
    for r in rr:
        if r.get('level')=='1':
            try:pw=int(r['width']);ph=int(r['height'])
            except Exception:pass
        if r.get('level')!='5':continue
        text=norm(r.get('text',''))
        if not text:continue
        try:
            words.append({'text':text,'page_num':r.get('page_num'),'block_num':r.get('block_num'),'par_num':r.get('par_num'),'line_num':r.get('line_num'),
                          'left':int(r['left']),'top':int(r['top']),'width':int(r['width']),'height':int(r['height']),'conf':float(r['conf'])})
        except Exception:continue
    if not pw:pw=max((w['left']+w['width'] for w in words),default=1)
    if not ph:ph=max((w['top']+w['height'] for w in words),default=1)
    return words,pw,ph

def enriched_fragments(words):
    groups=defaultdict(list);order=[]
    for w in words:
        k=(w['page_num'],w['block_num'],w['par_num'])
        if k not in groups:order.append(k)
        groups[k].append(w)
    units=[]
    para_words={}
    for pi,k in enumerate(order):
        ws=groups[k];para_words[pi]=ws
        linegroups=defaultdict(list);lo=[]
        for w in ws:
            lk=w['line_num']
            if lk not in linegroups:lo.append(lk)
            linegroups[lk].append(w)
        text=norm(' '.join(norm(' '.join(x['text'] for x in linegroups[lk])) for lk in lo))
        for u in sentence_units(text):units.append([u,{pi}])
    merged=[]
    for text,pids in units:
        typ,sig=candidate_type(text);n=token_count(text)
        if not merged:merged.append([text,typ,n,set(pids)]);continue
        prev=merged[-1]
        if typ=='expository_candidate' and prev[1]==typ and prev[2]+n<=120:
            prev[0]=norm(prev[0]+' '+text);prev[2]+=n;prev[3]|=pids
        else:merged.append([text,typ,n,set(pids)])
    return merged,para_words

def feature(text,pids,para_words,page_words,pw,ph):
    ws=[w for pid in pids for w in para_words[pid]]
    left=min(w['left'] for w in ws);top=min(w['top'] for w in ws);right=max(w['left']+w['width'] for w in ws);bottom=max(w['top']+w['height'] for w in ws)
    page_med=med([w['height'] for w in page_words if w['height']>0]) or 1
    frag_med=med([w['height'] for w in ws if w['height']>0]) or 0
    letters=[c for c in text if c.isalpha()]
    upper=sum(c.isupper() for c in letters)/len(letters) if letters else 0
    return {'height_ratio':frag_med/page_med,'bbox_width_ratio':(right-left)/max(pw,1),'bbox_height_ratio':(bottom-top)/max(ph,1),
            'top_ratio':top/max(ph,1),'uppercase_ratio':upper,'terminal_punctuation':int(text.rstrip().endswith(('.',',',';',':','?','!','¿','¡'))),
            'ocr_conf_median':med([w['conf'] for w in ws if w['conf']>=0]),'word_box_count':len(ws)}

def main():
    man=list(csv.DictReader(MANIFEST.open(encoding='utf-8')));struct={r['page_id']:r for r in csv.DictReader(STRUCTURE.open(encoding='utf-8'))}
    selected=[]
    for g in GENS:
        for typ in GROUPS:
            pool=[r for r in man if r['catalog_generation']==g and r['candidate_type']==typ]
            pool=sorted(pool,key=lambda r:h(r['fragment_id'],f'{g}:{typ}'))[:N_PER_GROUP_GEN]
            if len(pool)!=N_PER_GROUP_GEN:raise RuntimeError(f'insufficient {g} {typ}')
            selected.extend(pool)
    wanted=defaultdict(dict)
    for r in selected:wanted[r['page_id']][r['fragment_id']]=r
    results=[]
    with tempfile.TemporaryDirectory(prefix='ltmd-layout-proxy-') as td:
        temp=Path(td)
        for page_id,targets in wanted.items():
            s=struct[page_id];g=s['catalog_generation'];p=int(s['viewer_page']);psm=s['selected_psm'] or '3'
            img=temp/f'{g}_{p:03d}.jpg';out=temp/f'{g}_{p:03d}'
            download_with_retry(f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[g]}/{p:03d}.jpg",img)
            if not run_tesseract(img,out,psm):raise RuntimeError(f'OCR fail {page_id}')
            words,pw,ph=parse_tsv(out.with_suffix('.tsv'));merged,para_words=enriched_fragments(words)
            seen=set()
            for seq,(text,typ,n,pids) in enumerate(merged,1):
                fid=f'{page_id}-F{seq:03d}'
                if fid not in targets:continue
                t=targets[fid];digest=hashlib.sha256(norm(text).encode()).hexdigest()
                if digest!=t['text_sha256']:raise RuntimeError(f'hash mismatch {fid}')
                ft=feature(text,pids,para_words,words,pw,ph)
                results.append({'audit_version':VERSION,'fragment_id':fid,'catalog_generation':g,'candidate_type':t['candidate_type'],'token_count':t['token_count'],**{k:round(v,6) if isinstance(v,float) else v for k,v in ft.items()}});seen.add(fid)
            missing=set(targets)-seen
            if missing:raise RuntimeError(f'missing sampled fragments {page_id}: {sorted(missing)}')
            for x in temp.iterdir():
                try:x.unlink()
                except Exception:pass
    assert len(results)==len(selected)==160
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    summ=[]
    for g in GENS:
        for typ in GROUPS:
            rr=[r for r in results if r['catalog_generation']==g and r['candidate_type']==typ]
            hr=[float(r['height_ratio']) for r in rr];wr=[float(r['bbox_width_ratio']) for r in rr];ur=[float(r['uppercase_ratio']) for r in rr];tr=[float(r['top_ratio']) for r in rr]
            summ.append({'audit_version':VERSION,'catalog_generation':g,'candidate_type':typ,'n':len(rr),
                         'height_ratio_median':round(med(hr),4),'height_ratio_mean':round(mean(hr),4),'height_ratio_ge_1_2_pct':round(100*sum(x>=1.2 for x in hr)/len(hr),2),
                         'bbox_width_ratio_median':round(med(wr),4),'uppercase_ratio_median':round(med(ur),4),'uppercase_ge_0_8_pct':round(100*sum(x>=0.8 for x in ur)/len(ur),2),
                         'top_ratio_median':round(med(tr),4),'terminal_punctuation_pct':round(100*sum(int(r['terminal_punctuation']) for r in rr)/len(rr),2)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summ[0]));w.writeheader();w.writerows(summ)
    lines=['# Auditoría de layout para `heading_candidate`','',f'Versión: `{VERSION}`. Muestra determinista: 20 `heading_candidate` + 20 `expository_candidate` por generación (n=160).','',
           'La auditoría reconstruye OCR sólo temporalmente, verifica SHA-256 y persiste únicamente rasgos geométricos. No constituye validación humana de encabezados.','',
           '## Resumen']
    for r in summ:lines.append(f"- {r['catalog_generation']} {r['candidate_type']}: n={r['n']}, mediana height-ratio={r['height_ratio_median']}, ≥1.2={r['height_ratio_ge_1_2_pct']}%, mayúsculas ≥80%={r['uppercase_ge_0_8_pct']}%, puntuación terminal={r['terminal_punctuation_pct']}%.")
    lines+=['','## Uso permitido','Los rasgos de layout sirven para estimar si la categoría residual posee saliencia tipográfica distinta de texto expositivo. No autorizan llamar “encabezado real” a un fragmento individual ni sustituir una auditoría visual independiente.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(SUMMARY.read_text(encoding='utf-8'))

if __name__=='__main__':main()
