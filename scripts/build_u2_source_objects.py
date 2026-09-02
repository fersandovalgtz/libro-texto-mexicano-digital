#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SOURCE = "CONALITEG"
EXPECTED_CATALOG_ENTRIES = 42
EXPECTED_SOURCE_OBJECTS = 39
EXPECTED_SHARED_KEYS = {"P1LPM": 2, "P3LPM": 2, "P5LPM": 2}

REQUIRED_COLUMNS = {
    "catalog_entry_id",
    "cycle",
    "level",
    "grade",
    "viewer_key",
    "title",
    "publisher",
    "viewer_url",
    "public_repo_status",
    "source_checked",
}

OUTPUT_FIELDS = [
    "source_object_id",
    "source",
    "source_cycle",
    "cycle_label",
    "level",
    "viewer_key",
    "title",
    "publisher",
    "viewer_url",
    "catalog_entry_count",
    "catalog_grades",
    "public_repo_status",
    "source_checked",
]


def _single_query_value(query: dict[str, list[str]], name: str, row_id: str) -> str:
    values = query.get(name, [])
    if len(values) != 1 or not values[0]:
        raise RuntimeError(f"{row_id}: viewer_url must contain exactly one non-empty {name}= value")
    return values[0]


def _source_identity(row: dict[str, str]) -> tuple[str, str, str]:
    row_id = row["catalog_entry_id"]
    parsed = urlparse(row["viewer_url"])
    if parsed.scheme != "https" or parsed.netloc != "libros.conaliteg.gob.mx":
        raise RuntimeError(f"{row_id}: viewer_url is not an institutional HTTPS CONALITEG URL")

    query = parse_qs(parsed.query, keep_blank_values=True)
    source_cycle = _single_query_value(query, "ciclo", row_id)
    level = _single_query_value(query, "nivel", row_id)
    viewer_key = _single_query_value(query, "clave", row_id)

    if level != row["level"]:
        raise RuntimeError(f"{row_id}: nivel mismatch between row and viewer_url")
    if viewer_key != row["viewer_key"]:
        raise RuntimeError(f"{row_id}: viewer_key mismatch between row and viewer_url")
    if not source_cycle.isdigit() or len(source_cycle) != 4:
        raise RuntimeError(f"{row_id}: ciclo must be a four-digit source cycle")

    return source_cycle, level, viewer_key


def read_inventory(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f"inventory missing required columns: {sorted(missing)}")
        rows = list(reader)

    entry_ids = [row["catalog_entry_id"] for row in rows]
    if len(entry_ids) != len(set(entry_ids)):
        raise RuntimeError("catalog_entry_id values must be unique")
    return rows


def _one(rows: list[dict[str, str]], field: str, source_object_id: str) -> str:
    values = {row[field] for row in rows}
    if len(values) != 1:
        raise RuntimeError(f"{source_object_id}: conflicting {field} values across catalog entries")
    return next(iter(values))


def build_source_objects(
    inventory_path: Path,
    *,
    expected_catalog_entries: int = EXPECTED_CATALOG_ENTRIES,
    expected_source_objects: int = EXPECTED_SOURCE_OBJECTS,
    enforce_current_shared_keys: bool = True,
) -> list[dict[str, object]]:
    rows = read_inventory(inventory_path)
    if len(rows) != expected_catalog_entries:
        raise RuntimeError(
            f"catalog entry cardinality mismatch: expected {expected_catalog_entries}, got {len(rows)}"
        )

    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        source_cycle, level, viewer_key = _source_identity(row)
        groups[(source_cycle, level, viewer_key)].append(row)

    objects: list[dict[str, object]] = []
    for (source_cycle, level, viewer_key), group in groups.items():
        source_object_id = f"{SOURCE}:{source_cycle}:{level}:{viewer_key}"
        grades = sorted({int(row["grade"]) for row in group})
        if any(grade < 1 or grade > 6 for grade in grades):
            raise RuntimeError(f"{source_object_id}: grade outside primary range 1..6")

        objects.append(
            {
                "source_object_id": source_object_id,
                "source": SOURCE,
                "source_cycle": source_cycle,
                "cycle_label": _one(group, "cycle", source_object_id),
                "level": level,
                "viewer_key": viewer_key,
                "title": _one(group, "title", source_object_id),
                "publisher": _one(group, "publisher", source_object_id),
                "viewer_url": _one(group, "viewer_url", source_object_id),
                "catalog_entry_count": len(group),
                "catalog_grades": "|".join(str(grade) for grade in grades),
                "public_repo_status": _one(group, "public_repo_status", source_object_id),
                "source_checked": _one(group, "source_checked", source_object_id),
            }
        )

    objects.sort(key=lambda row: str(row["source_object_id"]))

    if len(objects) != expected_source_objects:
        raise RuntimeError(
            f"source object cardinality mismatch: expected {expected_source_objects}, got {len(objects)}"
        )

    if enforce_current_shared_keys:
        shared = {
            str(row["viewer_key"]): int(row["catalog_entry_count"])
            for row in objects
            if int(row["catalog_entry_count"]) > 1
        }
        if shared != EXPECTED_SHARED_KEYS:
            raise RuntimeError(
                f"shared-viewer invariant mismatch: expected {EXPECTED_SHARED_KEYS}, got {shared}"
            )

    return objects


def write_source_objects(rows: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def materialize(
    inventory_path: Path,
    output_path: Path,
    *,
    expected_catalog_entries: int = EXPECTED_CATALOG_ENTRIES,
    expected_source_objects: int = EXPECTED_SOURCE_OBJECTS,
    enforce_current_shared_keys: bool = True,
) -> list[dict[str, object]]:
    rows = build_source_objects(
        inventory_path,
        expected_catalog_entries=expected_catalog_entries,
        expected_source_objects=expected_source_objects,
        enforce_current_shared_keys=enforce_current_shared_keys,
    )
    write_source_objects(rows, output_path)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize LTMD-U2 source-object identities from the CONALITEG catalog inventory."
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("data/catalog/conaliteg_primaria_2026_2027_inventory.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/catalog/ltmd_u2_source_objects_2026_2027.csv"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = materialize(args.inventory, args.output)
    print(
        f"LTMD-U2 identity materialized: "
        f"{EXPECTED_CATALOG_ENTRIES} catalog entries -> {len(rows)} source objects"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
