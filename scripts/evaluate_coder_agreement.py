#!/usr/bin/env python3
"""Evaluate multi-label coder agreement for LTMD human codebook validation.

Input values are pipe-separated label sets. The script does not require or read
source fragment text. It reports:
- exact set agreement by dimension;
- per-fragment Jaccard;
- per-label raw/positive/negative agreement and Cohen's kappa.

Kappa is retained as one diagnostic and must not be interpreted without label
prevalence. See docs/CODER_AGREEMENT_PROTOCOL_0_1.md.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

DIMENSIONS = {
    "types": ("types_a", "types_b"),
    "actions": ("actions_a", "actions_b"),
    "positions": ("positions_a", "positions_b"),
}

SUMMARY_FIELDS = [
    "dimension","n_fragments","exact_matches","exact_match_rate",
    "mean_jaccard","median_jaccard","min_jaccard","max_jaccard"
]
LABEL_FIELDS = [
    "dimension","label","n","a_positive","b_positive","both_positive",
    "both_negative","raw_agreement","positive_agreement","negative_agreement",
    "cohen_kappa","mean_positive_prevalence"
]
FRAGMENT_FIELDS = [
    "sample_id","catalog_generation","dimension","set_a","set_b",
    "exact_match","jaccard"
]


def parse_set(value: str | None) -> set[str]:
    if not value:
        return set()
    return {x.strip() for x in value.split("|") if x.strip()}


def fmt(x: float | None) -> str:
    if x is None or math.isnan(x):
        return ""
    return f"{x:.4f}"


def jaccard(a: set[str], b: set[str]) -> float | None:
    union=a|b
    if not union:
        return None
    return len(a&b)/len(union)


def kappa_binary(a_vals: list[bool], b_vals: list[bool]) -> float | None:
    n=len(a_vals)
    if n==0:
        return None
    observed=sum(a==b for a,b in zip(a_vals,b_vals))/n
    pa=sum(a_vals)/n
    pb=sum(b_vals)/n
    expected=pa*pb+(1-pa)*(1-pb)
    if math.isclose(1-expected,0.0):
        return None
    return (observed-expected)/(1-expected)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="working/coder_agreement_input.csv")
    ap.add_argument("--summary",default="data/derived/coder_agreement_summary.csv")
    ap.add_argument("--labels",default="data/derived/coder_agreement_by_label.csv")
    ap.add_argument("--fragments",default="data/derived/coder_agreement_by_fragment.csv")
    args=ap.parse_args()

    rows=list(csv.DictReader(Path(args.input).open(encoding="utf-8",newline="")))
    if not rows:
        raise RuntimeError("Agreement input is empty")

    summaries=[]
    label_rows=[]
    fragment_rows=[]

    for dimension,(a_field,b_field) in DIMENSIONS.items():
        pairs=[]
        for row in rows:
            a=parse_set(row.get(a_field))
            b=parse_set(row.get(b_field))
            jac=jaccard(a,b)
            pairs.append((row,a,b,jac))
            fragment_rows.append({
                "sample_id":row.get("sample_id",""),
                "catalog_generation":row.get("catalog_generation",""),
                "dimension":dimension,
                "set_a":"|".join(sorted(a)),
                "set_b":"|".join(sorted(b)),
                "exact_match":"1" if a==b else "0",
                "jaccard":fmt(jac),
            })

        jacs=[jac for _,_,_,jac in pairs if jac is not None]
        exact=sum(a==b for _,a,b,_ in pairs)
        summaries.append({
            "dimension":dimension,
            "n_fragments":len(pairs),
            "exact_matches":exact,
            "exact_match_rate":fmt(exact/len(pairs)),
            "mean_jaccard":fmt(statistics.mean(jacs)) if jacs else "",
            "median_jaccard":fmt(statistics.median(jacs)) if jacs else "",
            "min_jaccard":fmt(min(jacs)) if jacs else "",
            "max_jaccard":fmt(max(jacs)) if jacs else "",
        })

        labels=sorted(set().union(*(a|b for _,a,b,_ in pairs)))
        n=len(pairs)
        for label in labels:
            av=[label in a for _,a,_,_ in pairs]
            bv=[label in b for _,_,b,_ in pairs]
            a_pos=sum(av); b_pos=sum(bv)
            both_pos=sum(a and b for a,b in zip(av,bv))
            both_neg=sum((not a) and (not b) for a,b in zip(av,bv))
            raw=(both_pos+both_neg)/n
            pos_den=a_pos+b_pos
            neg_den=(n-a_pos)+(n-b_pos)
            pos_agree=(2*both_pos/pos_den) if pos_den else None
            neg_agree=(2*both_neg/neg_den) if neg_den else None
            label_rows.append({
                "dimension":dimension,
                "label":label,
                "n":n,
                "a_positive":a_pos,
                "b_positive":b_pos,
                "both_positive":both_pos,
                "both_negative":both_neg,
                "raw_agreement":fmt(raw),
                "positive_agreement":fmt(pos_agree),
                "negative_agreement":fmt(neg_agree),
                "cohen_kappa":fmt(kappa_binary(av,bv)),
                "mean_positive_prevalence":fmt((a_pos+b_pos)/(2*n)),
            })

    outputs=[
        (Path(args.summary),SUMMARY_FIELDS,summaries),
        (Path(args.labels),LABEL_FIELDS,label_rows),
        (Path(args.fragments),FRAGMENT_FIELDS,fragment_rows),
    ]
    for path,fields,data in outputs:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("w",encoding="utf-8",newline="") as fh:
            w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(data)

    for row in summaries:
        print(row)

if __name__=="__main__":
    main()
