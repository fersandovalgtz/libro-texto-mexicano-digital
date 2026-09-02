#!/usr/bin/env python3
"""Re-observe the LTMD-U2 source-admission layer.

This command streams each canonical CONALITEG PDF exactly once, computes a
SHA-256 while discarding source bytes, and writes only non-substitutive technical
evidence. It intentionally does not persist PDFs or extracted text and does not
assess OCR, text verification, licensing, or semantic readiness.

Network access is required. This observer is not executed by normal CI; CI only
validates already materialized evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import time
import urllib.request
from pathlib import Path

ASSET_REGISTRY = Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv")
PAGE_REGISTRY = Path("data/catalog/ltmd_u2_page_count_resolution_2026_09_02.csv")
USER_AGENT = "LTMD-U2-source-admission-observer/0.1 (+research; non-redistributive)"

OUTPUT_FIELDS = [
    "source_object_id",
    "viewer_key",
    "asset_url",
    "observed_at",
    "expected_bytes",
    "bytes_received",
    "size_matches",
    "http_status",
    "content_type",
    "sha256",
    "pdf_signature",
    "eof_marker",
    "startxref_in_tail",
    "source_admission_state",
    "page_count",
    "source_pdf_persisted",
    "ocr_available_state",
    "text_verified_state",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def inspect_stream(response) -> dict[str, object]:
    """Hash an HTTP PDF response without retaining the body."""
    digest = hashlib.sha256()
    first = bytearray()
    tail = bytearray()
    received = 0
    while True:
        chunk = response.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        received += len(chunk)
        if len(first) < 16:
            first.extend(chunk[: 16 - len(first)])
        tail.extend(chunk)
        if len(tail) > 65536:
            del tail[:-65536]

    content_length = response.headers.get("Content-Length")
    return {
        "http_status": getattr(response, "status", None),
        "content_type": response.headers.get_content_type(),
        "content_length_header": int(content_length)
        if content_length and content_length.isdigit()
        else None,
        "bytes_received": received,
        "sha256": digest.hexdigest(),
        "pdf_signature": bytes(first).startswith(b"%PDF-"),
        "eof_marker": b"%%EOF" in tail,
        "startxref_in_tail": bool(
            re.search(rb"startxref\s+\d+\s+%%EOF", bytes(tail), flags=re.S)
        ),
    }


def observe_url(url: str, timeout: int) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return inspect_stream(response)


def materialize(observed_at: str, timeout: int, delay: float) -> list[dict[str, object]]:
    assets = _read_csv(ASSET_REGISTRY)
    pages = {row["source_object_id"]: row for row in _read_csv(PAGE_REGISTRY)}
    asset_ids = {row["source_object_id"] for row in assets}
    if len(assets) != 39 or len(pages) != 39 or asset_ids != set(pages):
        raise RuntimeError(
            f"canonical U2 input mismatch: assets={len(assets)} pages={len(pages)}"
        )

    output: list[dict[str, object]] = []
    for index, asset in enumerate(assets, start=1):
        expected_bytes = int(asset["total_bytes"])
        observation = observe_url(asset["asset_url"], timeout)
        size_matches = observation["bytes_received"] == expected_bytes
        admission_ok = all(
            [
                observation["http_status"] == 200,
                observation["content_type"] == "application/pdf",
                size_matches,
                observation["pdf_signature"],
                observation["eof_marker"],
                observation["startxref_in_tail"],
                bool(observation["sha256"]),
            ]
        )
        row = {
            "source_object_id": asset["source_object_id"],
            "viewer_key": asset["viewer_key"],
            "asset_url": asset["asset_url"],
            "observed_at": observed_at,
            "expected_bytes": expected_bytes,
            "bytes_received": observation["bytes_received"],
            "size_matches": size_matches,
            "http_status": observation["http_status"],
            "content_type": observation["content_type"],
            "sha256": observation["sha256"],
            "pdf_signature": observation["pdf_signature"],
            "eof_marker": observation["eof_marker"],
            "startxref_in_tail": observation["startxref_in_tail"],
            "source_admission_state": "admitted_full_body_verified"
            if admission_ok
            else "not_admitted",
            "page_count": int(pages[asset["source_object_id"]]["page_count"]),
            "source_pdf_persisted": False,
            "ocr_available_state": "not_assessed",
            "text_verified_state": "not_assessed",
        }
        output.append(row)
        print(
            f"[{index:02d}/39] {asset['viewer_key']} "
            f"state={row['source_admission_state']} bytes={row['bytes_received']} "
            f"sha256={row['sha256']}"
        )
        if delay and index < len(assets):
            time.sleep(delay)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--delay", type=float, default=0.25)
    parser.add_argument(
        "--output",
        default="data/catalog/ltmd_u2_source_admission_observed.csv",
    )
    args = parser.parse_args()

    rows = materialize(args.observed_at, args.timeout, args.delay)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    admitted = sum(row["source_admission_state"] == "admitted_full_body_verified" for row in rows)
    print(f"admitted={admitted}/{len(rows)}; source_pdf_bytes_persisted=0")
    return 0 if admitted == len(rows) == 39 else 1


if __name__ == "__main__":
    raise SystemExit(main())
