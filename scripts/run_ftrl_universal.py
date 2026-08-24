#!/usr/bin/env python3
"""Run the universal LTMD Full-Text Research Layer (FTRL) pipeline.

The command derives its execution universe from normalized, source-admitted page
manifests. It never assumes a wave-specific page count. Full OCR text, cached
source images and SQLite derivatives belong under local/ by default.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

VERSION = "LTMD_FTRL_RUNNER_0.1"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    required = {
        "wave",
        "operational_domain",
        "viewer_key",
        "canonical_viewer_key",
        "catalog_generation",
        "grade_code",
        "source_image_index",
        "source_asset_url",
        "sha256",
    }
    if not rows:
        raise SystemExit(f"normalized manifest is empty: {path}")
    if not required <= set(rows[0]):
        raise SystemExit(
            f"normalized manifest lacks required columns: {sorted(required - set(rows[0]))}"
        )
    seen: set[tuple[str, int]] = set()
    for row in rows:
        key = (row["viewer_key"], int(row["source_image_index"]))
        if key in seen:
            raise SystemExit(f"duplicate normalized page identity: {key}")
        seen.add(key)
        if row["viewer_key"] != row["canonical_viewer_key"]:
            raise SystemExit(
                f"source row must name its canonical processing object directly: {key}"
            )
    return rows


def partition_viewers(viewers: list[str], shard_count: int) -> list[list[str]]:
    shard_count = max(1, min(shard_count, len(viewers)))
    shards = [[] for _ in range(shard_count)]
    for index, viewer in enumerate(viewers):
        shards[index % shard_count].append(viewer)
    return [shard for shard in shards if shard]


def merge_jsonl(paths: list[Path], output: Path, expected_pages: int) -> None:
    records: list[dict] = []
    seen_ids: set[str] = set()
    seen_keys: set[tuple[str, int]] = set()
    for path in paths:
        with path.open(encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                page_id = row["page_id"]
                key = (row["viewer_key"], int(row["page_index"]))
                if page_id in seen_ids or key in seen_keys:
                    raise SystemExit(
                        f"duplicate OCR record during deterministic merge: {path}:{line_no}"
                    )
                seen_ids.add(page_id)
                seen_keys.add(key)
                records.append(row)

    records.sort(
        key=lambda row: (
            row["wave"],
            row.get("operational_domain", ""),
            int(row["catalog_generation"]),
            int(row["grade_code"]),
            row["canonical_viewer_key"],
            int(row["page_index"]),
        )
    )
    if len(records) != expected_pages:
        raise SystemExit(
            f"OCR page count mismatch: expected {expected_pages}, merged {len(records)}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(output.name + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as fh:
        for row in records:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    temp.replace(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", type=Path, default=Path("local/ftrl-u1"))
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/catalog/ltmd_u1_ftrl_source_registry.csv"),
    )
    parser.add_argument(
        "--coverage", type=Path, default=Path("data/catalog/ltmd_u1_coverage.csv")
    )
    parser.add_argument(
        "--identity-topology",
        type=Path,
        default=Path("data/catalog/ltmd_u1_wave_queue.csv"),
    )
    parser.add_argument("--source-id", action="append", dest="source_ids")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--tesseract", default="tesseract")
    parser.add_argument("--language", default="spa")
    parser.add_argument("--psm", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Normalize and report the source-admitted execution universe without OCR.",
    )
    args = parser.parse_args()

    if args.workers < 1:
        raise SystemExit("--workers must be >= 1")

    scripts = Path(__file__).resolve().parent
    metadata_dir = args.work_dir / "metadata"
    ocr_dir = args.work_dir / "ocr"
    cache_dir = args.work_dir / "source-cache"
    normalized = metadata_dir / "source_manifest.csv"
    identity_map = metadata_dir / "identity_map.csv"
    normalization_summary = metadata_dir / "normalization_summary.json"
    merged_ocr = args.work_dir / "page_ocr.jsonl"
    sqlite_db = args.work_dir / "fulltext.sqlite"

    normalize_cmd = [
        sys.executable,
        str(scripts / "normalize_ftrl_sources.py"),
        "--registry",
        str(args.registry),
        "--coverage",
        str(args.coverage),
        "--identity-topology",
        str(args.identity_topology),
        "--output",
        str(normalized),
        "--identity-output",
        str(identity_map),
        "--summary-output",
        str(normalization_summary),
    ]
    for source_id in args.source_ids or []:
        normalize_cmd.extend(["--source-id", source_id])
    run(normalize_cmd)

    rows = load_manifest(normalized)
    viewers = sorted({row["viewer_key"] for row in rows})
    waves = sorted({row["wave"] for row in rows})
    domains = sorted({row["operational_domain"] for row in rows})
    expected_pages = len(rows)
    plan = {
        "schema_version": VERSION,
        "status": "planned" if args.plan_only else "executing",
        "source_admitted_pages": expected_pages,
        "canonical_viewers": len(viewers),
        "waves": waves,
        "operational_domains": domains,
        "workers_requested": args.workers,
    }
    print(json.dumps(plan, ensure_ascii=False, sort_keys=True))

    if args.plan_only:
        return

    shards = partition_viewers(viewers, args.workers)
    ocr_dir.mkdir(parents=True, exist_ok=True)

    def run_shard(shard_index: int, shard_viewers: list[str]) -> Path:
        output = ocr_dir / f"shard-{shard_index:03d}.jsonl"
        cmd = [
            sys.executable,
            str(scripts / "build_page_ocr_corpus.py"),
            "--asset-manifest",
            str(normalized),
            "--output",
            str(output),
            "--cache-dir",
            str(cache_dir),
            "--tesseract",
            args.tesseract,
            "--language",
            args.language,
            "--psm",
            str(args.psm),
            "--timeout",
            str(args.timeout),
        ]
        if args.resume:
            cmd.append("--resume")
        for viewer in shard_viewers:
            cmd.extend(["--viewer-key", viewer])
        run(cmd)
        return output

    shard_outputs: list[Path] = []
    with ThreadPoolExecutor(max_workers=len(shards)) as pool:
        futures = {
            pool.submit(run_shard, index, viewers_for_shard): index
            for index, viewers_for_shard in enumerate(shards)
        }
        for future in as_completed(futures):
            shard_outputs.append(future.result())

    merge_jsonl(sorted(shard_outputs), merged_ocr, expected_pages)

    run(
        [
            sys.executable,
            str(scripts / "build_search_index.py"),
            "--input",
            str(merged_ocr),
            "--output",
            str(sqlite_db),
            "--identity-map",
            str(identity_map),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "validate_ocr_corpus.py"),
            "--input",
            str(merged_ocr),
            "--db",
            str(sqlite_db),
        ]
    )
    print(
        json.dumps(
            {
                "schema_version": VERSION,
                "status": "ok",
                "source_admitted_pages": expected_pages,
                "canonical_viewers": len(viewers),
                "shards": len(shards),
                "ocr_jsonl": str(merged_ocr),
                "sqlite": str(sqlite_db),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
