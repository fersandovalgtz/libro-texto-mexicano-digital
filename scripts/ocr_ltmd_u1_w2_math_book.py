#!/usr/bin/env python3
"""SHA-verified adaptive OCR metrics for one canonical LTMD-U1 W2 Mathematics viewer.

Version 0.2 operates on the reconciled source manifest. Only effectively
resolved, non-alias canonical viewers are processed. Source JPEGs are temporary,
verified against effective SHA-256/byte-size evidence, OCRed, then deleted.
Full OCR text is never persisted.
"""
from __future__ import annotations
import argparse,csv,hashlib,statistics,subprocess,tempfile
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/catalog/ltmd_u1_w2_math_reconciled_manifest.csv')
SUMMARY=Path('data/catalog/ltmd_u1_w2_math_reconciled_summary.csv')
ALIASES=Path('data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv')
SCOPE=Path('data/catalog/ltmd_u1_w2_scope.csv')
VERSION='LTMD_U1_W2_MATH_OCR_0.2'
UA='LibroTextoMexicanoDigital/U1-W2 Mathematics OCR 0.2'
FALLBACK_MIN_WORDS=5
TIMEOUT=60
EXPECTED_SCOPE=64
EXPECTED_READY=60
EXPECTED_ALIASES=3
EXPECTED_CANONICAL=57
FIELDS=['ocr_version','page_id','viewer_key','book_id','catalog_generation','grade','viewer_page','asset_status','effective_source_viewer_key','resolution_method','source_bytes','source_sha256_verified','attempts','selected_psm','recognized_words','ocr_chars','mean_word_confidence','median_word_confidence','low_confidence_word_rate','ocr_class','ocr_status','error']

def page_id(row): return f"U1-{row['viewer_key']}-P{int(row['viewer_page']):03d}"

def canonical_viewers():
    if not all(p.exists() for p in (MAN,SUMMARY,ALIASES,SCOPE)):
        raise SystemExit('W2 reconciled asset/alias evidence not materialized')
    scope=list(csv.DictReader(SCOPE.open(encoding='utf-8')))
    summary=list(csv.DictReader(SUMMARY.open(encoding='utf-8')))
    aliases=list(csv.DictReader(ALIASES.open(encoding='utf-8')))
    if len(scope)!=EXPECTED_SCOPE or len(summary)!=EXPECTED_SCOPE:
        raise SystemExit(f'W2 cardinality mismatch scope={len(scope)} summary={len(summary)}')
    sk={r['viewer_key'] for r in scope}; sm={r['viewer_key'] for r in summary}
    if sk!=sm: raise SystemExit('W2 scope/reconciled summary viewer mismatch')
    ready={r['viewer_key'] for r in summary if r['effective_asset_ready']=='1'}
    if len(ready)!=EXPECTED_READY: raise SystemExit(f'expected {EXPECTED_READY} effective-ready viewers, got {len(ready)}')
    alias={r['viewer_key'] for r in aliases if r.get('all_effective_pages_byte_identical_aligned')=='1'}
    if len(alias)!=EXPECTED_ALIASES or not alias<=ready:
        raise SystemExit(f'expected {EXPECTED_ALIASES} ready aliases, got {len(alias)}')
    canonical=ready-alias
    if len(canonical)!=EXPECTED_CANONICAL: raise SystemExit(f'expected {EXPECTED_CANONICAL} canonical viewers, got {len(canonical)}')
    return canonical

def gate_assets(viewer_key):
    canonical=canonical_viewers()
    if viewer_key not in canonical:
        raise SystemExit(f'viewer is not a W2 canonical compute viewer: {viewer_key}')

def download_verify(row,target):
    h=hashlib.sha256();total=0;url=row['effective_asset_url']
    if not url or not row['effective_sha256']: raise RuntimeError('missing effective source evidence')
    with urlopen(Request(url,headers={'User-Agent':UA}),timeout=45) as r, target.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            h.update(b);total+=len(b);f.write(b)
    got=h.hexdigest()
    if got!=row['effective_sha256']: raise RuntimeError(f"SHA256 mismatch expected={row['effective_sha256']} got={got}")
    if row.get('effective_byte_size') and total!=int(row['effective_byte_size']): raise RuntimeError(f"byte size mismatch expected={row['effective_byte_size']} got={total}")
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
    base={'ocr_version':VERSION,'page_id':pid,'viewer_key':row['viewer_key'],'book_id':row['book_id'],'catalog_generation':row['catalog_generation'],'grade':row['grade_code'],'viewer_page':row['viewer_page'],'asset_status':row['effective_asset_status'],'effective_source_viewer_key':row['effective_source_viewer_key'],'resolution_method':row['resolution_method']}
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
    source=[r for r in allrows if r['viewer_key']==args.viewer_key and r['effective_asset_status'] in ('source_jpeg','source_jpeg_recovered')]
    if not source: raise SystemExit(f'no effective W2 source rows for {args.viewer_key}')
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
