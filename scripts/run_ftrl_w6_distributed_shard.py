#!/usr/bin/env python3
"""Run one deterministic LTMD-U1 W6 FTRL shard.

Restricted OCR/SQLite/QC remain under local/ and must be encrypted by the
workflow before any Actions upload. Public evidence is metadata/hash only.
"""
from __future__ import annotations

import argparse, csv, hashlib, json, shutil, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_PAGES = 5258
EXPECTED_HISTORICAL = 42
EXPECTED_CANONICAL = 37
DEFAULT_SHARDS = 16
SCHEMA = "LTMD_FTRL_W6_DISTRIBUTED_SHARD_0.1"

def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True); subprocess.run(command, check=True)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def page_key_hash(viewer_key: str, page_index: int) -> str:
    return hashlib.sha256(f"{viewer_key}:src{page_index:04d}".encode("utf-8")).hexdigest()

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh: return list(csv.DictReader(fh))

def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows: raise SystemExit(f"refusing to write empty shard: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def sorted_source_rows(rows):
    return sorted(rows, key=lambda r: (int(r["catalog_generation"]), int(r["grade_code"]), r["viewer_key"], int(r["source_image_index"])))

def balanced_slice(rows, index, count):
    if count < 1 or not 0 <= index < count: raise SystemExit("invalid shard index/count")
    base, rem = divmod(len(rows), count); start = index * base + min(index, rem); size = base + (1 if index < rem else 0)
    return rows[start:start + size]

def require_environment() -> None:
    if shutil.which("tesseract") is None: raise SystemExit("Tesseract is required")
    langs = subprocess.run(["tesseract", "--list-langs"], check=True, capture_output=True, text=True).stdout.splitlines()
    if "spa" not in {x.strip() for x in langs}: raise SystemExit("Spanish Tesseract language data is required")
    conn = sqlite3.connect(":memory:")
    try: conn.execute("CREATE VIRTUAL TABLE smoke_fts USING fts5(text)")
    finally: conn.close()

def descriptor(path: Path) -> dict:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}

def jsonl_hashes(path: Path):
    hashes, count = [], 0
    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip(): continue
            row = json.loads(line)
            if row.get("wave") != "W6": raise SystemExit(f"non-W6 record at {path}:{line_number}")
            hashes.append(page_key_hash(str(row["viewer_key"]), int(row["page_index"]))); count += 1
    return sorted(hashes), count

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--shard-index", type=int, required=True); ap.add_argument("--shard-count", type=int, default=DEFAULT_SHARDS); ap.add_argument("--output-dir", type=Path, default=Path("local/ftrl-w6-distributed")); args = ap.parse_args()
    require_environment()
    root = args.output_dir; root.mkdir(parents=True, exist_ok=True)
    shard_name = f"shard_{args.shard_index:02d}_of_{args.shard_count:02d}"; shard_dir = root / shard_name; shard_dir.mkdir(parents=True, exist_ok=True)
    preflight = root / "ltmd_u1_w6_preflight.json"; full_asset = root / "ltmd_u1_w6_asset_manifest.csv"; processing = root / "ltmd_u1_w6_processing_inventory.csv"
    run([sys.executable, "scripts/preflight_ftrl_w6.py", "--output", str(preflight)])
    run([sys.executable, "scripts/build_ftrl_w6_inputs.py", "--asset-output", str(full_asset), "--processing-output", str(processing)])
    proc = read_csv(processing); canonical = {r["viewer_key"] for r in proc if r["technical_identity_covered"] == "1" and r["is_canonical_processing_object"] == "1"}
    if len(proc) != EXPECTED_HISTORICAL or len(canonical) != EXPECTED_CANONICAL: raise SystemExit("W6 processing denominator drift")
    rows = sorted_source_rows(read_csv(full_asset))
    if len(rows) != EXPECTED_PAGES: raise SystemExit(f"W6 source cardinality drift: {len(rows)} != {EXPECTED_PAGES}")
    shard_rows = balanced_slice(rows, args.shard_index, args.shard_count)
    expected_hashes = sorted(page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in shard_rows)
    if len(expected_hashes) != len(set(expected_hashes)): raise SystemExit("duplicate expected page key inside shard")

    prefix = f"w6_{shard_name}"; shard_asset = shard_dir / f"{prefix}_asset_manifest.csv"; jsonl = shard_dir / f"{prefix}_page_ocr.jsonl"; db = shard_dir / f"{prefix}_ocr_search.sqlite"; run_manifest = shard_dir / f"{prefix}_run_manifest.json"; qc_queue = shard_dir / f"{prefix}_qc_queue.json"; qc_summary = shard_dir / f"{prefix}_qc_summary.json"; evidence = shard_dir / f"{prefix}_evidence.json"
    write_csv(shard_asset, shard_rows)
    run([sys.executable, "scripts/build_page_ocr_corpus.py", "--asset-manifest", str(shard_asset), "--processing-inventory", str(processing), "--wave", "W6", "--output", str(jsonl), "--cache-dir", str(shard_dir / "assets"), "--resume"])
    run([sys.executable, "scripts/build_search_index.py", "--input", str(jsonl), "--processing-inventory", str(processing), "--output", str(db)])
    run([sys.executable, "scripts/validate_ocr_corpus.py", "--input", str(jsonl), "--db", str(db)])
    run([sys.executable, "scripts/summarize_ftrl_run.py", "--input", str(jsonl), "--db", str(db), "--asset-manifest", str(shard_asset), "--processing-inventory", str(processing), "--label", shard_name, "--output", str(run_manifest)])
    run([sys.executable, "scripts/build_ftrl_qc_queue.py", "--input", str(jsonl), "--queue-output", str(qc_queue), "--summary-output", str(qc_summary)])
    actual_hashes, actual_count = jsonl_hashes(jsonl)
    if actual_count != len(shard_rows) or actual_hashes != expected_hashes: raise SystemExit("W6 shard page inventory mismatch")
    rm = json.loads(run_manifest.read_text(encoding="utf-8")); qc = json.loads(qc_summary.read_text(encoding="utf-8"))
    if rm["status"] != "validated" or rm["database"]["sqlite_integrity"] != "ok": raise SystemExit("W6 shard validation failed")
    pages = len(shard_rows)
    if rm["corpus"]["page_records"] != pages or rm["database"]["page_rows"] != pages or rm["database"]["fts_rows"] != pages or qc["page_records"] != pages: raise SystemExit("W6 shard cardinality drift")
    payload = {
        "schema": SCHEMA, "status": "validated", "wave": "W6", "domain": "Geografía/Atlas",
        "shard_index": args.shard_index, "shard_count": args.shard_count, "page_records": pages,
        "page_key_hashes": expected_hashes, "canonical_viewers_in_shard": len({r["viewer_key"] for r in shard_rows}),
        "source_partition": {"full_source_pages": EXPECTED_PAGES, "algorithm": "stable sort (catalog_generation, grade_code, viewer_key, source_image_index) + balanced contiguous partition"},
        "validation": {"sqlite_integrity": "ok", "sqlite_pages": rm["database"]["page_rows"], "fts_rows": rm["database"]["fts_rows"], "qc_page_records": qc["page_records"]},
        "restricted_products": [descriptor(jsonl), descriptor(db), descriptor(qc_queue)], "text_free_products": [descriptor(shard_asset), descriptor(run_manifest), descriptor(qc_summary)],
        "execution": rm.get("execution"), "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epistemic_guards": ["distributed_computationally_validated != archival_complete", "ocr_available != text_verified", "corpus_ready != semantic_ready", "search_hit != historical_claim", "zero_hits != demonstrated_absence"],
    }
    evidence.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "shard": args.shard_index, "pages": pages, "evidence": str(evidence)}, sort_keys=True))

if __name__ == "__main__":
    main()
