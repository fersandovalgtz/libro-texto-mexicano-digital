#!/usr/bin/env python3
"""Create a machine-readable, text-free provenance manifest for an LTMD FTRL run."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sqlite3
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

VERSION = "LTMD_FTRL_RUN_0.1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        return path.name


def summarize_jsonl(path: Path) -> dict:
    page_count = 0
    canonical_viewers: set[str] = set()
    waves: set[str] = set()
    generations: set[int] = set()
    grades: set[int] = set()
    schema_versions: set[str] = set()
    pipeline_versions: set[str] = set()
    engine_versions: set[str] = set()
    languages: set[str] = set()
    psms: set[int] = set()
    confidences: list[float] = []
    confidence_missing = 0
    source_bytes = 0
    source_bytes_missing = 0
    chars = 0
    words = 0
    zero_text_pages = 0
    generated_at_values: list[str] = []
    generation_counts: Counter[str] = Counter()
    grade_counts: Counter[str] = Counter()

    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            page_count += 1
            canonical_viewers.add(str(row["viewer_key"]))
            waves.add(str(row["wave"]))
            generation = int(row["catalog_generation"])
            grade = int(row["grade_code"])
            generations.add(generation)
            grades.add(grade)
            generation_counts[str(generation)] += 1
            grade_counts[str(grade)] += 1
            schema_versions.add(str(row["schema_version"]))
            pipeline_versions.add(str(row["pipeline_version"]))
            engine_versions.add(str(row["ocr_engine_version"]))
            languages.add(str(row["ocr_language"]))
            psms.add(int(row["ocr_psm"]))
            confidence = row.get("ocr_confidence_mean")
            if confidence is None:
                confidence_missing += 1
            else:
                confidences.append(float(confidence))
            byte_size = row.get("source_byte_size")
            if byte_size is None:
                source_bytes_missing += 1
            else:
                source_bytes += int(byte_size)
            char_count = int(row["ocr_char_count"])
            word_count = int(row["ocr_word_count"])
            chars += char_count
            words += word_count
            if not str(row.get("search_text", "")).strip():
                zero_text_pages += 1
            if row.get("generated_at"):
                generated_at_values.append(str(row["generated_at"]))

    if page_count == 0:
        raise SystemExit("OCR corpus is empty")

    confidence_summary = {
        "observed_pages": len(confidences),
        "missing_pages": confidence_missing,
        "mean": round(statistics.fmean(confidences), 6) if confidences else None,
        "median": round(statistics.median(confidences), 6) if confidences else None,
        "minimum": round(min(confidences), 6) if confidences else None,
        "maximum": round(max(confidences), 6) if confidences else None,
    }
    return {
        "page_records": page_count,
        "canonical_viewers": len(canonical_viewers),
        "waves": sorted(waves),
        "catalog_generations": sorted(generations),
        "grade_codes": sorted(grades),
        "pages_by_generation": dict(sorted(generation_counts.items())),
        "pages_by_grade": dict(sorted(grade_counts.items(), key=lambda item: int(item[0]))),
        "schema_versions": sorted(schema_versions),
        "pipeline_versions": sorted(pipeline_versions),
        "ocr_engine_versions": sorted(engine_versions),
        "ocr_languages": sorted(languages),
        "ocr_psm_values": sorted(psms),
        "ocr_confidence": confidence_summary,
        "source_bytes_total_known": source_bytes,
        "source_byte_size_missing_pages": source_bytes_missing,
        "ocr_characters_total": chars,
        "ocr_words_total": words,
        "zero_search_text_pages": zero_text_pages,
        "record_generated_at_min": min(generated_at_values) if generated_at_values else None,
        "record_generated_at_max": max(generated_at_values) if generated_at_values else None,
    }


def summarize_db(path: Path) -> dict:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        pages = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        fts = conn.execute("SELECT COUNT(*) FROM pages_fts").fetchone()[0]
        identities = conn.execute("SELECT COUNT(*) FROM identities").fetchone()[0]
        metadata = dict(conn.execute("SELECT key,value FROM metadata"))
    finally:
        conn.close()
    if integrity != "ok" or pages != fts:
        raise SystemExit(
            f"SQLite validation failure: integrity={integrity}, pages={pages}, fts={fts}"
        )
    return {
        "sqlite_integrity": integrity,
        "page_rows": pages,
        "fts_rows": fts,
        "historical_identities": identities,
        "index_metadata": metadata,
    }


def file_descriptor(path: Path) -> dict:
    return {
        "path": portable_path(path),
        "sha256": sha256_file(path),
        "byte_size": path.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Local page OCR JSONL")
    parser.add_argument("--db", type=Path, required=True, help="Local SQLite FTS5 database")
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--processing-inventory", type=Path)
    parser.add_argument("--label", default="unspecified")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    for path in (args.input, args.db):
        if not path.exists():
            raise SystemExit(f"missing required input: {path}")
    for path in (args.asset_manifest, args.processing_inventory):
        if path is not None and not path.exists():
            raise SystemExit(f"missing provenance input: {path}")

    corpus = summarize_jsonl(args.input)
    database = summarize_db(args.db)
    if database["page_rows"] != corpus["page_records"]:
        raise SystemExit(
            "OCR JSONL and SQLite cardinalities differ: "
            f"jsonl={corpus['page_records']} sqlite={database['page_rows']}"
        )

    files = {
        "ocr_jsonl": file_descriptor(args.input),
        "sqlite_index": file_descriptor(args.db),
    }
    if args.asset_manifest is not None:
        files["asset_manifest"] = file_descriptor(args.asset_manifest)
    if args.processing_inventory is not None:
        files["processing_inventory"] = file_descriptor(args.processing_inventory)

    manifest = {
        "schema_version": VERSION,
        "run_label": args.label,
        "status": "validated",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "rights_note": (
            "This manifest contains metadata, hashes, cardinalities, and software/environment "
            "information only; it intentionally excludes OCR text and source images."
        ),
        "environment": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "sqlite_version": sqlite3.sqlite_version,
            "platform": platform.platform(),
        },
        "files": files,
        "corpus": corpus,
        "database": database,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_name(args.output.name + ".tmp")
    temp.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp.replace(args.output)
    print(
        json.dumps(
            {
                "status": "ok",
                "run_manifest": portable_path(args.output),
                "page_records": corpus["page_records"],
                "historical_identities": database["historical_identities"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
