#!/usr/bin/env python3
"""Normalize versioned W8 Artes topology for generic FTRL.

Only the 16 source-admitted canonical identities enter the computational corpus.
The four 2018 source-retained identities remain explicit in the canonical gate
and are never aliased, imputed, or silently absorbed into an admitted viewer.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_W8_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL = 20
EXPECTED_CANONICAL = 16
EXPECTED_WITHHELD = 4
EXPECTED_PAGES = 1490
WITHHELD = {
    "H2018P3EAA",
    "H2018P4EAA",
    "H2018P5EAA",
    "H2018P6EAA",
}
SHA = re.compile(r"^[0-9a-f]{64}$")
SOURCE_GATE = Path("data/catalog/ltmd_u1_w8_artes_source_admissibility.csv")
TOPOLOGY = Path("data/catalog/ltmd_u1_w8_processing_inventory.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w8_artes_asset_manifest.csv")


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
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w8_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w8_processing_inventory.csv")
    args = ap.parse_args()

    gate = read(SOURCE_GATE)
    topology = read(TOPOLOGY)
    manifest = read(MANIFEST)

    assert len(gate) == EXPECTED_HISTORICAL
    assert len(topology) == EXPECTED_HISTORICAL
    assert len({r["viewer_key"] for r in gate}) == EXPECTED_HISTORICAL
    assert {r["viewer_key"] for r in topology} == {r["viewer_key"] for r in gate}
    topo = {r["viewer_key"]: r for r in topology}

    admitted = [r for r in gate if n(r, "source_admissible") == 1]
    withheld = [r for r in gate if n(r, "source_admissible") == 0]
    admitted_keys = {r["viewer_key"] for r in admitted}
    withheld_keys = {r["viewer_key"] for r in withheld}

    assert len(admitted) == EXPECTED_CANONICAL
    assert len(withheld) == EXPECTED_WITHHELD
    assert withheld_keys == WITHHELD
    assert admitted_keys.isdisjoint(WITHHELD)

    for r in admitted:
        viewer = r["viewer_key"]
        t = topo[viewer]
        assert r["source_status"] == "SOURCE_ADMISSIBLE"
        assert n(r, "direct_asset_ready") == 1
        assert n(r, "internal_unserved") == 0
        assert n(r, "probe_errors") == 0
        assert n(r, "source_jpegs") == n(r, "declared_positions") - 1
        assert r["alias_state"] == "no_alias"
        assert t["source_status"] == "SOURCE_ADMISSIBLE"
        assert t["processing_mode"] == "direct_canonical"
        assert n(t, "is_canonical_processing_object") == 1
        assert n(t, "ocr_identity_eligible") == 1
        assert n(t, "source_page_count") == n(r, "source_jpegs")
        assert n(t, "declared_positions") == n(r, "declared_positions")
        assert n(t, "persistent_internal_source_gaps") == 0
        assert n(t, "probe_errors") == 0
        assert t["alias_state"] == "no_alias"

    for r in withheld:
        viewer = r["viewer_key"]
        t = topo[viewer]
        assert r["source_status"] == "SOURCE_RETAINED"
        assert n(r, "source_jpegs") == 0
        assert n(r, "direct_asset_ready") == 0
        assert n(r, "internal_unserved") == n(r, "declared_positions")
        assert n(r, "probe_errors") == 0
        assert r["alias_state"] == "no_alias"
        assert t["source_status"] == "SOURCE_RETAINED"
        assert t["processing_mode"] == "withheld_source"
        assert n(t, "is_canonical_processing_object") == 0
        assert n(t, "ocr_identity_eligible") == 0
        assert n(t, "source_page_count") == 0
        assert n(t, "persistent_internal_source_gaps") == n(t, "declared_positions")
        assert t["alias_state"] == "no_alias"

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
            "source_processing_basis": f"{r['admissibility_version']}:{r['source_status']}",
            "interpretive_limit": "technical FTRL only; four retained W8 identities remain outside the corpus; OCR availability does not imply text verification or semantic validation",
        })

    afields = [
        "audit_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "viewer_page", "source_image_index", "source_asset_url", "asset_status", "byte_size",
        "sha256", "processing_mode", "source_provenance",
    ]
    aout: list[dict[str, object]] = []
    seen: set[tuple[str, int]] = set()
    counts: Counter[str] = Counter()
    retained_source_rows = 0

    for r in manifest:
        viewer = r["viewer_key"]
        if viewer in WITHHELD and r.get("asset_status") == "source_jpeg":
            retained_source_rows += 1
        if viewer not in admitted_keys or r.get("asset_status") != "source_jpeg":
            continue

        index = n(r, "source_image_index")
        key = (viewer, index)
        assert key not in seen
        seen.add(key)
        assert n(r, "byte_size") > 0
        assert SHA.fullmatch(r["sha256"])
        assert r["source_asset_url"].startswith(f"https://historico.conaliteg.gob.mx/c/{viewer}/")
        assert n(r, "http_status") == 200
        assert r["probe_state"] == "served_image"
        assert r["content_type"].lower().startswith("image/")
        assert not r.get("error")

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
    assert retained_source_rows == 0

    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(
        f"Built W8 FTRL inputs: historical={EXPECTED_HISTORICAL}, "
        f"canonical={len(pout)}, withheld={len(withheld)}, pages={len(aout)}"
    )


if __name__ == "__main__":
    main()
