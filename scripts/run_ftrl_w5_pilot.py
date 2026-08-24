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
QUERY_PROTOCOL = Path("data/research/ltmd_ftrl_w5_preregistered_queries.csv")


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
        help="Optional ad hoc FTS5 query to execute after validation",
    )
    parser.add_argument(
        "--run-preregistered-queries",
        action="store_true",
        help="Execute the frozen W5 historiographic query protocol after a full run",
    )
    args = parser.parse_args()

    if args.pages < 1:
        raise SystemExit("--pages must be >= 1")
    if args.run_preregistered_queries and not args.full:
        raise SystemExit("--run-preregistered-queries requires --full")
    required_paths = [ASSET_MANIFEST, PROCESSING_INVENTORY]
    if args.run_preregistered_queries:
        required_paths.append(QUERY_PROTOCOL)
    for path in required_paths:
        if not path.exists():
            raise SystemExit(f"Run from the repository root; missing {path}")
    require_environment()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    label = "full" if args.full else f"pilot_{args.pages}"
    jsonl = args.output_dir / f"ltmd_u1_w5_{label}_page_ocr.jsonl"
    db = args.output_dir / f"ltmd_u1_w5_{label}_ocr_search.sqlite"
    run_manifest = args.output_dir / f"ltmd_u1_w5_{label}_run_manifest.json"
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
    run(
        [
            sys.executable,
            "scripts/summarize_ftrl_run.py",
            "--input",
            str(jsonl),
            "--db",
            str(db),
            "--asset-manifest",
            str(ASSET_MANIFEST),
            "--processing-inventory",
            str(PROCESSING_INVENTORY),
            "--label",
            label,
            "--output",
            str(run_manifest),
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

    if args.run_preregistered_queries:
        candidates = args.output_dir / "ltmd_u1_w5_query_candidates.json"
        query_summary = args.output_dir / "ltmd_u1_w5_query_summary.json"
        run(
            [
                sys.executable,
                "scripts/run_ftrl_query_protocol.py",
                "--db",
                str(db),
                "--protocol",
                str(QUERY_PROTOCOL),
                "--output",
                str(candidates),
                "--summary-output",
                str(query_summary),
            ]
        )

    print(f"FTRL W5 {label} ready: {db}")
    print(f"Run provenance manifest: {run_manifest}")


if __name__ == "__main__":
    main()
