#!/usr/bin/env python3
"""Validate that distributed W1 shard evidence exhaustively covers LTMD-U1 W1."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_PAGES = 6516
EXPECTED_HISTORICAL = 40
EXPECTED_CANONICAL = 36
SCHEMA = "LTMD_FTRL_W1_DISTRIBUTED_GLOBAL_0.1"
SHARD_SCHEMA = "LTMD_FTRL_W1_DISTRIBUTED_SHARD_0.1"
FORBIDDEN_KEYS = {"ocr_text_raw", "search_text", "snippet", "text"}


def page_key_hash(viewer_key: str, page_index: int) -> str:
    raw = f"{viewer_key}:src{page_index:04d}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def walk_no_text(value) -> None:
    if isinstance(value, dict):
        hits = FORBIDDEN_KEYS & set(value)
        if hits:
            raise AssertionError(f"forbidden restricted-text key(s) in public evidence: {sorted(hits)}")
        for child in value.values():
            walk_no_text(child)
    elif isinstance(value, list):
        for child in value:
            walk_no_text(child)


def expected_hashes(asset_manifest: Path, processing_inventory: Path) -> set[str]:
    processing = list(csv.DictReader(processing_inventory.open(encoding="utf-8", newline="")))
    canonical = {
        row["viewer_key"]
        for row in processing
        if row["technical_identity_covered"] == "1" and row["is_canonical_processing_object"] == "1"
    }
    if len(processing) != EXPECTED_HISTORICAL:
        raise AssertionError(f"W1 processing denominator drift: {len(processing)}")
    if len(canonical) != EXPECTED_CANONICAL:
        raise AssertionError(f"W1 canonical processing-object drift: {len(canonical)}")
    rows = list(csv.DictReader(asset_manifest.open(encoding="utf-8", newline="")))
    selected = [r for r in rows if r["asset_status"] == "source_jpeg" and r["viewer_key"] in canonical]
    if len(selected) != EXPECTED_PAGES:
        raise AssertionError(f"W1 source page drift: {len(selected)} != {EXPECTED_PAGES}")
    hashes = {page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in selected}
    if len(hashes) != EXPECTED_PAGES:
        raise AssertionError("expected W1 page-key hashes are not unique")
    return hashes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--asset-manifest", type=Path, required=True)
    parser.add_argument("--processing-inventory", type=Path, required=True)
    parser.add_argument("--shard-count", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    paths = sorted(args.evidence_root.rglob("w1_shard_*_evidence.json"))
    if len(paths) != args.shard_count:
        raise AssertionError(f"expected {args.shard_count} shard evidence files, found {len(paths)}")

    shard_rows: list[dict] = []
    all_hashes: list[str] = []
    source_commits: set[str] = set()
    workflow_runs: set[str] = set()
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        walk_no_text(data)
        if data["schema"] != SHARD_SCHEMA or data["status"] != "validated":
            raise AssertionError(f"invalid shard evidence: {path}")
        if data["wave"] != "W1" or data["shard_count"] != args.shard_count:
            raise AssertionError(f"wrong W1 shard metadata: {path}")
        if data["validation"]["sqlite_integrity"] != "ok":
            raise AssertionError(f"SQLite integrity failed: {path}")
        pages = int(data["page_records"])
        if data["validation"]["sqlite_pages"] != pages or data["validation"]["fts_rows"] != pages:
            raise AssertionError(f"SQLite/FTS cardinality drift: {path}")
        if data["validation"]["qc_page_records"] != pages:
            raise AssertionError(f"QC cardinality drift: {path}")
        hashes = list(data["page_key_hashes"])
        if len(hashes) != pages or len(set(hashes)) != pages:
            raise AssertionError(f"page-key hash cardinality drift: {path}")
        all_hashes.extend(hashes)
        execution = data.get("execution") or {}
        ci = execution.get("ci") or {}
        vcs = execution.get("vcs") or {}
        if vcs.get("dirty_tracked_worktree") is not False:
            raise AssertionError(f"dirty or unknown tracked worktree in shard: {path}")
        if vcs.get("commit"):
            source_commits.add(vcs["commit"])
        if ci.get("run_id"):
            workflow_runs.add(str(ci["run_id"]))
        shard_rows.append(data)

    indices = [int(x["shard_index"]) for x in shard_rows]
    if sorted(indices) != list(range(args.shard_count)):
        raise AssertionError(f"shard index set is incomplete: {sorted(indices)}")
    if len(source_commits) != 1:
        raise AssertionError(f"distributed shards do not share one source commit: {sorted(source_commits)}")
    if len(workflow_runs) != 1:
        raise AssertionError(f"distributed shards do not share one workflow run: {sorted(workflow_runs)}")

    counts = Counter(int(x["page_records"]) for x in shard_rows)
    if sum(k * v for k, v in counts.items()) != EXPECTED_PAGES:
        raise AssertionError(f"distributed page total drift: {counts}")
    if len(all_hashes) != EXPECTED_PAGES or len(set(all_hashes)) != EXPECTED_PAGES:
        raise AssertionError("distributed W1 contains duplicate or missing page-key hashes")

    expected = expected_hashes(args.asset_manifest, args.processing_inventory)
    observed = set(all_hashes)
    if observed != expected:
        missing = len(expected - observed)
        extra = len(observed - expected)
        raise AssertionError(f"distributed page universe differs from W1 source manifest: missing={missing}, extra={extra}")

    output = {
        "schema": SCHEMA,
        "status": "distributed_computationally_validated",
        "wave": "W1",
        "domain": "Ciencias Naturales",
        "historical_identities": EXPECTED_HISTORICAL,
        "canonical_processing_objects": EXPECTED_CANONICAL,
        "page_records": EXPECTED_PAGES,
        "shard_count": args.shard_count,
        "shard_page_count_distribution": {str(k): v for k, v in sorted(counts.items())},
        "source_commit": next(iter(source_commits)),
        "workflow_run_id": next(iter(workflow_runs)),
        "page_partition_complete": True,
        "page_partition_unique": True,
        "all_shard_sqlite_integrity_ok": True,
        "all_shard_fts_cardinality_ok": True,
        "all_shard_qc_cardinality_ok": True,
        "restricted_outputs_publicly_uploaded_plaintext": False,
        "archival_complete": False,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epistemic_guards": [
            "distributed_computationally_validated != archival_complete",
            "ocr_available != text_verified",
            "corpus_ready != semantic_ready",
            "search_hit != historical_claim",
        ],
    }
    walk_no_text(output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
