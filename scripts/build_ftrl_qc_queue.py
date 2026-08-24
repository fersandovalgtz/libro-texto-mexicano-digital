#!/usr/bin/env python3
"""Build a text-free OCR quality-control queue from an LTMD FTRL page corpus.

The input JSONL may contain restricted OCR text. Outputs intentionally exclude OCR
text and search text, retaining only page identifiers, hashes, diagnostic metrics,
and flags needed for reproducible quality-control review.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

VERSION = "LTMD_FTRL_QC_0.1"


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSONL at line {line_number}: {exc}") from exc
            required = {
                "page_id",
                "viewer_key",
                "canonical_viewer_key",
                "wave",
                "catalog_generation",
                "grade_code",
                "page_index",
                "source_sha256",
                "ocr_sha256",
                "ocr_char_count",
                "ocr_word_count",
            }
            missing = required - set(row)
            if missing:
                raise SystemExit(
                    f"record at line {line_number} lacks required keys: {sorted(missing)}"
                )
            records.append(row)
    if not records:
        raise SystemExit("input corpus is empty")
    return records


def classify(
    row: dict,
    review_confidence: float,
    critical_confidence: float,
    short_chars: int,
) -> tuple[list[str], int]:
    flags: list[str] = []
    confidence = row.get("ocr_confidence_mean")
    char_count = int(row.get("ocr_char_count") or 0)
    word_count = int(row.get("ocr_word_count") or 0)
    search_text = row.get("search_text")

    if not search_text:
        flags.append("zero_search_text")
    if confidence is None:
        flags.append("missing_confidence")
    else:
        confidence = float(confidence)
        if confidence < critical_confidence:
            flags.append("low_confidence_critical")
        elif confidence < review_confidence:
            flags.append("low_confidence_review")
    if 0 < char_count < short_chars:
        flags.append("very_short_text")
    if char_count == 0:
        flags.append("zero_ocr_chars")
    if word_count == 0:
        flags.append("zero_ocr_words")

    weights = {
        "zero_search_text": 100,
        "zero_ocr_chars": 100,
        "zero_ocr_words": 80,
        "missing_confidence": 70,
        "low_confidence_critical": 60,
        "low_confidence_review": 30,
        "very_short_text": 20,
    }
    priority = sum(weights[flag] for flag in set(flags))
    return flags, priority


def safe_number(value):
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number):
        return None
    return number


def summarize(records: list[dict], queue: list[dict], thresholds: dict) -> dict:
    flags = Counter()
    by_generation = defaultdict(Counter)
    by_grade = defaultdict(Counter)
    by_viewer = defaultdict(Counter)
    confidences: list[float] = []

    for source, diagnostic in zip(records, queue):
        confidence = safe_number(source.get("ocr_confidence_mean"))
        if confidence is not None:
            confidences.append(confidence)
        for flag in diagnostic["flags"]:
            flags[flag] += 1
            by_generation[str(source["catalog_generation"])][flag] += 1
            by_grade[str(source["grade_code"])][flag] += 1
            by_viewer[str(source["canonical_viewer_key"])][flag] += 1

    confidence_summary = {
        "observed_pages": len(confidences),
        "missing_pages": len(records) - len(confidences),
        "minimum": min(confidences) if confidences else None,
        "median": statistics.median(confidences) if confidences else None,
        "mean": statistics.fmean(confidences) if confidences else None,
        "maximum": max(confidences) if confidences else None,
    }
    return {
        "schema_version": VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "rights_note": "Text-free OCR quality-control summary; contains no OCR or search text.",
        "thresholds": thresholds,
        "page_records": len(records),
        "pages_flagged": sum(1 for item in queue if item["flags"]),
        "pages_unflagged": sum(1 for item in queue if not item["flags"]),
        "flag_counts": dict(sorted(flags.items())),
        "confidence": confidence_summary,
        "flag_counts_by_generation": {
            key: dict(sorted(value.items())) for key, value in sorted(by_generation.items())
        },
        "flag_counts_by_grade": {
            key: dict(sorted(value.items(), key=lambda item: item[0]))
            for key, value in sorted(by_grade.items(), key=lambda item: int(item[0]))
        },
        "flag_counts_by_canonical_viewer": {
            key: dict(sorted(value.items())) for key, value in sorted(by_viewer.items())
        },
    }


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--queue-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--review-confidence", type=float, default=80.0)
    parser.add_argument("--critical-confidence", type=float, default=70.0)
    parser.add_argument("--short-chars", type=int, default=100)
    args = parser.parse_args()

    if not 0 <= args.critical_confidence <= args.review_confidence <= 100:
        raise SystemExit("confidence thresholds must satisfy 0 <= critical <= review <= 100")
    if args.short_chars < 1:
        raise SystemExit("--short-chars must be >= 1")

    records = load_records(args.input)
    queue: list[dict] = []
    for row in records:
        flags, priority = classify(
            row,
            args.review_confidence,
            args.critical_confidence,
            args.short_chars,
        )
        queue.append(
            {
                "page_id": row["page_id"],
                "viewer_key": row["viewer_key"],
                "canonical_viewer_key": row["canonical_viewer_key"],
                "wave": row["wave"],
                "catalog_generation": row["catalog_generation"],
                "grade_code": row["grade_code"],
                "page_index": row["page_index"],
                "viewer_page": row.get("viewer_page"),
                "source_sha256": row["source_sha256"],
                "ocr_sha256": row["ocr_sha256"],
                "ocr_confidence_mean": safe_number(row.get("ocr_confidence_mean")),
                "ocr_char_count": int(row.get("ocr_char_count") or 0),
                "ocr_word_count": int(row.get("ocr_word_count") or 0),
                "flags": sorted(flags),
                "priority_score": priority,
            }
        )

    queue.sort(
        key=lambda item: (
            -item["priority_score"],
            item["catalog_generation"],
            item["grade_code"],
            item["canonical_viewer_key"],
            item["page_index"],
        )
    )
    thresholds = {
        "review_confidence_below": args.review_confidence,
        "critical_confidence_below": args.critical_confidence,
        "very_short_text_below_chars": args.short_chars,
    }
    summary = summarize(records, queue, thresholds)

    queue_payload = {
        "schema_version": VERSION,
        "generated_at": summary["generated_at"],
        "rights_note": "Text-free page-level OCR QC queue; contains no OCR or search text.",
        "thresholds": thresholds,
        "pages": queue,
    }
    write_json(args.queue_output, queue_payload)
    write_json(args.summary_output, summary)

    print(
        json.dumps(
            {
                "status": "ok",
                "page_records": summary["page_records"],
                "pages_flagged": summary["pages_flagged"],
                "flag_counts": summary["flag_counts"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
