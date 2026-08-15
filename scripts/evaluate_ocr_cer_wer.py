#!/usr/bin/env python3
"""Compute CER/WER from a private working CSV and publish metrics only.

Input is expected to remain outside GitHub and contain:
`validation_id,book_id,catalog_generation,page_id,reference_text,hypothesis_text`.
The output intentionally omits both text fields.
"""
from __future__ import annotations
import argparse,csv,re,unicodedata
from pathlib import Path

OUT_FIELDS=('validation_id','book_id','catalog_generation','page_id','reference_chars','hypothesis_chars','char_edits','cer','reference_words','hypothesis_words','word_edits','wer','status')

def norm_text(s:str)->str:
    s=unicodedata.normalize('NFC',s or '')
    s=s.replace('\r\n','\n').replace('\r','\n')
    return re.sub(r'\s+',' ',s).strip()

def edit_distance(a,b):
    if len(a)<len(b): a,b=b,a
    prev=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        cur=[i]
        for j,y in enumerate(b,1):
            cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
        prev=cur
    return prev[-1]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('--output',default='data/derived/ocr_cer_wer_metrics.csv'); ap.add_argument('--casefold',action='store_true'); args=ap.parse_args()
    rows=list(csv.DictReader(Path(args.input).open(encoding='utf-8',newline=''))); out=[]
    for r in rows:
        ref=norm_text(r.get('reference_text','')); hyp=norm_text(r.get('hypothesis_text',''))
        if args.casefold: ref=ref.casefold(); hyp=hyp.casefold()
        if not ref:
            out.append({'validation_id':r.get('validation_id',''),'book_id':r.get('book_id',''),'catalog_generation':r.get('catalog_generation',''),'page_id':r.get('page_id',''),'reference_chars':0,'hypothesis_chars':len(hyp),'char_edits':'','cer':'','reference_words':0,'hypothesis_words':len(hyp.split()),'word_edits':'','wer':'','status':'missing_reference'}); continue
        cd=edit_distance(ref,hyp); rw=ref.split(); hw=hyp.split(); wd=edit_distance(rw,hw)
        out.append({'validation_id':r.get('validation_id',''),'book_id':r.get('book_id',''),'catalog_generation':r.get('catalog_generation',''),'page_id':r.get('page_id',''),'reference_chars':len(ref),'hypothesis_chars':len(hyp),'char_edits':cd,'cer':f'{cd/len(ref):.6f}','reference_words':len(rw),'hypothesis_words':len(hw),'word_edits':wd,'wer':f'{wd/len(rw):.6f}' if rw else '','status':'ok'})
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=OUT_FIELDS); w.writeheader(); w.writerows(out)
    ok=[r for r in out if r['status']=='ok']
    print(f'CER/WER computed for {len(ok)}/{len(out)} rows; output contains metrics only.')
if __name__=='__main__': main()
