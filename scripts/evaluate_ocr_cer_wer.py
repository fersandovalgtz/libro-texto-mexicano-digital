#!/usr/bin/env python3
"""Compute CER/WER from a PRIVATE working CSV and publish metrics only.

The evaluator implements the preregistered conventions in
`docs/OCR_TRANSCRIPTION_CONVENTIONS.md` and reports two metric families:

- orthographic: layout-normalized, preserving case, accents and meaningful
  punctuation;
- lexical: casefolded and punctuation/symbol neutralized, preserving letters,
  diacritics and numbers. This is the primary family for analytical viability.

The output intentionally omits both reference and OCR text. It retains region
metadata so the comparison remains auditable without redistributing source text.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path

OUT_FIELDS=(
    'validation_id','book_id','catalog_generation','page_id','reference_scope',
    'crop_x0','crop_y0','crop_x1','crop_y1',
    'reference_chars_orthographic','hypothesis_chars_orthographic',
    'char_edits_orthographic','cer_orthographic',
    'reference_words_orthographic','hypothesis_words_orthographic',
    'word_edits_orthographic','wer_orthographic',
    'reference_chars_lexical','hypothesis_chars_lexical',
    'char_edits_lexical','cer_lexical',
    'reference_words_lexical','hypothesis_words_lexical',
    'word_edits_lexical','wer_lexical',
    # Convenience aliases used in narrative summaries / legacy consumers.
    # They intentionally point to the PRIMARY lexical family.
    'cer','wer','status'
)

TYPOGRAPHIC_TRANSLATION=str.maketrans({
    '\u2018':"'", '\u2019':"'", '\u201a':"'", '\u201b':"'",
    '\u201c':'"', '\u201d':'"', '\u201e':'"', '\u201f':'"',
    '\u00ab':'"', '\u00bb':'"',
    '\u2010':'-', '\u2011':'-', '\u2012':'-', '\u2013':'-',
    '\u2014':'-', '\u2212':'-',
    '\u2026':'...',
    '\u00a0':' ',
})


def normalize_orthographic(s:str)->str:
    """Normalize layout artifacts while retaining linguistic orthography."""
    s=unicodedata.normalize('NFC',s or '')
    s=s.replace('\r\n','\n').replace('\r','\n')
    s=s.translate(TYPOGRAPHIC_TRANSLATION)
    # Rejoin words split only because the printed/OCR line wrapped.
    # A genuine in-word hyphen that is not followed by a newline remains.
    s=re.sub(r'(?<=\w)-[ \t]*\n[ \t]*(?=\w)', '', s)
    # Dot leaders in indices are layout, not linguistic punctuation. This also
    # neutralizes repeated spaced leader patterns such as '. . . .'.
    s=re.sub(r'(?:\.[ \t]*){3,}', ' ', s)
    s=re.sub(r'\s+',' ',s).strip()
    return s


def normalize_lexical(s:str)->str:
    """Normalize to lexical content while preserving accents and numbers."""
    s=normalize_orthographic(s).casefold()
    out=[]
    for ch in s:
        cat=unicodedata.category(ch)
        if cat.startswith(('L','M','N')):
            out.append(ch)
        else:
            out.append(' ')
    return re.sub(r'\s+',' ',''.join(out)).strip()


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


def metric_family(ref:str,hyp:str,prefix:str)->dict:
    """Return edit counts/rates for one already-normalized text family."""
    rw=ref.split(); hw=hyp.split()
    if not ref:
        return {
            f'reference_chars_{prefix}':0,
            f'hypothesis_chars_{prefix}':len(hyp),
            f'char_edits_{prefix}':'',f'cer_{prefix}':'',
            f'reference_words_{prefix}':0,
            f'hypothesis_words_{prefix}':len(hw),
            f'word_edits_{prefix}':'',f'wer_{prefix}':'',
        }
    cd=edit_distance(ref,hyp)
    wd=edit_distance(rw,hw)
    return {
        f'reference_chars_{prefix}':len(ref),
        f'hypothesis_chars_{prefix}':len(hyp),
        f'char_edits_{prefix}':cd,
        f'cer_{prefix}':f'{cd/len(ref):.6f}',
        f'reference_words_{prefix}':len(rw),
        f'hypothesis_words_{prefix}':len(hw),
        f'word_edits_{prefix}':wd,
        f'wer_{prefix}':f'{wd/len(rw):.6f}' if rw else '',
    }


def blank_metrics()->dict:
    return {field:'' for field in OUT_FIELDS if field not in {
        'validation_id','book_id','catalog_generation','page_id','reference_scope',
        'crop_x0','crop_y0','crop_x1','crop_y1','status'
    }}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input',help='Private CSV containing reference and OCR hypothesis text')
    ap.add_argument('--output',default='data/derived/ocr_cer_wer_metrics.csv')
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
        }
        if scope_error:
            out.append({**base,**blank_metrics(),'status':scope_error})
            continue

        raw_ref=first(r,'human_reference_text_private','reference_text')
        raw_hyp=first(r,'ocr_region_text_private','hypothesis_text')
        ref_o=normalize_orthographic(raw_ref)
        hyp_o=normalize_orthographic(raw_hyp)
        ref_l=normalize_lexical(raw_ref)
        hyp_l=normalize_lexical(raw_hyp)

        if not ref_o:
            metrics={**metric_family(ref_o,hyp_o,'orthographic'),
                     **metric_family(ref_l,hyp_l,'lexical')}
            out.append({**base,**metrics,'cer':'','wer':'','status':'missing_reference'})
            continue

        metrics={**metric_family(ref_o,hyp_o,'orthographic'),
                 **metric_family(ref_l,hyp_l,'lexical')}
        status='ok_blank_hypothesis' if not hyp_o else 'ok'
        out.append({
            **base,**metrics,
            'cer':metrics['cer_lexical'],
            'wer':metrics['wer_lexical'],
            'status':status,
        })

    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=OUT_FIELDS)
        w.writeheader(); w.writerows(out)

    ok=[r for r in out if str(r['status']).startswith('ok')]
    print(f'CER/WER computed for {len(ok)}/{len(out)} rows; output contains metrics/region metadata only.')
    print('Primary aliases cer/wer = lexical metrics; orthographic metrics are retained separately.')

if __name__=='__main__':
    main()
