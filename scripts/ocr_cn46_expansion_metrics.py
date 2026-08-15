#!/usr/bin/env python3
"""Hash-verified adaptive OCR metrics for the CN4/CN6 expansion.

Every source JPEG is reconstructed in a temporary directory, SHA-256 checked
against `cn46_page_manifest.csv`, OCRed, and deleted. Only technical metrics are
persisted. No OCR transcription or source image is committed.
"""
from __future__ import annotations
import csv,hashlib,statistics,subprocess,tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request,urlopen

MAN=Path('data/expansion/cn46_page_manifest.csv')
OUT=Path('data/expansion/cn46_ocr_page_metrics.csv')
SUMMARY=Path('data/expansion/cn46_ocr_summary.csv')
REPORT=Path('data/expansion/cn46_ocr_report.md')
VERSION='CN46_OCR_0.1'
UA='LibroTextoMexicanoDigital/0.1 CN46 OCR'
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
    got=h.hexdigest();expected=row['sha256']
    if got!=expected:raise RuntimeError(f'SHA256 mismatch expected={expected} got={got}')
    if row.get('byte_size') and total!=int(row['byte_size']):raise RuntimeError(f'byte size mismatch expected={row["byte_size"]} got={total}')
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
    source=[r for r in csv.DictReader(MAN.open(encoding='utf-8',newline='')) if r['asset_status']=='source_jpeg']
    if len(source)!=1888 or any(not r['sha256'] for r in source):raise SystemExit('complete CN46_PAGE_MANIFEST_0.2 required')
    with tempfile.TemporaryDirectory(prefix='ltmd-cn46-ocr-') as td:
        tmp=Path(td)
        with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda r:process(r,tmp),source))
    rows.sort(key=lambda r:(r['book_id'],int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    summary=[]
    for bid in sorted({r['book_id'] for r in rows}):
        rr=[r for r in rows if r['book_id']==bid]
        summary.append({'ocr_version':VERSION,'book_id':bid,'catalog_generation':rr[0]['catalog_generation'],'grade':rr[0]['grade'],'source_pages':len(rr),'sha_verified':sum(str(r['source_sha256_verified'])=='1' for r in rr),'text_detected':sum(r['ocr_class']=='text_detected' for r in rr),'no_text_detected':sum(r['ocr_class']=='no_text_detected' for r in rr),'unresolved':sum(r['ocr_class']=='unresolved' for r in rr),'psm3':sum(str(r['selected_psm'])=='3' for r in rr),'psm11':sum(str(r['selected_psm'])=='11' for r in rr),'psm6':sum(str(r['selected_psm'])=='6' for r in rr)})
    with SUMMARY.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    total=len(rows);text=sum(r['ocr_class']=='text_detected' for r in rows);unres=sum(r['ocr_class']=='unresolved' for r in rows);verified=sum(str(r['source_sha256_verified'])=='1' for r in rows)
    lines=['# OCR técnico — expansión CN4/CN6','',f'Versión: `{VERSION}`. Todas las páginas se reconstruyen temporalmente y su SHA-256 se verifica antes del OCR.','',f'- JPEG procesados: **{total:,}**.\n- SHA-256 verificados: **{verified:,}**.\n- Texto detectado: **{text:,}/{total:,} ({100*text/total:.2f}%)**.\n- No-text: **{sum(r["ocr_class"]=="no_text_detected" for r in rows)}**.\n- Unresolved: **{unres}**.','', '## Por objeto']
    for s in summary:lines.append(f"- `{s['book_id']}`: {s['text_detected']}/{s['source_pages']} text; no-text={s['no_text_detected']}; unresolved={s['unresolved']}; psm3={s['psm3']}, psm11={s['psm11']}, psm6={s['psm6']}.")
    lines+=['','## Restricción','`text_detected` mide cobertura técnica, no exactitud CER/WER. El OCR íntegro no se persiste. Páginas `no_text_detected` o `unresolved` se conservan como diagnósticos y no se sustituyen silenciosamente. Esta expansión permanece técnica y no adquiere estatus `semantic_ready` por completar OCR.']
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))
    # Hash/provenance failures are fatal; legitimate OCR non-text/unresolved rows are reportable.
    if verified!=total:raise SystemExit(f'provenance failure: only {verified}/{total} source hashes verified')

if __name__=='__main__':main()
