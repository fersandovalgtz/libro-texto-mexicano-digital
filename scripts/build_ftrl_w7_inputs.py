#!/usr/bin/env python3
"""Normalize versioned W7 Formación Cívica y Ética topology for generic FTRL.

Only source-admitted canonical identities enter the computational corpus. The
five historically retained identities remain explicit in the source gate and
are never aliased, imputed, or silently absorbed into an admitted viewer.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_W7_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL = 30
EXPECTED_CANONICAL = 25
EXPECTED_WITHHELD = 5
EXPECTED_PAGES = 3261
WITHHELD = {
    "H2014P5FCA",
    "H2018P3FCA",
    "H2018P4FCA",
    "H2018P5FCA",
    "H2018P6FCA",
}
SHA = re.compile(r"^[0-9a-f]{64}$")
SOURCE_GATE = Path("data/catalog/ltmd_u1_w7_source_admissibility.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv")


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
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w7_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w7_processing_inventory.csv")
    args = ap.parse_args()

    gate = read(SOURCE_GATE)
    manifest = read(MANIFEST)
    assert len(gate) == EXPECTED_HISTORICAL
    assert len({r["viewer_key"] for r in gate}) == EXPECTED_HISTORICAL

    admitted = [r for r in gate if r["decision"] == "ocr_source_admitted"]
    withheld = [r for r in gate if r["decision"] != "ocr_source_admitted"]
    admitted_keys = {r["viewer_key"] for r in admitted}
    withheld_keys = {r["viewer_key"] for r in withheld}

    assert len(admitted) == EXPECTED_CANONICAL
    assert len(withheld) == EXPECTED_WITHHELD
    assert withheld_keys == WITHHELD
    assert admitted_keys.isdisjoint(WITHHELD)
    assert all(n(r, "ocr_source_admitted") == 1 for r in admitted)
    assert all(n(r, "direct_asset_ready") == 1 for r in admitted)
    assert all(n(r, "internal_unserved") == 0 for r in admitted)
    assert all(n(r, "ocr_source_admitted") == 0 for r in withheld)
    assert all(n(r, "direct_asset_ready") == 0 for r in withheld)
    assert all(r["decision"].startswith("withheld_source_") for r in withheld)
    assert all(n(r, "source_jpegs") == n(r, "declared_positions") - 1 for r in admitted)
    assert sum(n(r, "source_jpegs") for r in admitted) == EXPECTED_PAGES

    pfields = [
        "processing_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "processing_mode", "canonical_processing_viewer_key", "technical_identity_covered",
        "is_canonical_processing_object", "declared_positions", "direct_source_jpegs",
        "persistent_internal_source_gaps", "source_processing_basis", "interpretive_limit",
    ]
    pout: list[dict[str, object]] = []
    for r in admitted:
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
            "direct_source_jpegs": n(r, "source_jpegs"),
            "persistent_internal_source_gaps": 0,
            "source_processing_basis": f"{r['gate_version']}:{r['reason_code']}",
            "interpretive_limit": "technical FTRL only; retained W7 identities remain outside the corpus; OCR availability does not imply text verification or semantic validation",
        })

    afields = [
        "audit_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "viewer_page", "source_image_index", "source_asset_url", "asset_status", "byte_size",
        "sha256", "processing_mode", "source_provenance",
    ]
    aout: list[dict[str, object]] = []
    seen: set[tuple[str, int]] = set()
    counts: Counter[str] = Counter()
    retained_served_rows = 0

    for r in manifest:
        viewer = r["viewer_key"]
        if viewer in WITHHELD and r.get("asset_status") == "source_jpeg":
            retained_served_rows += 1
        if viewer not in admitted_keys or r.get("asset_status") != "source_jpeg":
            continue

        index = n(r, "source_image_index")
        key = (viewer, index)
        assert key not in seen
        seen.add(key)
        assert n(r, "byte_size") > 0
        assert SHA.fullmatch(r["sha256"])
        assert r["source_asset_url"].startswith(f"https://historico.conaliteg.gob.mx/c/{viewer}/")
        if r.get("http_status"):
            assert n(r, "http_status") == 200
        if r.get("probe_state"):
            assert r["probe_state"] == "served_image"

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
            "source_provenance": f"{r['audit_version']}:historico_conaliteg_direct_jpeg",
        })

    expected_counts = {r["viewer_key"]: n(r, "source_jpegs") for r in admitted}
    assert dict(counts) == expected_counts
    assert len(aout) == len(seen) == EXPECTED_PAGES
    assert sum(int(r["direct_source_jpegs"]) for r in pout) == EXPECTED_PAGES
    assert not ({r["viewer_key"] for r in aout} & WITHHELD)
    # H2014P5FCA legitimately has served source rows, but the identity remains
    # retained because its exact internal gap is unresolved. They must never
    # enter the FTRL output merely because individual JPEGs are available.
    assert retained_served_rows > 0

    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(
        f"Built W7 FTRL inputs: historical={EXPECTED_HISTORICAL}, "
        f"canonical={len(pout)}, withheld={len(withheld)}, pages={len(aout)}"
    )


if __name__ == "__main__":
    main()
