#!/usr/bin/env python3
"""Normalize versioned W11 Otros/No clasificados topology for generic FTRL.

The public inputs contain source metadata/hashes only. Restricted OCR text and
SQLite outputs are generated under local/ by the per-book runner and must never
be committed.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_W11_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL = 111
EXPECTED_ADMITTED = 107
EXPECTED_CANONICAL = 106
EXPECTED_ALIASES = 1
EXPECTED_WITHHELD = 4
EXPECTED_PAGES = 19862
WITHHELD = {"H2014P1EAM", "H2014P2EAM", "H2014P3COL", "H2014P3MOR"}
EXPECTED_ALIAS = {"H2008P4CI270": "H1993P4CI192"}
SHA = re.compile(r"^[0-9a-f]{64}$")
SOURCE_GATE = Path("data/catalog/ltmd_u1_w11_source_admissibility.csv")
TOPOLOGY = Path("data/catalog/ltmd_u1_w11_processing_inventory.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w11_canonical_page_manifest.csv")


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
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w11_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w11_processing_inventory.csv")
    args = ap.parse_args()

    gate = read(SOURCE_GATE)
    topology = read(TOPOLOGY)
    manifest = read(MANIFEST)

    assert len(gate) == EXPECTED_HISTORICAL
    assert len(topology) == EXPECTED_HISTORICAL
    gate_keys = {r["viewer_key"] for r in gate}
    topo_keys = {r["viewer_key"] for r in topology}
    assert len(gate_keys) == EXPECTED_HISTORICAL
    assert topo_keys == gate_keys
    topo = {r["viewer_key"]: r for r in topology}

    admitted = [r for r in gate if n(r, "ocr_source_admitted") == 1]
    withheld = [r for r in gate if n(r, "ocr_source_admitted") == 0]
    admitted_keys = {r["viewer_key"] for r in admitted}
    withheld_keys = {r["viewer_key"] for r in withheld}
    assert len(admitted) == EXPECTED_ADMITTED
    assert len(withheld) == EXPECTED_WITHHELD
    assert withheld_keys == WITHHELD
    assert admitted_keys.isdisjoint(WITHHELD)

    canonical = [
        topo[k] for k in admitted_keys
        if topo[k]["processing_mode"] == "direct_canonical"
        and n(topo[k], "is_canonical_processing_object") == 1
    ]
    aliases = [
        topo[k] for k in admitted_keys
        if topo[k]["processing_mode"] == "exact_source_alias"
        and n(topo[k], "is_canonical_processing_object") == 0
    ]
    assert len(canonical) == EXPECTED_CANONICAL
    assert len(aliases) == EXPECTED_ALIASES
    canonical_keys = {r["viewer_key"] for r in canonical}
    alias_map = {r["viewer_key"]: r["canonical_viewer_key"] for r in aliases}
    assert alias_map == EXPECTED_ALIAS
    assert all(target in canonical_keys for target in alias_map.values())

    for row in withheld:
        t = topo[row["viewer_key"]]
        assert t["source_admitted"] == "0"
        assert t["processing_mode"] == "withheld_source"
        assert n(t, "is_canonical_processing_object") == 0
        assert not t["canonical_viewer_key"]
        assert n(row, "internal_unserved") > 0
    for row in canonical:
        assert row["source_admitted"] == "1"
        assert row["canonical_viewer_key"] == row["viewer_key"]
        assert SHA.fullmatch(row["source_sequence_sha256"])

    pfields = [
        "processing_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "processing_mode", "canonical_processing_viewer_key", "technical_identity_covered",
        "is_canonical_processing_object", "declared_positions", "direct_source_jpegs",
        "persistent_internal_source_gaps", "source_processing_basis", "interpretive_limit",
    ]
    gate_by = {r["viewer_key"]: r for r in gate}
    pout: list[dict[str, object]] = []
    for t in sorted(canonical, key=lambda r: (n(r, "catalog_generation"), n(r, "grade_code"), r["viewer_key"])):
        viewer = t["viewer_key"]
        g = gate_by[viewer]
        assert n(g, "internal_unserved") == 0
        assert n(g, "probe_errors") == 0
        assert n(g, "source_jpegs") == n(t, "source_pages")
        pout.append({
            "processing_version": VERSION,
            "viewer_key": viewer,
            "catalog_generation": n(t, "catalog_generation"),
            "grade_code": n(t, "grade_code"),
            "title_core": t["title_core"],
            "processing_mode": "direct_canonical",
            "canonical_processing_viewer_key": viewer,
            "technical_identity_covered": 1,
            "is_canonical_processing_object": 1,
            "declared_positions": n(g, "declared_positions"),
            "direct_source_jpegs": n(t, "source_pages"),
            "persistent_internal_source_gaps": 0,
            "source_processing_basis": f"{t['topology_version']}:{g['source_state']}:{t['technical_route']}",
            "interpretive_limit": (
                "technical FTRL only; four source-retained identities remain outside the corpus; "
                "one admitted historical identity is an exact full-sequence alias; OCR availability "
                "does not imply text verification or semantic validation"
            ),
        })

    assert len(manifest) == EXPECTED_PAGES
    assert {r["viewer_key"] for r in manifest} == canonical_keys
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
        assert viewer in canonical_keys
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

    expected_counts = Counter({r["viewer_key"]: int(r["direct_source_jpegs"]) for r in pout})
    assert counts == expected_counts
    assert len(aout) == len(seen) == EXPECTED_PAGES
    assert sum(expected_counts.values()) == EXPECTED_PAGES
    assert not ({r["viewer_key"] for r in aout} & WITHHELD)
    assert not ({r["viewer_key"] for r in aout} & set(EXPECTED_ALIAS))

    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(
        "Built W11 FTRL inputs: "
        f"historical={EXPECTED_HISTORICAL}, admitted={EXPECTED_ADMITTED}, "
        f"canonical={len(pout)}, aliases={len(aliases)}, withheld={len(withheld)}, pages={len(aout)}"
    )


if __name__ == "__main__":
    main()
