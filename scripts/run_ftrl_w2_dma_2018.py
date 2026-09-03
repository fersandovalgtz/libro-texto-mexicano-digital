#!/usr/bin/env python3
"""Run the W2 DMA 2018 FTRL downstream locally/private only.

This orchestrator deliberately does not publish OCR or source images. It discovers
source-admitted manifest rows for the four route-resolved DMA 2018 identities,
builds a local filtered manifest, performs page OCR, builds/validates FTS5, and
emits a text-free run provenance manifest.

The complete OCR JSONL, SQLite database, filtered source manifest, and downloaded
assets remain under ``local/`` and are not intended for version control.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

TARGETS = {
    "H2018P3DMA",
    "H2018P4DMA",
    "H2018P5DMA",
    "H2018P6DMA",
}
EXPECTED_PAGES = 892
ASSET_REQUIRED = {
    "viewer_key",
    "catalog_generation",
    "grade_code",
    "title_core",
    "source_image_index",
    "source_asset_url",
    "asset_status",
    "sha256",
}


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


def discover_asset_rows(catalog_dir: Path) -> tuple[list[dict[str, str]], list[Path]]:
    selected: dict[tuple[str, int], dict[str, str]] = {}
    sources: list[Path] = []
    for path in sorted(catalog_dir.glob("*.csv")):
        try:
            with path.open(encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                if not reader.fieldnames or not ASSET_REQUIRED <= set(reader.fieldnames):
                    continue
                matched_here = False
                for row in reader:
                    if row.get("viewer_key") not in TARGETS:
                        continue
                    if row.get("asset_status") != "source_jpeg":
                        continue
                    try:
                        page_index = int(row["source_image_index"])
                    except (TypeError, ValueError) as exc:
                        raise SystemExit(f"invalid source_image_index in {path}") from exc
                    key = (row["viewer_key"], page_index)
                    previous = selected.get(key)
                    if previous and previous.get("sha256") != row.get("sha256"):
                        raise SystemExit(
                            f"conflicting SHA-256 for {key}: {previous.get('sha256')} vs {row.get('sha256')}"
                        )
                    selected[key] = row
                    matched_here = True
                if matched_here:
                    sources.append(path)
        except UnicodeDecodeError:
            continue

    rows = list(selected.values())
    rows.sort(key=lambda r: (r["viewer_key"], int(r["source_image_index"])))
    observed = {r["viewer_key"] for r in rows}
    missing = TARGETS - observed
    if missing:
        raise SystemExit(f"missing target identities in source-admitted manifests: {sorted(missing)}")
    if len(rows) != EXPECTED_PAGES:
        raise SystemExit(
            f"W2 DMA 2018 cardinality mismatch: expected {EXPECTED_PAGES} pages, observed {len(rows)}"
        )
    return rows, sources


def write_filtered_manifest(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog-dir", type=Path, default=Path("data/catalog"))
    parser.add_argument("--output-dir", type=Path, default=Path("local/ftrl/w2_dma_2018"))
    parser.add_argument("--pages", type=int, help="Optional smoke-test page limit. Omit for all 892 pages.")
    args = parser.parse_args()

    if args.pages is not None and args.pages < 1:
        raise SystemExit("--pages must be >= 1")
    if not args.catalog_dir.exists():
        raise SystemExit(f"missing catalog directory: {args.catalog_dir}")
    require_environment()

    rows, source_files = discover_asset_rows(args.catalog_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    filtered_manifest = args.output_dir / "w2_dma_2018_asset_manifest.csv"
    jsonl = args.output_dir / "w2_dma_2018_page_ocr.jsonl"
    db = args.output_dir / "w2_dma_2018_ocr_search.sqlite"
    run_manifest = args.output_dir / "w2_dma_2018_run_manifest.json"
    cache = args.output_dir / "assets"
    write_filtered_manifest(rows, filtered_manifest)

    build = [
        sys.executable,
        "scripts/build_page_ocr_corpus.py",
        "--asset-manifest",
        str(filtered_manifest),
        "--wave",
        "W2",
        "--output",
        str(jsonl),
        "--cache-dir",
        str(cache),
        "--resume",
    ]
    if args.pages is not None:
        build += ["--max-pages", str(args.pages)]
    run(build)

    run([
        sys.executable,
        "scripts/build_search_index.py",
        "--input",
        str(jsonl),
        "--output",
        str(db),
    ])
    run([
        sys.executable,
        "scripts/validate_ocr_corpus.py",
        "--input",
        str(jsonl),
        "--db",
        str(db),
    ])
    run([
        sys.executable,
        "scripts/summarize_ftrl_run.py",
        "--input",
        str(jsonl),
        "--db",
        str(db),
        "--asset-manifest",
        str(filtered_manifest),
        "--label",
        "w2_dma_2018_full" if args.pages is None else f"w2_dma_2018_smoke_{args.pages}",
        "--output",
        str(run_manifest),
    ])

    print(f"Validated W2 DMA 2018 FTRL output: {run_manifest}")
    print(f"Discovered source rows from {len(source_files)} repository manifest file(s).")
    print("Rights guard: do not commit OCR JSONL, SQLite database, filtered manifest, or source assets.")
    print("semantic_ready remains false/not-promoted without explicit human validation.")


if __name__ == "__main__":
    main()
