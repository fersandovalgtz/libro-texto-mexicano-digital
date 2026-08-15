#!/usr/bin/env python3
"""Select a deterministic 25% double-coding subset for SEMB 0.3.

Reads only the frozen human-reference sample. Output exposes opaque sample IDs
only; generation and development/validation role remain hidden from annotators.
"""
from __future__ import annotations
import csv, hashlib
from collections import defaultdict
from pathlib import Path

SRC=Path('data/validation/semb03_human_reference_sample.csv')
OUT=Path('data/validation/semb03_reliability_subset.csv')
VERSION='SEMB03_RELIABILITY_SAMPLE_0.1'


def h(s): return hashlib.sha256((VERSION+'|'+s).encode()).hexdigest()


def main():
    rows=list(csv.DictReader(SRC.open(encoding='utf-8')))
    bygen=defaultdict(list)
    for r in rows: bygen[r['catalog_generation']].append(r)
    chosen=[]
    for gen in ('1972','1988','1993','2014'):
        pool=sorted(bygen[gen],key=lambda r:h(r['fragment_id']))
        assert len(pool)==120
        chosen.extend(pool[:30])
    assert len(chosen)==120 and len({r['sample_id'] for r in chosen})==120
    # Re-sort opaquely so output order does not preserve generation blocks.
    chosen=sorted(chosen,key=lambda r:h(r['sample_id']+'|order'))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['sample_id','reliability_sample_version'])
        w.writeheader()
        for r in chosen:w.writerow({'sample_id':r['sample_id'],'reliability_sample_version':VERSION})
    print('reliability subset',len(chosen))

if __name__=='__main__': main()
