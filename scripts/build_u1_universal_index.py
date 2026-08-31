#!/usr/bin/env python3
"""Build the private corpus-wide LTMD-U1 universal SQLite/FTS5 index.

Version: LTMD_U1_UNIVERSAL_INDEX_0.1

The builder reconciles page-level FTRL SQLite databases into one private search index.
It may read OCR-derived search text and source URLs, but those values remain inside the
private SQLite output. The companion manifest is text-free and suitable for public audit.

Reproducibility rules:
- source databases are identified in the public manifest by content hash, not local path/name;
- reconciled pages are inserted in global `page_id` ascending order, independent of input filenames;
- duplicate page IDs are accepted only when their technical fingerprint is identical.

Scientific boundary:
    ocr_available != text_verified
    search_hit != historical_claim
    computational_candidate != semantic_ready
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Iterable

VERSION = "LTMD_U1_UNIVERSAL_INDEX_0.1"
EXPECTED_U1_PAGES = 86549
EXPECTED_U1_OBJECTS = 492

CORE_COLUMNS = (
    "page_id",
    "viewer_key",
    "canonical_viewer_key",
    "wave",
    "catalog_generation",
    "grade_code",
    "title_core",
    "page_index",
    "viewer_page",
    "source_asset_url",
    "source_sha256",
    "ocr_sha256",
    "ocr_confidence_mean",
    "search_text",
)

OPTIONAL_COLUMNS = (
    "source_byte_size",
    "ocr_engine",
    "ocr_engine_version",
    "ocr_language",
    "ocr_psm",
    "search_text_sha256",
    "ocr_char_count",
    "ocr_word_count",
    "generated_at",
)

PRIVATE_OUTPUT_COLUMNS = CORE_COLUMNS + OPTIONAL_COLUMNS


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_db_paths(explicit: Iterable[str], directories: Iterable[str], pattern: str) -> list[Path]:
    paths: set[Path] = set()
    for value in explicit:
        path = Path(value).expanduser().resolve()
        if not path.is_file():
            raise RuntimeError(f"input SQLite does not exist: {path}")
        paths.add(path)
    for value in directories:
        root = Path(value).expanduser().resolve()
        if not root.is_dir():
            raise RuntimeError(f"input directory does not exist: {root}")
        for path in root.rglob(pattern):
            if path.is_file():
                paths.add(path.resolve())
    result = sorted(paths, key=lambda path: str(path))
    if not result:
        raise RuntimeError("no input SQLite databases were found")
    return result


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f"PRAGMA table_info({quote_identifier(table)})")}


def page_fingerprint(row: dict) -> tuple:
    return (
        row.get("canonical_viewer_key"),
        row.get("source_sha256"),
        row.get("ocr_sha256"),
        str(row.get("catalog_generation")),
        str(row.get("page_index")),
        str(row.get("viewer_page")),
    )


def iter_source_pages(db_paths: list[Path]):
    """Yield globally page_id-sorted canonical rows; fail on conflicting duplicates."""
    seen: dict[str, tuple[tuple, dict]] = {}
    duplicate_rows = 0
    for db_path in db_paths:
        connection = sqlite3.connect(str(db_path))
        connection.row_factory = sqlite3.Row
        try:
            columns = table_columns(connection, "pages")
            missing = set(CORE_COLUMNS) - columns
            if missing:
                raise RuntimeError(
                    f"{db_path.name}: pages table missing required columns: " + ", ".join(sorted(missing))
                )
            selected = [name for name in PRIVATE_OUTPUT_COLUMNS if name in columns]
            sql = "SELECT " + ", ".join(quote_identifier(name) for name in selected) + " FROM pages"
            for source_row in connection.execute(sql):
                row = {name: source_row[name] if name in source_row.keys() else None for name in PRIVATE_OUTPUT_COLUMNS}
                page_id = str(row.get("page_id") or "").strip()
                if not page_id:
                    raise RuntimeError(f"{db_path.name}: blank page_id")
                fingerprint = page_fingerprint(row)
                previous = seen.get(page_id)
                if previous is not None:
                    if previous[0] != fingerprint:
                        raise RuntimeError(f"conflicting duplicate page_id: {page_id} in {db_path.name}")
                    duplicate_rows += 1
                    continue
                seen[page_id] = (fingerprint, row)
        finally:
            connection.close()

    iter_source_pages.duplicate_rows = duplicate_rows
    for page_id in sorted(seen):
        yield seen[page_id][1]


iter_source_pages.duplicate_rows = 0


def canonical_input_hashes(db_paths: list[Path]) -> list[dict]:
    """Return content-addressed input identities independent of local filenames and paths."""
    records = [
        {"sha256": sha256_file(path), "bytes": path.stat().st_size}
        for path in db_paths
    ]
    records.sort(key=lambda row: (row["sha256"], row["bytes"]))
    return records


def initialize_index(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA foreign_keys=ON;
        PRAGMA journal_mode=DELETE;
        PRAGMA synchronous=NORMAL;

        CREATE TABLE index_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE pages (
            id INTEGER PRIMARY KEY,
            page_id TEXT NOT NULL UNIQUE,
            viewer_key TEXT NOT NULL,
            canonical_viewer_key TEXT NOT NULL,
            wave TEXT,
            catalog_generation INTEGER,
            grade_code INTEGER,
            title_core TEXT,
            page_index INTEGER,
            viewer_page INTEGER,
            source_asset_url TEXT,
            source_sha256 TEXT,
            source_byte_size INTEGER,
            ocr_engine TEXT,
            ocr_engine_version TEXT,
            ocr_language TEXT,
            ocr_psm INTEGER,
            ocr_sha256 TEXT,
            search_text TEXT NOT NULL,
            search_text_sha256 TEXT,
            ocr_confidence_mean REAL,
            ocr_char_count INTEGER,
            ocr_word_count INTEGER,
            generated_at TEXT
        );

        CREATE INDEX pages_generation_idx ON pages(catalog_generation);
        CREATE INDEX pages_grade_idx ON pages(grade_code);
        CREATE INDEX pages_wave_idx ON pages(wave);
        CREATE INDEX pages_object_idx ON pages(canonical_viewer_key);
        CREATE INDEX pages_source_sha_idx ON pages(source_sha256);
        CREATE INDEX pages_ocr_sha_idx ON pages(ocr_sha256);

        CREATE VIRTUAL TABLE pages_fts USING fts5(
            search_text,
            content='pages',
            content_rowid='id',
            tokenize='unicode61 remove_diacritics 2'
        );
        """
    )


def insert_page(connection: sqlite3.Connection, row: dict) -> None:
    values = [row.get(name) for name in PRIVATE_OUTPUT_COLUMNS]
    search_index = PRIVATE_OUTPUT_COLUMNS.index("search_text")
    values[search_index] = values[search_index] or ""
    sql = (
        "INSERT INTO pages (" + ", ".join(quote_identifier(name) for name in PRIVATE_OUTPUT_COLUMNS) + ") "
        + "VALUES (" + ", ".join("?" for _ in PRIVATE_OUTPUT_COLUMNS) + ")"
    )
    connection.execute(sql, values)


def verify_index(connection: sqlite3.Connection, expected_pages: int | None, expected_objects: int | None) -> dict:
    page_count = connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    object_count = connection.execute("SELECT COUNT(DISTINCT canonical_viewer_key) FROM pages").fetchone()[0]
    fts_count = connection.execute("SELECT COUNT(*) FROM pages_fts").fetchone()[0]
    if page_count != fts_count:
        raise RuntimeError(f"FTS cardinality mismatch: pages={page_count}, pages_fts={fts_count}")
    if expected_pages is not None and page_count != expected_pages:
        raise RuntimeError(f"page cardinality mismatch: got {page_count}, expected {expected_pages}")
    if expected_objects is not None and object_count != expected_objects:
        raise RuntimeError(f"object cardinality mismatch: got {object_count}, expected {expected_objects}")

    duplicate_page_ids = connection.execute(
        "SELECT COUNT(*) FROM (SELECT page_id FROM pages GROUP BY page_id HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    if duplicate_page_ids:
        raise RuntimeError(f"universal index contains duplicate page_id values: {duplicate_page_ids}")

    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if integrity != "ok":
        raise RuntimeError(f"SQLite integrity_check failed: {integrity}")

    return {
        "unique_pages": page_count,
        "unique_canonical_objects": object_count,
        "fts_rows": fts_count,
        "duplicate_page_ids": duplicate_page_ids,
        "sqlite_integrity_check": integrity,
    }


def summarize_dimensions(connection: sqlite3.Connection) -> dict:
    def counter(query: str) -> dict[str, int]:
        return {str(key): int(value) for key, value in connection.execute(query)}

    return {
        "by_generation": counter(
            "SELECT catalog_generation, COUNT(*) FROM pages GROUP BY catalog_generation ORDER BY catalog_generation"
        ),
        "by_wave": counter("SELECT wave, COUNT(*) FROM pages GROUP BY wave ORDER BY wave"),
        "by_grade": counter("SELECT grade_code, COUNT(*) FROM pages GROUP BY grade_code ORDER BY grade_code"),
    }


def write_meta(connection: sqlite3.Connection, values: dict[str, object]) -> None:
    connection.executemany(
        "INSERT OR REPLACE INTO index_meta(key, value) VALUES (?, ?)",
        [(key, json.dumps(value, ensure_ascii=False, sort_keys=True)) for key, value in sorted(values.items())],
    )


def build_index(
    db_paths: list[Path],
    output_path: Path,
    manifest_path: Path,
    expected_pages: int | None,
    expected_objects: int | None,
) -> dict:
    output_path = output_path.expanduser().resolve()
    manifest_path = manifest_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    input_hashes = canonical_input_hashes(db_paths)

    connection = sqlite3.connect(str(output_path))
    try:
        initialize_index(connection)
        for row in iter_source_pages(db_paths):
            insert_page(connection, row)
        connection.commit()

        connection.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
        connection.commit()

        verification = verify_index(connection, expected_pages, expected_objects)
        dimensions = summarize_dimensions(connection)
        write_meta(
            connection,
            {
                "builder_version": VERSION,
                "canonical_row_order": "page_id_ascending",
                "unique_pages": verification["unique_pages"],
                "unique_canonical_objects": verification["unique_canonical_objects"],
                "text_verified": False,
                "semantic_ready": False,
                "private_index": True,
            },
        )
        connection.commit()
        connection.execute("VACUUM")
    finally:
        connection.close()

    index_sha256 = sha256_file(output_path)
    manifest = {
        "manifest_version": VERSION,
        "input": {
            "database_count": len(db_paths),
            "database_hashes": input_hashes,
            "database_hash_order": "sha256_ascending",
            "private_paths_emitted": False,
        },
        "reconciliation": {
            **verification,
            "identical_duplicate_rows_deduplicated": int(iter_source_pages.duplicate_rows),
            "conflicts": 0,
            "canonical_row_order": "page_id_ascending",
        },
        "dimensions": dimensions,
        "index": {
            "format": "SQLite3 + FTS5",
            "fts_table": "pages_fts",
            "tokenizer": "unicode61 remove_diacritics 2",
            "canonical_row_order": "page_id_ascending",
            "sha256": index_sha256,
            "private": True,
            "contains_search_text": True,
            "publish_index_file": False,
        },
        "scientific_state": {
            "ocr_available": True,
            "text_verified": False,
            "semantic_ready": False,
            "search_result_state": "computational_candidate",
            "human_validation_required_for_semantic_ready": True,
        },
        "privacy": {
            "ocr_text_in_manifest": False,
            "source_urls_in_manifest": False,
            "page_ids_in_manifest": False,
            "private_storage_paths_in_manifest": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", action="append", default=[], help="Explicit input SQLite; repeatable")
    parser.add_argument("--db-dir", action="append", default=[], help="Directory searched recursively; repeatable")
    parser.add_argument("--glob", default="*.sqlite", help="Filename glob used under --db-dir")
    parser.add_argument("--output", required=True, help="Private universal SQLite output")
    parser.add_argument("--manifest", required=True, help="Text-free JSON manifest output")
    parser.add_argument("--expected-pages", type=int, default=EXPECTED_U1_PAGES)
    parser.add_argument("--expected-objects", type=int, default=EXPECTED_U1_OBJECTS)
    parser.add_argument(
        "--no-u1-cardinality-gate",
        action="store_true",
        help="Disable 86,549/492 gates for synthetic tests or non-U1 development only",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    db_paths = collect_db_paths(args.db, args.db_dir, args.glob)
    expected_pages = None if args.no_u1_cardinality_gate else args.expected_pages
    expected_objects = None if args.no_u1_cardinality_gate else args.expected_objects
    manifest = build_index(
        db_paths,
        Path(args.output),
        Path(args.manifest),
        expected_pages,
        expected_objects,
    )
    print(json.dumps({
        "builder_version": VERSION,
        "database_count": manifest["input"]["database_count"],
        "unique_pages": manifest["reconciliation"]["unique_pages"],
        "unique_canonical_objects": manifest["reconciliation"]["unique_canonical_objects"],
        "index_sha256": manifest["index"]["sha256"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
