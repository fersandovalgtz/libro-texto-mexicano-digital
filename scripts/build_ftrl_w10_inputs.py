#!/usr/bin/env python3
"""Normalize versioned W10 Integrados/Multiarea topology for generic FTRL.

Only the 68 source-admitted canonical identities enter the computational corpus.
H2014P1ENA remains an explicit source-retained historical identity and is never
aliased, imputed, or silently absorbed into an admitted viewer.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_W10_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL = 69
EXPECTED_CANONICAL = 68
EXPECTED_WITHHELD = 1
EXPECTED_PAGES = 11937
WITHHELD = {"H2014P1ENA"}
SHA = re.compile(r"^[0-9a-f]{64}$")
SOURCE_GATE = Path("data/catalog/ltmd_u1_w10_source_admissibility.csv")
TOPOLOGY = Path("data/catalog/ltmd_u1_w10_processing_inventory.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w10_canonical_page_manifest.csv")


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
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w10_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w10_processing_inventory.csv")
    args = ap.parse_args()

    gate = read(SOURCE_GATE)
    topology = read(TOPOLOGY)
    manifest = read(MANIFEST)

    assert len(gate) == EXPECTED_HISTORICAL
    assert len(topology) == EXPECTED_HISTORICAL
    assert len({r["viewer_key"] for r in gate}) == EXPECTED_HISTORICAL
    assert {r["viewer_key"] for r in topology} == {r["viewer_key"] for r in gate}
    topo = {r["viewer_key"]: r for r in topology}

    admitted = [r for r in gate if n(r, "ocr_source_admitted") == 1]
    withheld = [r for r in gate if n(r, "ocr_source_admitted") == 0]
    admitted_keys = {r["viewer_key"] for r in admitted}
    withheld_keys = {r["viewer_key"] for r in withheld}

    assert len(admitted) == EXPECTED_CANONICAL
    assert len(withheld) == EXPECTED_WITHHELD
    assert withheld_keys == WITHHELD
    assert admitted_keys.isdisjoint(WITHHELD)

    canonical = []
    aliases = []
    for r in admitted:
        t = topo[r["viewer_key"]]
        assert t["source_admitted"] == "1"
        if t["processing_mode"] == "direct_canonical":
            canonical.append(t)
        elif t["processing_mode"] == "exact_source_alias":
            aliases.append(t)
        else:
            raise AssertionError(f"unexpected admitted W10 processing mode: {t}")
    assert len(canonical) == EXPECTED_CANONICAL
    assert not aliases
    assert all(n(r, "is_canonical_processing_object") == 1 for r in canonical)

    for r in withheld:
        t = topo[r["viewer_key"]]
        assert r["source_state"].startswith("withheld_")
        assert t["source_admitted"] == "0"
        assert t["processing_mode"] == "withheld_source"
        assert n(t, "is_canonical_processing_object") == 0
        assert t["canonical_viewer_key"] == ""

    pfields = [
        "processing_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "processing_mode", "canonical_processing_viewer_key", "technical_identity_covered",
        "is_canonical_processing_object", "declared_positions", "direct_source_jpegs",
        "persistent_internal_source_gaps", "source_processing_basis", "interpretive_limit",
    ]
    pout: list[dict[str, object]] = []
    gate_by = {r["viewer_key"]: r for r in gate}
    for t in canonical:
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
            "source_processing_basis": f"{t['topology_version']}:{g['source_state']}",
            "interpretive_limit": "technical FTRL only; H2014P1ENA remains source-retained outside the corpus; OCR availability does not imply text verification or semantic validation",
        })

    assert len(manifest) == EXPECTED_PAGES
    assert {r["viewer_key"] for r in manifest} == admitted_keys
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
        assert viewer in admitted_keys
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

    expected_counts = {r["viewer_key"]: int(r["direct_source_jpegs"]) for r in pout}
    assert dict(counts) == expected_counts
    assert len(aout) == len(seen) == EXPECTED_PAGES
    assert sum(int(r["direct_source_jpegs"]) for r in pout) == EXPECTED_PAGES
    assert not ({r["viewer_key"] for r in aout} & WITHHELD)

    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(
        f"Built W10 FTRL inputs: historical={EXPECTED_HISTORICAL}, canonical={len(pout)}, "
        f"withheld={len(withheld)}, pages={len(aout)}"
    )


if __name__ == "__main__":
    main()
