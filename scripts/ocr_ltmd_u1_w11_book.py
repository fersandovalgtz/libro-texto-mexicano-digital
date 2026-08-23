#!/usr/bin/env python3
"""OCR one canonical W11 viewer after the strict source gate.

Allowed viewers and page cardinalities come only from the published W11 topology.
Source images are temporary, byte-size/SHA-256 verified, and never persisted.
Only technical OCR metrics are written.
"""
from __future__ import annotations
import argparse,csv,hashlib,os,statistics,subprocess,tempfile,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

MAN=Path('data/catalog/ltmd_u1_w11_canonical_page_manifest.csv')
PROC=Path('data/catalog/ltmd_u1_w11_processing_inventory.csv')
TOPOLOGY_VERSION='LTMD_U1_W11_PROCESSING_TOPOLOGY_0.1'
VERSION='LTMD_U1_W11_OCR_0.1'
UA='LibroTextoMexicanoDigital/U1-W11 OCR 0.1'
FALLBACK_MIN_WORDS=5
TIMEOUT=60
SOURCE_ATTEMPTS=3
SOURCE_TIMEOUT=45
EXPECTED_IDENTITIES=111
FIELDS=['ocr_version','page_id','viewer_key','catalog_generation','grade','title_core','viewer_page','source_image_index','processing_mode','source_provenance','source_bytes','source_sha256_verified','attempts','selected_psm','recognized_words','ocr_chars','mean_word_confidence','median_word_confidence','low_confidence_word_rate','ocr_class','ocr_status','error']

def load_topology()->set[str]:
    proc=list(csv.DictReader(PROC.open(encoding='utf-8',newline='')))
    man=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    if len(proc)!=EXPECTED_IDENTITIES or len({r['viewer_key'] for r in proc})!=EXPECTED_IDENTITIES:raise SystemExit('W11 processing inventory cardinality mismatch')
    if {r['topology_version'] for r in proc}!={TOPOLOGY_VERSION}:raise SystemExit('W11 topology version mismatch')
    canonical={r['viewer_key'] for r in proc if r['source_admitted']=='1' and r['is_canonical_processing_object']=='1'}
    admitted={r['viewer_key'] for r in proc if r['source_admitted']=='1'}
    if not canonical or not admitted or not canonical<=admitted:raise SystemExit('W11 topology has no valid admitted canonical cohort')
    if any(r['processing_mode']!='direct_canonical' for r in proc if r['viewer_key'] in canonical):raise SystemExit('W11 canonical processing mode mismatch')
    if not man or {r['viewer_key'] for r in man}!=canonical:raise SystemExit('W11 canonical page manifest viewer mismatch')
    if {r['manifest_version'] for r in man}!={TOPOLOGY_VERSION}:raise SystemExit('W11 canonical manifest version mismatch')
    ids=[r['page_id'] for r in man]
    if len(ids)!=len(set(ids)):raise SystemExit('duplicate W11 canonical page IDs')
    if any(r['asset_status']!='source_jpeg' or r['processing_mode']!='direct_canonical' or not r['sha256'] or len(r['sha256'])!=64 or int(r['byte_size'])<=0 for r in man):raise SystemExit('W11 canonical page provenance mismatch')
    by={k:0 for k in canonical}
    for r in man:by[r['viewer_key']]+=1
    pmap={r['viewer_key']:r for r in proc}
    for k,n in by.items():
        if n!=int(pmap[k]['source_pages']):raise SystemExit(f'W11 source-page count mismatch {k}: {n}/{pmap[k]["source_pages"]}')
    return canonical

def download_verify(row:dict[str,str],target:Path)->tuple[int,int]:
    last=''
    for attempt in range(1,SOURCE_ATTEMPTS+1):
        target.unlink(missing_ok=True);h=hashlib.sha256();total=0
        try:
            with urlopen(Request(row['source_asset_url'],headers={'User-Agent':UA}),timeout=SOURCE_TIMEOUT) as response,target.open('wb') as f:
                while True:
                    b=response.read(1024*1024)
                    if not b:break
                    h.update(b);total+=len(b);f.write(b)
            if h.hexdigest()!=row['sha256']:raise RuntimeError('SHA256 mismatch')
            if total!=int(row['byte_size']):raise RuntimeError('byte-size mismatch')
            return total,attempt
        except (HTTPError,URLError,TimeoutError,OSError,RuntimeError) as exc:
            last=f'{type(exc).__name__}: {exc}';target.unlink(missing_ok=True)
            if attempt<SOURCE_ATTEMPTS:time.sleep(attempt)
    raise RuntimeError(f'source verification failed after {SOURCE_ATTEMPTS} attempts: {last}')

def run_ocr(image:Path,psm:int)->dict[str,object]:
    env=os.environ.copy();env['OMP_THREAD_LIMIT']='1'
    cp=subprocess.run(['tesseract',str(image),'stdout','-l','spa','--psm',str(psm),'tsv'],capture_output=True,text=True,timeout=TIMEOUT,env=env)
    if cp.returncode:raise RuntimeError(cp.stderr.strip() or f'tesseract exit {cp.returncode}')
    words=[];confs=[]
    for r in csv.DictReader(cp.stdout.splitlines(),delimiter='\t'):
        text=(r.get('text') or '').strip()
        try:conf=float(r.get('conf') or -1)
        except ValueError:conf=-1
        if text and conf>=0:words.append(text);confs.append(conf)
    low=sum(c<60 for c in confs)/len(confs) if confs else 1.0
    return {'recognized_words':len(words),'ocr_chars':sum(len(w) for w in words),'mean_word_confidence':f'{statistics.mean(confs):.2f}' if confs else '','median_word_confidence':f'{statistics.median(confs):.2f}' if confs else '','low_confidence_word_rate':f'{low:.4f}'}

def score(m):return (int(m['recognized_words']),float(m['mean_word_confidence'] or 0))

def process(row:dict[str,str],tmp:Path)->dict[str,object]:
    pid=row['page_id'];image=tmp/f'{pid}.jpg';attempts=[];errors=[]
    base={'ocr_version':VERSION,'page_id':pid,'viewer_key':row['viewer_key'],'catalog_generation':row['catalog_generation'],'grade':row['grade_code'],'title_core':row['title_core'],'viewer_page':row['viewer_page'],'source_image_index':row['source_image_index'],'processing_mode':row['processing_mode'],'source_provenance':row['source_provenance']}
    empty={'recognized_words':'','ocr_chars':'','mean_word_confidence':'','median_word_confidence':'','low_confidence_word_rate':''}
    try:
        size,source_attempts=download_verify(row,image);attempts.append(f'source:ok:{source_attempts}');baseline=None
        try:baseline=run_ocr(image,3);attempts.append(f"psm3:ok:{baseline['recognized_words']}")
        except subprocess.TimeoutExpired:attempts.append('psm3:timeout');errors.append(f'psm3 timeout>{TIMEOUT}s')
        except Exception as exc:attempts.append('psm3:error');errors.append(f'psm3 {type(exc).__name__}: {exc}')
        if baseline and int(baseline['recognized_words'])>0:
            return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':3,**baseline,'ocr_class':'text_detected','ocr_status':'ok','error':' | '.join(errors)}
        fallback=[]
        for psm in (11,6):
            try:m=run_ocr(image,psm);attempts.append(f"psm{psm}:ok:{m['recognized_words']}");fallback.append((psm,m))
            except subprocess.TimeoutExpired:attempts.append(f'psm{psm}:timeout');errors.append(f'psm{psm} timeout>{TIMEOUT}s')
            except Exception as exc:attempts.append(f'psm{psm}:error');errors.append(f'psm{psm} {type(exc).__name__}: {exc}')
        valid=[x for x in fallback if int(x[1]['recognized_words'])>=FALLBACK_MIN_WORDS]
        if valid:
            psm,m=max(valid,key=lambda x:score(x[1]));return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':psm,**m,'ocr_class':'text_detected','ocr_status':'ok','error':' | '.join(errors)}
        observed=[]
        if baseline is not None:observed.append((3,baseline))
        observed+=fallback
        if observed:
            _,m=max(observed,key=lambda x:score(x[1]));return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':'',**m,'ocr_class':'no_text_detected','ocr_status':'ok','error':' | '.join(errors)}
        return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':'',**empty,'ocr_class':'unresolved','ocr_status':'error','error':' | '.join(errors)}
    except Exception as exc:
        attempts.append('source:error');return {**base,'source_bytes':'','source_sha256_verified':0,'attempts':';'.join(attempts),'selected_psm':'',**empty,'ocr_class':'unresolved','ocr_status':'error','error':f'{type(exc).__name__}: {exc}'}
    finally:image.unlink(missing_ok=True)

def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--viewer-key',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w11_ocr');a=ap.parse_args();canonical=load_topology()
    if a.viewer_key not in canonical:raise SystemExit(f'viewer not W11 OCR-eligible canonical: {a.viewer_key}')
    source=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r['viewer_key']==a.viewer_key]
    source.sort(key=lambda r:int(r['viewer_page']))
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w11-ocr-') as td:rows=[process(r,Path(td)) for r in source]
    verified=sum(str(r['source_sha256_verified'])=='1' for r in rows);unresolved=sum(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in rows)
    if verified!=len(rows):raise SystemExit(f'provenance failure {a.viewer_key}: {verified}/{len(rows)}')
    d=Path(a.output_dir);d.mkdir(parents=True,exist_ok=True);out=d/f'ocr_{a.viewer_key.lower()}.csv'
    with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    print(f"{a.viewer_key}: pages={len(rows)} sha={verified} text={sum(r['ocr_class']=='text_detected' for r in rows)} no_text={sum(r['ocr_class']=='no_text_detected' for r in rows)} unresolved={unresolved}")
    if unresolved:raise SystemExit(f'{a.viewer_key}: unresolved OCR pages={unresolved}')

if __name__=='__main__':main()
