#!/usr/bin/env python3
"""Build a local SQLite FTS5 index from LTMD page-level OCR JSONL."""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path

VERSION = "LTMD_FTRL_INDEX_0.1"


def load_records(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSON at {path}:{line_number}: {exc}") from exc
    if not records:
        raise SystemExit("OCR corpus is empty")
    return records


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE pages (
            id INTEGER PRIMARY KEY,
            page_id TEXT NOT NULL UNIQUE,
            viewer_key TEXT NOT NULL,
            canonical_viewer_key TEXT NOT NULL,
            wave TEXT NOT NULL,
            catalog_generation INTEGER NOT NULL,
            grade_code INTEGER NOT NULL,
            title_core TEXT NOT NULL,
            page_index INTEGER NOT NULL,
            viewer_page INTEGER,
            source_asset_url TEXT NOT NULL,
            source_sha256 TEXT NOT NULL,
            source_byte_size INTEGER,
            ocr_engine TEXT NOT NULL,
            ocr_engine_version TEXT NOT NULL,
            ocr_language TEXT NOT NULL,
            ocr_psm INTEGER NOT NULL,
            ocr_text_raw TEXT NOT NULL,
            ocr_sha256 TEXT NOT NULL,
            search_text TEXT NOT NULL,
            search_text_sha256 TEXT NOT NULL,
            ocr_confidence_mean REAL,
            ocr_char_count INTEGER NOT NULL,
            ocr_word_count INTEGER NOT NULL,
            pipeline_version TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            UNIQUE(viewer_key, page_index)
        );
        CREATE INDEX pages_wave_idx ON pages(wave);
        CREATE INDEX pages_generation_idx ON pages(catalog_generation);
        CREATE INDEX pages_grade_idx ON pages(grade_code);
        CREATE INDEX pages_viewer_idx ON pages(viewer_key);

        CREATE TABLE identities (
            viewer_key TEXT PRIMARY KEY,
            canonical_viewer_key TEXT NOT NULL,
            catalog_generation INTEGER,
            grade_code INTEGER,
            title_core TEXT,
            processing_mode TEXT,
            technical_identity_covered INTEGER NOT NULL DEFAULT 1,
            is_canonical_processing_object INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX identities_canonical_idx ON identities(canonical_viewer_key);
        """
    )
    try:
        conn.execute(
            """
            CREATE VIRTUAL TABLE pages_fts USING fts5(
                search_text,
                content='pages',
                content_rowid='id',
                tokenize='unicode61 remove_diacritics 2'
            )
            """
        )
    except sqlite3.OperationalError as exc:
        raise SystemExit(
            "SQLite FTS5 is unavailable in this Python/SQLite build"
        ) from exc


def insert_pages(conn: sqlite3.Connection, records: list[dict]) -> None:
    columns = [
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
        "source_byte_size",
        "ocr_engine",
        "ocr_engine_version",
        "ocr_language",
        "ocr_psm",
        "ocr_text_raw",
        "ocr_sha256",
        "search_text",
        "search_text_sha256",
        "ocr_confidence_mean",
        "ocr_char_count",
        "ocr_word_count",
        "pipeline_version",
        "generated_at",
    ]
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT INTO pages ({','.join(columns)}) VALUES ({placeholders})"
    for record in records:
        missing = [key for key in columns if key not in record]
        if missing:
            raise SystemExit(f"{record.get('page_id', '<unknown>')} missing {missing}")
        conn.execute(sql, [record[key] for key in columns])

    conn.execute(
        "INSERT INTO pages_fts(rowid, search_text) SELECT id, search_text FROM pages"
    )


def load_identities(
    conn: sqlite3.Connection,
    records: list[dict],
    processing_inventory: Path | None,
) -> None:
    if processing_inventory is None:
        derived = {}
        for record in records:
            derived.setdefault(
                record["viewer_key"],
                (
                    record["viewer_key"],
                    record["canonical_viewer_key"],
                    record["catalog_generation"],
                    record["grade_code"],
                    record["title_core"],
                    "canonical_ocr_record",
                    1,
                    1,
                ),
            )
        conn.executemany(
            "INSERT INTO identities VALUES (?,?,?,?,?,?,?,?)", derived.values()
        )
        return

    rows = list(
        csv.DictReader(processing_inventory.open(encoding="utf-8", newline=""))
    )
    required = {
        "viewer_key",
        "canonical_processing_viewer_key",
        "catalog_generation",
        "grade_code",
        "title_core",
        "processing_mode",
        "technical_identity_covered",
        "is_canonical_processing_object",
    }
    if not rows or not required <= set(rows[0]):
        raise SystemExit(f"processing inventory lacks required columns: {sorted(required)}")

    page_canonicals = {record["viewer_key"] for record in records}
    values = []
    for row in rows:
        canonical = row["canonical_processing_viewer_key"]
        if row["technical_identity_covered"] != "1":
            continue
        if canonical not in page_canonicals:
            continue
        values.append(
            (
                row["viewer_key"],
                canonical,
                int(row["catalog_generation"]),
                int(row["grade_code"]),
                row["title_core"],
                row["processing_mode"],
                int(row["technical_identity_covered"]),
                int(row["is_canonical_processing_object"]),
            )
        )
    conn.executemany("INSERT INTO identities VALUES (?,?,?,?,?,?,?,?)", values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Page OCR JSONL")
    parser.add_argument("--output", type=Path, required=True, help="SQLite database")
    parser.add_argument("--processing-inventory", type=Path)
    args = parser.parse_args()

    records = load_records(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        args.output.unlink()

    conn = sqlite3.connect(args.output)
    try:
        create_schema(conn)
        insert_pages(conn, records)
        load_identities(conn, records, args.processing_inventory)
        conn.executemany(
            "INSERT INTO metadata(key,value) VALUES (?,?)",
            [
                ("index_version", VERSION),
                ("source_jsonl", str(args.input)),
                ("page_count", str(len(records))),
            ],
        )
        conn.commit()
        pages = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        fts = conn.execute("SELECT COUNT(*) FROM pages_fts").fetchone()[0]
        identities = conn.execute("SELECT COUNT(*) FROM identities").fetchone()[0]
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if pages != len(records) or fts != pages or integrity != "ok":
            raise SystemExit(
                f"index validation failed: pages={pages}, fts={fts}, integrity={integrity}"
            )
        conn.execute("PRAGMA journal_mode=DELETE")
    finally:
        conn.close()

    print(
        f"Built {args.output}: pages={pages}, FTS rows={fts}, "
        f"historical identities={identities}"
    )


if __name__ == "__main__":
    main()
