#!/usr/bin/env python3
"""Normalize versioned W6 Geografía/Atlas source topology for generic FTRL."""
from __future__ import annotations

import argparse, csv, re
from pathlib import Path
from urllib.parse import urlparse

VERSION = "LTMD_U1_W6_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL = 42
EXPECTED_CANONICAL = 37
EXPECTED_ALIASES = 5
EXPECTED_PAGES = 5258
EXPECTED_RECOVERED = 2
SHA = re.compile(r"^[0-9a-f]{64}$")
PROCESSING = Path("data/catalog/ltmd_u1_w6_geography_atlas_processing_inventory.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w6_geography_atlas_canonical_page_manifest.csv")

def read(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))

def n(row, key):
    v = row.get(key, "")
    if v in {"", None}:
        raise AssertionError(f"missing {key}: {row}")
    return int(float(v))

def write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)

def source_index(url: str) -> int:
    stem = Path(urlparse(url).path).stem
    if not stem.isdigit():
        raise AssertionError(f"non-numeric W6 source image index: {url}")
    return int(stem)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w6_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w6_processing_inventory.csv")
    a = ap.parse_args()
    processing = read(PROCESSING); manifest = read(MANIFEST)
    assert len(processing) == EXPECTED_HISTORICAL
    by = {r["viewer_key"]: r for r in processing}; assert len(by) == EXPECTED_HISTORICAL
    canonical = {r["viewer_key"] for r in processing if n(r, "is_canonical_processing_object") == 1}
    assert len(canonical) == EXPECTED_CANONICAL and len(processing) - len(canonical) == EXPECTED_ALIASES
    assert all(n(r, "technical_identity_covered") == 1 and n(r, "persistent_source_gaps") == 0 for r in processing)

    pfields = ["processing_version","viewer_key","catalog_generation","grade_code","title_core","processing_mode","canonical_processing_viewer_key","technical_identity_covered","is_canonical_processing_object","declared_positions","direct_source_jpegs","persistent_internal_source_gaps","source_processing_basis","interpretive_limit"]
    pout = []
    for r in processing:
        target = r["canonical_processing_viewer_key"]; assert target in canonical
        source_pages = n(r, "direct_source_pages_for_processing") + n(r, "recovered_source_pages_for_processing")
        pout.append({
            "processing_version": VERSION,
            "viewer_key": r["viewer_key"],
            "catalog_generation": n(r, "catalog_generation"),
            "grade_code": n(r, "grade_code"),
            "title_core": r["title_core"],
            "processing_mode": r["processing_mode"],
            "canonical_processing_viewer_key": target,
            "technical_identity_covered": 1,
            "is_canonical_processing_object": n(r, "is_canonical_processing_object"),
            "declared_positions": n(r, "declared_positions"),
            "direct_source_jpegs": source_pages if n(r, "is_canonical_processing_object") == 1 else 0,
            "persistent_internal_source_gaps": 0,
            "source_processing_basis": f"{r['topology_version']}:{r['processing_mode']}",
            "interpretive_limit": "Technical source topology only; aliases/recovery do not imply bibliographic, curricular, semantic, or historical equivalence.",
        })

    assert len(manifest) == EXPECTED_PAGES and {r["viewer_key"] for r in manifest} == canonical
    afields = ["audit_version","viewer_key","catalog_generation","grade_code","title_core","viewer_page","source_image_index","source_asset_url","asset_status","byte_size","sha256","processing_mode","source_provenance"]
    aout = []; seen = set(); recovered = 0
    for r in manifest:
        idx = source_index(r["source_asset_url"])
        key = (r["viewer_key"], idx); assert key not in seen; seen.add(key)
        assert n(r, "byte_size") > 0 and SHA.fullmatch(r["sha256"])
        provenance = r["source_kind"]
        if r["source_kind"] == "cryptographically_recovered_same_position_reference":
            recovered += 1
            provenance += f":reference={r['recovery_reference_viewer_key']}:original={r['original_source_asset_url']}"
        aout.append({
            "audit_version": VERSION,
            "viewer_key": r["viewer_key"],
            "catalog_generation": n(r, "catalog_generation"),
            "grade_code": n(r, "grade_code"),
            "title_core": r["title_core"],
            "viewer_page": n(r, "viewer_page"),
            "source_image_index": idx,
            "source_asset_url": r["source_asset_url"],
            "asset_status": "source_jpeg",
            "byte_size": n(r, "byte_size"),
            "sha256": r["sha256"],
            "processing_mode": by[r["viewer_key"]]["processing_mode"],
            "source_provenance": provenance,
        })
    assert len(aout) == EXPECTED_PAGES and len(seen) == EXPECTED_PAGES and recovered == EXPECTED_RECOVERED
    write(Path(a.processing_output), pout, pfields); write(Path(a.asset_output), aout, afields)
    print(f"Built W6 FTRL inputs: historical={len(pout)}, canonical={len(canonical)}, aliases={EXPECTED_ALIASES}, pages={len(aout)}, recovered={recovered}")

if __name__ == "__main__":
    main()
