#!/usr/bin/env python3
"""Run W5 FTRL in canonical-object shards without publishing OCR intermediates."""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

VERSION = "LTMD_FTRL_PARALLEL_RUN_0.1"
ASSET_MANIFEST = Path("data/catalog/ltmd_u1_w5_history_asset_manifest.csv")
PROCESSING_INVENTORY = Path("data/catalog/ltmd_u1_w5_history_processing_inventory.csv")
QUERY_PROTOCOL = Path("data/research/ltmd_ftrl_w5_preregistered_queries.csv")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def load_processing_topology(path: Path) -> tuple[list[dict], int]:
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    required = {
        "viewer_key",
        "catalog_generation",
        "grade_code",
        "technical_identity_covered",
        "is_canonical_processing_object",
        "direct_source_jpegs",
    }
    if not rows or not required <= set(rows[0]):
        raise SystemExit(f"processing inventory lacks required columns: {sorted(required)}")

    canonical = []
    historical_identities = 0
    for row in rows:
        if row["technical_identity_covered"] == "1":
            historical_identities += 1
        if (
            row["technical_identity_covered"] == "1"
            and row["is_canonical_processing_object"] == "1"
        ):
            canonical.append(
                {
                    "viewer_key": row["viewer_key"],
                    "catalog_generation": int(row["catalog_generation"]),
                    "grade_code": int(row["grade_code"]),
                    "direct_source_jpegs": int(row["direct_source_jpegs"]),
                }
            )
    canonical.sort(
        key=lambda row: (
            row["catalog_generation"],
            row["grade_code"],
            row["viewer_key"],
        )
    )
    if not canonical:
        raise SystemExit("processing inventory contains no canonical W5 objects")
    return canonical, historical_identities


def run_checked(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def run_shard(
    item: dict,
    output_dir: Path,
    cache_dir: Path,
    max_pages_per_viewer: int | None,
) -> dict:
    viewer_key = item["viewer_key"]
    output = output_dir / "shards" / f"{viewer_key}.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "scripts/build_page_ocr_corpus.py",
        "--asset-manifest",
        str(ASSET_MANIFEST),
        "--processing-inventory",
        str(PROCESSING_INVENTORY),
        "--wave",
        "W5",
        "--viewer-key",
        viewer_key,
        "--output",
        str(output),
        "--cache-dir",
        str(cache_dir),
        "--resume",
    ]
    expected = item["direct_source_jpegs"]
    if max_pages_per_viewer is not None:
        command += ["--max-pages", str(max_pages_per_viewer)]
        expected = min(expected, max_pages_per_viewer)

    env = os.environ.copy()
    env.setdefault("OMP_THREAD_LIMIT", "1")
    started = time.monotonic()
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    elapsed = round(time.monotonic() - started, 3)
    if result.returncode != 0:
        raise RuntimeError(
            f"shard {viewer_key} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    observed = sum(1 for line in output.open(encoding="utf-8") if line.strip())
    if observed != expected:
        raise RuntimeError(
            f"shard {viewer_key} cardinality mismatch: expected={expected} observed={observed}"
        )
    print(
        f"[{viewer_key}] shard validated: pages={observed} elapsed_seconds={elapsed}",
        flush=True,
    )
    return {
        **item,
        "expected_pages": expected,
        "observed_pages": observed,
        "elapsed_seconds": elapsed,
        "output": output,
    }


def merge_shards(shards: list[dict], destination: Path) -> int:
    records: list[dict] = []
    seen: set[str] = set()
    for shard in shards:
        viewer_key = shard["viewer_key"]
        with shard["output"].open(encoding="utf-8") as fh:
            for line_number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        f"invalid JSON in shard {viewer_key}:{line_number}: {exc}"
                    ) from exc
                if record.get("viewer_key") != viewer_key:
                    raise RuntimeError(
                        f"shard {viewer_key} contains foreign viewer {record.get('viewer_key')}"
                    )
                page_id = str(record["page_id"])
                if page_id in seen:
                    raise RuntimeError(f"duplicate page_id across shards: {page_id}")
                seen.add(page_id)
                records.append(record)

    records.sort(
        key=lambda row: (
            int(row["catalog_generation"]),
            int(row["grade_code"]),
            str(row["viewer_key"]),
            int(row["page_index"]),
        )
    )
    expected = sum(int(shard["expected_pages"]) for shard in shards)
    if len(records) != expected:
        raise RuntimeError(
            f"merged cardinality mismatch: expected={expected} observed={len(records)}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    temp.replace(destination)
    return len(records)


def write_parallel_summary(
    path: Path,
    started_at: str,
    elapsed_seconds: float,
    workers: int,
    shards: list[dict],
    complete_w5: bool,
    expected_historical_identities: int,
) -> None:
    payload = {
        "schema_version": VERSION,
        "started_at": started_at,
        "finished_at": utc_now(),
        "elapsed_seconds": round(elapsed_seconds, 3),
        "workers": workers,
        "complete_w5": complete_w5,
        "canonical_viewers": len(shards),
        "expected_pages": sum(int(shard["expected_pages"]) for shard in shards),
        "observed_pages": sum(int(shard["observed_pages"]) for shard in shards),
        "expected_historical_identities": expected_historical_identities,
        "rights_note": (
            "Text-free operational summary. Shard OCR, merged OCR, SQLite index, and OCR snippets "
            "remain local and are not included."
        ),
        "shards": [
            {
                "viewer_key": shard["viewer_key"],
                "catalog_generation": shard["catalog_generation"],
                "grade_code": shard["grade_code"],
                "expected_pages": shard["expected_pages"],
                "observed_pages": shard["observed_pages"],
                "elapsed_seconds": shard["elapsed_seconds"],
            }
            for shard in shards
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 2))
    parser.add_argument("--output-dir", type=Path, default=Path("local/ftrl"))
    parser.add_argument(
        "--viewer-key",
        action="append",
        dest="viewer_keys",
        help="Restrict the run to selected canonical viewer_key values; repeat as needed",
    )
    parser.add_argument(
        "--max-pages-per-viewer",
        type=int,
        help="Bound each selected shard for integration tests; omit for complete objects",
    )
    parser.add_argument(
        "--run-preregistered-queries",
        action="store_true",
        help="Run the frozen W5 query protocol; allowed only for complete W5",
    )
    args = parser.parse_args()

    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")
    if args.max_pages_per_viewer is not None and args.max_pages_per_viewer < 1:
        raise SystemExit("--max-pages-per-viewer must be >= 1")
    for path in (ASSET_MANIFEST, PROCESSING_INVENTORY):
        if not path.exists():
            raise SystemExit(f"Run from the repository root; missing {path}")
    if args.run_preregistered_queries and not QUERY_PROTOCOL.exists():
        raise SystemExit(f"missing query protocol: {QUERY_PROTOCOL}")

    require_environment()
    canonical, expected_historical_identities = load_processing_topology(
        PROCESSING_INVENTORY
    )
    all_keys = {item["viewer_key"] for item in canonical}
    requested = set(args.viewer_keys) if args.viewer_keys else all_keys
    unknown = requested - all_keys
    if unknown:
        raise SystemExit(
            "requested viewer_key values are not canonical W5 objects: "
            + ", ".join(sorted(unknown))
        )
    selected = [item for item in canonical if item["viewer_key"] in requested]
    complete_w5 = requested == all_keys and args.max_pages_per_viewer is None
    if args.run_preregistered_queries and not complete_w5:
        raise SystemExit("--run-preregistered-queries requires the complete W5 cohort")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.output_dir / "w5" / "assets"
    full_jsonl = args.output_dir / "ltmd_u1_w5_full_page_ocr.jsonl"
    db = args.output_dir / "ltmd_u1_w5_full_ocr_search.sqlite"
    run_manifest = args.output_dir / "ltmd_u1_w5_full_run_manifest.json"
    parallel_summary = args.output_dir / "ltmd_u1_w5_full_parallel_summary.json"

    started_at = utc_now()
    started = time.monotonic()
    completed: list[dict] = []
    max_workers = min(args.workers, len(selected))
    print(
        f"Launching W5 shards: canonical_viewers={len(selected)} workers={max_workers} "
        f"complete_w5={complete_w5}",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(
                run_shard,
                item,
                args.output_dir,
                cache_dir,
                args.max_pages_per_viewer,
            ): item["viewer_key"]
            for item in selected
        }
        try:
            for future in as_completed(futures):
                completed.append(future.result())
        except Exception:
            for pending in futures:
                pending.cancel()
            raise

    completed.sort(
        key=lambda row: (
            row["catalog_generation"],
            row["grade_code"],
            row["viewer_key"],
        )
    )
    merged_pages = merge_shards(completed, full_jsonl)
    print(f"Merged validated shards: pages={merged_pages} -> {full_jsonl}", flush=True)

    run_checked(
        [
            sys.executable,
            "scripts/build_search_index.py",
            "--input",
            str(full_jsonl),
            "--processing-inventory",
            str(PROCESSING_INVENTORY),
            "--output",
            str(db),
        ]
    )
    run_checked(
        [
            sys.executable,
            "scripts/validate_ocr_corpus.py",
            "--input",
            str(full_jsonl),
            "--db",
            str(db),
        ]
    )
    run_checked(
        [
            sys.executable,
            "scripts/summarize_ftrl_run.py",
            "--input",
            str(full_jsonl),
            "--db",
            str(db),
            "--asset-manifest",
            str(ASSET_MANIFEST),
            "--processing-inventory",
            str(PROCESSING_INVENTORY),
            "--label",
            "full" if complete_w5 else "parallel_subset",
            "--output",
            str(run_manifest),
        ]
    )

    manifest = json.loads(run_manifest.read_text(encoding="utf-8"))
    expected_pages = sum(int(row["expected_pages"]) for row in completed)
    if manifest["corpus"]["page_records"] != expected_pages:
        raise SystemExit("run manifest page cardinality does not match merged shards")
    if manifest["corpus"]["canonical_viewers"] != len(completed):
        raise SystemExit("run manifest canonical-viewer cardinality does not match shards")
    if complete_w5 and manifest["database"]["historical_identities"] != expected_historical_identities:
        raise SystemExit(
            "complete W5 historical-identity cardinality mismatch: "
            f"expected={expected_historical_identities} "
            f"observed={manifest['database']['historical_identities']}"
        )

    if args.run_preregistered_queries:
        run_checked(
            [
                sys.executable,
                "scripts/run_ftrl_query_protocol.py",
                "--db",
                str(db),
                "--protocol",
                str(QUERY_PROTOCOL),
                "--output",
                str(args.output_dir / "ltmd_u1_w5_query_candidates.json"),
                "--summary-output",
                str(args.output_dir / "ltmd_u1_w5_query_summary.json"),
                "--locator-output",
                str(args.output_dir / "ltmd_u1_w5_query_locators.json"),
            ]
        )

    elapsed = time.monotonic() - started
    write_parallel_summary(
        parallel_summary,
        started_at,
        elapsed,
        max_workers,
        completed,
        complete_w5,
        expected_historical_identities,
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "complete_w5": complete_w5,
                "canonical_viewers": len(completed),
                "pages": expected_pages,
                "historical_identities": manifest["database"]["historical_identities"],
                "elapsed_seconds": round(elapsed, 3),
                "run_manifest": str(run_manifest),
                "parallel_summary": str(parallel_summary),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
