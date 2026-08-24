#!/usr/bin/env python3
"""Fail-closed preflight for LTMD-U1 W1 Ciencias Naturales FTRL.

The gate reconciles four documentary layers without downloading source assets or
reading OCR text:
1) the W1 family readiness register;
2) the direct SHA-256 manifest summary;
3) the audited CN4/CN6 expansion manifest;
4) the versioned CN5 pilot SHA-256 page manifests, cross-checked against prior
   OCR source-byte metrics and the preserved CI provenance record.

The output is text-free. A technically audited OCR does not substitute for a
page-level cryptographic source anchor.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

SCHEMA = "LTMD_FTRL_W1_PREFLIGHT_0.2"
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


def canonical_json_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_csv_sha256(rows: list[dict[str, str]]) -> str:
    return canonical_json_sha256(rows)


def load_pilot_anchor(anchor_dir: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    if not anchor_dir.exists():
        return [], {}
    rows: list[dict[str, str]] = []
    file_hashes: dict[str, str] = {}
    expected_fields = {"viewer_page", "source_image_index", "byte_size", "sha256"}
    for path in sorted(anchor_dir.glob("*.csv")):
        stem = path.stem
        bid = stem.rsplit("-part", 1)[0] if "-part" in stem else stem
        if bid not in PILOT_BOOKS:
            raise AssertionError(f"unexpected pilot anchor file: {path.name}")
        loaded = read_csv(path)
        file_hashes[path.name] = canonical_csv_sha256(loaded)
        if loaded:
            assert set(loaded[0]) == expected_fields, f"pilot compact schema drift: {path.name}"
        for row in loaded:
            viewer_page = int(row["viewer_page"])
            enriched = dict(row)
            enriched["book_id"] = bid
            enriched["page_id"] = f"{bid}-VP{viewer_page:03d}"
            enriched["asset_status"] = "source_jpeg"
            rows.append(enriched)
    return rows, file_hashes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readiness", default="data/catalog/ciencias_naturales_family_asset_readiness.csv")
    ap.add_argument("--direct-summary", default="data/catalog/ciencias_naturales_pending_page_manifest_summary.csv")
    ap.add_argument("--cn46-summary", default="data/expansion/cn46_page_manifest_summary.csv")
    ap.add_argument("--pilot-inventory", default="data/book_inventory.csv")
    ap.add_argument("--pilot-sha-dir", default="data/catalog/cn5_pilot_sha")
    ap.add_argument("--pilot-sha-summary", default="data/catalog/cn5_pilot_sha_manifest_summary.json")
    ap.add_argument("--pilot-sha-provenance", default="data/catalog/cn5_pilot_sha_provenance.json")
    ap.add_argument("--pilot-ocr-metrics", default="data/derived/ocr_page_metrics.csv")
    ap.add_argument("--output", default="local/ftrl/ltmd_u1_w1_preflight.json")
    ap.add_argument("--require-cryptographic-ready", action="store_true")
    args = ap.parse_args()

    readiness = read_csv(Path(args.readiness))
    direct = read_csv(Path(args.direct_summary))
    cn46 = read_csv(Path(args.cn46_summary))
    pilot_inventory = read_csv(Path(args.pilot_inventory))
    pilot_rows, pilot_file_hashes = load_pilot_anchor(Path(args.pilot_sha_dir))

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
    pilot_inventory_by_id = {r["book_id"]: r for r in pilot_inventory}
    assert len(pilot_inventory_by_id) == len(pilot_inventory), "duplicate book_id in pilot inventory"

    pilot_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    pilot_byte_matches = 0
    pilot_anchor_files_validated = 0
    pilot_anchor_summary_validated = False

    if pilot_rows:
        assert {r["book_id"] for r in pilot_rows} == PILOT_BOOKS, "pilot SHA manifest book set drift"
        assert len(pilot_rows) == 759, len(pilot_rows)
        assert len({r["page_id"] for r in pilot_rows}) == 759, "duplicate pilot page_id"
        assert all(r["asset_status"] == "source_jpeg" for r in pilot_rows), "non-JPEG pilot row"
        assert all(len(r["sha256"]) == 64 and set(r["sha256"]) <= set("0123456789abcdef") for r in pilot_rows), "invalid pilot SHA-256"
        for row in pilot_rows:
            pilot_by_id[row["book_id"]].append(row)

        expected_files = {
            "LTMD-CN5-G1972-part01.csv", "LTMD-CN5-G1972-part02.csv", "LTMD-CN5-G1972-part03.csv",
            "LTMD-CN5-G1988-part01.csv", "LTMD-CN5-G1988-part02.csv",
            "LTMD-CN5-G1993-part01.csv", "LTMD-CN5-G1993-part02.csv",
            "LTMD-CN5-G2014-part01.csv", "LTMD-CN5-G2014-part02.csv",
        }
        assert set(pilot_file_hashes) == expected_files, f"pilot anchor file set drift: {sorted(pilot_file_hashes)}"

        summary_path = Path(args.pilot_sha_summary)
        provenance_path = Path(args.pilot_sha_provenance)
        assert summary_path.exists(), "pilot SHA summary missing"
        assert provenance_path.exists(), "pilot SHA provenance missing"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        assert summary["schema"] == "LTMD_CN5_PILOT_SHA_ANCHOR_0.1"
        assert summary["status"] == "validated"
        assert summary["books"] == 4
        assert summary["source_jpegs"] == 759
        assert summary["prior_ocr_metric_byte_matches"] == 759
        assert summary["source_byte_drift"] == 0
        assert provenance["schema"] == "LTMD_CN5_PILOT_SHA_PROVENANCE_0.1"
        assert provenance["publication_scope"] == "metadata_and_hashes_only_no_source_bytes_no_ocr_text"
        assert provenance["summary_canonical_sha256"] == canonical_json_sha256(summary), "pilot summary canonical hash drift"
        assert provenance["compact_manifest_canonical_sha256"] == pilot_file_hashes, "pilot compact-manifest canonical hash drift"
        pilot_anchor_files_validated = len(pilot_file_hashes)
        pilot_anchor_summary_validated = True

        metrics = read_csv(Path(args.pilot_ocr_metrics))
        metric_bytes = {
            r["page_id"]: int(r["source_bytes"])
            for r in metrics
            if r["book_id"] in PILOT_BOOKS and r["asset_status"] == "source_jpeg"
        }
        assert len(metric_bytes) == 759, len(metric_bytes)
        for row in pilot_rows:
            pid = row["page_id"]
            assert pid in metric_bytes, f"pilot page absent from prior OCR metrics: {pid}"
            assert int(row["byte_size"]) == metric_bytes[pid], f"pilot source-byte drift: {pid}"
            pilot_byte_matches += 1

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
        if bid in PILOT_BOOKS:
            if bid in pilot_by_id:
                candidates.append("pilot_sha256_manifest")
            elif bid in pilot_inventory_by_id:
                candidates.append("pilot_reconstructible_unanchored")

        if not candidates:
            missing_layer.append(bid)
            continue
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
        elif candidates[0] == "pilot_sha256_manifest":
            rows = pilot_by_id[bid]
            assert len(rows) == resolved, f"pilot page mismatch: {bid}"
            assert len({r["page_id"] for r in rows}) == resolved, f"pilot page-id mismatch: {bid}"
        else:
            row = pilot_inventory_by_id[bid]
            assert as_int(row, "source_asset_count") == resolved, f"pilot asset mismatch: {bid}"

        if strategy in {"direct_sha256_manifest", "direct_manifest_plus_focused_gap_audit"}:
            assert candidates[0] == "direct_sha256_manifest", f"strategy/layer mismatch: {bid}"
        elif strategy == "existing_pilot_or_cn46_manifest":
            assert candidates[0] in {
                "cn46_sha256_manifest",
                "pilot_sha256_manifest",
                "pilot_reconstructible_unanchored",
            }, f"strategy/layer mismatch: {bid}"
        else:
            raise AssertionError(f"unexpected canonical strategy: {bid}: {strategy}")

    assert not missing_layer, f"canonical objects without documentary layer: {missing_layer}"
    assert not overlaps, f"overlapping canonical layers: {overlaps}"

    cn46_outside = sorted(set(cn46_by_id) - historical)
    page_count = sum(as_int(r_by_id[bid], "resolved_source_assets") for bid in canonical)
    internal_holes = sum(as_int(r_by_id[bid], "internal_unserved_positions") for bid in canonical)
    terminal_synthetic = sum(as_int(r_by_id[bid], "terminal_synthetic") for bid in canonical)
    unanchored = sorted(bid for bid, layer in coverage.items() if layer == "pilot_reconstructible_unanchored")

    assert len(historical) == 37, len(historical)
    assert len(aliases) == 4, len(aliases)
    assert len(canonical) == 33, len(canonical)
    assert page_count == 5926, page_count
    assert internal_holes == 3, internal_holes
    if pilot_rows:
        assert len(pilot_by_id) == 4
        assert sum(len(v) for v in pilot_by_id.values()) == 759
        assert pilot_byte_matches == 759
        assert pilot_anchor_files_validated == 9
        assert pilot_anchor_summary_validated

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
        "pilot_sha256_objects": len(pilot_by_id),
        "pilot_sha256_pages": sum(len(v) for v in pilot_by_id.values()),
        "pilot_prior_ocr_byte_matches": pilot_byte_matches,
        "pilot_anchor_files_validated": pilot_anchor_files_validated,
        "pilot_anchor_summary_validated": pilot_anchor_summary_validated,
        "unanchored_pilot_objects": unanchored,
        "cn46_objects_outside_w1_readiness": cn46_outside,
        "interpretation": "Cryptographic readiness validates source identity and routing only; it does not make OCR text verified or the wave semantic-ready.",
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.require_cryptographic_ready and status != "ready":
        raise SystemExit("W1 is not cryptographically ready for full FTRL")


if __name__ == "__main__":
    main()
