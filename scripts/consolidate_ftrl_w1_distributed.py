#!/usr/bin/env python3
"""Privately consolidate decrypted distributed W1 FTRL shards into canonical full products.

This script contains no credentials and is safe to version publicly. It must be run
only where the encrypted shard handoffs have already been decrypted under the
project's private preservation controls. The produced OCR JSONL/SQLite remain
restricted and must not be committed or uploaded plaintext to public Actions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_PAGES = 6516
EXPECTED_SHARDS = 16
SCHEMA = "LTMD_FTRL_W1_PRIVATE_CONSOLIDATION_0.1"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def descriptor(path: Path) -> dict:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def page_key_hash(viewer_key: str, page_index: int) -> str:
    return hashlib.sha256(f"{viewer_key}:src{page_index:04d}".encode("utf-8")).hexdigest()


def expected_page_hashes(asset_manifest: Path, processing_inventory: Path) -> set[str]:
    proc = list(csv.DictReader(processing_inventory.open(encoding="utf-8", newline="")))
    canonical = {
        r["viewer_key"] for r in proc
        if r["technical_identity_covered"] == "1" and r["is_canonical_processing_object"] == "1"
    }
    rows = list(csv.DictReader(asset_manifest.open(encoding="utf-8", newline="")))
    selected = [r for r in rows if r["asset_status"] == "source_jpeg" and r["viewer_key"] in canonical]
    if len(selected) != EXPECTED_PAGES:
        raise SystemExit(f"canonical source page cardinality drift: {len(selected)}")
    hashes = {page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in selected}
    if len(hashes) != EXPECTED_PAGES:
        raise SystemExit("canonical source page identities are not unique")
    return hashes


def load_shard_records(root: Path, shard_count: int) -> list[dict]:
    paths = sorted(root.rglob("w1_shard_*_of_16_page_ocr.jsonl"))
    if len(paths) != shard_count:
        raise SystemExit(f"expected {shard_count} decrypted shard JSONL files, found {len(paths)}")
    records: list[dict] = []
    page_ids: set[str] = set()
    page_keys: set[tuple[str, int]] = set()
    for path in paths:
        with path.open(encoding="utf-8") as fh:
            for line_number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                page_id = str(row["page_id"])
                key = (str(row["viewer_key"]), int(row["page_index"]))
                if page_id in page_ids or key in page_keys:
                    raise SystemExit(f"duplicate page across decrypted shards: {page_id}")
                if row.get("wave") != "W1":
                    raise SystemExit(f"non-W1 record in {path}:{line_number}")
                page_ids.add(page_id)
                page_keys.add(key)
                records.append(row)
    if len(records) != EXPECTED_PAGES:
        raise SystemExit(f"decrypted distributed page total drift: {len(records)} != {EXPECTED_PAGES}")
    records.sort(key=lambda r: (int(r["catalog_generation"]), int(r["grade_code"]), str(r["viewer_key"]), int(r["page_index"])))
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-root", type=Path, required=True)
    parser.add_argument("--asset-manifest", type=Path, required=True)
    parser.add_argument("--processing-inventory", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--distributed-run-id", required=True)
    parser.add_argument("--distributed-source-commit", required=True)
    parser.add_argument("--shard-count", type=int, default=EXPECTED_SHARDS)
    args = parser.parse_args()

    records = load_shard_records(args.shard_root, args.shard_count)
    observed_hashes = {page_key_hash(str(r["viewer_key"]), int(r["page_index"])) for r in records}
    expected_hashes = expected_page_hashes(args.asset_manifest, args.processing_inventory)
    if observed_hashes != expected_hashes:
        raise SystemExit(f"private consolidated page universe mismatch: missing={len(expected_hashes-observed_hashes)}, extra={len(observed_hashes-expected_hashes)}")

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    jsonl = out / "ltmd_u1_w1_full_page_ocr.jsonl"
    db = out / "ltmd_u1_w1_full_ocr_search.sqlite"
    qc_queue = out / "ltmd_u1_w1_full_qc_queue.json"
    qc_summary = out / "ltmd_u1_w1_full_qc_summary.json"
    run_manifest = out / "ltmd_u1_w1_full_run_manifest.json"
    evidence = out / "ltmd_u1_w1_private_consolidation_evidence.json"

    with jsonl.open("w", encoding="utf-8", newline="\n") as fh:
        for row in records:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    run([
        sys.executable, "scripts/build_search_index.py",
        "--input", str(jsonl),
        "--processing-inventory", str(args.processing_inventory),
        "--output", str(db),
    ])
    run([sys.executable, "scripts/validate_ocr_corpus.py", "--input", str(jsonl), "--db", str(db)])
    run([
        sys.executable, "scripts/summarize_ftrl_run.py",
        "--input", str(jsonl),
        "--db", str(db),
        "--asset-manifest", str(args.asset_manifest),
        "--processing-inventory", str(args.processing_inventory),
        "--label", "full_distributed_consolidated",
        "--output", str(run_manifest),
    ])
    run([
        sys.executable, "scripts/build_ftrl_qc_queue.py",
        "--input", str(jsonl),
        "--queue-output", str(qc_queue),
        "--summary-output", str(qc_summary),
    ])

    rm = json.loads(run_manifest.read_text(encoding="utf-8"))
    qc = json.loads(qc_summary.read_text(encoding="utf-8"))
    if rm["status"] != "validated" or rm["corpus"]["page_records"] != EXPECTED_PAGES:
        raise SystemExit("private consolidated run manifest failed")
    if rm["database"]["page_rows"] != EXPECTED_PAGES or rm["database"]["fts_rows"] != EXPECTED_PAGES:
        raise SystemExit("private consolidated SQLite cardinality failed")
    if rm["database"]["sqlite_integrity"] != "ok" or qc["page_records"] != EXPECTED_PAGES:
        raise SystemExit("private consolidated integrity/QC failed")
    if rm["database"]["historical_identities"] != 40:
        raise SystemExit(f"private consolidated historical identity drift: {rm['database']['historical_identities']}")

    payload = {
        "schema": SCHEMA,
        "status": "private_consolidation_validated",
        "wave": "W1",
        "domain": "Ciencias Naturales",
        "distributed_run_id": str(args.distributed_run_id),
        "distributed_source_commit": args.distributed_source_commit,
        "shard_count": args.shard_count,
        "historical_identities": 40,
        "canonical_processing_objects": 36,
        "page_records": EXPECTED_PAGES,
        "page_partition_complete": True,
        "page_partition_unique": True,
        "sqlite_integrity": "ok",
        "fts_rows": EXPECTED_PAGES,
        "products": [descriptor(jsonl), descriptor(db), descriptor(qc_queue), descriptor(qc_summary), descriptor(run_manifest)],
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "archival_complete": False,
        "epistemic_guards": [
            "private_consolidation_validated != archival_complete",
            "ocr_available != text_verified",
            "corpus_ready != semantic_ready",
        ],
    }
    evidence.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "page_records": EXPECTED_PAGES, "evidence": str(evidence)}, sort_keys=True))


if __name__ == "__main__":
    main()
