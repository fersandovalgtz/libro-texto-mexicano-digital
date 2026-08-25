#!/usr/bin/env python3
"""Validate exhaustive, unique, text-free evidence for distributed W3 FTRL."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_PAGES = 20765
EXPECTED_HISTORICAL = 130
EXPECTED_CANONICAL = 114
DEFAULT_SHARDS = 52
SCHEMA = "LTMD_FTRL_W3_DISTRIBUTED_GLOBAL_0.1"
SHARD_SCHEMA = "LTMD_FTRL_W3_DISTRIBUTED_SHARD_0.1"
FORBIDDEN_KEYS = {"ocr_text_raw", "search_text", "snippet", "text"}


def page_key_hash(viewer_key: str, page_index: int) -> str:
    return hashlib.sha256(f"{viewer_key}:src{page_index:04d}".encode("utf-8")).hexdigest()


def walk_no_text(value) -> None:
    if isinstance(value, dict):
        hits = FORBIDDEN_KEYS & set(value)
        if hits:
            raise AssertionError(f"forbidden restricted-text key(s): {sorted(hits)}")
        for child in value.values():
            walk_no_text(child)
    elif isinstance(value, list):
        for child in value:
            walk_no_text(child)


def expected_hashes(asset_manifest: Path, processing_inventory: Path) -> set[str]:
    processing = list(csv.DictReader(processing_inventory.open(encoding="utf-8", newline="")))
    canonical = {r["viewer_key"] for r in processing if r["technical_identity_covered"] == "1" and r["is_canonical_processing_object"] == "1"}
    if len(processing) != EXPECTED_HISTORICAL or len(canonical) != EXPECTED_CANONICAL:
        raise AssertionError("W3 processing denominator drift")
    rows = list(csv.DictReader(asset_manifest.open(encoding="utf-8", newline="")))
    selected = [r for r in rows if r["asset_status"] == "source_jpeg" and r["viewer_key"] in canonical]
    if len(selected) != EXPECTED_PAGES:
        raise AssertionError(f"W3 source page drift: {len(selected)}")
    hashes = {page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in selected}
    if len(hashes) != EXPECTED_PAGES:
        raise AssertionError("expected W3 page identities are not unique")
    return hashes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--asset-manifest", type=Path, required=True)
    ap.add_argument("--processing-inventory", type=Path, required=True)
    ap.add_argument("--shard-count", type=int, default=DEFAULT_SHARDS)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    paths = sorted(args.evidence_root.rglob("w3_shard_*_evidence.json"))
    if len(paths) != args.shard_count:
        raise AssertionError(f"expected {args.shard_count} shard evidence files, found {len(paths)}")

    shard_rows, all_hashes = [], []
    commits, runs = set(), set()
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        walk_no_text(data)
        if data["schema"] != SHARD_SCHEMA or data["status"] != "validated" or data["wave"] != "W3" or data["shard_count"] != args.shard_count:
            raise AssertionError(f"invalid shard evidence: {path}")
        pages = int(data["page_records"])
        v = data["validation"]
        if v["sqlite_integrity"] != "ok" or v["sqlite_pages"] != pages or v["fts_rows"] != pages or v["qc_page_records"] != pages:
            raise AssertionError(f"W3 shard validation/cardinality drift: {path}")
        hashes = list(data["page_key_hashes"])
        if len(hashes) != pages or len(set(hashes)) != pages:
            raise AssertionError(f"W3 shard page-key drift: {path}")
        all_hashes.extend(hashes)
        execution = data.get("execution") or {}
        vcs, ci = execution.get("vcs") or {}, execution.get("ci") or {}
        if vcs.get("dirty_tracked_worktree") is not False:
            raise AssertionError(f"dirty tracked worktree: {path}")
        if vcs.get("commit"):
            commits.add(vcs["commit"])
        if ci.get("run_id"):
            runs.add(str(ci["run_id"]))
        shard_rows.append(data)

    indices = sorted(int(x["shard_index"]) for x in shard_rows)
    if indices != list(range(args.shard_count)):
        raise AssertionError(f"incomplete W3 shard index set: {indices}")
    if len(commits) != 1 or len(runs) != 1:
        raise AssertionError(f"W3 shards do not share one commit/run: commits={sorted(commits)}, runs={sorted(runs)}")

    counts = Counter(int(x["page_records"]) for x in shard_rows)
    if sum(k * v for k, v in counts.items()) != EXPECTED_PAGES:
        raise AssertionError(f"W3 distributed page total drift: {counts}")
    if len(all_hashes) != EXPECTED_PAGES or len(set(all_hashes)) != EXPECTED_PAGES:
        raise AssertionError("W3 distributed union has duplicate or missing page hashes")
    expected = expected_hashes(args.asset_manifest, args.processing_inventory)
    observed = set(all_hashes)
    if observed != expected:
        raise AssertionError(f"W3 union differs from canonical manifest: missing={len(expected-observed)}, extra={len(observed-expected)}")

    output = {
        "schema": SCHEMA, "status": "distributed_computationally_validated", "wave": "W3", "domain": "Español/Lengua",
        "historical_identities": EXPECTED_HISTORICAL, "canonical_processing_objects": EXPECTED_CANONICAL,
        "page_records": EXPECTED_PAGES, "shard_count": args.shard_count,
        "shard_page_count_distribution": {str(k): v for k, v in sorted(counts.items())},
        "source_commit": next(iter(commits)), "workflow_run_id": next(iter(runs)),
        "page_partition_complete": True, "page_partition_unique": True,
        "all_shard_sqlite_integrity_ok": True, "all_shard_fts_cardinality_ok": True, "all_shard_qc_cardinality_ok": True,
        "restricted_outputs_publicly_uploaded_plaintext": False, "archival_complete": False,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epistemic_guards": ["distributed_computationally_validated != archival_complete", "ocr_available != text_verified", "corpus_ready != semantic_ready", "search_hit != historical_claim"],
    }
    walk_no_text(output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
