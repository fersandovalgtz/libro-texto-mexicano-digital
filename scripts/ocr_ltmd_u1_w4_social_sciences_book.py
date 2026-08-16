#!/usr/bin/env python3
"""SHA-verified adaptive OCR metrics for one canonical LTMD-U1 W4 Social Sciences viewer."""
from __future__ import annotations

import argparse,csv,hashlib,os,statistics,subprocess,tempfile
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv')
PROC=Path('data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv')
VERSION='LTMD_U1_W4_SOCIAL_SCIENCES_OCR_0.1'
UA='LibroTextoMexicanoDigital/U1-W4 Social Sciences OCR 0.1'
FALLBACK_MIN_WORDS=5
TIMEOUT=60
EXPECTED_IDENTITIES=14
EXPECTED_CANONICAL=14
EXPECTED_SOURCE_PAGES=2414
FIELDS=['ocr_version','page_id','viewer_key','catalog_generation','grade','title_core','viewer_page','source_image_index','processing_mode','source_provenance','source_bytes','source_sha256_verified','attempts','selected_psm','recognized_words','ocr_chars','mean_word_confidence','median_word_confidence','low_confidence_word_rate','ocr_class','ocr_status','error']

def page_id(r):return f"U1-{r['viewer_key']}-P{int(r['viewer_page']):03d}"

def load_topology():
    proc=list(csv.DictReader(PROC.open(encoding='utf-8',newline='')));man=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    if len(proc)!=EXPECTED_IDENTITIES or len({r['viewer_key'] for r in proc})!=EXPECTED_IDENTITIES:raise SystemExit('W4 processing inventory cardinality mismatch')
    canonical={r['viewer_key'] for r in proc if r['is_canonical_processing_object']=='1'}
    eligible={r['viewer_key'] for r in proc if r['ocr_identity_eligible']=='1'}
    if canonical!=eligible or len(canonical)!=EXPECTED_CANONICAL:raise SystemExit('W4 topology must contain exactly 14 eligible canonicals and zero aliases')
    if any(r['processing_mode']!='direct_canonical' for r in proc):raise SystemExit('W4 unexpected processing mode')
    if any(int(r['persistent_internal_source_gaps'] or 0)!=0 for r in proc):raise SystemExit('W4 unexpected persistent source gap')
    if len(man)!=EXPECTED_SOURCE_PAGES or {r['viewer_key'] for r in man}!=canonical:raise SystemExit('W4 canonical page manifest cardinality/coverage mismatch')
    if any(r['asset_status']!='source_jpeg' for r in man):raise SystemExit('W4 canonical page manifest contains non-source row')
    pids=[page_id(r) for r in man]
    if len(pids)!=len(set(pids)):raise SystemExit('duplicate W4 canonical page IDs')
    return canonical

def download_verify(row,target):
    h=hashlib.sha256();total=0
    with urlopen(Request(row['source_asset_url'],headers={'User-Agent':UA}),timeout=45) as response,target.open('wb') as f:
        while True:
            block=response.read(1024*1024)
            if not block:break
            h.update(block);total+=len(block);f.write(block)
    if h.hexdigest()!=row['sha256']:raise RuntimeError('SHA256 mismatch')
    if row.get('byte_size') and total!=int(row['byte_size']):raise RuntimeError('byte-size mismatch')
    return total

def run_ocr(image,psm):
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

def process(row,tmp):
    pid=page_id(row);image=tmp/f'{pid}.jpg';attempts=[];errors=[]
    base={'ocr_version':VERSION,'page_id':pid,'viewer_key':row['viewer_key'],'catalog_generation':row['catalog_generation'],'grade':row['grade_code'],'title_core':row['title_core'],'viewer_page':row['viewer_page'],'source_image_index':row['source_image_index'],'processing_mode':row['processing_mode'],'source_provenance':row['source_provenance']}
    empty={'recognized_words':'','ocr_chars':'','mean_word_confidence':'','median_word_confidence':'','low_confidence_word_rate':''}
    try:
        size=download_verify(row,image);baseline=None
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
        return {**base,'source_bytes':'','source_sha256_verified':0,'attempts':';'.join(attempts),'selected_psm':'',**empty,'ocr_class':'unresolved','ocr_status':'error','error':f'{type(exc).__name__}: {exc}'}
    finally:image.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--viewer-key',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w4_social_sciences_ocr');a=ap.parse_args();canonical=load_topology()
    if a.viewer_key not in canonical:raise SystemExit(f'viewer not W4 canonical: {a.viewer_key}')
    source=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r['viewer_key']==a.viewer_key]
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w4-ss-ocr-') as td:rows=[process(r,Path(td)) for r in source]
    rows.sort(key=lambda r:int(r['viewer_page']));verified=sum(str(r['source_sha256_verified'])=='1' for r in rows);unresolved=sum(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in rows)
    if verified!=len(rows):raise SystemExit(f'provenance failure {a.viewer_key}: {verified}/{len(rows)}')
    outdir=Path(a.output_dir);outdir.mkdir(parents=True,exist_ok=True);out=outdir/f"ocr_{a.viewer_key.lower()}.csv"
    with out.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    print(f"{a.viewer_key}: pages={len(rows)} sha={verified} text={sum(r['ocr_class']=='text_detected' for r in rows)} no_text={sum(r['ocr_class']=='no_text_detected' for r in rows)} unresolved={unresolved}")
    if unresolved:raise SystemExit(f'{a.viewer_key}: unresolved OCR pages={unresolved}')
if __name__=='__main__':main()
