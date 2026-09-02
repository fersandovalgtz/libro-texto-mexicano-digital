#!/usr/bin/env python3
"""Observe LTMD-U2 full-body source admission for the canonical 39 objects.

The institutional PDF response is streamed once per object. Bytes are hashed and
immediately discarded; no source PDF or extracted text is written to disk.
Only non-substitutive technical evidence is materialized as CSV/JSON.

This layer does NOT assess OCR availability, text verification, licensing, or
semantic readiness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

UA = "LTMD-U2-source-admission-batch/0.1 (+research; non-redistributive)"
ASSET_REGISTRY = Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv")
PAGE_REGISTRY = Path("data/catalog/ltmd_u2_page_count_resolution_2026_09_02.csv")

FIELDS = [
    "source_object_id", "viewer_key", "asset_url", "observed_at",
    "expected_bytes", "content_length_header", "bytes_received", "size_matches",
    "http_status", "content_type", "etag", "last_modified", "sha256",
    "pdf_signature", "eof_marker", "startxref_in_tail", "source_admission_state",
    "page_count_state", "page_count", "source_pdf_persisted",
    "ocr_available_state", "text_verified_state", "rights_state",
    "evidence_scope", "error",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def stream_and_hash(url: str, timeout: int) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/pdf"})
    sha = hashlib.sha256()
    first = bytearray()
    tail = bytearray()
    received = 0
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status = getattr(response, "status", None)
        content_type = response.headers.get_content_type()
        content_length = response.headers.get("Content-Length")
        etag = response.headers.get("ETag")
        last_modified = response.headers.get("Last-Modified")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            sha.update(chunk)
            received += len(chunk)
            if len(first) < 16:
                first.extend(chunk[: 16 - len(first)])
            tail.extend(chunk)
            if len(tail) > 65536:
                del tail[:-65536]
    return {
        "http_status": status,
        "content_type": content_type,
        "content_length_header": int(content_length) if content_length and content_length.isdigit() else None,
        "etag": etag,
        "last_modified": last_modified,
        "bytes_received": received,
        "sha256": sha.hexdigest(),
        "pdf_signature": bytes(first).startswith(b"%PDF-"),
        "eof_marker": b"%%EOF" in tail,
        "startxref_in_tail": bool(re.search(rb"startxref\s+\d+\s+%%EOF", bytes(tail), flags=re.S)),
    }


def observe(row: dict[str, str], page: dict[str, str], observed_at: str, timeout: int) -> dict:
    expected = int(row["total_bytes"])
    out = {
        "source_object_id": row["source_object_id"],
        "viewer_key": row["viewer_key"],
        "asset_url": row["asset_url"],
        "observed_at": observed_at,
        "expected_bytes": expected,
        "page_count_state": page.get("page_count_state", "not_observed"),
        "page_count": int(page["page_count"]) if page.get("page_count") else None,
        "source_pdf_persisted": False,
        "ocr_available_state": "not_assessed",
        "text_verified_state": "not_assessed",
        "rights_state": "third_party_source_not_redistributable_by_default",
        "evidence_scope": (
            "full-body streaming SHA-256 + HTTP/content-type + exact byte count + PDF/startxref/EOF markers; "
            "no source persistence, OCR assessment, text verification, licensing inference, or semantic validation"
        ),
        "error": "none",
    }
    try:
        obs = stream_and_hash(row["asset_url"], timeout)
        out.update(obs)
        out["size_matches"] = obs["bytes_received"] == expected
        ok = all([
            obs["http_status"] == 200,
            obs["content_type"] == "application/pdf",
            out["size_matches"],
            obs["pdf_signature"],
            obs["eof_marker"],
            obs["startxref_in_tail"],
            bool(obs["sha256"]),
        ])
        out["source_admission_state"] = "admitted_full_body_verified" if ok else "not_admitted"
    except Exception as exc:
        out["source_admission_state"] = "probe_error"
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--observed-at", default="2026-09-02")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--delay", type=float, default=0.25)
    ap.add_argument("--output-csv", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    assets = read_csv(ASSET_REGISTRY)
    pages = {r["source_object_id"]: r for r in read_csv(PAGE_REGISTRY)}
    if len(assets) != 39 or len(pages) != 39:
        raise SystemExit(f"canonical input cardinality mismatch: assets={len(assets)} pages={len(pages)}")
    if {r["source_object_id"] for r in assets} != set(pages):
        raise SystemExit("asset/page-count source_object_id sets differ")

    results = []
    for i, row in enumerate(assets, 1):
        result = observe(row, pages[row["source_object_id"]], args.observed_at, args.timeout)
        results.append(result)
        print(
            f"[{i:02d}/39] {row['viewer_key']} state={result['source_admission_state']} "
            f"bytes={result.get('bytes_received')} sha256={result.get('sha256')}"
        )
        if i < len(assets) and args.delay:
            time.sleep(args.delay)

    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output_csv).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({k: r.get(k) for k in FIELDS} for r in results)

    states = Counter(r["source_admission_state"] for r in results)
    total_bytes = sum(int(r.get("bytes_received") or 0) for r in results)
    summary = {
        "schema": "LTMD_U2_SOURCE_ADMISSION_BATCH_0.1",
        "observed_at": args.observed_at,
        "total_objects": len(results),
        "states": dict(states),
        "admitted_sources": states.get("admitted_full_body_verified", 0),
        "total_source_bytes_streamed": total_bytes,
        "source_pdf_bytes_persisted": False,
        "extracted_text_persisted": False,
        "ocr_available_state": "not_assessed",
        "text_verified_state": "not_assessed",
        "rights_state": "third_party_source_not_redistributable_by_default",
        "method": "full_body_streaming_sha256_transport_size_pdf_markers",
        "input_asset_registry": str(ASSET_REGISTRY),
        "input_page_registry": str(PAGE_REGISTRY),
        "results": results,
    }
    Path(args.output_json).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["total_objects", "states", "total_source_bytes_streamed", "method"]}))
    return 0 if states == {"admitted_full_body_verified": 39} else 1


if __name__ == "__main__":
    raise SystemExit(main())
