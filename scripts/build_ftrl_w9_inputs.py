#!/usr/bin/env python3
"""Normalize versioned W9 Educación Física topology for generic FTRL."""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_W9_FTRL_INPUTS_0.1"
EXPECTED = {
    "H2008P1ED252": 114,
    "H2008P2ED260": 106,
    "H2008P5ED280": 114,
    "H2008P6ED287": 114,
}
EXPECTED_HISTORICAL = 4
EXPECTED_CANONICAL = 4
EXPECTED_PAGES = sum(EXPECTED.values())
SHA = re.compile(r"^[0-9a-f]{64}$")
PROCESSING = Path("data/catalog/ltmd_u1_w9_processing_inventory.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w9_canonical_page_manifest.csv")


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
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w9_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w9_processing_inventory.csv")
    args = ap.parse_args()

    processing = read(PROCESSING)
    manifest = read(MANIFEST)
    assert len(processing) == EXPECTED_HISTORICAL
    by = {r["viewer_key"]: r for r in processing}
    assert set(by) == set(EXPECTED)
    assert len(by) == EXPECTED_HISTORICAL
    assert all(r["source_status"] == "SOURCE_ADMISSIBLE" for r in processing)
    assert all(r["processing_mode"] == "direct_canonical" for r in processing)
    assert all(n(r, "ocr_identity_eligible") == 1 for r in processing)
    assert all(n(r, "is_canonical_processing_object") == 1 for r in processing)
    assert all(n(r, "persistent_internal_source_gaps") == 0 for r in processing)
    assert all(n(r, "probe_errors") == 0 for r in processing)
    assert all(r["semantic_state"] == "WAITING_HUMAN_REFERENCE" for r in processing)
    assert all(r["alias_state"] == "no_alias" for r in processing)

    for viewer, pages in EXPECTED.items():
        r = by[viewer]
        assert n(r, "source_page_count") == pages
        assert n(r, "declared_positions") == pages + 1

    pfields = [
        "processing_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "processing_mode", "canonical_processing_viewer_key", "technical_identity_covered",
        "is_canonical_processing_object", "declared_positions", "direct_source_jpegs",
        "persistent_internal_source_gaps", "source_processing_basis", "interpretive_limit",
    ]
    pout: list[dict[str, object]] = []
    for r in processing:
        viewer = r["viewer_key"]
        pout.append({
            "processing_version": VERSION,
            "viewer_key": viewer,
            "catalog_generation": n(r, "catalog_generation"),
            "grade_code": n(r, "grade_code"),
            "title_core": r["title_core"],
            "processing_mode": "direct_canonical",
            "canonical_processing_viewer_key": viewer,
            "technical_identity_covered": 1,
            "is_canonical_processing_object": 1,
            "declared_positions": n(r, "declared_positions"),
            "direct_source_jpegs": n(r, "source_page_count"),
            "persistent_internal_source_gaps": 0,
            "source_processing_basis": f"{r['topology_version']}:official_source_sha256_topology",
            "interpretive_limit": "technical FTRL only; OCR availability does not imply text verification or semantic validation",
        })

    assert len(manifest) == EXPECTED_PAGES
    assert set(r["viewer_key"] for r in manifest) == set(EXPECTED)
    afields = [
        "audit_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "viewer_page", "source_image_index", "source_asset_url", "asset_status", "byte_size",
        "sha256", "processing_mode", "source_provenance",
    ]
    aout: list[dict[str, object]] = []
    seen: set[tuple[str, int]] = set()
    counts: Counter[str] = Counter()
    for r in manifest:
        viewer = r["viewer_key"]
        index = n(r, "source_image_index")
        key = (viewer, index)
        assert key not in seen
        seen.add(key)
        assert viewer in EXPECTED
        assert r["processing_mode"] == "direct_canonical"
        assert r["asset_status"] == "source_jpeg"
        assert n(r, "byte_size") > 0
        assert SHA.fullmatch(r["sha256"])
        assert r["source_asset_url"].startswith(f"https://historico.conaliteg.gob.mx/c/{viewer}/")
        counts[viewer] += 1
        aout.append({
            "audit_version": VERSION,
            "viewer_key": viewer,
            "catalog_generation": n(r, "catalog_generation"),
            "grade_code": n(r, "grade_code"),
            "title_core": r["title_core"],
            "viewer_page": n(r, "viewer_page"),
            "source_image_index": index,
            "source_asset_url": r["source_asset_url"],
            "asset_status": "source_jpeg",
            "byte_size": n(r, "byte_size"),
            "sha256": r["sha256"],
            "processing_mode": "direct_canonical",
            "source_provenance": r["source_provenance"],
        })
    assert dict(counts) == EXPECTED
    assert len(aout) == len(seen) == EXPECTED_PAGES
    assert sum(int(r["direct_source_jpegs"]) for r in pout) == EXPECTED_PAGES

    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(f"Built W9 FTRL inputs: historical={len(pout)}, canonical={EXPECTED_CANONICAL}, pages={len(aout)}")


if __name__ == "__main__":
    main()
