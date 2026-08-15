#!/usr/bin/env python3
"""Summarize final OCR metrics by catalog generation and book quartile.

This is a TECHNICAL profile only. It must not be interpreted as pedagogical
content or historical text length until CER/WER and content coding are complete.

Quartiles are calculated against structural viewer `page_count`, preserving the
same positional convention used by the preregistered sampling design.
"""
from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path

INVENTORY=Path('data/book_inventory.csv')
METRICS=Path('data/derived/ocr_page_metrics.csv')
OUTPUT=Path('data/derived/ocr_structure_by_quartile.csv')

FIELDS=[
    'catalog_generation','quartile','source_assets','text_pages','fallback_pages',
    'psm3_pages','psm11_pages','psm6_pages','recognized_words_accepted',
    'mean_words_per_text_page','median_words_per_text_page',
    'mean_word_confidence_page_mean','median_word_confidence_page_mean',
    'mean_low_confidence_rate','median_low_confidence_rate',
    'mean_source_bytes','median_source_bytes'
]


def quartile(viewer_page:int,page_count:int)->str:
    ratio=viewer_page/page_count
    if ratio<=0.25: return 'Q1'
    if ratio<=0.50: return 'Q2'
    if ratio<=0.75: return 'Q3'
    return 'Q4'


def fmean(values):
    return f'{statistics.mean(values):.4f}' if values else ''


def fmedian(values):
    return f'{statistics.median(values):.4f}' if values else ''


def main()->None:
    inventory={r['catalog_generation']:int(r['page_count']) for r in csv.DictReader(INVENTORY.open(encoding='utf-8',newline=''))}
    metrics=list(csv.DictReader(METRICS.open(encoding='utf-8',newline='')))
    groups=defaultdict(list)
    for r in metrics:
        gen=r['catalog_generation']
        q=quartile(int(r['viewer_page']),inventory[gen])
        groups[(gen,q)].append(r)

    out=[]
    for gen in ('1972','1988','1993','2014'):
        for q in ('Q1','Q2','Q3','Q4'):
            rs=groups[(gen,q)]
            text=[r for r in rs if r['ocr_class']=='text_detected']
            words=[int(r['recognized_words'] or 0) for r in text]
            conf=[float(r['mean_word_confidence']) for r in text if r['mean_word_confidence']]
            low=[float(r['low_confidence_word_rate']) for r in text if r['low_confidence_word_rate']]
            sizes=[int(r['source_bytes']) for r in rs if r['source_bytes']]
            out.append({
                'catalog_generation':gen,
                'quartile':q,
                'source_assets':len(rs),
                'text_pages':len(text),
                'fallback_pages':sum(r['selected_psm'] in {'6','11'} for r in rs),
                'psm3_pages':sum(r['selected_psm']=='3' for r in rs),
                'psm11_pages':sum(r['selected_psm']=='11' for r in rs),
                'psm6_pages':sum(r['selected_psm']=='6' for r in rs),
                'recognized_words_accepted':sum(words),
                'mean_words_per_text_page':fmean(words),
                'median_words_per_text_page':fmedian(words),
                'mean_word_confidence_page_mean':fmean(conf),
                'median_word_confidence_page_mean':fmedian(conf),
                'mean_low_confidence_rate':fmean(low),
                'median_low_confidence_rate':fmedian(low),
                'mean_source_bytes':fmean(sizes),
                'median_source_bytes':fmedian(sizes),
            })

    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with OUTPUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(out)

    for r in out:
        print(r)

if __name__=='__main__':
    main()
