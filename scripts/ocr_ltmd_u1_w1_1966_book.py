#!/usr/bin/env python3
"""Per-book SHA-verified adaptive OCR metrics for LTMD-U1 W1 1966.

Source images are temporary, verified against the frozen W1 manifest, OCRed and
deleted. Full OCR text is never written.
"""
from __future__ import annotations
import argparse,csv,hashlib,statistics,subprocess,tempfile
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/catalog/ltmd_u1_w1_1966_page_manifest.csv')
VERSION='LTMD_U1_W1_1966_OCR_0.1'
UA='LibroTextoMexicanoDigital/U1-W1 1966 OCR'
FALLBACK_MIN_WORDS=5
TIMEOUT=60
FIELDS=['ocr_version','page_id','book_id','catalog_generation','grade','viewer_page','asset_status','source_bytes','source_sha256_verified','attempts','selected_psm','recognized_words','ocr_chars','mean_word_confidence','median_word_confidence','low_confidence_word_rate','ocr_class','ocr_status','error']

def download_verify(row,target):
    h=hashlib.sha256();total=0
    with urlopen(Request(row['source_asset_url'],headers={'User-Agent':UA}),timeout=45) as r, target.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b:break
            h.update(b);total+=len(b);f.write(b)
    got=h.hexdigest()
    if got!=row['sha256']:raise RuntimeError(f"SHA256 mismatch expected={row['sha256']} got={got}")
    if row.get('byte_size') and total!=int(row['byte_size']):raise RuntimeError(f"byte size mismatch expected={row['byte_size']} got={total}")
    return total

def run_ocr(image,psm):
    proc=subprocess.run(['tesseract',str(image),'stdout','-l','spa','--psm',str(psm),'tsv'],capture_output=True,text=True,timeout=TIMEOUT)
    if proc.returncode:raise RuntimeError(proc.stderr.strip() or f'tesseract exit {proc.returncode}')
    rr=list(csv.DictReader(proc.stdout.splitlines(),delimiter='\t'));words=[];confs=[]
    for r in rr:
        txt=(r.get('text') or '').strip()
        try:conf=float(r.get('conf') or -1)
        except ValueError:conf=-1
        if txt and conf>=0:words.append(txt);confs.append(conf)
    low=sum(c<60 for c in confs)/len(confs) if confs else 1.0
    return {'recognized_words':len(words),'ocr_chars':sum(len(w) for w in words),'mean_word_confidence':f'{statistics.mean(confs):.2f}' if confs else '','median_word_confidence':f'{statistics.median(confs):.2f}' if confs else '','low_confidence_word_rate':f'{low:.4f}'}

def score(m):return (int(m['recognized_words']),float(m['mean_word_confidence'] or 0))

def process(row,tmp):
    image=tmp/f"{row['page_id']}.jpg";attempts=[];errors=[]
    base={'ocr_version':VERSION,'page_id':row['page_id'],'book_id':row['book_id'],'catalog_generation':row['catalog_generation'],'grade':row['grade_code'],'viewer_page':row['viewer_page'],'asset_status':row['asset_status']}
    empty={'recognized_words':'','ocr_chars':'','mean_word_confidence':'','median_word_confidence':'','low_confidence_word_rate':''}
    try:
        size=download_verify(row,image);baseline=None
        try:baseline=run_ocr(image,3);attempts.append(f"psm3:ok:{baseline['recognized_words']}")
        except subprocess.TimeoutExpired:attempts.append('psm3:timeout');errors.append(f'psm3 timeout>{TIMEOUT}s')
        except Exception as e:attempts.append('psm3:error');errors.append(f'psm3 {type(e).__name__}: {e}')
        if baseline and int(baseline['recognized_words'])>0:
            return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':3,**baseline,'ocr_class':'text_detected','ocr_status':'ok','error':' | '.join(errors)}
        fallback=[]
        for psm in (11,6):
            try:m=run_ocr(image,psm);attempts.append(f"psm{psm}:ok:{m['recognized_words']}");fallback.append((psm,m))
            except subprocess.TimeoutExpired:attempts.append(f'psm{psm}:timeout');errors.append(f'psm{psm} timeout>{TIMEOUT}s')
            except Exception as e:attempts.append(f'psm{psm}:error');errors.append(f'psm{psm} {type(e).__name__}: {e}')
        valid=[x for x in fallback if int(x[1]['recognized_words'])>=FALLBACK_MIN_WORDS]
        if valid:
            psm,m=max(valid,key=lambda x:score(x[1]));return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':psm,**m,'ocr_class':'text_detected','ocr_status':'ok','error':' | '.join(errors)}
        observed=[]
        if baseline is not None:observed.append((3,baseline))
        observed+=fallback
        if observed:
            _,m=max(observed,key=lambda x:score(x[1]));return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':'',**m,'ocr_class':'no_text_detected','ocr_status':'ok','error':' | '.join(errors)}
        return {**base,'source_bytes':size,'source_sha256_verified':1,'attempts':';'.join(attempts),'selected_psm':'',**empty,'ocr_class':'unresolved','ocr_status':'error','error':' | '.join(errors)}
    except Exception as e:
        return {**base,'source_bytes':'','source_sha256_verified':0,'attempts':';'.join(attempts),'selected_psm':'',**empty,'ocr_class':'unresolved','ocr_status':'error','error':f'{type(e).__name__}: {e}'}
    finally:image.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--book-id',required=True);ap.add_argument('--output-dir',default='data/work/ltmd_u1_w1_1966_ocr');args=ap.parse_args()
    allrows=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    source=[r for r in allrows if r['book_id']==args.book_id and r['asset_status']=='source_jpeg']
    if not source:raise SystemExit(f'no W1 1966 source rows for {args.book_id}')
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w1-1966-ocr-') as td:
        tmp=Path(td);outrows=[process(r,tmp) for r in source]
    outrows.sort(key=lambda r:int(r['viewer_page']))
    verified=sum(str(r['source_sha256_verified'])=='1' for r in outrows)
    if verified!=len(outrows):raise SystemExit(f'provenance failure {args.book_id}: {verified}/{len(outrows)} SHA verified')
    outdir=Path(args.output_dir);outdir.mkdir(parents=True,exist_ok=True);slug=args.book_id.lower().replace('u1-','')
    out=outdir/f'ocr_{slug}.csv'
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(outrows)
    text=sum(r['ocr_class']=='text_detected' for r in outrows);no=sum(r['ocr_class']=='no_text_detected' for r in outrows);unres=sum(r['ocr_class']=='unresolved' for r in outrows)
    print(f'{args.book_id}: pages={len(outrows)} sha={verified} text={text} no_text={no} unresolved={unres} out={out}')
    if unres:raise SystemExit(f'{args.book_id}: unresolved OCR pages={unres}')

if __name__=='__main__':main()
