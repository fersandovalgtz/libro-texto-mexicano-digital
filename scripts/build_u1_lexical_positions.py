#!/usr/bin/env python3
"""Materialize private lexical positions and aggregate unigram statistics from LTMD-U1 FTS5.

Version: LTMD_U1_LEXICAL_POSITIONS_BUILDER_0.1

The output SQLite is PRIVATE. It contains the normalized FTS5 vocabulary and token positions
needed for dispersion, n-grams and co-occurrence analysis. Public output is limited to a
text-free aggregate summary.

Scientific boundaries:
  ocr_available != text_verified
  frequency != semantic meaning
  computational_candidate != semantic_ready
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

BUILDER_VERSION = "LTMD_U1_LEXICAL_POSITIONS_BUILDER_0.1"
ARTIFACT_VERSION = "LTMD_U1_LEXICAL_POSITIONS_0.1"
INDEX_VERSION = "LTMD_U1_UNIVERSAL_INDEX_0.1"
EXPECTED_TOKENIZER = "unicode61 remove_diacritics 2"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_index_meta(connection: sqlite3.Connection) -> dict:
    tables = {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
    }
    missing = {"pages", "pages_fts", "index_meta"} - tables
    if missing:
        raise RuntimeError("not an LTMD-U1 Universal Index; missing: " + ", ".join(sorted(missing)))
    meta = {}
    for key, raw in connection.execute("SELECT key, value FROM index_meta"):
        try:
            meta[key] = json.loads(raw)
        except json.JSONDecodeError:
            meta[key] = raw
    if meta.get("builder_version") != INDEX_VERSION:
        raise RuntimeError(f"unsupported Universal Index version: {meta.get('builder_version')!r}")
    fts_sql = connection.execute("SELECT sql FROM sqlite_master WHERE name='pages_fts'").fetchone()[0]
    normalized = " ".join(fts_sql.split())
    if "unicode61 remove_diacritics 2" not in normalized:
        raise RuntimeError("Universal Index tokenizer differs from the canonical LTMD-U1 tokenizer")
    return meta


def verify_source(path: Path, expected_sha256: str | None) -> str | None:
    if not path.is_file():
        raise RuntimeError("Universal Index file is unavailable")
    if expected_sha256 is None:
        return None
    expected = expected_sha256.strip().lower()
    if not SHA256_RE.fullmatch(expected):
        raise RuntimeError("expected index SHA-256 is invalid")
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError("Universal Index SHA-256 mismatch")
    return actual


def _remove_sqlite_family(path: Path) -> None:
    for candidate in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
        if candidate.exists():
            candidate.unlink()


def build_private_artifact(index_path: Path, output_path: Path, *, overwrite: bool = False) -> dict:
    index_path = index_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    if output_path.exists() and not overwrite:
        raise RuntimeError("output already exists; pass --overwrite to replace it")
    if overwrite:
        _remove_sqlite_family(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source = sqlite3.connect(f"file:{index_path}?mode=ro", uri=True, timeout=60)
    try:
        source_meta = read_index_meta(source)
        source.execute("ATTACH DATABASE ? AS lex", (str(output_path),))
        source.executescript(
            """
            PRAGMA lex.journal_mode=WAL;
            PRAGMA lex.synchronous=NORMAL;
            PRAGMA lex.cache_size=-200000;
            CREATE TABLE lex.meta(key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
            CREATE TABLE lex.terms(
                term_id INTEGER PRIMARY KEY,
                term TEXT NOT NULL UNIQUE,
                page_count INTEGER NOT NULL,
                occurrence_count INTEGER NOT NULL
            );
            CREATE TABLE lex.objects(
                object_id INTEGER PRIMARY KEY,
                canonical_viewer_key TEXT NOT NULL UNIQUE
            );
            CREATE TABLE lex.pages(
                page_rowid INTEGER PRIMARY KEY,
                object_id INTEGER NOT NULL,
                generation INTEGER,
                grade_code INTEGER,
                wave TEXT
            );
            CREATE TABLE lex.token_positions(
                term_id INTEGER NOT NULL,
                page_rowid INTEGER NOT NULL,
                token_offset INTEGER NOT NULL
            );
            CREATE VIRTUAL TABLE temp.vocab_row USING fts5vocab(main, pages_fts, 'row');
            CREATE VIRTUAL TABLE temp.vocab_instance USING fts5vocab(main, pages_fts, 'instance');
            """
        )
        source.execute(
            "INSERT INTO lex.terms(term,page_count,occurrence_count) "
            "SELECT term,doc,cnt FROM vocab_row ORDER BY term"
        )
        source.execute(
            "INSERT INTO lex.objects(canonical_viewer_key) "
            "SELECT DISTINCT canonical_viewer_key FROM main.pages ORDER BY canonical_viewer_key"
        )
        source.execute(
            """
            INSERT INTO lex.pages(page_rowid,object_id,generation,grade_code,wave)
            SELECT p.id,o.object_id,p.catalog_generation,p.grade_code,p.wave
            FROM main.pages p
            JOIN lex.objects o ON o.canonical_viewer_key=p.canonical_viewer_key
            ORDER BY p.id
            """
        )
        source.commit()

        source.execute(
            """
            INSERT INTO lex.token_positions(term_id,page_rowid,token_offset)
            SELECT t.term_id,v.doc,v.offset
            FROM vocab_instance v
            JOIN lex.terms t ON t.term=v.term
            """
        )
        source.commit()

        source.execute(
            "CREATE INDEX lex.idx_token_positions_page_offset "
            "ON token_positions(page_rowid,token_offset)"
        )
        source.commit()
        source.execute(
            "CREATE INDEX lex.idx_token_positions_term_page "
            "ON token_positions(term_id,page_rowid)"
        )
        source.commit()

        source.execute(
            """
            CREATE TABLE lex.term_pages(
                term_id INTEGER NOT NULL,
                page_rowid INTEGER NOT NULL,
                PRIMARY KEY(term_id,page_rowid)
            ) WITHOUT ROWID
            """
        )
        source.execute(
            "INSERT INTO lex.term_pages(term_id,page_rowid) "
            "SELECT term_id,page_rowid FROM lex.token_positions GROUP BY term_id,page_rowid"
        )
        source.commit()

        source.execute(
            """
            CREATE TABLE lex.term_stats(
                term_id INTEGER PRIMARY KEY,
                page_count INTEGER NOT NULL,
                occurrence_count INTEGER NOT NULL,
                object_count INTEGER NOT NULL,
                generation_count INTEGER NOT NULL,
                grade_count INTEGER NOT NULL,
                wave_count INTEGER NOT NULL
            )
            """
        )
        source.execute(
            """
            INSERT INTO lex.term_stats
            SELECT t.term_id,t.page_count,t.occurrence_count,
                   COUNT(DISTINCT p.object_id),
                   COUNT(DISTINCT p.generation),
                   COUNT(DISTINCT p.grade_code),
                   COUNT(DISTINCT p.wave)
            FROM lex.terms t
            JOIN lex.term_pages tp ON tp.term_id=t.term_id
            JOIN lex.pages p ON p.page_rowid=tp.page_rowid
            GROUP BY t.term_id
            """
        )
        source.commit()

        counts = {
            "unique_terms": int(source.execute("SELECT COUNT(*) FROM lex.terms").fetchone()[0]),
            "token_instances": int(source.execute("SELECT COUNT(*) FROM lex.token_positions").fetchone()[0]),
            "term_page_relations": int(source.execute("SELECT COUNT(*) FROM lex.term_pages").fetchone()[0]),
            "unique_pages": int(source.execute("SELECT COUNT(*) FROM lex.pages").fetchone()[0]),
            "unique_objects": int(source.execute("SELECT COUNT(*) FROM lex.objects").fetchone()[0]),
            "term_stats_rows": int(source.execute("SELECT COUNT(*) FROM lex.term_stats").fetchone()[0]),
        }
        expected_pages = int(source_meta.get("unique_pages", counts["unique_pages"]))
        expected_objects = int(source_meta.get("unique_canonical_objects", counts["unique_objects"]))
        if counts["unique_pages"] != expected_pages:
            raise RuntimeError("lexical page count does not match Universal Index")
        if counts["unique_objects"] != expected_objects:
            raise RuntimeError("lexical object count does not match Universal Index")
        if counts["term_stats_rows"] != counts["unique_terms"]:
            raise RuntimeError("term_stats does not cover the full vocabulary")

        metadata = {
            "builder_version": BUILDER_VERSION,
            "artifact_version": ARTIFACT_VERSION,
            "source_index_version": INDEX_VERSION,
            "tokenizer": EXPECTED_TOKENIZER,
            **counts,
            "private": True,
            "full_vocabulary_private": True,
            "token_positions_private": True,
            "text_verified": False,
            "semantic_ready": False,
            "default_result_state": "exploratory_signal",
        }
        for key, value in metadata.items():
            source.execute(
                "INSERT INTO lex.meta(key,value) VALUES(?,?)",
                (key, json.dumps(value, ensure_ascii=False)),
            )
        source.commit()
        quick = source.execute("PRAGMA lex.quick_check").fetchone()[0]
        if quick != "ok":
            raise RuntimeError("lexical artifact quick_check failed")
        source.execute("PRAGMA lex.wal_checkpoint(TRUNCATE)")
        source.execute("PRAGMA lex.journal_mode=DELETE")
        source.commit()
    finally:
        source.close()

    return {
        "builder_version": BUILDER_VERSION,
        "artifact_version": ARTIFACT_VERSION,
        "source_index_version": INDEX_VERSION,
        "tokenizer": EXPECTED_TOKENIZER,
        "counts": counts,
        "private_artifact": {
            "bytes": output_path.stat().st_size,
            "sha256": sha256_file(output_path),
            "publish": False,
        },
        "privacy": {
            "full_vocabulary_emitted_publicly": False,
            "token_positions_emitted_publicly": False,
            "ocr_text_emitted_publicly": False,
            "page_ids_emitted_publicly": False,
            "source_urls_emitted_publicly": False,
            "rare_terms_publish_by_default": False,
        },
        "scientific_state": {
            "text_verified": False,
            "semantic_ready": False,
            "default_result_state": "exploratory_signal",
            "frequency_is_semantic_claim": False,
        },
    }


def run(index_path: Path, output_path: Path, *, expected_index_sha256: str | None = None, overwrite: bool = False) -> dict:
    verified_source_sha = verify_source(index_path, expected_index_sha256)
    summary = build_private_artifact(index_path, output_path, overwrite=overwrite)
    summary["source_index_sha256"] = verified_source_sha
    return summary


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True, help="Private LTMD-U1 Universal Index SQLite")
    parser.add_argument("--output", required=True, help="Private lexical-position SQLite output")
    parser.add_argument("--summary", help="Optional public-safe aggregate JSON summary")
    parser.add_argument("--expected-index-sha256")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    summary = run(
        Path(args.index),
        Path(args.output),
        expected_index_sha256=args.expected_index_sha256,
        overwrite=args.overwrite,
    )
    payload = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.summary:
        Path(args.summary).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
