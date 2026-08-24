#!/usr/bin/env python3
"""Run LTMD-U1 W1 Ciencias Naturales through the FTRL pipeline."""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


def require_environment() -> None:
    if shutil.which("tesseract") is None:
        raise SystemExit("Tesseract is required but was not found on PATH")
    langs = subprocess.run(
        ["tesseract", "--list-langs"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if "spa" not in {lang.strip() for lang in langs}:
        raise SystemExit("Tesseract Spanish language data ('spa') is required")
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE VIRTUAL TABLE smoke_fts USING fts5(text)")
    except sqlite3.OperationalError as exc:
        raise SystemExit("SQLite FTS5 support is required") from exc
    finally:
        conn.close()


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit(f"cannot write empty shard: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def balanced_shards(rows: list[dict[str, str]], count: int) -> list[list[dict[str, str]]]:
    count = max(1, min(count, len(rows)))
    base, remainder = divmod(len(rows), count)
    shards: list[list[dict[str, str]]] = []
    start = 0
    for index in range(count):
        size = base + (1 if index < remainder else 0)
        shards.append(rows[start : start + size])
        start += size
    assert sum(len(shard) for shard in shards) == len(rows)
    return shards


def run_ocr_shards(
    *,
    rows: list[dict[str, str]],
    processing_inventory: Path,
    output_dir: Path,
    workers: int,
) -> Path:
    shard_dir = output_dir / "w1" / "shards"
    cache_root = output_dir / "w1" / "assets"
    shards = balanced_shards(rows, workers)
    processes: list[tuple[int, subprocess.Popen]] = []
    outputs: list[Path] = []

    for index, shard_rows in enumerate(shards):
        manifest = shard_dir / f"asset_manifest_{index:02d}.csv"
        output = shard_dir / f"page_ocr_{index:02d}.jsonl"
        cache = cache_root / f"shard_{index:02d}"
        write_rows(manifest, shard_rows)
        outputs.append(output)
        command = [
            sys.executable,
            "scripts/build_page_ocr_corpus.py",
            "--asset-manifest",
            str(manifest),
            "--processing-inventory",
            str(processing_inventory),
            "--wave",
            "W1",
            "--output",
            str(output),
            "--cache-dir",
            str(cache),
            "--resume",
        ]
        print("+", " ".join(command), flush=True)
        processes.append((index, subprocess.Popen(command)))

    failed: list[tuple[int, int]] = []
    for index, process in processes:
        code = process.wait()
        if code:
            failed.append((index, code))
    if failed:
        raise SystemExit(f"W1 OCR shard failure(s): {failed}")

    combined = output_dir / "ltmd_u1_w1_full_page_ocr.jsonl"
    temp = combined.with_name(combined.name + ".tmp")
    page_ids: set[str] = set()
    count = 0
    with temp.open("w", encoding="utf-8", newline="\n") as out:
        for path in outputs:
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    page_id = str(record["page_id"])
                    if page_id in page_ids:
                        raise SystemExit(f"duplicate OCR page_id across shards: {page_id}")
                    page_ids.add(page_id)
                    out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                    count += 1
    temp.replace(combined)
    if count != len(rows):
        raise SystemExit(f"combined OCR cardinality mismatch: {count} != {len(rows)}")
    return combined


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--pages", type=int, default=12)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=Path("local/ftrl"))
    args = parser.parse_args()

    if args.pages < 1:
        raise SystemExit("--pages must be >= 1")
    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")
    require_environment()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    preflight = args.output_dir / "ltmd_u1_w1_preflight.json"
    run(
        [
            sys.executable,
            "scripts/preflight_ftrl_w1.py",
            "--require-cryptographic-ready",
            "--output",
            str(preflight),
        ]
    )

    asset_manifest = args.output_dir / "ltmd_u1_w1_asset_manifest.csv"
    processing_inventory = args.output_dir / "ltmd_u1_w1_processing_inventory.csv"
    run(
        [
            sys.executable,
            "scripts/build_ftrl_w1_inputs.py",
            "--asset-output",
            str(asset_manifest),
            "--processing-output",
            str(processing_inventory),
        ]
    )

    rows = read_rows(asset_manifest)
    if len(rows) != 5926:
        raise SystemExit(f"normalized W1 asset cardinality drifted: {len(rows)}")
    if not args.full:
        rows = rows[: args.pages]
        label = f"pilot_{len(rows)}"
        pilot_manifest = args.output_dir / f"ltmd_u1_w1_{label}_asset_manifest.csv"
        write_rows(pilot_manifest, rows)
        provenance_asset_manifest = pilot_manifest
        jsonl = args.output_dir / f"ltmd_u1_w1_{label}_page_ocr.jsonl"
        run(
            [
                sys.executable,
                "scripts/build_page_ocr_corpus.py",
                "--asset-manifest",
                str(pilot_manifest),
                "--processing-inventory",
                str(processing_inventory),
                "--wave",
                "W1",
                "--output",
                str(jsonl),
                "--cache-dir",
                str(args.output_dir / "w1" / "assets" / label),
                "--resume",
            ]
        )
    else:
        label = "full"
        provenance_asset_manifest = asset_manifest
        jsonl = run_ocr_shards(
            rows=rows,
            processing_inventory=processing_inventory,
            output_dir=args.output_dir,
            workers=args.workers,
        )

    db = args.output_dir / f"ltmd_u1_w1_{label}_ocr_search.sqlite"
    run_manifest = args.output_dir / f"ltmd_u1_w1_{label}_run_manifest.json"
    qc_queue = args.output_dir / f"ltmd_u1_w1_{label}_qc_queue.json"
    qc_summary = args.output_dir / f"ltmd_u1_w1_{label}_qc_summary.json"

    run(
        [
            sys.executable,
            "scripts/build_search_index.py",
            "--input",
            str(jsonl),
            "--processing-inventory",
            str(processing_inventory),
            "--output",
            str(db),
        ]
    )
    run(
        [
            sys.executable,
            "scripts/validate_ocr_corpus.py",
            "--input",
            str(jsonl),
            "--db",
            str(db),
        ]
    )
    run(
        [
            sys.executable,
            "scripts/summarize_ftrl_run.py",
            "--input",
            str(jsonl),
            "--db",
            str(db),
            "--asset-manifest",
            str(provenance_asset_manifest),
            "--processing-inventory",
            str(processing_inventory),
            "--label",
            label,
            "--output",
            str(run_manifest),
        ]
    )
    run(
        [
            sys.executable,
            "scripts/build_ftrl_qc_queue.py",
            "--input",
            str(jsonl),
            "--queue-output",
            str(qc_queue),
            "--summary-output",
            str(qc_summary),
        ]
    )

    print(f"FTRL W1 {label} ready: {db}")
    print(f"Run provenance manifest: {run_manifest}")
    print(f"Text-free QC summary: {qc_summary}")


if __name__ == "__main__":
    main()
