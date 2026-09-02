#!/usr/bin/env python3
"""Validate the materialized LTMD-U2 source-admission evidence layer."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

DEFAULT_SOURCE = Path("data/catalog/ltmd_u2_source_admission_2026_09_02.csv")
ASSET_REGISTRY = Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv")
PAGE_REGISTRY = Path("data/catalog/ltmd_u2_page_count_resolution_2026_09_02.csv")
MANIFEST = Path("data/catalog/ltmd_u2_source_admission_0_1.manifest.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def is_true(value: str) -> bool:
    return value.strip().lower() == "true"


def is_false(value: str) -> bool:
    return value.strip().lower() == "false"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(source: Path) -> list[str]:
    errors: list[str] = []
    rows = read_csv(source)
    assets = {r["source_object_id"]: r for r in read_csv(ASSET_REGISTRY)}
    pages = {r["source_object_id"]: r for r in read_csv(PAGE_REGISTRY)}

    if len(rows) != 39:
        errors.append(f"source-admission cardinality must be 39, got {len(rows)}")
    ids = [r["source_object_id"] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("source_object_id values must be unique")
    if set(ids) != set(assets):
        errors.append("source-admission IDs do not exactly match asset registry")
    if set(ids) != set(pages):
        errors.append("source-admission IDs do not exactly match page-count registry")

    for row in rows:
        sid = row["source_object_id"]
        asset = assets.get(sid)
        page = pages.get(sid)
        if not asset or not page:
            continue
        prefix = f"{sid}: "
        if row["viewer_key"] != asset["viewer_key"]:
            errors.append(prefix + "viewer_key mismatch")
        if row["asset_url"] != asset["asset_url"]:
            errors.append(prefix + "asset_url mismatch")
        if row["expected_bytes"] != asset["total_bytes"]:
            errors.append(prefix + "expected_bytes differs from asset registry")
        if row["bytes_received"] != row["expected_bytes"]:
            errors.append(prefix + "bytes_received does not equal expected_bytes")
        if not is_true(row["size_matches"]):
            errors.append(prefix + "size_matches must be true")
        if row["http_status"] != "200":
            errors.append(prefix + "http_status must be 200")
        if row["content_type"] != "application/pdf":
            errors.append(prefix + "content_type must be application/pdf")
        if not SHA256_RE.fullmatch(row["sha256"]):
            errors.append(prefix + "sha256 must be 64 lowercase hex characters")
        for marker in ("pdf_signature", "eof_marker", "startxref_in_tail"):
            if not is_true(row[marker]):
                errors.append(prefix + f"{marker} must be true")
        if row["source_admission_state"] != "admitted_full_body_verified":
            errors.append(prefix + "source_admission_state is not admitted_full_body_verified")
        if row["page_count"] != page["page_count"]:
            errors.append(prefix + "page_count differs from canonical page-count registry")
        if not is_false(row["source_pdf_persisted"]):
            errors.append(prefix + "source_pdf_persisted must be false")
        if row["ocr_available_state"] != "not_assessed":
            errors.append(prefix + "ocr_available_state must remain not_assessed")
        if row["text_verified_state"] != "not_assessed":
            errors.append(prefix + "text_verified_state must remain not_assessed")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("total_source_objects") != 39:
        errors.append("manifest total_source_objects must be 39")
    if manifest.get("admitted_source_objects") != 39:
        errors.append("manifest admitted_source_objects must be 39")
    if manifest.get("source_pdf_bytes_persisted") is not False:
        errors.append("manifest source_pdf_bytes_persisted must be false")
    if manifest.get("ocr_available_state") != "not_assessed":
        errors.append("manifest OCR state must remain not_assessed")
    if manifest.get("text_verified_state") != "not_assessed":
        errors.append("manifest text state must remain not_assessed")
    expected_hash = manifest.get("materialization", {}).get("canonical_csv_sha256")
    actual_hash = file_sha256(source)
    if expected_hash != actual_hash:
        errors.append(
            f"canonical CSV SHA-256 mismatch: manifest={expected_hash} actual={actual_hash}"
        )

    unique_hashes = len({r["sha256"] for r in rows})
    print(
        f"objects={len(rows)} unique_sha256={unique_hashes} "
        f"csv_sha256={actual_hash} errors={len(errors)}"
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    errors = validate(args.source)
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
