#!/usr/bin/env python3
"""Audit FRAGSEG manifest using derived metadata only.

No OCR/source text is read. Produces reproducible size/density/uncertainty summaries.
"""
from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path('data/derived/fragment_manifest.csv')
OUT = Path('data/derived/fragment_segmentation_audit.csv')
PAGE_OUT = Path('data/derived/fragment_page_density_audit.csv')
VERSION = 'FRAGAUDIT_0.1'


def quantile(xs, q):
    if not xs:
        return 0.0
    ys = sorted(xs)
    if len(ys) == 1:
        return float(ys[0])
    pos = (len(ys)-1)*q
    lo = math.floor(pos); hi = math.ceil(pos)
    if lo == hi:
        return float(ys[lo])
    return ys[lo] + (ys[hi]-ys[lo])*(pos-lo)


def summarize(rows, gen, ctype):
    toks=[int(r['token_count']) for r in rows]
    chars=[int(r['char_count']) for r in rows]
    uncertain=sum(int(r['uncertain_boundary']) for r in rows)
    return {
        'catalog_generation':gen,
        'candidate_type':ctype,
        'fragment_count':len(rows),
        'token_min':min(toks) if toks else 0,
        'token_p05':round(quantile(toks,.05),2),
        'token_p25':round(quantile(toks,.25),2),
        'token_median':round(quantile(toks,.5),2),
        'token_p75':round(quantile(toks,.75),2),
        'token_p95':round(quantile(toks,.95),2),
        'token_max':max(toks) if toks else 0,
        'mean_tokens':round(sum(toks)/len(toks),2) if toks else 0,
        'mean_chars':round(sum(chars)/len(chars),2) if chars else 0,
        'uncertain_count':uncertain,
        'uncertain_rate':round(uncertain/len(rows),6) if rows else 0,
        'gt120_tokens':sum(x>120 for x in toks),
        'gt250_tokens':sum(x>250 for x in toks),
        'gt500_tokens':sum(x>500 for x in toks),
        'le3_tokens':sum(x<=3 for x in toks),
        'audit_version':VERSION,
    }


def main():
    rows=list(csv.DictReader(SRC.open(encoding='utf-8')))
    assert rows, 'empty manifest'
    assert len({r['fragment_id'] for r in rows})==len(rows)
    groups=defaultdict(list)
    for r in rows:
        groups[(r['catalog_generation'],r['candidate_type'])].append(r)
        groups[(r['catalog_generation'],'ALL')].append(r)
        groups[('ALL',r['candidate_type'])].append(r)
        groups[('ALL','ALL')].append(r)
    summaries=[summarize(v,*k) for k,v in sorted(groups.items())]
    fields=list(summaries[0].keys())
    with OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(summaries)

    bypage=defaultdict(list)
    for r in rows: bypage[r['page_id']].append(r)
    page_rows=[]
    for pid,rs in sorted(bypage.items()):
        toks=sum(int(r['token_count']) for r in rs)
        uncertain=sum(int(r['uncertain_boundary']) for r in rs)
        types=Counter(r['candidate_type'] for r in rs)
        page_rows.append({
            'page_id':pid,
            'catalog_generation':rs[0]['catalog_generation'],
            'viewer_page':rs[0]['viewer_page'],
            'source_structure_class':rs[0]['source_structure_class'],
            'fragment_count':len(rs),
            'total_fragment_tokens':toks,
            'mean_fragment_tokens':round(toks/len(rs),2),
            'heading_share':round(types['heading_candidate']/len(rs),6),
            'question_share':round(types['question_candidate']/len(rs),6),
            'instruction_share':round(types['instruction_candidate']/len(rs),6),
            'uncertain_count':uncertain,
            'audit_version':VERSION,
        })
    with PAGE_OUT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(page_rows[0].keys())); w.writeheader(); w.writerows(page_rows)

    overall=[x for x in summaries if x['catalog_generation']=='ALL' and x['candidate_type']=='ALL'][0]
    print('fragments',len(rows),'pages',len(bypage))
    print('overall',overall)
    for g in ['1972','1988','1993','2014']:
        s=[x for x in summaries if x['catalog_generation']==g and x['candidate_type']=='ALL'][0]
        print(g,s)
    assert overall['gt500_tokens']==0, overall
    assert overall['uncertain_rate'] <= .05, overall

if __name__=='__main__':
    main()
