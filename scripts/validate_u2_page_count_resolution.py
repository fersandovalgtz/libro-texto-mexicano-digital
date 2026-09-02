#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

EXPECTED_OBJECTS = 39
EXPECTED_TOTAL_PAGES = 10392
EXPECTED_METHOD = "targeted_tail_startxref_classic_xref_catalog_pages_count"
EXPECTED_EVIDENCE_SCOPE = (
    "structural trailer/xref/catalog/root-/Pages-/Count only; "
    "no page enumeration, text extraction, OCR, or semantic validation"
)
REQUIRED_FIELDS = {
    "source_object_id",
    "viewer_key",
    "asset_url",
    "observed_at",
    "page_count_state",
    "page_count",
    "remote_total_bytes",
    "network_bytes_fetched",
    "range_requests",
    "max_network_bytes",
    "startxref_offset",
    "xref_kind",
    "xref_sections_traversed",
    "root_ref",
    "pages_ref",
    "method",
    "source_admission_state",
    "text_verification_state",
    "evidence_scope",
    "error",
}


def read_csv(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = set(reader.fieldnames or [])
    if not rows:
        raise RuntimeError(f"{path}: no rows")
    return rows, fields


def positive_int(value: str, *, field: str, source_id: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]*", value):
        raise RuntimeError(f"{source_id}: {field} must be a positive integer")
    return int(value)


def validate_resolution(
    source_objects_path: Path,
    asset_resolution_path: Path,
    page_count_path: Path,
    *,
    expected_objects: int = EXPECTED_OBJECTS,
    expected_total_pages: int = EXPECTED_TOTAL_PAGES,
) -> list[dict[str, str]]:
    source_rows, _ = read_csv(source_objects_path)
    asset_rows, _ = read_csv(asset_resolution_path)
    page_rows, page_fields = read_csv(page_count_path)

    if len(source_rows) != expected_objects:
        raise RuntimeError(f"source-object cardinality mismatch: expected {expected_objects}, got {len(source_rows)}")
    if len(asset_rows) != expected_objects:
        raise RuntimeError(f"asset-resolution cardinality mismatch: expected {expected_objects}, got {len(asset_rows)}")
    if len(page_rows) != expected_objects:
        raise RuntimeError(f"page-count cardinality mismatch: expected {expected_objects}, got {len(page_rows)}")

    missing_fields = REQUIRED_FIELDS - page_fields
    if missing_fields:
        raise RuntimeError(f"page-count observations missing required columns: {sorted(missing_fields)}")

    source_by_id = {row["source_object_id"]: row for row in source_rows}
    asset_by_id = {row["source_object_id"]: row for row in asset_rows}
    page_by_id = {row["source_object_id"]: row for row in page_rows}
    if len(source_by_id) != len(source_rows):
        raise RuntimeError("source_object_id values must be unique in source-object registry")
    if len(asset_by_id) != len(asset_rows):
        raise RuntimeError("source_object_id values must be unique in asset-resolution registry")
    if len(page_by_id) != len(page_rows):
        raise RuntimeError("source_object_id values must be unique in page-count resolution")

    canonical_ids = set(source_by_id)
    if set(asset_by_id) != canonical_ids:
        raise RuntimeError("asset-resolution identities do not match canonical source objects")
    if set(page_by_id) != canonical_ids:
        missing = sorted(canonical_ids - set(page_by_id))
        extra = sorted(set(page_by_id) - canonical_ids)
        raise RuntimeError(f"page-count identity mismatch: missing={missing}, extra={extra}")

    total_pages = 0
    for row in page_rows:
        source_id = row["source_object_id"]
        source = source_by_id[source_id]
        asset = asset_by_id[source_id]

        if row["viewer_key"] != source["viewer_key"] or row["viewer_key"] != asset["viewer_key"]:
            raise RuntimeError(f"{source_id}: viewer_key mismatch")
        if row["asset_url"] != asset["asset_url"]:
            raise RuntimeError(f"{source_id}: asset_url mismatch")
        if asset["asset_resolution_state"] != "resolved_pdf":
            raise RuntimeError(f"{source_id}: page-count evidence requires resolved_pdf asset")
        if row["remote_total_bytes"] != asset["total_bytes"]:
            raise RuntimeError(f"{source_id}: remote_total_bytes changed from asset-resolution observation")

        if row["observed_at"] != "2026-09-02":
            raise RuntimeError(f"{source_id}: unexpected observed_at")
        if row["page_count_state"] != "observed":
            raise RuntimeError(f"{source_id}: page_count_state must be observed")
        page_count = positive_int(row["page_count"], field="page_count", source_id=source_id)
        total_pages += page_count

        network_bytes = positive_int(row["network_bytes_fetched"], field="network_bytes_fetched", source_id=source_id)
        max_network = positive_int(row["max_network_bytes"], field="max_network_bytes", source_id=source_id)
        positive_int(row["range_requests"], field="range_requests", source_id=source_id)
        positive_int(row["startxref_offset"], field="startxref_offset", source_id=source_id)
        positive_int(row["xref_sections_traversed"], field="xref_sections_traversed", source_id=source_id)
        if network_bytes > max_network:
            raise RuntimeError(f"{source_id}: network budget exceeded in versioned observation")

        if row["xref_kind"] != "classic":
            raise RuntimeError(f"{source_id}: expected classic xref evidence")
        if not re.fullmatch(r"[1-9][0-9]* [0-9]+ R", row["root_ref"]):
            raise RuntimeError(f"{source_id}: invalid root_ref")
        if not re.fullmatch(r"[1-9][0-9]* [0-9]+ R", row["pages_ref"]):
            raise RuntimeError(f"{source_id}: invalid pages_ref")
        if row["method"] != EXPECTED_METHOD:
            raise RuntimeError(f"{source_id}: unexpected method")
        if row["evidence_scope"] != EXPECTED_EVIDENCE_SCOPE:
            raise RuntimeError(f"{source_id}: unexpected evidence_scope")
        if row["error"] != "none":
            raise RuntimeError(f"{source_id}: successful resolution cannot contain an error")

        if row["source_admission_state"] != "not_assessed":
            raise RuntimeError(f"{source_id}: page-count evidence cannot promote source admission")
        if row["text_verification_state"] != "not_assessed":
            raise RuntimeError(f"{source_id}: page-count evidence cannot promote text verification")

    if total_pages != expected_total_pages:
        raise RuntimeError(f"structural page total mismatch: expected {expected_total_pages}, got {total_pages}")

    return page_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate LTMD-U2 structural page-count resolution against canonical U2 identities and resolved PDF assets.")
    parser.add_argument("--source-objects", type=Path, default=Path("data/catalog/ltmd_u2_source_objects_2026_2027.csv"))
    parser.add_argument("--asset-resolution", type=Path, default=Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv"))
    parser.add_argument("--page-counts", type=Path, default=Path("data/catalog/ltmd_u2_page_count_resolution_2026_09_02.csv"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate_resolution(args.source_objects, args.asset_resolution, args.page_counts)
    counts = [int(row["page_count"]) for row in rows]
    total_network = sum(int(row["network_bytes_fetched"]) for row in rows)
    print(
        "LTMD-U2 page-count resolution valid: "
        f"objects={len(rows)} pages={sum(counts)} min={min(counts)} max={max(counts)} "
        f"network_bytes={total_network}; source_admission_state and text_verification_state remain not_assessed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
