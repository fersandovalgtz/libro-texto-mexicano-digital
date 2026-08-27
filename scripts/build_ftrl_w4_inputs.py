#!/usr/bin/env python3
"""Normalize versioned W4 Ciencias Sociales topology for generic FTRL."""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

VERSION = "LTMD_U1_W4_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL = 14
EXPECTED_CANONICAL = 14
EXPECTED_PAGES = 2414
SHA = re.compile(r"^[0-9a-f]{64}$")
PROCESSING = Path("data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv")


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def n(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value in {"", None}:
        raise AssertionError(f"missing {key}: {row}")
    return int(float(value))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w4_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w4_processing_inventory.csv")
    args = ap.parse_args()

    processing = read(PROCESSING)
    manifest = read(MANIFEST)
    assert len(processing) == EXPECTED_HISTORICAL
    by = {r["viewer_key"]: r for r in processing}
    assert len(by) == EXPECTED_HISTORICAL
    assert all(n(r, "ocr_identity_eligible") == 1 for r in processing)
    canonical = {r["viewer_key"] for r in processing if n(r, "is_canonical_processing_object") == 1}
    assert len(canonical) == EXPECTED_CANONICAL
    assert all(r["processing_mode"] == "direct_canonical" for r in processing)
    assert all(n(r, "persistent_internal_source_gaps") == 0 for r in processing)

    pfields = [
        "processing_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "processing_mode", "canonical_processing_viewer_key", "technical_identity_covered",
        "is_canonical_processing_object", "declared_positions", "direct_source_jpegs",
        "persistent_internal_source_gaps", "source_processing_basis", "interpretive_limit",
    ]
    pout: list[dict[str, object]] = []
    for r in processing:
        assert r["canonical_processing_viewer_key"] == r["viewer_key"]
        pout.append({
            "processing_version": VERSION,
            "viewer_key": r["viewer_key"],
            "catalog_generation": n(r, "catalog_generation"),
            "grade_code": n(r, "grade_code"),
            "title_core": r["title_core"],
            "processing_mode": r["processing_mode"],
            "canonical_processing_viewer_key": r["viewer_key"],
            "technical_identity_covered": 1,
            "is_canonical_processing_object": 1,
            "declared_positions": n(r, "declared_positions"),
            "direct_source_jpegs": n(r, "direct_source_jpegs"),
            "persistent_internal_source_gaps": 0,
            "source_processing_basis": f"{r['processing_version']}:{r['evidence_basis']}",
            "interpretive_limit": r["interpretive_limit"],
        })

    assert len(manifest) == EXPECTED_PAGES
    assert {r["viewer_key"] for r in manifest} == canonical
    afields = [
        "audit_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "viewer_page", "source_image_index", "source_asset_url", "asset_status", "byte_size",
        "sha256", "processing_mode", "source_provenance",
    ]
    aout: list[dict[str, object]] = []
    seen = set()
    for r in manifest:
        key = (r["viewer_key"], int(r["source_image_index"]))
        assert key not in seen
        seen.add(key)
        assert r["asset_status"] == "source_jpeg"
        assert n(r, "byte_size") > 0 and SHA.fullmatch(r["sha256"])
        aout.append({
            "audit_version": VERSION,
            "viewer_key": r["viewer_key"],
            "catalog_generation": n(r, "catalog_generation"),
            "grade_code": n(r, "grade_code"),
            "title_core": r["title_core"],
            "viewer_page": n(r, "viewer_page"),
            "source_image_index": n(r, "source_image_index"),
            "source_asset_url": r["source_asset_url"],
            "asset_status": "source_jpeg",
            "byte_size": n(r, "byte_size"),
            "sha256": r["sha256"],
            "processing_mode": by[r["viewer_key"]]["processing_mode"],
            "source_provenance": r["source_provenance"],
        })
    assert len(aout) == len(seen) == EXPECTED_PAGES
    assert sum(int(r["direct_source_jpegs"]) for r in pout) == EXPECTED_PAGES

    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(f"Built W4 FTRL inputs: historical={len(pout)}, canonical={len(canonical)}, pages={len(aout)}")


if __name__ == "__main__":
    main()
