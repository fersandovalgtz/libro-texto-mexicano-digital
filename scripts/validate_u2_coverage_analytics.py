#!/usr/bin/env python3
"""Validate LTMD-U2 coverage/Analytics 0.1 without accessing source books."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

SOURCE = Path("data/analytics/ltmd_u2_source_coverage_0_1.csv")
ENTRY = Path("data/analytics/ltmd_u2_catalog_entry_coverage_0_1.csv")
MANIFEST = Path("data/analytics/ltmd_u2_coverage_analytics_manifest_0_1.json")
SOURCE_OBJECTS = Path("data/catalog/ltmd_u2_source_objects_2026_2027.csv")
INVENTORY = Path("data/catalog/conaliteg_primaria_2026_2027_inventory.csv")
PAGE_COUNT = Path("data/catalog/ltmd_u2_page_count_resolution_2026_09_02.csv")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    source = read_csv(SOURCE)
    entry = read_csv(ENTRY)
    source_objects = read_csv(SOURCE_OBJECTS)
    inventory = read_csv(INVENTORY)
    pages = {r["source_object_id"]: int(r["page_count"]) for r in read_csv(PAGE_COUNT)}
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if len(source) != 39:
        errors.append(f"source coverage denominator must be 39, got {len(source)}")
    if len(entry) != 42:
        errors.append(f"catalog-entry coverage denominator must be 42, got {len(entry)}")

    source_ids = {r["source_object_id"] for r in source}
    canonical_source_ids = {r["source_object_id"] for r in source_objects}
    if source_ids != canonical_source_ids:
        errors.append("source coverage IDs differ from canonical U2 source-object universe")
    entry_ids = {r["catalog_entry_id"] for r in entry}
    if entry_ids != {r["catalog_entry_id"] for r in inventory}:
        errors.append("entry coverage IDs differ from canonical U2 catalog-entry universe")

    source_by_viewer = {r["viewer_key"]: r for r in source}
    for row in source:
        sid = row["source_object_id"]
        expected = {
            "cataloged_state": "cataloged",
            "reader_shell_state": "resolved",
            "asset_resolution_state": "resolved_pdf",
            "page_count_state": "observed",
            "source_admission_state": "admitted_full_body_verified",
            "text_access_observation_state": "blocked_by_password_required_encryption",
            "embedded_text_sample_state": "not_assessed_due_to_access_block",
            "ocr_available_state": "not_assessed",
            "text_verified_state": "not_assessed",
            "semantic_ready_state": "not_assessed",
        }
        for field, value in expected.items():
            if row[field] != value:
                errors.append(f"{sid}: {field}={row[field]!r}, expected {value!r}")
        if int(row["page_count"]) != pages.get(sid):
            errors.append(f"{sid}: page_count does not match canonical page-count layer")

    for row in entry:
        viewer = row["viewer_key"]
        state = source_by_viewer.get(viewer)
        if state is None:
            errors.append(f"{row['catalog_entry_id']}: viewer_key missing from source coverage")
            continue
        expected_sid = f"CONALITEG:2026:primaria:{viewer}"
        if row["source_object_id"] != expected_sid:
            errors.append(f"{row['catalog_entry_id']}: source_object_id mismatch")
        for field in (
            "cataloged_state", "reader_shell_state", "asset_resolution_state",
            "page_count_state", "page_count", "source_admission_state",
            "text_access_observation_state", "embedded_text_sample_state",
            "ocr_available_state", "text_verified_state", "semantic_ready_state",
        ):
            if row[field] != state[field]:
                errors.append(f"{row['catalog_entry_id']}: propagated {field} mismatch")

    denominators = manifest.get("denominators", {})
    if denominators != {"catalog_entries": 42, "source_objects": 39}:
        errors.append(f"manifest denominators invalid: {denominators}")
    total_pages = sum(pages.values())
    if manifest.get("source_object_metrics", {}).get("total_observed_pages") != total_pages:
        errors.append("manifest total_observed_pages differs from canonical page-count layer")

    guards = manifest.get("separation_guards", {})
    for guard in (
        "catalog_entry_is_not_source_object",
        "u2_denominators_are_separate_from_u1",
        "content_access_blocked_does_not_imply_no_embedded_text",
        "content_access_blocked_does_not_imply_ocr_needed",
        "ocr_available_does_not_imply_text_verified",
    ):
        if guards.get(guard) is not True:
            errors.append(f"manifest guard {guard} must be true")
    for guard in ("source_pdf_bytes_persisted", "extracted_text_persisted"):
        if guards.get(guard) is not False:
            errors.append(f"manifest guard {guard} must be false")

    materialization = manifest.get("materialization", {})
    if materialization.get("source_csv_sha256") != sha256(SOURCE):
        errors.append("source coverage CSV SHA-256 mismatch")
    if materialization.get("entry_csv_sha256") != sha256(ENTRY):
        errors.append("entry coverage CSV SHA-256 mismatch")

    print(
        f"catalog_entries={len(entry)} source_objects={len(source)} "
        f"pages={total_pages} errors={len(errors)}"
    )
    return errors


def main() -> int:
    errors = validate()
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
