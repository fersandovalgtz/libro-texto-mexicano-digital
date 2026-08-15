#!/usr/bin/env python3
"""Build a supplementary OCR stress sample without altering the primary CER/WER sample.

Selection is metadata-only and deterministic. For each catalog generation, choose
three pages outside the 48-page primary sample, prioritizing pages that required
fallback OCR (`psm 11` or `psm 6`). Difficulty ordering uses high
`low_confidence_word_rate`, then low mean confidence, then viewer page.

The resulting 12-page supplement is for *diagnostic accuracy of the adaptive
OCR path*. It must never be pooled with the preregistered 48-page primary sample
when estimating the primary CER/WER summary unless explicitly reported as a
separate sensitivity analysis.
"""
from __future__ import annotations

import csv
from pathlib import Path

PRIMARY = Path("data/samples/ocr_cer_wer_page_sample.csv")
METRICS = Path("data/derived/ocr_page_metrics.csv")
OUTPUT = Path("data/samples/ocr_cer_wer_stress_sample.csv")

FIELDS = [
    "sample_id","sample_type","catalog_generation","page_id","viewer_page",
    "selected_psm","recognized_words","mean_word_confidence",
    "low_confidence_word_rate","source_asset_url","selection_reason",
    "target_reference_words","reference_status","second_review_status"
]

VIEWER_KEYS = {
    "1972":"H1972P5CI084",
    "1988":"H1988P5CI123",
    "1993":"H1993P5CI200",
    "2014":"H2014P5CNA",
}


def difficulty_key(row: dict[str,str]) -> tuple[float,float,int]:
    try: low=float(row["low_confidence_word_rate"] or 0)
    except ValueError: low=0.0
    try: conf=float(row["mean_word_confidence"] or 100)
    except ValueError: conf=100.0
    return (-low, conf, int(row["viewer_page"]))


def source_url(gen: str, viewer_page: int) -> str:
    key=VIEWER_KEYS[gen]
    image_index=0 if viewer_page==1 else viewer_page
    return f"https://historico.conaliteg.gob.mx/c/{key}/{image_index:03d}.jpg"


def main() -> None:
    primary={r["page_id"] for r in csv.DictReader(PRIMARY.open(encoding="utf-8",newline=""))}
    metrics=list(csv.DictReader(METRICS.open(encoding="utf-8",newline="")))
    selected=[]

    for gen in ("1972","1988","1993","2014"):
        pool=[
            r for r in metrics
            if r["catalog_generation"]==gen
            and r["page_id"] not in primary
            and r["ocr_class"]=="text_detected"
            and r["selected_psm"] in {"11","6"}
        ]
        if len(pool)<3:
            raise RuntimeError(f"{gen}: only {len(pool)} eligible fallback pages outside primary sample")

        p11=sorted([r for r in pool if r["selected_psm"]=="11"],key=difficulty_key)
        p6=sorted([r for r in pool if r["selected_psm"]=="6"],key=difficulty_key)
        picks=[]
        if p11:
            picks.append(p11[0])
        if p6:
            picks.append(p6[0])
        remaining=sorted([r for r in pool if r not in picks],key=difficulty_key)
        for r in remaining:
            if len(picks)>=3: break
            picks.append(r)

        if len(picks)!=3:
            raise RuntimeError(f"{gen}: expected 3 stress pages, got {len(picks)}")

        for idx,r in enumerate(picks,1):
            vp=int(r["viewer_page"])
            selected.append({
                "sample_id":f"LTMD-STRESS-{gen}-{idx:02d}",
                "sample_type":"supplementary_ocr_stress",
                "catalog_generation":gen,
                "page_id":r["page_id"],
                "viewer_page":vp,
                "selected_psm":r["selected_psm"],
                "recognized_words":r["recognized_words"],
                "mean_word_confidence":r["mean_word_confidence"],
                "low_confidence_word_rate":r["low_confidence_word_rate"],
                "source_asset_url":source_url(gen,vp),
                "selection_reason":f"fallback_psm{r['selected_psm']}_outside_primary_ranked_by_difficulty",
                "target_reference_words":120,
                "reference_status":"pending",
                "second_review_status":"pending",
            })

    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with OUTPUT.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(selected)

    assert len(selected)==12
    for gen in ("1972","1988","1993","2014"):
        rs=[r for r in selected if r["catalog_generation"]==gen]
        print(gen,[(r["page_id"],r["selected_psm"],r["mean_word_confidence"],r["low_confidence_word_rate"]) for r in rs])

if __name__=="__main__":
    main()
