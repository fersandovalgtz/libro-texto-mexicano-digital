#!/usr/bin/env python3
"""Build LTMD-U2 coverage/Analytics 0.1 from already observed public metadata states.

This builder performs deterministic joins only. It does not download source books,
inspect source content, infer OCR need, or promote text/semantic states.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

INVENTORY = Path("data/catalog/conaliteg_primaria_2026_2027_inventory.csv")
SOURCE_OBJECTS = Path("data/catalog/ltmd_u2_source_objects_2026_2027.csv")
READER_SHELL = Path("data/catalog/ltmd_u2_reader_shell_resolution_2026_09_02.csv")
ASSET = Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv")
PAGE_COUNT = Path("data/catalog/ltmd_u2_page_count_resolution_2026_09_02.csv")
SOURCE_ADMISSION = Path("data/catalog/ltmd_u2_source_admission_2026_09_02.csv")
TEXT_ACCESS = Path("data/catalog/ltmd_u2_text_access_observation_2026_09_02.csv")

SOURCE_FIELDS = [
    "source_object_id", "viewer_key", "source_cycle", "cycle_label", "level",
    "catalog_entry_count", "catalog_grades", "cataloged_state",
    "reader_shell_state", "asset_resolution_state", "page_count_state", "page_count",
    "source_admission_state", "text_access_observation_state",
    "embedded_text_sample_state", "ocr_available_state", "text_verified_state",
    "semantic_ready_state",
]

ENTRY_FIELDS = [
    "catalog_entry_id", "cycle", "level", "grade", "viewer_key", "source_object_id",
    "shared_viewer", "cataloged_state", "reader_shell_state", "asset_resolution_state",
    "page_count_state", "page_count", "source_admission_state",
    "text_access_observation_state", "embedded_text_sample_state",
    "ocr_available_state", "text_verified_state", "semantic_ready_state",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def index(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in out:
            raise ValueError(f"duplicate {key}: {value}")
        out[value] = row
    return out


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    inventory = read_csv(INVENTORY)
    sources = read_csv(SOURCE_OBJECTS)
    shell = index(read_csv(READER_SHELL), "source_object_id")
    assets = index(read_csv(ASSET), "source_object_id")
    pages = index(read_csv(PAGE_COUNT), "source_object_id")
    admission = index(read_csv(SOURCE_ADMISSION), "source_object_id")
    text_access = index(read_csv(TEXT_ACCESS), "source_object_id")

    if len(inventory) != 42:
        raise ValueError(f"catalog denominator must be 42, got {len(inventory)}")
    if len(sources) != 39:
        raise ValueError(f"source-object denominator must be 39, got {len(sources)}")

    source_index = index(sources, "source_object_id")
    expected_ids = set(source_index)
    for name, layer in {
        "reader_shell": shell,
        "asset": assets,
        "page_count": pages,
        "source_admission": admission,
        "text_access": text_access,
    }.items():
        if set(layer) != expected_ids:
            raise ValueError(f"{name} IDs do not exactly match source-object universe")

    entries_by_viewer: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inventory:
        entries_by_viewer[row["viewer_key"]].append(row)

    source_rows: list[dict[str, object]] = []
    for source in sorted(sources, key=lambda r: r["source_object_id"]):
        sid = source["source_object_id"]
        viewer = source["viewer_key"]
        entries = entries_by_viewer.get(viewer, [])
        expected_count = int(source["catalog_entry_count"])
        if len(entries) != expected_count:
            raise ValueError(f"{sid}: catalog_entry_count mismatch")
        grades = "|".join(sorted((r["grade"] for r in entries), key=int))
        if grades != source["catalog_grades"]:
            raise ValueError(f"{sid}: catalog_grades mismatch: {grades} != {source['catalog_grades']}")

        row: dict[str, object] = {
            "source_object_id": sid,
            "viewer_key": viewer,
            "source_cycle": source["source_cycle"],
            "cycle_label": source["cycle_label"],
            "level": source["level"],
            "catalog_entry_count": expected_count,
            "catalog_grades": source["catalog_grades"],
            "cataloged_state": "cataloged",
            "reader_shell_state": shell[sid]["reader_shell_state"],
            "asset_resolution_state": assets[sid]["asset_resolution_state"],
            "page_count_state": pages[sid]["page_count_state"],
            "page_count": int(pages[sid]["page_count"]),
            "source_admission_state": admission[sid]["source_admission_state"],
            "text_access_observation_state": text_access[sid]["text_access_observation_state"],
            "embedded_text_sample_state": text_access[sid]["embedded_text_sample_state"],
            "ocr_available_state": text_access[sid]["ocr_available_state"],
            "text_verified_state": text_access[sid]["text_verified_state"],
            "semantic_ready_state": "not_assessed",
        }
        source_rows.append(row)

    source_by_viewer = {row["viewer_key"]: row for row in source_rows}
    if set(source_by_viewer) != set(entries_by_viewer):
        raise ValueError("catalog viewer keys and source-object viewer keys do not reconcile")

    entry_rows: list[dict[str, object]] = []
    for entry in sorted(inventory, key=lambda r: r["catalog_entry_id"]):
        state = source_by_viewer[entry["viewer_key"]]
        entry_rows.append({
            "catalog_entry_id": entry["catalog_entry_id"],
            "cycle": entry["cycle"],
            "level": entry["level"],
            "grade": int(entry["grade"]),
            "viewer_key": entry["viewer_key"],
            "source_object_id": state["source_object_id"],
            "shared_viewer": entry["shared_viewer"],
            "cataloged_state": state["cataloged_state"],
            "reader_shell_state": state["reader_shell_state"],
            "asset_resolution_state": state["asset_resolution_state"],
            "page_count_state": state["page_count_state"],
            "page_count": state["page_count"],
            "source_admission_state": state["source_admission_state"],
            "text_access_observation_state": state["text_access_observation_state"],
            "embedded_text_sample_state": state["embedded_text_sample_state"],
            "ocr_available_state": state["ocr_available_state"],
            "text_verified_state": state["text_verified_state"],
            "semantic_ready_state": state["semantic_ready_state"],
        })

    def count(rows: list[dict[str, object]], field: str) -> dict[str, int]:
        return dict(sorted(Counter(str(r[field]) for r in rows).items()))

    summary: dict[str, object] = {
        "schema": "LTMD_U2_COVERAGE_ANALYTICS_MANIFEST_0.1",
        "cohort": "CONALITEG primaria 2026-2027",
        "source_cycle": "2026",
        "observation_cut": "2026-09-02",
        "denominators": {
            "catalog_entries": len(entry_rows),
            "source_objects": len(source_rows),
        },
        "source_object_metrics": {
            "total_observed_pages": sum(int(r["page_count"]) for r in source_rows),
            "cataloged_state": count(source_rows, "cataloged_state"),
            "reader_shell_state": count(source_rows, "reader_shell_state"),
            "asset_resolution_state": count(source_rows, "asset_resolution_state"),
            "page_count_state": count(source_rows, "page_count_state"),
            "source_admission_state": count(source_rows, "source_admission_state"),
            "text_access_observation_state": count(source_rows, "text_access_observation_state"),
            "embedded_text_sample_state": count(source_rows, "embedded_text_sample_state"),
            "ocr_available_state": count(source_rows, "ocr_available_state"),
            "text_verified_state": count(source_rows, "text_verified_state"),
            "semantic_ready_state": count(source_rows, "semantic_ready_state"),
        },
        "catalog_entry_metrics": {
            "cataloged_state": count(entry_rows, "cataloged_state"),
            "reader_shell_state": count(entry_rows, "reader_shell_state"),
            "asset_resolution_state": count(entry_rows, "asset_resolution_state"),
            "page_count_state": count(entry_rows, "page_count_state"),
            "source_admission_state": count(entry_rows, "source_admission_state"),
            "text_access_observation_state": count(entry_rows, "text_access_observation_state"),
            "embedded_text_sample_state": count(entry_rows, "embedded_text_sample_state"),
            "ocr_available_state": count(entry_rows, "ocr_available_state"),
            "text_verified_state": count(entry_rows, "text_verified_state"),
            "semantic_ready_state": count(entry_rows, "semantic_ready_state"),
        },
        "separation_guards": {
            "catalog_entry_is_not_source_object": True,
            "u2_denominators_are_separate_from_u1": True,
            "content_access_blocked_does_not_imply_no_embedded_text": True,
            "content_access_blocked_does_not_imply_ocr_needed": True,
            "ocr_available_does_not_imply_text_verified": True,
            "source_pdf_bytes_persisted": False,
            "extracted_text_persisted": False,
        },
        "evidence_scope": "non-substitutive metadata/state aggregation only; no source PDF, OCR, extracted text, or semantic promotion",
    }
    return source_rows, entry_rows, summary


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-output", type=Path, default=Path("data/analytics/ltmd_u2_source_coverage_0_1.csv"))
    parser.add_argument("--entry-output", type=Path, default=Path("data/analytics/ltmd_u2_catalog_entry_coverage_0_1.csv"))
    parser.add_argument("--manifest-output", type=Path, default=Path("data/analytics/ltmd_u2_coverage_analytics_manifest_0_1.json"))
    args = parser.parse_args()

    source_rows, entry_rows, summary = build()
    write_csv(args.source_output, SOURCE_FIELDS, source_rows)
    write_csv(args.entry_output, ENTRY_FIELDS, entry_rows)
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)

    summary["materialization"] = {
        "source_csv": str(args.source_output),
        "entry_csv": str(args.entry_output),
    }
    args.manifest_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Reopen after writing so digests describe exact materialized bytes.
    summary["materialization"]["source_csv_sha256"] = sha256(args.source_output)
    summary["materialization"]["entry_csv_sha256"] = sha256(args.entry_output)
    args.manifest_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "catalog_entries": len(entry_rows),
        "source_objects": len(source_rows),
        "total_observed_pages": summary["source_object_metrics"]["total_observed_pages"],
        "source_csv_sha256": summary["materialization"]["source_csv_sha256"],
        "entry_csv_sha256": summary["materialization"]["entry_csv_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
