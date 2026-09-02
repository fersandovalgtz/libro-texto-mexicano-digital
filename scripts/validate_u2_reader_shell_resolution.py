#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

EXPECTED_SOURCE_OBJECTS = 39
REQUIRED_OBSERVATION_FIELDS = {
    "source_object_id",
    "viewer_key",
    "viewer_url",
    "observed_at",
    "probe_method",
    "transport_observation",
    "content_type_observation",
    "http_status_observation",
    "observed_title",
    "reader_shell_state",
    "asset_resolution_state",
    "page_count_observation",
    "source_admission_state",
    "observation_note",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = set(reader.fieldnames or [])
    if not rows:
        raise RuntimeError(f"{path}: no rows")
    return rows


def validate_resolution(
    source_objects_path: Path,
    observations_path: Path,
    *,
    expected_source_objects: int = EXPECTED_SOURCE_OBJECTS,
) -> list[dict[str, str]]:
    source_rows = read_csv(source_objects_path)
    observation_rows = read_csv(observations_path)

    if len(source_rows) != expected_source_objects:
        raise RuntimeError(
            f"source-object cardinality mismatch: expected {expected_source_objects}, got {len(source_rows)}"
        )
    if len(observation_rows) != expected_source_objects:
        raise RuntimeError(
            f"observation cardinality mismatch: expected {expected_source_objects}, got {len(observation_rows)}"
        )

    missing_fields = REQUIRED_OBSERVATION_FIELDS - set(observation_rows[0])
    if missing_fields:
        raise RuntimeError(f"observations missing required columns: {sorted(missing_fields)}")

    source_by_id = {row["source_object_id"]: row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise RuntimeError("source_object_id values must be unique in source-object registry")

    observed_ids = [row["source_object_id"] for row in observation_rows]
    if len(observed_ids) != len(set(observed_ids)):
        raise RuntimeError("source_object_id values must be unique in reader-shell observations")

    if set(observed_ids) != set(source_by_id):
        missing = sorted(set(source_by_id) - set(observed_ids))
        extra = sorted(set(observed_ids) - set(source_by_id))
        raise RuntimeError(f"reader-shell identity mismatch: missing={missing}, extra={extra}")

    for row in observation_rows:
        source = source_by_id[row["source_object_id"]]
        source_id = row["source_object_id"]

        if row["viewer_key"] != source["viewer_key"]:
            raise RuntimeError(f"{source_id}: viewer_key does not match canonical source object")
        if row["viewer_url"] != source["viewer_url"]:
            raise RuntimeError(f"{source_id}: viewer_url does not match canonical source object")

        if row["reader_shell_state"] not in {"resolved", "unresolved", "ambiguous"}:
            raise RuntimeError(f"{source_id}: invalid reader_shell_state")
        if row["transport_observation"] not in {"fetch_succeeded", "fetch_failed", "ambiguous"}:
            raise RuntimeError(f"{source_id}: invalid transport_observation")
        if row["asset_resolution_state"] not in {
            "not_observed",
            "resolved",
            "unresolved",
            "ambiguous",
        }:
            raise RuntimeError(f"{source_id}: invalid asset_resolution_state")

        if row["reader_shell_state"] == "resolved" and row["transport_observation"] != "fetch_succeeded":
            raise RuntimeError(f"{source_id}: resolved reader shell requires fetch_succeeded")

        if row["asset_resolution_state"] == "not_observed" and row["page_count_observation"] != "not_observed":
            raise RuntimeError(
                f"{source_id}: page count cannot be asserted while asset_resolution_state=not_observed"
            )

        if row["source_admission_state"] != "not_assessed":
            raise RuntimeError(
                f"{source_id}: reader-shell evidence cannot promote source_admission_state"
            )

    return observation_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate LTMD-U2 reader-shell observations against canonical source-object identities."
    )
    parser.add_argument(
        "--source-objects",
        type=Path,
        default=Path("data/catalog/ltmd_u2_source_objects_2026_2027.csv"),
    )
    parser.add_argument(
        "--observations",
        type=Path,
        default=Path("data/catalog/ltmd_u2_reader_shell_resolution_2026_09_02.csv"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = validate_resolution(args.source_objects, args.observations)
    resolved = sum(row["reader_shell_state"] == "resolved" for row in rows)
    unresolved = sum(row["reader_shell_state"] == "unresolved" for row in rows)
    ambiguous = sum(row["reader_shell_state"] == "ambiguous" for row in rows)
    print(
        "LTMD-U2 reader-shell resolution valid: "
        f"total={len(rows)} resolved={resolved} unresolved={unresolved} ambiguous={ambiguous}; "
        "source_admission_state remains not_assessed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
