#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

EXPECTED_SOURCE_OBJECTS = 39
REQUIRED_FIELDS = {
    "source_object_id",
    "viewer_key",
    "asset_url",
    "observed_at",
    "http_status",
    "asset_resolution_state",
    "content_type",
    "accept_ranges",
    "total_bytes",
    "pdf_signature",
    "source_admission_state",
    "page_count_observation",
}


def read_csv(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = set(reader.fieldnames or [])
    if not rows:
        raise RuntimeError(f"{path}: no rows")
    return rows, fields


def canonical_asset_url(source: dict[str, str]) -> str:
    return (
        "https://libros.conaliteg.gob.mx/pdf-reader/assets/"
        f"{source['level']}/{source['source_cycle']}/{source['viewer_key']}.pdf"
    )


def validate_asset_resolution(
    source_objects_path: Path,
    observations_path: Path,
    *,
    expected_source_objects: int = EXPECTED_SOURCE_OBJECTS,
) -> list[dict[str, str]]:
    source_rows, _ = read_csv(source_objects_path)
    observation_rows, observation_fields = read_csv(observations_path)

    if len(source_rows) != expected_source_objects:
        raise RuntimeError(
            f"source-object cardinality mismatch: expected {expected_source_objects}, got {len(source_rows)}"
        )
    if len(observation_rows) != expected_source_objects:
        raise RuntimeError(
            f"asset-resolution cardinality mismatch: expected {expected_source_objects}, got {len(observation_rows)}"
        )

    missing_fields = REQUIRED_FIELDS - observation_fields
    extra_fields = observation_fields - REQUIRED_FIELDS
    if missing_fields:
        raise RuntimeError(f"asset resolution missing required columns: {sorted(missing_fields)}")
    if extra_fields:
        raise RuntimeError(f"asset resolution has unexpected columns: {sorted(extra_fields)}")

    source_by_id = {row["source_object_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise RuntimeError("source_object_id values must be unique in source-object registry")

    observed_ids = [row["source_object_id"] for row in observation_rows]
    if len(observed_ids) != len(set(observed_ids)):
        raise RuntimeError("source_object_id values must be unique in asset-resolution evidence")
    if set(observed_ids) != set(source_by_id):
        missing = sorted(set(source_by_id) - set(observed_ids))
        extra = sorted(set(observed_ids) - set(source_by_id))
        raise RuntimeError(f"asset-resolution identity mismatch: missing={missing}, extra={extra}")

    for row in observation_rows:
        source_id = row["source_object_id"]
        source = source_by_id[source_id]

        if row["viewer_key"] != source["viewer_key"]:
            raise RuntimeError(f"{source_id}: viewer_key does not match canonical source object")
        if row["asset_url"] != canonical_asset_url(source):
            raise RuntimeError(f"{source_id}: asset_url does not match current-reader route")

        if row["asset_resolution_state"] != "resolved_pdf":
            raise RuntimeError(f"{source_id}: stable evidence requires asset_resolution_state=resolved_pdf")
        if row["http_status"] != "206":
            raise RuntimeError(f"{source_id}: resolved PDF evidence requires HTTP 206")
        if row["content_type"] != "application/pdf":
            raise RuntimeError(f"{source_id}: resolved PDF evidence requires application/pdf")
        if row["accept_ranges"] != "bytes":
            raise RuntimeError(f"{source_id}: resolved PDF evidence requires byte ranges")
        if row["pdf_signature"] != "true":
            raise RuntimeError(f"{source_id}: resolved PDF evidence requires a %PDF- signature")

        try:
            total_bytes = int(row["total_bytes"])
        except ValueError as exc:
            raise RuntimeError(f"{source_id}: total_bytes must be an integer") from exc
        if total_bytes <= 32:
            raise RuntimeError(f"{source_id}: total_bytes is inconsistent with the bounded range probe")

        if row["source_admission_state"] != "not_assessed":
            raise RuntimeError(f"{source_id}: asset evidence cannot promote source_admission_state")
        if row["page_count_observation"] != "not_observed":
            raise RuntimeError(f"{source_id}: asset evidence cannot assert page_count_observation")

    return observation_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate LTMD-U2 transport-level PDF asset resolution against canonical source objects."
    )
    parser.add_argument(
        "--source-objects",
        type=Path,
        default=Path("data/catalog/ltmd_u2_source_objects_2026_2027.csv"),
    )
    parser.add_argument(
        "--observations",
        type=Path,
        default=Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate_asset_resolution(args.source_objects, args.observations)
    print(
        "LTMD-U2 asset resolution valid: "
        f"total={len(rows)} resolved_pdf={len(rows)}; "
        "source_admission_state=not_assessed; page_count_observation=not_observed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
