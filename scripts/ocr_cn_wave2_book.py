#!/usr/bin/env python3
"""Per-book SHA-verified adaptive OCR metrics for CN Wave 2.

Source images are downloaded to a temporary directory, verified against the
frozen Wave 2 page manifest, OCRed and deleted. Full OCR text is never written.
"""
from __future__ import annotations
import argparse,csv,hashlib,statistics,subprocess,tempfile
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/expansion/cn_wave2_page_manifest.csv')
VERSION='CN_WAVE2_OCR_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN Wave2 OCR'
MODES=(3,11,6)
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
    base={'ocr_version':VERSION,'page_id':row['page_id'],'book_id':row['book_id'],'catalog_generation':row['catalog_generation'],'grade':row['grade'],'viewer_page':row['viewer_page'],'asset_status':row['asset_status']}
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
    ap=argparse.ArgumentParser();ap.add_argument('--book-id',required=True);ap.add_argument('--output-dir',default='data/work/cn_wave2_ocr');args=ap.parse_args()
    allrows=list(csv.DictReader(MAN.open(encoding='utf-8',newline='')))
    source=[r for r in allrows if r['book_id']==args.book_id and r['asset_status']=='source_jpeg']
    if not source:raise SystemExit(f'no Wave2 source rows for {args.book_id}')
    expected={r['book_id'] for r in allrows}
    if args.book_id not in expected:raise SystemExit(f'{args.book_id} not in Wave2 manifest')
    with tempfile.TemporaryDirectory(prefix='ltmd-cn-wave2-ocr-') as td:
        tmp=Path(td);rows=[process(r,tmp) for r in source]
    rows.sort(key=lambda r:int(r['viewer_page']))
    verified=sum(str(r['source_sha256_verified'])=='1' for r in rows)
    if verified!=len(rows):raise SystemExit(f'provenance failure {args.book_id}: {verified}/{len(rows)} SHA verified')
    outdir=Path(args.output_dir);outdir.mkdir(parents=True,exist_ok=True);slug=args.book_id.lower().replace('ltmd-','')
    out=outdir/f'ocr_{slug}.csv'
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    text=sum(r['ocr_class']=='text_detected' for r in rows);no=sum(r['ocr_class']=='no_text_detected' for r in rows);unres=sum(r['ocr_class']=='unresolved' for r in rows)
    print(f'{args.book_id}: pages={len(rows)} sha={verified} text={text} no_text={no} unresolved={unres} out={out}')

if __name__=='__main__':main()
