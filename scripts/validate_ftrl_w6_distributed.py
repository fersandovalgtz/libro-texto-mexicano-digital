#!/usr/bin/env python3
"""Validate exhaustive, unique, text-free evidence for distributed W6 FTRL."""
from __future__ import annotations

import argparse, csv, hashlib, json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_PAGES = 5258
EXPECTED_HISTORICAL = 42
EXPECTED_CANONICAL = 37
DEFAULT_SHARDS = 16
SCHEMA = "LTMD_FTRL_W6_DISTRIBUTED_GLOBAL_0.1"
SHARD_SCHEMA = "LTMD_FTRL_W6_DISTRIBUTED_SHARD_0.1"
FORBIDDEN_KEYS = {"ocr_text_raw", "search_text", "snippet", "text"}

def page_key_hash(viewer_key: str, page_index: int) -> str:
    return hashlib.sha256(f"{viewer_key}:src{page_index:04d}".encode("utf-8")).hexdigest()

def walk_no_text(value) -> None:
    if isinstance(value, dict):
        hits = FORBIDDEN_KEYS & set(value)
        if hits: raise AssertionError(f"forbidden restricted-text key(s): {sorted(hits)}")
        for child in value.values(): walk_no_text(child)
    elif isinstance(value, list):
        for child in value: walk_no_text(child)

def expected_hashes(asset_manifest: Path, processing_inventory: Path) -> set[str]:
    proc = list(csv.DictReader(processing_inventory.open(encoding="utf-8", newline="")))
    canonical = {r["viewer_key"] for r in proc if r["technical_identity_covered"] == "1" and r["is_canonical_processing_object"] == "1"}
    if len(proc) != EXPECTED_HISTORICAL or len(canonical) != EXPECTED_CANONICAL: raise SystemExit("W6 processing denominator drift")
    rows = list(csv.DictReader(asset_manifest.open(encoding="utf-8", newline="")))
    selected = [r for r in rows if r["asset_status"] == "source_jpeg" and r["viewer_key"] in canonical]
    if len(selected) != EXPECTED_PAGES: raise SystemExit(f"W6 canonical source page drift: {len(selected)}")
    hashes = {page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in selected}
    if len(hashes) != EXPECTED_PAGES: raise SystemExit("W6 canonical page identities are not unique")
    return hashes

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--evidence-root", type=Path, required=True); ap.add_argument("--asset-manifest", type=Path, required=True); ap.add_argument("--processing-inventory", type=Path, required=True); ap.add_argument("--shard-count", type=int, default=DEFAULT_SHARDS); ap.add_argument("--output", type=Path, required=True); args = ap.parse_args()
    files = sorted(args.evidence_root.rglob("w6_shard_*_evidence.json"))
    if len(files) != args.shard_count: raise SystemExit(f"expected {args.shard_count} W6 shard evidence files, found {len(files)}")
    expected = expected_hashes(args.asset_manifest, args.processing_inventory); observed = []; shard_indices = set(); run_ids = set(); source_commits = set(); sizes = Counter()
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8")); walk_no_text(d)
        if d.get("schema") != SHARD_SCHEMA or d.get("status") != "validated" or d.get("wave") != "W6": raise SystemExit(f"invalid W6 shard evidence: {p}")
        idx = int(d["shard_index"]); shard_indices.add(idx); sizes[int(d["page_records"])] += 1
        if int(d["shard_count"]) != args.shard_count: raise SystemExit("W6 shard-count drift")
        hashes = list(d["page_key_hashes"])
        if len(hashes) != int(d["page_records"]) or len(hashes) != len(set(hashes)): raise SystemExit(f"W6 shard hash cardinality failure: {p}")
        observed.extend(hashes)
        v = d["validation"]
        if v["sqlite_integrity"] != "ok" or int(v["sqlite_pages"]) != int(d["page_records"]) or int(v["fts_rows"]) != int(d["page_records"]) or int(v["qc_page_records"]) != int(d["page_records"]): raise SystemExit(f"W6 shard validation cardinality failure: {p}")
        ex = d.get("execution") or {}
        ci = ex.get("ci") or {}
        vcs = ex.get("vcs") or {}
        if ci.get("run_id"): run_ids.add(str(ci["run_id"]))
        if ci.get("sha"): source_commits.add(str(ci["sha"]))
        elif vcs.get("commit"): source_commits.add(str(vcs["commit"]))
    if shard_indices != set(range(args.shard_count)): raise SystemExit(f"W6 shard index coverage drift: {sorted(shard_indices)}")
    if len(observed) != EXPECTED_PAGES or len(set(observed)) != EXPECTED_PAGES: raise SystemExit(f"W6 global union is not unique/exhaustive: records={len(observed)} unique={len(set(observed))}")
    obs = set(observed)
    if obs != expected: raise SystemExit(f"W6 global union mismatch: missing={len(expected-obs)} extra={len(obs-expected)}")
    if sizes != Counter({329: 10, 328: 6}): raise SystemExit(f"W6 shard-size topology drift: {sizes}")
    if len(run_ids) != 1: raise SystemExit(f"W6 shards do not share one workflow run: {sorted(run_ids)}")
    if len(source_commits) != 1: raise SystemExit(f"W6 shards do not share one source commit: {sorted(source_commits)}")
    payload = {
        "schema": SCHEMA, "status": "distributed_computationally_validated", "wave": "W6", "domain": "Geografía/Atlas",
        "historical_identities": EXPECTED_HISTORICAL, "canonical_processing_objects": EXPECTED_CANONICAL, "shard_count": args.shard_count,
        "page_records": EXPECTED_PAGES, "unique_page_records": EXPECTED_PAGES, "expected_page_records": EXPECTED_PAGES,
        "shard_size_distribution": {str(k): v for k, v in sorted(sizes.items())}, "page_partition_complete": True, "page_partition_unique": True,
        "workflow_run_ids_observed": sorted(run_ids), "source_commits_observed": sorted(source_commits),
        "same_source_commit_and_workflow_run": True,
        "archival_complete": False, "text_verified": False, "semantic_ready": False,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epistemic_guards": ["distributed_computationally_validated != archival_complete", "ocr_available != text_verified", "corpus_ready != semantic_ready", "search_hit != historical_claim", "zero_hits != demonstrated_absence"],
    }
    walk_no_text(payload); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "pages": EXPECTED_PAGES, "shards": args.shard_count, "sizes": dict(sizes), "output": str(args.output)}, sort_keys=True))

if __name__ == "__main__":
    main()
