#!/usr/bin/env python3
"""Compute CER/WER from a PRIVATE working CSV and publish metrics only.

Supported private-input schemas:

1. Current Drive-oriented schema:
   `sample_id,generation,page_id,reference_scope,crop_x0,crop_y0,crop_x1,crop_y1,
    human_reference_text_private,ocr_region_text_private,...`

2. Legacy minimal schema:
   `validation_id,book_id,catalog_generation,page_id,reference_text,hypothesis_text`

The output intentionally omits both reference and OCR text. It retains region
metadata so the comparison remains auditable without redistributing source text.
See `docs/OCR_REFERENCE_ALIGNMENT_PROTOCOL.md`.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path

OUT_FIELDS=(
    'validation_id','book_id','catalog_generation','page_id','reference_scope',
    'crop_x0','crop_y0','crop_x1','crop_y1','reference_chars','hypothesis_chars',
    'char_edits','cer','reference_words','hypothesis_words','word_edits','wer',
    'casefolded','status'
)


def norm_text(s:str)->str:
    s=unicodedata.normalize('NFC',s or '')
    s=s.replace('\r\n','\n').replace('\r','\n')
    return re.sub(r'\s+',' ',s).strip()


def edit_distance(a,b):
    if len(a)<len(b):
        a,b=b,a
    prev=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        cur=[i]
        for j,y in enumerate(b,1):
            cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
        prev=cur
    return prev[-1]


def first(row:dict,*names:str)->str:
    for name in names:
        value=row.get(name)
        if value is not None and str(value).strip()!='':
            return str(value)
    return ''


def validate_scope(row:dict)->tuple[str,str]:
    scope=first(row,'reference_scope')
    if not scope:
        # Legacy inputs may omit explicit scope.
        return '', ''
    if scope not in {'full_page','crop_block'}:
        return scope, 'invalid_reference_scope'
    if scope=='crop_block':
        vals=[]
        for field in ('crop_x0','crop_y0','crop_x1','crop_y1'):
            raw=first(row,field)
            try:
                vals.append(float(raw))
            except (TypeError,ValueError):
                return scope, f'missing_or_invalid_{field}'
        x0,y0,x1,y1=vals
        if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
            return scope, 'invalid_crop_bounds'
    return scope, ''


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input',help='Private CSV containing reference and OCR hypothesis text')
    ap.add_argument('--output',default='data/derived/ocr_cer_wer_metrics.csv')
    ap.add_argument('--casefold',action='store_true')
    args=ap.parse_args()

    rows=list(csv.DictReader(Path(args.input).open(encoding='utf-8',newline='')))
    out=[]
    for r in rows:
        validation_id=first(r,'sample_id','validation_id')
        book_id=first(r,'book_id')
        generation=first(r,'generation','catalog_generation')
        page_id=first(r,'page_id')
        scope,scope_error=validate_scope(r)
        base={
            'validation_id':validation_id,
            'book_id':book_id,
            'catalog_generation':generation,
            'page_id':page_id,
            'reference_scope':scope,
            'crop_x0':first(r,'crop_x0'),
            'crop_y0':first(r,'crop_y0'),
            'crop_x1':first(r,'crop_x1'),
            'crop_y1':first(r,'crop_y1'),
            'casefolded':'1' if args.casefold else '0',
        }
        if scope_error:
            out.append({**base,'reference_chars':'','hypothesis_chars':'','char_edits':'','cer':'','reference_words':'','hypothesis_words':'','word_edits':'','wer':'','status':scope_error})
            continue

        ref=norm_text(first(r,'human_reference_text_private','reference_text'))
        hyp=norm_text(first(r,'ocr_region_text_private','hypothesis_text'))
        if args.casefold:
            ref=ref.casefold(); hyp=hyp.casefold()

        if not ref:
            out.append({**base,'reference_chars':0,'hypothesis_chars':len(hyp),'char_edits':'','cer':'','reference_words':0,'hypothesis_words':len(hyp.split()),'word_edits':'','wer':'','status':'missing_reference'})
            continue
        if not hyp:
            # A genuinely blank hypothesis is evaluable: every reference char/word is a deletion.
            cd=len(ref); rw=ref.split(); wd=len(rw)
            out.append({**base,'reference_chars':len(ref),'hypothesis_chars':0,'char_edits':cd,'cer':f'{cd/len(ref):.6f}','reference_words':len(rw),'hypothesis_words':0,'word_edits':wd,'wer':f'{wd/len(rw):.6f}' if rw else '','status':'ok_blank_hypothesis'})
            continue

        cd=edit_distance(ref,hyp)
        rw=ref.split(); hw=hyp.split(); wd=edit_distance(rw,hw)
        out.append({**base,'reference_chars':len(ref),'hypothesis_chars':len(hyp),'char_edits':cd,'cer':f'{cd/len(ref):.6f}','reference_words':len(rw),'hypothesis_words':len(hw),'word_edits':wd,'wer':f'{wd/len(rw):.6f}' if rw else '','status':'ok'})

    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=OUT_FIELDS)
        w.writeheader(); w.writerows(out)

    ok=[r for r in out if str(r['status']).startswith('ok')]
    print(f'CER/WER computed for {len(ok)}/{len(out)} rows; output contains metrics/region metadata only.')

if __name__=='__main__':
    main()
