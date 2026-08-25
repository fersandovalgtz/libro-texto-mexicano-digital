#!/usr/bin/env python3
"""Run one deterministic W1 FTRL shard without publishing restricted OCR text.

This runner elevates W1 sharding to the workflow/job level so that the exhaustive
6,516-page corpus is not coupled to GitHub-hosted runners' per-job time limit.
Each shard is independently OCR'd, indexed, validated, QC'd, and summarized.
Restricted bytes remain under local/ for encryption by the workflow.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_W1_SOURCE_PAGES = 6516
SCHEMA = "LTMD_FTRL_W1_DISTRIBUTED_SHARD_0.1"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def page_key_hash(viewer_key: str, page_index: int) -> str:
    raw = f"{viewer_key}:src{page_index:04d}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit(f"refusing to write empty shard manifest: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sorted_source_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        rows,
        key=lambda r: (
            int(r["catalog_generation"]),
            int(r["grade_code"]),
            r["viewer_key"],
            int(r["source_image_index"]),
        ),
    )


def balanced_slice(rows: list[dict[str, str]], shard_index: int, shard_count: int) -> list[dict[str, str]]:
    if shard_count < 1:
        raise SystemExit("--shard-count must be >= 1")
    if not 0 <= shard_index < shard_count:
        raise SystemExit("--shard-index must satisfy 0 <= index < count")
    base, remainder = divmod(len(rows), shard_count)
    start = shard_index * base + min(shard_index, remainder)
    size = base + (1 if shard_index < remainder else 0)
    return rows[start : start + size]


def require_environment() -> None:
    if shutil.which("tesseract") is None:
        raise SystemExit("Tesseract is required")
    langs = subprocess.run(
        ["tesseract", "--list-langs"], check=True, capture_output=True, text=True
    ).stdout.splitlines()
    if "spa" not in {x.strip() for x in langs}:
        raise SystemExit("Spanish Tesseract language data is required")
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE VIRTUAL TABLE smoke_fts USING fts5(text)")
    finally:
        conn.close()


def jsonl_actual_hashes(path: Path) -> tuple[list[str], int]:
    hashes: list[str] = []
    count = 0
    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("wave") != "W1":
                raise SystemExit(f"non-W1 record at {path}:{line_number}")
            hashes.append(page_key_hash(str(row["viewer_key"]), int(row["page_index"])))
            count += 1
    return sorted(hashes), count


def descriptor(path: Path) -> dict:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-count", type=int, default=16)
    parser.add_argument("--output-dir", type=Path, default=Path("local/ftrl-w1-distributed"))
    args = parser.parse_args()

    require_environment()
    root = args.output_dir
    root.mkdir(parents=True, exist_ok=True)
    shard_name = f"shard_{args.shard_index:02d}_of_{args.shard_count:02d}"
    shard_dir = root / shard_name
    shard_dir.mkdir(parents=True, exist_ok=True)

    preflight = root / "ltmd_u1_w1_preflight.json"
    full_asset = root / "ltmd_u1_w1_asset_manifest.csv"
    processing = root / "ltmd_u1_w1_processing_inventory.csv"
    run([
        sys.executable,
        "scripts/preflight_ftrl_w1.py",
        "--require-cryptographic-ready",
        "--output",
        str(preflight),
    ])
    run([
        sys.executable,
        "scripts/build_ftrl_w1_inputs.py",
        "--asset-output",
        str(full_asset),
        "--processing-output",
        str(processing),
    ])

    rows = sorted_source_rows(read_csv(full_asset))
    if len(rows) != EXPECTED_W1_SOURCE_PAGES:
        raise SystemExit(f"W1 source cardinality drift: {len(rows)} != {EXPECTED_W1_SOURCE_PAGES}")
    shard_rows = balanced_slice(rows, args.shard_index, args.shard_count)
    expected_hashes = sorted(
        page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in shard_rows
    )
    if len(expected_hashes) != len(set(expected_hashes)):
        raise SystemExit("duplicate expected page key inside deterministic shard")

    shard_asset = shard_dir / f"w1_{shard_name}_asset_manifest.csv"
    jsonl = shard_dir / f"w1_{shard_name}_page_ocr.jsonl"
    db = shard_dir / f"w1_{shard_name}_ocr_search.sqlite"
    run_manifest = shard_dir / f"w1_{shard_name}_run_manifest.json"
    qc_queue = shard_dir / f"w1_{shard_name}_qc_queue.json"
    qc_summary = shard_dir / f"w1_{shard_name}_qc_summary.json"
    evidence = shard_dir / f"w1_{shard_name}_evidence.json"
    write_csv(shard_asset, shard_rows)

    run([
        sys.executable,
        "scripts/build_page_ocr_corpus.py",
        "--asset-manifest",
        str(shard_asset),
        "--processing-inventory",
        str(processing),
        "--wave",
        "W1",
        "--output",
        str(jsonl),
        "--cache-dir",
        str(shard_dir / "assets"),
        "--resume",
    ])
    run([
        sys.executable,
        "scripts/build_search_index.py",
        "--input",
        str(jsonl),
        "--processing-inventory",
        str(processing),
        "--output",
        str(db),
    ])
    run([sys.executable, "scripts/validate_ocr_corpus.py", "--input", str(jsonl), "--db", str(db)])
    run([
        sys.executable,
        "scripts/summarize_ftrl_run.py",
        "--input",
        str(jsonl),
        "--db",
        str(db),
        "--asset-manifest",
        str(shard_asset),
        "--processing-inventory",
        str(processing),
        "--label",
        shard_name,
        "--output",
        str(run_manifest),
    ])
    run([
        sys.executable,
        "scripts/build_ftrl_qc_queue.py",
        "--input",
        str(jsonl),
        "--queue-output",
        str(qc_queue),
        "--summary-output",
        str(qc_summary),
    ])

    actual_hashes, actual_count = jsonl_actual_hashes(jsonl)
    if actual_count != len(shard_rows):
        raise SystemExit(f"shard OCR cardinality mismatch: {actual_count} != {len(shard_rows)}")
    if actual_hashes != expected_hashes:
        raise SystemExit("shard OCR page-key inventory differs from deterministic source partition")

    rm = json.loads(run_manifest.read_text(encoding="utf-8"))
    qc = json.loads(qc_summary.read_text(encoding="utf-8"))
    if rm["status"] != "validated":
        raise SystemExit("shard run manifest is not validated")
    if rm["corpus"]["page_records"] != len(shard_rows):
        raise SystemExit("shard run-manifest page count drift")
    if rm["database"]["page_rows"] != len(shard_rows) or rm["database"]["fts_rows"] != len(shard_rows):
        raise SystemExit("shard SQLite cardinality drift")
    if rm["database"]["sqlite_integrity"] != "ok":
        raise SystemExit("shard SQLite integrity failure")
    if qc["page_records"] != len(shard_rows):
        raise SystemExit("shard QC cardinality drift")

    payload = {
        "schema": SCHEMA,
        "status": "validated",
        "wave": "W1",
        "domain": "Ciencias Naturales",
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "page_records": len(shard_rows),
        "page_key_hashes": expected_hashes,
        "canonical_viewers_in_shard": len({r["viewer_key"] for r in shard_rows}),
        "source_partition": {
            "full_source_pages": EXPECTED_W1_SOURCE_PAGES,
            "algorithm": "stable sort (generation, grade, viewer_key, source_image_index) + balanced contiguous partition",
        },
        "validation": {
            "sqlite_integrity": rm["database"]["sqlite_integrity"],
            "sqlite_pages": rm["database"]["page_rows"],
            "fts_rows": rm["database"]["fts_rows"],
            "qc_page_records": qc["page_records"],
        },
        "restricted_products": [descriptor(jsonl), descriptor(db), descriptor(qc_queue)],
        "text_free_products": [descriptor(shard_asset), descriptor(run_manifest), descriptor(qc_summary)],
        "execution": rm.get("execution"),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epistemic_guards": [
            "ocr_available != text_verified",
            "corpus_ready != semantic_ready",
            "search_hit != historical_claim",
            "computationally_validated != archival_complete",
        ],
    }
    evidence.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "shard": args.shard_index, "pages": len(shard_rows), "evidence": str(evidence)}, sort_keys=True))


if __name__ == "__main__":
    main()
