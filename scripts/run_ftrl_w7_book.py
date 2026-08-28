#!/usr/bin/env python3
"""Run one deterministic LTMD-U1 W7 FTRL book unit.

Restricted OCR/SQLite/QC stay under local/ and must be encrypted before any
Actions upload. Public evidence is metadata/hash only. Retained W7 identities
are excluded upstream by the normalized input builder.
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

EXPECTED_HISTORICAL = 30
EXPECTED_CANONICAL = 25
EXPECTED_WITHHELD = 5
EXPECTED_TOTAL = 3261
SCHEMA = "LTMD_FTRL_W7_BOOK_UNIT_0.1"


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
    return hashlib.sha256(f"{viewer_key}:src{page_index:04d}".encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit(f"refusing to write empty unit: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


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


def descriptor(path: Path) -> dict[str, object]:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def jsonl_hashes(path: Path, viewer_key: str) -> tuple[list[str], int]:
    hashes: list[str] = []
    count = 0
    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("wave") != "W7" or row.get("viewer_key") != viewer_key:
                raise SystemExit(f"foreign W7 record at {path}:{line_number}")
            hashes.append(page_key_hash(viewer_key, int(row["page_index"])))
            count += 1
    return sorted(hashes), count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viewer-key", required=True)
    ap.add_argument("--output-dir", type=Path, default=Path("local/ftrl-w7"))
    args = ap.parse_args()
    require_environment()

    viewer = args.viewer_key
    root = args.output_dir
    unit = root / viewer
    unit.mkdir(parents=True, exist_ok=True)
    full_asset = root / "ltmd_u1_w7_asset_manifest.csv"
    processing = root / "ltmd_u1_w7_processing_inventory.csv"
    run([
        sys.executable,
        "scripts/build_ftrl_w7_inputs.py",
        "--asset-output",
        str(full_asset),
        "--processing-output",
        str(processing),
    ])

    proc = read_csv(processing)
    if len(proc) != EXPECTED_CANONICAL:
        raise SystemExit("W7 canonical processing denominator drift")
    canonical = {
        r["viewer_key"]
        for r in proc
        if r["technical_identity_covered"] == "1"
        and r["is_canonical_processing_object"] == "1"
    }
    if len(canonical) != EXPECTED_CANONICAL or viewer not in canonical:
        raise SystemExit(f"viewer is not a W7 source-admitted canonical identity: {viewer}")
    if any(r["persistent_internal_source_gaps"] != "0" for r in proc):
        raise SystemExit("W7 admitted processing inventory contains a source gap")

    by = {r["viewer_key"]: r for r in proc}
    pages_expected = int(by[viewer]["direct_source_jpegs"])
    assets = read_csv(full_asset)
    if len(assets) != EXPECTED_TOTAL:
        raise SystemExit("W7 global source cardinality drift")
    if len({r["viewer_key"] for r in assets}) != EXPECTED_CANONICAL:
        raise SystemExit("W7 source-admitted viewer denominator drift")
    rows = sorted(
        [r for r in assets if r["viewer_key"] == viewer],
        key=lambda r: int(r["source_image_index"]),
    )
    if len(rows) != pages_expected:
        raise SystemExit(f"W7 {viewer} source cardinality drift: {len(rows)} != {pages_expected}")

    expected_hashes = sorted(
        page_key_hash(viewer, int(r["source_image_index"])) for r in rows
    )
    if len(expected_hashes) != len(set(expected_hashes)):
        raise SystemExit("duplicate expected page key inside W7 book unit")

    prefix = f"w7_{viewer}"
    unit_asset = unit / f"{prefix}_asset_manifest.csv"
    jsonl = unit / f"{prefix}_page_ocr.jsonl"
    db = unit / f"{prefix}_ocr_search.sqlite"
    run_manifest = unit / f"{prefix}_run_manifest.json"
    qc_queue = unit / f"{prefix}_qc_queue.json"
    qc_summary = unit / f"{prefix}_qc_summary.json"
    evidence = unit / f"{prefix}_evidence.json"
    write_csv(unit_asset, rows)

    run([
        sys.executable,
        "scripts/build_page_ocr_corpus.py",
        "--asset-manifest",
        str(unit_asset),
        "--processing-inventory",
        str(processing),
        "--wave",
        "W7",
        "--output",
        str(jsonl),
        "--cache-dir",
        str(unit / "assets"),
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
        str(unit_asset),
        "--processing-inventory",
        str(processing),
        "--label",
        viewer,
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

    actual_hashes, actual_count = jsonl_hashes(jsonl, viewer)
    if actual_count != pages_expected or actual_hashes != expected_hashes:
        raise SystemExit("W7 book page inventory mismatch")
    rm = json.loads(run_manifest.read_text(encoding="utf-8"))
    qc = json.loads(qc_summary.read_text(encoding="utf-8"))
    if rm["status"] != "validated" or rm["database"]["sqlite_integrity"] != "ok":
        raise SystemExit("W7 book validation failed")
    if (
        rm["corpus"]["page_records"] != pages_expected
        or rm["database"]["page_rows"] != pages_expected
        or rm["database"]["fts_rows"] != pages_expected
        or qc["page_records"] != pages_expected
    ):
        raise SystemExit("W7 book cardinality drift")

    payload = {
        "schema": SCHEMA,
        "status": "validated",
        "wave": "W7",
        "domain": "Formación Cívica y Ética",
        "viewer_key": viewer,
        "page_records": pages_expected,
        "page_key_hashes": expected_hashes,
        "source_partition": {
            "historical_identities": EXPECTED_HISTORICAL,
            "canonical_processing_objects": EXPECTED_CANONICAL,
            "withheld_identities": EXPECTED_WITHHELD,
            "full_admitted_source_pages": EXPECTED_TOTAL,
            "unit": "one source-admitted canonical viewer/book",
        },
        "validation": {
            "sqlite_integrity": "ok",
            "sqlite_pages": rm["database"]["page_rows"],
            "fts_rows": rm["database"]["fts_rows"],
            "qc_page_records": qc["page_records"],
        },
        "restricted_products": [descriptor(jsonl), descriptor(db), descriptor(qc_queue)],
        "text_free_products": [descriptor(unit_asset), descriptor(run_manifest), descriptor(qc_summary)],
        "execution": rm.get("execution"),
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "epistemic_guards": [
            "computationally_validated != archival_complete",
            "ocr_available != text_verified",
            "corpus_ready != semantic_ready",
            "retained_source_identity != alias_candidate",
            "search_hit != historical_claim",
            "zero_hits != demonstrated_absence",
        ],
    }
    evidence.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"status": "ok", "viewer_key": viewer, "pages": pages_expected, "evidence": str(evidence)},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
