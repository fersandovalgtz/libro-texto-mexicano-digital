#!/usr/bin/env python3
"""Validate exhaustive, unique, text-free evidence for distributed W4 FTRL."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_PAGES = 2414
EXPECTED_HISTORICAL = 14
EXPECTED_CANONICAL = 14
DEFAULT_SHARDS = 8
SCHEMA = "LTMD_FTRL_W4_DISTRIBUTED_GLOBAL_0.1"
SHARD_SCHEMA = "LTMD_FTRL_W4_DISTRIBUTED_SHARD_0.1"
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
    proc = list(csv.DictReader(processing_inventory.open(encoding="utf-8", newline="")))
    canonical = {r["viewer_key"] for r in proc if r["technical_identity_covered"] == "1" and r["is_canonical_processing_object"] == "1"}
    if len(proc) != EXPECTED_HISTORICAL or len(canonical) != EXPECTED_CANONICAL:
        raise SystemExit("W4 processing denominator drift")
    rows = list(csv.DictReader(asset_manifest.open(encoding="utf-8", newline="")))
    selected = [r for r in rows if r["asset_status"] == "source_jpeg" and r["viewer_key"] in canonical]
    if len(selected) != EXPECTED_PAGES:
        raise SystemExit(f"W4 canonical source page drift: {len(selected)}")
    hashes = {page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in selected}
    if len(hashes) != EXPECTED_PAGES:
        raise SystemExit("W4 canonical page identities are not unique")
    return hashes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--asset-manifest", type=Path, required=True)
    ap.add_argument("--processing-inventory", type=Path, required=True)
    ap.add_argument("--shard-count", type=int, default=DEFAULT_SHARDS)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    files = sorted(args.evidence_root.rglob("w4_shard_*_evidence.json"))
    if len(files) != args.shard_count:
        raise SystemExit(f"expected {args.shard_count} W4 shard evidence files, found {len(files)}")
    expected = expected_hashes(args.asset_manifest, args.processing_inventory)
    observed: list[str] = []
    shard_indices = set()
    run_ids = set()
    source_commits = set()
    sizes: Counter[int] = Counter()

    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        walk_no_text(data)
        if data.get("schema") != SHARD_SCHEMA or data.get("status") != "validated" or data.get("wave") != "W4":
            raise SystemExit(f"invalid W4 shard evidence: {path}")
        idx = int(data["shard_index"])
        shard_indices.add(idx)
        sizes[int(data["page_records"])] += 1
        if int(data["shard_count"]) != args.shard_count:
            raise SystemExit("W4 shard-count drift")
        hashes = list(data["page_key_hashes"])
        if len(hashes) != int(data["page_records"]) or len(hashes) != len(set(hashes)):
            raise SystemExit(f"W4 shard hash cardinality failure: {path}")
        observed.extend(hashes)
        validation = data["validation"]
        if validation["sqlite_integrity"] != "ok" or int(validation["sqlite_pages"]) != int(data["page_records"]) or int(validation["fts_rows"]) != int(data["page_records"]) or int(validation["qc_page_records"]) != int(data["page_records"]):
            raise SystemExit(f"W4 shard validation cardinality failure: {path}")
        execution = data.get("execution") or {}
        ci = execution.get("ci") or {}
        vcs = execution.get("vcs") or {}
        if ci.get("run_id"):
            run_ids.add(str(ci["run_id"]))
        if ci.get("sha"):
            source_commits.add(str(ci["sha"]))
        elif vcs.get("commit"):
            source_commits.add(str(vcs["commit"]))

    if shard_indices != set(range(args.shard_count)):
        raise SystemExit(f"W4 shard index coverage drift: {sorted(shard_indices)}")
    if len(observed) != EXPECTED_PAGES or len(set(observed)) != EXPECTED_PAGES:
        raise SystemExit(f"W4 global union is not unique/exhaustive: records={len(observed)} unique={len(set(observed))}")
    observed_set = set(observed)
    if observed_set != expected:
        raise SystemExit(f"W4 global union mismatch: missing={len(expected-observed_set)} extra={len(observed_set-expected)}")
    if sizes != Counter({302: 6, 301: 2}):
        raise SystemExit(f"W4 shard-size topology drift: {sizes}")
    if len(run_ids) != 1:
        raise SystemExit(f"W4 shards do not share one workflow run: {sorted(run_ids)}")
    if len(source_commits) != 1:
        raise SystemExit(f"W4 shards do not share one source commit: {sorted(source_commits)}")

    payload = {
        "schema": SCHEMA,
        "status": "distributed_computationally_validated",
        "wave": "W4",
        "domain": "Ciencias Sociales",
        "historical_identities": EXPECTED_HISTORICAL,
        "canonical_processing_objects": EXPECTED_CANONICAL,
        "shard_count": args.shard_count,
        "page_records": EXPECTED_PAGES,
        "unique_page_records": EXPECTED_PAGES,
        "expected_page_records": EXPECTED_PAGES,
        "shard_size_distribution": {str(k): v for k, v in sorted(sizes.items())},
        "page_partition_complete": True,
        "page_partition_unique": True,
        "workflow_run_ids_observed": sorted(run_ids),
        "source_commits_observed": sorted(source_commits),
        "same_source_commit_and_workflow_run": True,
        "archival_complete": False,
        "text_verified": False,
        "semantic_ready": False,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epistemic_guards": ["distributed_computationally_validated != archival_complete", "ocr_available != text_verified", "corpus_ready != semantic_ready", "search_hit != historical_claim", "zero_hits != demonstrated_absence"],
    }
    walk_no_text(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "pages": EXPECTED_PAGES, "shards": args.shard_count, "sizes": dict(sizes), "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
