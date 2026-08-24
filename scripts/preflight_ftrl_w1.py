#!/usr/bin/env python3
"""Fail-closed preflight for LTMD-U1 W1 Ciencias Naturales FTRL.

This script reconciles the three documentary layers that currently describe W1:
1) the family readiness register;
2) the direct SHA-256 manifest summary;
3) the CN4/CN6 audited expansion manifest;
4) the original CN5 pilot inventory, whose page-level SHA manifest is not
   currently versioned in main.

It does not download source assets or OCR text. Its output is text-free.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

SCHEMA = "LTMD_FTRL_W1_PREFLIGHT_0.1"
PILOT_BOOKS = {
    "LTMD-CN5-G1972",
    "LTMD-CN5-G1988",
    "LTMD-CN5-G1993",
    "LTMD-CN5-G2014",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def as_int(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value == "":
        raise AssertionError(f"missing integer field {key}: {row}")
    return int(value)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readiness", default="data/catalog/ciencias_naturales_family_asset_readiness.csv")
    ap.add_argument("--direct-summary", default="data/catalog/ciencias_naturales_pending_page_manifest_summary.csv")
    ap.add_argument("--cn46-summary", default="data/expansion/cn46_page_manifest_summary.csv")
    ap.add_argument("--pilot-inventory", default="data/book_inventory.csv")
    ap.add_argument("--output", default="local/ftrl/ltmd_u1_w1_preflight.json")
    ap.add_argument("--require-cryptographic-ready", action="store_true")
    args = ap.parse_args()

    readiness = read_csv(Path(args.readiness))
    direct = read_csv(Path(args.direct_summary))
    cn46 = read_csv(Path(args.cn46_summary))
    pilot = read_csv(Path(args.pilot_inventory))

    r_by_id = {r["book_id"]: r for r in readiness}
    assert len(r_by_id) == len(readiness), "duplicate book_id in readiness"

    historical = set(r_by_id)
    aliases = {bid: r["alias_to_book_id"] for bid, r in r_by_id.items() if r["alias_to_book_id"]}
    canonical = historical - set(aliases)

    for alias, target in aliases.items():
        assert target in historical, f"alias target absent: {alias} -> {target}"
        assert not r_by_id[target]["alias_to_book_id"], f"alias target is itself alias: {target}"
        assert r_by_id[alias]["asset_readiness"] == "full_alias_same_bytes", alias
        assert as_int(r_by_id[alias], "resolved_source_assets") == as_int(r_by_id[target], "resolved_source_assets"), alias

    direct_by_id = {r["book_id"]: r for r in direct}
    assert len(direct_by_id) == len(direct), "duplicate book_id in direct summary"
    cn46_by_id = {r["book_id"]: r for r in cn46}
    assert len(cn46_by_id) == len(cn46), "duplicate book_id in CN46 summary"
    pilot_by_id = {r["book_id"]: r for r in pilot}
    assert len(pilot_by_id) == len(pilot), "duplicate book_id in pilot inventory"

    coverage: dict[str, str] = {}
    missing_layer: list[str] = []
    overlaps: dict[str, list[str]] = {}

    for bid in sorted(canonical):
        strategy = r_by_id[bid]["asset_strategy"]
        candidates: list[str] = []
        if bid in direct_by_id and as_int(direct_by_id[bid], "source_jpegs") > 0:
            candidates.append("direct_sha256_manifest")
        if bid in cn46_by_id:
            candidates.append("cn46_sha256_manifest")
        if bid in PILOT_BOOKS and bid in pilot_by_id:
            candidates.append("pilot_reconstructible_unanchored")

        if not candidates:
            missing_layer.append(bid)
            continue
        # Pilot CN5 objects are intentionally distinct from CN46; if a future
        # manifest creates overlap this gate must stop until provenance is resolved.
        if len(candidates) > 1:
            overlaps[bid] = candidates
            continue
        coverage[bid] = candidates[0]

        resolved = as_int(r_by_id[bid], "resolved_source_assets")
        if candidates[0] == "direct_sha256_manifest":
            row = direct_by_id[bid]
            assert as_int(row, "source_jpegs") == resolved, f"direct page mismatch: {bid}"
            assert as_int(row, "unique_source_hashes") == resolved, f"direct hash mismatch: {bid}"
        elif candidates[0] == "cn46_sha256_manifest":
            row = cn46_by_id[bid]
            assert as_int(row, "source_jpegs") == resolved, f"CN46 page mismatch: {bid}"
            assert as_int(row, "unique_source_hashes") == resolved, f"CN46 hash mismatch: {bid}"
        else:
            row = pilot_by_id[bid]
            assert as_int(row, "source_asset_count") == resolved, f"pilot asset mismatch: {bid}"

        # Strategy declarations must agree with the physical layer actually found.
        if strategy in {"direct_sha256_manifest", "direct_manifest_plus_focused_gap_audit"}:
            assert candidates[0] == "direct_sha256_manifest", f"strategy/layer mismatch: {bid}"
        elif strategy == "existing_pilot_or_cn46_manifest":
            assert candidates[0] in {"cn46_sha256_manifest", "pilot_reconstructible_unanchored"}, f"strategy/layer mismatch: {bid}"
        else:
            raise AssertionError(f"unexpected canonical strategy: {bid}: {strategy}")

    assert not missing_layer, f"canonical objects without documentary layer: {missing_layer}"
    assert not overlaps, f"overlapping canonical layers: {overlaps}"

    # CN46 contains one documented object outside the W1 readiness universe;
    # its existence must never expand W1 implicitly.
    cn46_outside = sorted(set(cn46_by_id) - historical)

    page_count = sum(as_int(r_by_id[bid], "resolved_source_assets") for bid in canonical)
    internal_holes = sum(as_int(r_by_id[bid], "internal_unserved_positions") for bid in canonical)
    terminal_synthetic = sum(as_int(r_by_id[bid], "terminal_synthetic") for bid in canonical)
    unanchored = sorted(bid for bid, layer in coverage.items() if layer == "pilot_reconstructible_unanchored")

    # Frozen W1 reconciliation gates. These are derived from the versioned
    # readiness register, not from OCR output.
    assert len(historical) == 37, len(historical)
    assert len(aliases) == 4, len(aliases)
    assert len(canonical) == 33, len(canonical)
    assert page_count == 5926, page_count
    assert internal_holes == 3, internal_holes
    assert unanchored == sorted(PILOT_BOOKS), unanchored

    status = "ready" if not unanchored else "blocked_missing_versioned_pilot_sha_manifest"
    result = {
        "schema": SCHEMA,
        "wave": "W1",
        "domain": "Ciencias Naturales",
        "status": status,
        "historical_identities": len(historical),
        "canonical_processing_objects": len(canonical),
        "byte_identical_aliases": len(aliases),
        "source_admitted_jpegs": page_count,
        "internal_unserved_positions": internal_holes,
        "terminal_synthetic_positions": terminal_synthetic,
        "canonical_layer_counts": {
            layer: sum(v == layer for v in coverage.values())
            for layer in sorted(set(coverage.values()))
        },
        "unanchored_pilot_objects": unanchored,
        "cn46_objects_outside_w1_readiness": cn46_outside,
        "interpretation": "A technically audited prior OCR does not substitute for a versioned page-level SHA-256 source manifest required by FTRL.",
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.require_cryptographic_ready and unanchored:
        raise SystemExit("W1 is not cryptographically ready for full FTRL: version the four pilot CN5 SHA-256 page manifests first")


if __name__ == "__main__":
    main()
