#!/usr/bin/env python3
"""SHA-verified adaptive OCR metrics for one LTMD-U1 W2 Mathematics viewer.

The worker refuses to run unless the consolidated 64-viewer asset audit is
complete and every viewer is direct_asset_ready. Source JPEGs are temporary,
verified against the frozen asset manifest, OCRed, then deleted. Full OCR text
is never persisted.
"""
from __future__ import annotations
import argparse,csv,hashlib,statistics,subprocess,tempfile
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv')
ASSET_SUMMARY=Path('data/catalog/ltmd_u1_w2_math_asset_summary.csv')
SCOPE=Path('data/catalog/ltmd_u1_w2_scope.csv')
VERSION='LTMD_U1_W2_MATH_OCR_0.1'
UA='LibroTextoMexicanoDigital/U1-W2 Mathematics OCR'
FALLBACK_MIN_WORDS=5
TIMEOUT=60
FIELDS=['ocr_version','page_id','viewer_key','book_id','catalog_generation','grade','viewer_page','asset_status','source_bytes','source_sha256_verified','attempts','selected_psm','recognized_words','ocr_chars','mean_word_confidence','median_word_confidence','low_confidence_word_rate','ocr_class','ocr_status','error']

def page_id(row):
    return f"U1-{row['viewer_key']}-P{int(row['viewer_page']):03d}"

def gate_assets(viewer_key):
    if not (MAN.exists() and ASSET_SUMMARY.exists() and SCOPE.exists()):
        raise SystemExit('W2 asset audit not materialized')
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8')))
    summary=list(csv.DictReader(ASSET_SUMMARY.open(encoding='utf-8')))
    if len(scope)!=64 or len(summary)!=64:
        raise SystemExit(f'W2 asset gate cardinality mismatch scope={len(scope)} summary={len(summary)}')
    if {r['viewer_key'] for r in scope}!={r['viewer_key'] for r in summary}:
        raise SystemExit('W2 asset gate viewer set mismatch')
    bad=[r['viewer_key'] for r in summary if r['direct_asset_ready']!='1' or int(r['internal_unserved'])!=0 or int(r['probe_errors'])!=0]
    if bad:
        raise SystemExit(f'W2 asset gate closed: {len(bad)} viewers not ready; first={bad[:5]}')
    if viewer_key not in {r['viewer_key'] for r in summary}:
        raise SystemExit(f'viewer not in frozen W2 scope: {viewer_key}')

def download_verify(row,target):
    h=hashlib.sha256();total=0
    with urlopen(Request(row['source_asset_url'],headers={'User-Agent':UA}),timeout=45) as r, target.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            h.update(b);total+=len(b);f.write(b)
    got=h.hexdigest()
    if got!=row['sha256']: raise RuntimeError(f"SHA256 mismatch expected={row['sha256']} got={got}")
    if row.get('byte_size') and total!=int(row['byte_size']): raise RuntimeError(f"byte size mismatch expected={row['byte_size']} got={total}")
    return total

def run_ocr(image,psm):
    proc=subprocess.run(['tesseract',str(image),'stdout','-l','spa','--psm',str(psm),'tsv'],capture_output=True,text=True,timeout=TIMEOUT)
    if proc.returncode: raise RuntimeError(proc.stderr.strip() or f'tesseract exit {proc.returncode}')
    rr=list(csv.DictReader(proc.stdout.splitlines(),delimiter='\t'));words=[];confs=[]
    for r in rr:
        txt=(r.get('text') or '').strip()
        try: conf=float(r.get('conf') or -1)
        except ValueError: conf=-1
        if txt and conf>=0: words.append(txt);confs.append(conf)
    low=sum(c<60 for c in confs)/len(confs) if confs else 1.0
    return {'recognized_words':len(words),'ocr_chars':sum(len(w) for w in words),'mean_word_confidence':f'{statistics.mean(confs):.2f}' if confs else '','median_word_confidence':f'{statistics.median(confs):.2f}' if confs else '','low_confidence_word_rate':f'{low:.4f}'}

def score(m): return (int(m['recognized_words']),float(m['mean_word_confidence'] or 0))

def process(row,tmp):
    pid=page_id(row);image=tmp/f'{pid}.jpg';attempts=[];errors=[]
    base={'ocr_version':VERSION,'page_id':pid,'viewer_key':row['viewer_key'],'book_id':row['book_id'],'catalog_generation':row['catalog_generation'],'grade':row['grade_code'],'viewer_page':row['viewer_page'],'asset_status':row['asset_status']}
    empty={'recognized_words':'','ocr_chars':'','mean_word_confidence':'','median_word_confidence':'','low_confidence_word_rate':''}
    try:
        size=download_verify(row,image);baseline=None
        try: baseline=run_ocr(image,3);attempts.append(f"psm3:ok:{baseline['recognized_words']}")
        except subprocess.TimeoutExpired: attempts.append('psm3:timeout');errors.append(f'psm3 timeout>{TIMEOUT}s')
        except Exception as e: attempts.append('psm3:error');errors.append(f'psm3 {type(e).__name__}: {e}')
        if baseline and int(baseline['recognized_words'])>0:
            return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':3,**baseline,'ocr_class':'text_detected','ocr_status':'ok','error':' | '.join(errors)}
        fallback=[]
        for psm in (11,6):
            try: m=run_ocr(image,psm);attempts.append(f"psm{psm}:ok:{m['recognized_words']}");fallback.append((psm,m))
            except subprocess.TimeoutExpired: attempts.append(f'psm{psm}:timeout');errors.append(f'psm{psm} timeout>{TIMEOUT}s')
            except Exception as e: attempts.append(f'psm{psm}:error');errors.append(f'psm{psm} {type(e).__name__}: {e}')
        valid=[x for x in fallback if int(x[1]['recognized_words'])>=FALLBACK_MIN_WORDS]
        if valid:
            psm,m=max(valid,key=lambda x:score(x[1]));return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':psm,**m,'ocr_class':'text_detected','ocr_status':'ok','error':' | '.join(errors)}
        observed=[]
        if baseline is not None: observed.append((3,baseline))
        observed+=fallback
        if observed:
            _,m=max(observed,key=lambda x:score(x[1]));return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':'',**m,'ocr_class':'no_text_detected','ocr_status':'ok','error':' | '.join(errors)}
        return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':'',**empty,'ocr_class':'unresolved','ocr_status':'error','error':' | '.join(errors)}
    except Exception as e:
        return {**base,'source_bytes':'','source_sha256_verified':0,'attempts':';'.join(attempts),'selected_psm':'',**empty,'ocr_class':'unresolved','ocr_status':'error','error':f'{type(e).__name__}: {e}'}
    finally: image.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--viewer-key',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w2_math_ocr');args=ap.parse_args()
    gate_assets(args.viewer_key)
    allrows=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    source=[r for r in allrows if r['viewer_key']==args.viewer_key and r['asset_status']=='source_jpeg']
    if not source: raise SystemExit(f'no W2 source rows for {args.viewer_key}')
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w2-math-ocr-') as td:
        outrows=[process(r,Path(td)) for r in source]
    outrows.sort(key=lambda r:int(r['viewer_page']))
    verified=sum(str(r['source_sha256_verified'])=='1' for r in outrows)
    if verified!=len(outrows): raise SystemExit(f'provenance failure {args.viewer_key}: {verified}/{len(outrows)} SHA verified')
    unresolved=sum(r['ocr_class']=='unresolved' or r['ocr_status']!='ok' for r in outrows)
    outdir=Path(args.output_dir);outdir.mkdir(parents=True,exist_ok=True);out=outdir/f"ocr_{args.viewer_key.lower()}.csv"
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(outrows)
    text=sum(r['ocr_class']=='text_detected' for r in outrows);no=sum(r['ocr_class']=='no_text_detected' for r in outrows)
    print(f'{args.viewer_key}: pages={len(outrows)} sha={verified} text={text} no_text={no} unresolved={unresolved} out={out}')
    if unresolved: raise SystemExit(f'{args.viewer_key}: unresolved OCR pages={unresolved}')
if __name__=='__main__': main()
