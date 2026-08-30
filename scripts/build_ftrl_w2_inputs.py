#!/usr/bin/env python3
"""Normalize reconciled W2 Mathematics evidence for generic FTRL.

Public inputs contain only source metadata and cryptographic evidence. Restricted
OCR, SQLite and QC outputs are generated under local/ by the per-book runner and
must never be committed.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_W2_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL = 64
EXPECTED_ADMITTED = 60
EXPECTED_CANONICAL = 57
EXPECTED_ALIASES = 3
EXPECTED_WITHHELD = 4
EXPECTED_PAGES = 11945
WITHHELD = {"H2018P3DMA", "H2018P4DMA", "H2018P5DMA", "H2018P6DMA"}
EXPECTED_ALIAS = {
    "H1982P4MA388": "H1972P4MA083",
    "H1982P5MA394": "H1972P5MA089",
    "H1982P6MA399": "H1972P6MA094",
}
SHA = re.compile(r"^[0-9a-f]{64}$")
SCOPE = Path("data/catalog/ltmd_u1_w2_scope.csv")
SUMMARY = Path("data/catalog/ltmd_u1_w2_math_reconciled_summary.csv")
ALIASES = Path("data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w2_math_reconciled_manifest.csv")


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
    ap.add_argument("--asset-output", default="local/ftrl/ltmd_u1_w2_asset_manifest.csv")
    ap.add_argument("--processing-output", default="local/ftrl/ltmd_u1_w2_processing_inventory.csv")
    args = ap.parse_args()

    scope = read(SCOPE)
    summary = read(SUMMARY)
    aliases = read(ALIASES)
    manifest = read(MANIFEST)

    assert len(scope) == EXPECTED_HISTORICAL
    assert len(summary) == EXPECTED_HISTORICAL
    scope_keys = [r["viewer_key"] for r in scope]
    assert len(scope_keys) == len(set(scope_keys)) == EXPECTED_HISTORICAL
    summary_by = {r["viewer_key"]: r for r in summary}
    scope_by = {r["viewer_key"]: r for r in scope}
    assert set(summary_by) == set(scope_by)

    ready = {k for k, r in summary_by.items() if n(r, "effective_asset_ready") == 1}
    withheld = set(scope_by) - ready
    assert len(ready) == EXPECTED_ADMITTED
    assert len(withheld) == EXPECTED_WITHHELD
    assert withheld == WITHHELD
    assert all(n(summary_by[k], "effective_unresolved") > 0 for k in WITHHELD)

    alias_map = {
        r["viewer_key"]: r["canonical_viewer_key"]
        for r in aliases
        if n(r, "all_effective_pages_byte_identical_aligned") == 1
    }
    assert len(alias_map) == EXPECTED_ALIASES
    assert alias_map == EXPECTED_ALIAS
    assert set(alias_map) <= ready
    assert set(alias_map.values()) <= ready

    canonical_keys = ready - set(alias_map)
    assert len(canonical_keys) == EXPECTED_CANONICAL
    assert set(alias_map.values()) <= canonical_keys

    pfields = [
        "processing_version", "viewer_key", "catalog_generation", "grade_code", "title_core",
        "processing_mode", "canonical_processing_viewer_key", "technical_identity_covered",
        "is_canonical_processing_object", "declared_positions", "direct_source_jpegs",
        "persistent_internal_source_gaps", "source_processing_basis", "interpretive_limit",
    ]
    pout: list[dict[str, object]] = []
    for viewer in scope_keys:
        if viewer not in canonical_keys:
            continue
        s = summary_by[viewer]
        meta = scope_by[viewer]
        assert n(s, "effective_unresolved") == 0
        assert n(s, "effective_real_jpeg") > 0
        assert n(s, "declared_rows") == n(s, "effective_real_jpeg") + n(s, "terminal_synthetic")
        pout.append({
            "processing_version": VERSION,
            "viewer_key": viewer,
            "catalog_generation": n(meta, "catalog_generation"),
            "grade_code": n(meta, "grade_code"),
            "title_core": meta["title_core"],
            "processing_mode": "direct_canonical",
            "canonical_processing_viewer_key": viewer,
            "technical_identity_covered": 1,
            "is_canonical_processing_object": 1,
            "declared_positions": n(s, "declared_rows"),
            "direct_source_jpegs": n(s, "effective_real_jpeg"),
            "persistent_internal_source_gaps": 0,
            "source_processing_basis": f"{s['reconcile_version']}:effective_asset_ready",
            "interpretive_limit": (
                "technical FTRL only; four DMA 2018 identities remain active retentions; "
                "three admitted historical identities are exact full-sequence aliases; "
                "OCR availability does not imply text verification or semantic validation"
            ),
        })
    assert len(pout) == EXPECTED_CANONICAL

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
        if viewer not in canonical_keys:
            continue
        if r["effective_asset_status"] not in {"source_jpeg", "source_jpeg_recovered"}:
            continue
        index = n(r, "source_image_index")
        key = (viewer, index)
        assert key not in seen, key
        seen.add(key)
        assert SHA.fullmatch(r["effective_sha256"]), (viewer, index)
        assert n(r, "effective_byte_size") > 0
        assert r["effective_asset_url"].startswith("https://historico.conaliteg.gob.mx/c/")
        assert r["effective_source_viewer_key"]
        counts[viewer] += 1
        aout.append({
            "audit_version": VERSION,
            "viewer_key": viewer,
            "catalog_generation": n(r, "catalog_generation"),
            "grade_code": n(r, "grade_code"),
            "title_core": r["title_core"],
            "viewer_page": n(r, "viewer_page"),
            "source_image_index": index,
            "source_asset_url": r["effective_asset_url"],
            "asset_status": "source_jpeg",
            "byte_size": n(r, "effective_byte_size"),
            "sha256": r["effective_sha256"],
            "processing_mode": "direct_canonical",
            "source_provenance": (
                f"{r['reconcile_version']}:{r['resolution_method']}:"
                f"effective_source={r['effective_source_viewer_key']}"
            ),
        })

    expected_counts = Counter({r["viewer_key"]: int(r["direct_source_jpegs"]) for r in pout})
    assert counts == expected_counts, (counts - expected_counts, expected_counts - counts)
    assert len(aout) == len(seen) == EXPECTED_PAGES
    assert sum(expected_counts.values()) == EXPECTED_PAGES
    assert not ({r["viewer_key"] for r in aout} & WITHHELD)
    assert not ({r["viewer_key"] for r in aout} & set(EXPECTED_ALIAS))

    write(Path(args.processing_output), pout, pfields)
    write(Path(args.asset_output), aout, afields)
    print(
        "Built W2 FTRL inputs: "
        f"historical={EXPECTED_HISTORICAL}, admitted={EXPECTED_ADMITTED}, "
        f"canonical={len(pout)}, aliases={len(alias_map)}, withheld={len(withheld)}, pages={len(aout)}"
    )


if __name__ == "__main__":
    main()
