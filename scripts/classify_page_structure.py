#!/usr/bin/env python3
"""Classify structural page type from OCR metrics + non-textual keyword flags.

Outputs only derived metadata. No source text is persisted.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

METRICS = Path("data/derived/ocr_page_metrics.csv")
FLAGS = Path("data/derived/structural_keyword_flags.csv")
OUT = Path("data/derived/page_structure.csv")
SUMMARY = Path("data/derived/page_structure_summary.csv")
VERSION = "PAGESTRUCT_0.2"


def fnum(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def inum(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def load_flags():
    if not FLAGS.exists():
        return {}
    return {r["page_id"]: r for r in csv.DictReader(FLAGS.open(encoding="utf-8"))}


def classify(r, k):
    words = inum(r.get("recognized_words"))
    conf = fnum(r.get("mean_word_confidence"), 0.0) or 0.0
    low = fnum(r.get("low_confidence_word_rate"), 1.0)
    psm = inum(r.get("selected_psm"), 0)
    ocr_class = r.get("ocr_class", "")

    front_zone = inum(k.get("front_zone", 0))
    end_zone = inum(k.get("end_zone", 0))
    fs = inum(k.get("front_matter_score", 0))
    ns = inum(k.get("toc_navigation_score", 0))
    bs = inum(k.get("bibliography_credits_score", 0))

    is_fallback = psm in (6, 11)
    strong_visual_noise = (
        ocr_class == "no_text_detected"
        or (is_fallback and conf < 50 and low >= 0.65)
        or (words <= 3 and conf < 50)
    )
    strong_text = words >= 120 and conf >= 75 and low <= 0.25
    moderate_text = words >= 20 and conf >= 60 and low <= 0.40
    dense_end_uncertain = end_zone and words >= 800 and conf < 85

    flags = []
    if front_zone: flags.append("front_zone")
    if end_zone: flags.append("end_zone")
    if is_fallback: flags.append("fallback_psm")
    if strong_visual_noise: flags.append("visual_noise")
    if strong_text: flags.append("text_rich")
    elif moderate_text: flags.append("text_present")
    if dense_end_uncertain: flags.append("dense_end_uncertain")
    if fs: flags.append("front_kw")
    if ns: flags.append("nav_kw")
    if bs: flags.append("biblio_credit_kw")

    # Structural keyword classes override generic text/image classes only when
    # there is direct keyword evidence, never position alone.
    if bs >= 2 or (bs >= 1 and (front_zone or end_zone) and conf >= 55):
        primary = "bibliography_or_credits"
        certainty = "high" if bs >= 2 else "medium"
        rule = "KW_BIBLIO_CREDITS"
    elif ns >= 2 or (ns >= 1 and front_zone and conf >= 65):
        primary = "toc_or_navigation"
        certainty = "high" if ns >= 2 else "medium"
        rule = "KW_NAVIGATION"
    elif fs >= 1 and front_zone and conf >= 55:
        primary = "front_matter"
        certainty = "medium" if fs == 1 else "high"
        rule = "KW_FRONT_MATTER"
    elif strong_visual_noise:
        primary = "visual_only"
        certainty = "high" if (is_fallback and low >= 0.80) or ocr_class == "no_text_detected" else "medium"
        rule = "OCR_VISUAL_NOISE"
    # PAGESTRUCT 0.2: an extremely dense, lower-confidence page in the final
    # 16-page zone is not confidently body text. If no structural keyword has
    # already resolved it, preserve it as unknown rather than force textual.
    elif dense_end_uncertain:
        primary = "unknown"
        certainty = "medium"
        rule = "END_ZONE_DENSE_UNCERTAIN"
    elif strong_text:
        primary = "textual"
        certainty = "high"
        rule = "OCR_TEXT_RICH"
    elif moderate_text:
        primary = "mixed_text_image"
        certainty = "medium"
        rule = "OCR_MODERATE_TEXT"
    elif words >= 4 and conf >= 75 and low <= 0.30:
        primary = "mixed_text_image"
        certainty = "low"
        rule = "OCR_SPARSE_HIGH_CONF"
    else:
        primary = "unknown"
        certainty = "low"
        rule = "CONSERVATIVE_UNKNOWN"

    return primary, certainty, rule, ";".join(flags)


def main():
    flags = load_flags()
    rows = list(csv.DictReader(METRICS.open(encoding="utf-8")))
    out = []
    for r in rows:
        if r.get("asset_status") != "source_jpeg":
            continue
        k = flags.get(r["page_id"], {})
        primary, certainty, rule, evidence = classify(r, k)
        out.append({
            "page_id": r["page_id"],
            "book_id": r["book_id"],
            "catalog_generation": r["catalog_generation"],
            "viewer_page": r["viewer_page"],
            "selected_psm": r["selected_psm"],
            "recognized_words": r["recognized_words"],
            "mean_word_confidence": r["mean_word_confidence"],
            "low_confidence_word_rate": r["low_confidence_word_rate"],
            "ocr_class": r["ocr_class"],
            "front_matter_score": k.get("front_matter_score", ""),
            "toc_navigation_score": k.get("toc_navigation_score", ""),
            "bibliography_credits_score": k.get("bibliography_credits_score", ""),
            "primary_structure": primary,
            "classification_certainty": certainty,
            "classification_rule": rule,
            "evidence_flags": evidence,
            "classifier_version": VERSION,
        })

    fields = list(out[0].keys())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)

    counts = defaultdict(Counter)
    for r in out:
        counts[r["catalog_generation"]][r["primary_structure"]] += 1
        counts["ALL"][r["primary_structure"]] += 1
    classes = ["textual", "mixed_text_image", "visual_only", "front_matter", "toc_or_navigation", "bibliography_or_credits", "unknown"]
    with SUMMARY.open("w", encoding="utf-8", newline="") as f:
        fields2 = ["catalog_generation", "n_pages"] + classes
        w = csv.DictWriter(f, fieldnames=fields2); w.writeheader()
        for gen in ["1972", "1988", "1993", "2014", "ALL"]:
            c = counts[gen]
            row = {"catalog_generation": gen, "n_pages": sum(c.values())}
            row.update({cl: c[cl] for cl in classes})
            w.writerow(row)
    print(f"wrote {len(out)} rows to {OUT}")
    print(SUMMARY.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
