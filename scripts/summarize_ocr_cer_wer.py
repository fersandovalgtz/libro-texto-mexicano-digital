#!/usr/bin/env python3
"""Aggregate CER/WER metrics without reading private source/reference text.

Input is the metrics-only CSV produced by `evaluate_ocr_cer_wer.py`.
Outputs generation-level and overall summaries for:
- primary preregistered sample (`LTMD-CER-*`);
- supplementary stress sample (`LTMD-STRESS-*`).

Primary and stress results are intentionally kept separate.
"""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

FIELDS=[
    'sample_type','catalog_generation','n_valid','reference_chars','char_edits',
    'weighted_cer','mean_cer','median_cer','max_cer','reference_words','word_edits',
    'weighted_wer','mean_wer','median_wer','max_wer','cer_le_0_02','cer_le_0_05',
    'cer_le_0_10','cer_gt_0_10'
]


def sample_type(validation_id:str)->str:
    if validation_id.startswith('LTMD-STRESS-'):
        return 'stress'
    if validation_id.startswith('LTMD-CER-'):
        return 'primary'
    return 'other'


def ff(x:float)->str:
    return f'{x:.6f}'


def summarize(kind:str,gen:str,rows:list[dict])->dict:
    valid=[r for r in rows if str(r.get('status','')).startswith('ok') and r.get('cer') not in ('',None)]
    cer=[float(r['cer']) for r in valid]
    wer=[float(r['wer']) for r in valid if r.get('wer') not in ('',None)]
    ref_chars=sum(int(r['reference_chars']) for r in valid)
    char_edits=sum(int(r['char_edits']) for r in valid)
    ref_words=sum(int(r['reference_words']) for r in valid)
    word_edits=sum(int(r['word_edits']) for r in valid if r.get('word_edits') not in ('',None))
    return {
        'sample_type':kind,
        'catalog_generation':gen,
        'n_valid':len(valid),
        'reference_chars':ref_chars,
        'char_edits':char_edits,
        'weighted_cer':ff(char_edits/ref_chars) if ref_chars else '',
        'mean_cer':ff(statistics.mean(cer)) if cer else '',
        'median_cer':ff(statistics.median(cer)) if cer else '',
        'max_cer':ff(max(cer)) if cer else '',
        'reference_words':ref_words,
        'word_edits':word_edits,
        'weighted_wer':ff(word_edits/ref_words) if ref_words else '',
        'mean_wer':ff(statistics.mean(wer)) if wer else '',
        'median_wer':ff(statistics.median(wer)) if wer else '',
        'max_wer':ff(max(wer)) if wer else '',
        'cer_le_0_02':sum(x<=0.02 for x in cer),
        'cer_le_0_05':sum(x<=0.05 for x in cer),
        'cer_le_0_10':sum(x<=0.10 for x in cer),
        'cer_gt_0_10':sum(x>0.10 for x in cer),
    }


def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',default='data/derived/ocr_cer_wer_metrics.csv')
    ap.add_argument('--output',default='data/derived/ocr_cer_wer_summary.csv')
    args=ap.parse_args()

    rows=list(csv.DictReader(Path(args.input).open(encoding='utf-8',newline='')))
    groups=defaultdict(list)
    for r in rows:
        groups[(sample_type(r.get('validation_id','')),r.get('catalog_generation',''))].append(r)

    out=[]
    for kind in ('primary','stress'):
        kind_rows=[r for r in rows if sample_type(r.get('validation_id',''))==kind]
        if not kind_rows:
            continue
        gens=sorted({r.get('catalog_generation','') for r in kind_rows if r.get('catalog_generation','')})
        for gen in gens:
            out.append(summarize(kind,gen,[r for r in kind_rows if r.get('catalog_generation','')==gen]))
        out.append(summarize(kind,'TOTAL',kind_rows))

    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(out)
    for row in out:
        print(row)

if __name__=='__main__':
    main()
