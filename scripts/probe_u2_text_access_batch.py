#!/usr/bin/env python3
"""Observe bounded PDF text-access state across all 39 canonical LTMD-U2 objects.

This experimental batch reuses the three-parser pilot contract. Each admitted
source is downloaded to a temporary directory, verified byte-for-byte and by
SHA-256 against the canonical source-admission registry, inspected, and then
deleted. No PDF body or extracted text is retained or emitted.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from probe_u2_text_layer_pilot import inspect_object, package_version

SOURCE_ADMISSION = Path("data/catalog/ltmd_u2_source_admission_2026_09_02.csv")

CSV_FIELDS = [
    "source_object_id",
    "viewer_key",
    "expected_page_count",
    "canonical_body_verified",
    "sha256",
    "pypdf_encrypted",
    "pypdf_blank_password_result",
    "pypdf_open_state",
    "pymupdf_needs_password",
    "pymupdf_blank_password_result",
    "pymupdf_open_state",
    "pikepdf_open_state",
    "max_sample_non_whitespace_chars",
    "text_layer_observation_state",
    "potential_ocr_need_state",
    "ocr_available_state",
    "text_verified_state",
    "source_pdf_persisted",
    "extracted_text_persisted",
    "error",
]


def read_rows() -> list[dict[str, str]]:
    with SOURCE_ADMISSION.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 39:
        raise RuntimeError(f"expected 39 canonical source-admission rows, got {len(rows)}")
    if len({r["source_object_id"] for r in rows}) != 39:
        raise RuntimeError("source_object_id is not unique in source-admission registry")
    return rows


def parser_map(result: dict) -> dict[str, dict]:
    return {p["parser"]: p for p in result.get("parsers", [])}


def max_non_ws(result: dict) -> int:
    values = [
        item["non_whitespace_chars"]
        for parser in result.get("parsers", [])
        for item in parser.get("sample_counts", [])
        if item.get("state") == "observed"
    ]
    return max(values or [0])


def flatten(result: dict) -> dict:
    parsers = parser_map(result)
    pypdf = parsers.get("pypdf", {})
    pymupdf = parsers.get("PyMuPDF", {})
    pikepdf = parsers.get("pikepdf", {})
    transport = result.get("transport_verification", {})
    return {
        "source_object_id": result["source_object_id"],
        "viewer_key": result["viewer_key"],
        "expected_page_count": result["expected_page_count"],
        "canonical_body_verified": transport.get("canonical_body_verified"),
        "sha256": transport.get("sha256"),
        "pypdf_encrypted": pypdf.get("encrypted"),
        "pypdf_blank_password_result": pypdf.get("blank_password_result"),
        "pypdf_open_state": pypdf.get("open_state"),
        "pymupdf_needs_password": pymupdf.get("needs_password"),
        "pymupdf_blank_password_result": pymupdf.get("blank_password_result"),
        "pymupdf_open_state": pymupdf.get("open_state"),
        "pikepdf_open_state": pikepdf.get("open_state"),
        "max_sample_non_whitespace_chars": max_non_ws(result),
        "text_layer_observation_state": result["text_layer_observation_state"],
        "potential_ocr_need_state": result["potential_ocr_need_state"],
        "ocr_available_state": result["ocr_available_state"],
        "text_verified_state": result["text_verified_state"],
        "source_pdf_persisted": result["source_pdf_persisted"],
        "extracted_text_persisted": result["extracted_text_persisted"],
        "error": "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--delay", type=float, default=0.20)
    parser.add_argument("--output-json", default="u2-text-access-all-39.json")
    parser.add_argument("--output-csv", default="u2-text-access-all-39.csv")
    args = parser.parse_args()

    results = []
    failures = []
    rows = read_rows()
    for index, row in enumerate(rows, start=1):
        result = None
        last_error = None
        for attempt in range(1, 4):
            try:
                result = inspect_object(row, args.timeout)
                result["observed_at"] = args.observed_at
                break
            except Exception as exc:
                last_error = f"{type(exc).__name__}:{exc}"
                if attempt < 3:
                    time.sleep(attempt)
        if result is None:
            failures.append({"source_object_id": row["source_object_id"], "viewer_key": row["viewer_key"], "error": last_error})
            print(f"[{index:02d}/39] {row['viewer_key']} observation_error={last_error}")
        else:
            results.append(result)
            print(
                f"[{index:02d}/39] {row['viewer_key']} "
                f"state={result['text_layer_observation_state']} "
                f"max_sample_non_ws_chars={max_non_ws(result)}"
            )
        if args.delay and index < len(rows):
            time.sleep(args.delay)

    states: dict[str, int] = {}
    for result in results:
        state = result["text_layer_observation_state"]
        states[state] = states.get(state, 0) + 1

    payload = {
        "schema": "LTMD_U2_TEXT_ACCESS_OBSERVATION_0.1_EXPERIMENTAL",
        "observed_at": args.observed_at,
        "total_source_objects": 39,
        "observed_objects": len(results),
        "failed_objects": len(failures),
        "states": states,
        "packages": {
            "pypdf": package_version("pypdf"),
            "PyMuPDF": package_version("PyMuPDF"),
            "pikepdf": package_version("pikepdf"),
            "cryptography": package_version("cryptography"),
        },
        "source_pdf_bytes_persisted": False,
        "extracted_text_persisted": False,
        "ocr_available_state": "not_assessed",
        "text_verified_state": "not_assessed",
        "epistemic_guards": [
            "source_admitted != embedded_text_observed",
            "embedded_text_observed != ocr_available",
            "ocr_available != text_verified",
            "text_verified != semantic_ready",
            "publicly_accessible != openly_licensed",
        ],
        "objects": results,
        "failures": failures,
    }
    Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with Path(args.output_csv).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow(flatten(result))
        for failure in failures:
            row = {field: "" for field in CSV_FIELDS}
            row.update(failure)
            writer.writerow(row)

    print(json.dumps({"observed": len(results), "failed": len(failures), "states": states}, sort_keys=True))
    return 0 if len(results) == 39 and not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
