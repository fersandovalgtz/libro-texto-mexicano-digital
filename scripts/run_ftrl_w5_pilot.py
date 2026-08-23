#!/usr/bin/env python3
"""Orchestrate the LTMD FTRL W5 History pilot with one command."""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

ASSET_MANIFEST = Path("data/catalog/ltmd_u1_w5_history_asset_manifest.csv")
PROCESSING_INVENTORY = Path("data/catalog/ltmd_u1_w5_history_processing_inventory.csv")


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="Process the complete W5 canonical source-admitted cohort",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help="Pilot page limit when --full is not used (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("local/ftrl"),
    )
    parser.add_argument(
        "--query",
        help="Optional FTS5 query to execute after validation",
    )
    args = parser.parse_args()

    if args.pages < 1:
        raise SystemExit("--pages must be >= 1")
    for path in (ASSET_MANIFEST, PROCESSING_INVENTORY):
        if not path.exists():
            raise SystemExit(f"Run from the repository root; missing {path}")
    require_environment()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    label = "full" if args.full else f"pilot_{args.pages}"
    jsonl = args.output_dir / f"ltmd_u1_w5_{label}_page_ocr.jsonl"
    db = args.output_dir / f"ltmd_u1_w5_{label}_ocr_search.sqlite"
    cache = args.output_dir / "w5" / "assets"

    build = [
        sys.executable,
        "scripts/build_page_ocr_corpus.py",
        "--asset-manifest",
        str(ASSET_MANIFEST),
        "--processing-inventory",
        str(PROCESSING_INVENTORY),
        "--wave",
        "W5",
        "--output",
        str(jsonl),
        "--cache-dir",
        str(cache),
        "--resume",
    ]
    if not args.full:
        build += ["--max-pages", str(args.pages)]
    run(build)

    run(
        [
            sys.executable,
            "scripts/build_search_index.py",
            "--input",
            str(jsonl),
            "--processing-inventory",
            str(PROCESSING_INVENTORY),
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

    if args.query:
        run(
            [
                sys.executable,
                "scripts/query_ocr_corpus.py",
                "--db",
                str(db),
                "--query",
                args.query,
                "--format",
                "json",
            ]
        )

    print(f"FTRL W5 {label} ready: {db}")


if __name__ == "__main__":
    main()
