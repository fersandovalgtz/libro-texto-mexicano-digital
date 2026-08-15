#!/usr/bin/env python3
"""Audit whether the preregistered CER/WER sample represents OCR modes/difficulty.

Joins only metadata/metrics. No OCR transcription is read or persisted.
The primary 48-page sample is never modified by this script.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

SAMPLE = Path("data/samples/ocr_cer_wer_page_sample.csv")
METRICS = Path("data/derived/ocr_page_metrics.csv")
OUT = Path("data/derived/cer_sample_technical_profile.csv")
SUMMARY = Path("data/derived/cer_sample_technical_summary.csv")

FIELDS = [
    "sample_id","catalog_generation","role","page_id","viewer_page",
    "selected_psm","recognized_words","mean_word_confidence",
    "median_word_confidence","low_confidence_word_rate","ocr_class",
    "technical_stratum"
]


def technical_stratum(metric: dict[str,str]) -> str:
    if metric["ocr_class"] != "text_detected":
        return "no_text"
    if metric["selected_psm"] in {"6", "11"}:
        return "fallback"
    try:
        conf=float(metric["mean_word_confidence"] or 0)
        low=float(metric["low_confidence_word_rate"] or 0)
    except ValueError:
        return "baseline_unknown_quality"
    if conf < 80 or low >= 0.20:
        return "baseline_high_difficulty"
    if conf < 90 or low >= 0.08:
        return "baseline_moderate_difficulty"
    return "baseline_high_confidence"


def main() -> None:
    samples=list(csv.DictReader(SAMPLE.open(encoding="utf-8",newline="")))
    metrics={r["page_id"]:r for r in csv.DictReader(METRICS.open(encoding="utf-8",newline=""))}
    if len(samples)!=48:
        raise RuntimeError(f"Expected 48 preregistered sample rows, got {len(samples)}")

    joined=[]
    missing=[]
    for s in samples:
        m=metrics.get(s["page_id"])
        if not m:
            missing.append(s["page_id"])
            continue
        joined.append({
            "sample_id":s["sample_id"],
            "catalog_generation":s["catalog_generation"],
            "role":s["role"],
            "page_id":s["page_id"],
            "viewer_page":s["viewer_page"],
            "selected_psm":m["selected_psm"],
            "recognized_words":m["recognized_words"],
            "mean_word_confidence":m["mean_word_confidence"],
            "median_word_confidence":m["median_word_confidence"],
            "low_confidence_word_rate":m["low_confidence_word_rate"],
            "ocr_class":m["ocr_class"],
            "technical_stratum":technical_stratum(m),
        })
    if missing:
        raise RuntimeError("Missing page metrics: "+", ".join(missing))

    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(joined)

    summary_fields=[
        "catalog_generation","sample_pages","psm3","psm11","psm6","no_text",
        "fallback_pages","high_difficulty_pages","moderate_difficulty_pages",
        "high_confidence_pages"
    ]
    rows=[]
    for gen in ["1972","1988","1993","2014","TOTAL"]:
        rs=joined if gen=="TOTAL" else [r for r in joined if r["catalog_generation"]==gen]
        strata=Counter(r["technical_stratum"] for r in rs)
        rows.append({
            "catalog_generation":gen,
            "sample_pages":len(rs),
            "psm3":sum(r["selected_psm"]=="3" for r in rs),
            "psm11":sum(r["selected_psm"]=="11" for r in rs),
            "psm6":sum(r["selected_psm"]=="6" for r in rs),
            "no_text":sum(r["ocr_class"]!="text_detected" for r in rs),
            "fallback_pages":strata["fallback"],
            "high_difficulty_pages":strata["baseline_high_difficulty"],
            "moderate_difficulty_pages":strata["baseline_moderate_difficulty"],
            "high_confidence_pages":strata["baseline_high_confidence"],
        })
    with SUMMARY.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=summary_fields); w.writeheader(); w.writerows(rows)

    for row in rows:
        print(row)

if __name__=="__main__":
    main()
