#!/usr/bin/env python3
"""Build private dimensional lexical statistics from LTMD-U1 lexical positions.

Version: LTMD_U1_LEXICAL_DIMENSIONS_BUILDER_0.1

This stage never reads OCR/FTS5. It consumes the private lexical-position artifact and emits
only aggregate term-by-dimension statistics plus exact denominators. The output remains private.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

BUILDER_VERSION = "LTMD_U1_LEXICAL_DIMENSIONS_BUILDER_0.1"
ARTIFACT_VERSION = "LTMD_U1_LEXICAL_DIMENSIONS_0.1"
SOURCE_VERSION = "LTMD_U1_LEXICAL_POSITIONS_0.1"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
DIMENSIONS = (("generation", "generation"), ("grade_code", "grade_code"), ("wave", "wave"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_meta(c: sqlite3.Connection) -> dict:
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required = {"meta", "pages", "terms", "token_positions", "term_pages", "term_stats"}
    missing = required - tables
    if missing:
        raise RuntimeError("not an LTMD lexical-position artifact; missing: " + ", ".join(sorted(missing)))
    meta = {}
    for k, raw in c.execute("SELECT key,value FROM meta"):
        try:
            meta[k] = json.loads(raw)
        except json.JSONDecodeError:
            meta[k] = raw
    if meta.get("version") != SOURCE_VERSION and meta.get("artifact_version") != SOURCE_VERSION:
        raise RuntimeError("unsupported lexical-position artifact version")
    return meta


def verify_source(path: Path, expected_sha256: str | None) -> str | None:
    if not path.is_file():
        raise RuntimeError("lexical-position artifact is unavailable")
    if expected_sha256 is None:
        return None
    expected = expected_sha256.strip().lower()
    if not SHA256_RE.fullmatch(expected):
        raise RuntimeError("expected lexical-position SHA-256 is invalid")
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError("lexical-position SHA-256 mismatch")
    return actual


def remove_sqlite_family(path: Path) -> None:
    for p in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
        if p.exists():
            p.unlink()


def build(source_path: Path, output_path: Path, *, overwrite: bool = False) -> dict:
    source_path = source_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    if output_path.exists() and not overwrite:
        raise RuntimeError("output already exists; pass --overwrite to replace it")
    if overwrite:
        remove_sqlite_family(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True, timeout=60)
    try:
        meta = load_meta(c)
        c.execute("ATTACH DATABASE ? AS d", (str(output_path),))
        c.executescript(
            """
            PRAGMA d.journal_mode=WAL;
            PRAGMA d.synchronous=NORMAL;
            PRAGMA d.cache_size=-200000;
            CREATE TABLE d.meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID;
            CREATE TABLE d.term_page_stats(
                term_id INTEGER NOT NULL,
                page_rowid INTEGER NOT NULL,
                occurrence_count INTEGER NOT NULL,
                PRIMARY KEY(term_id,page_rowid)
            ) WITHOUT ROWID;
            CREATE TABLE d.term_dimension_stats(
                dimension TEXT NOT NULL,
                value TEXT NOT NULL,
                term_id INTEGER NOT NULL,
                occurrence_count INTEGER NOT NULL,
                page_count INTEGER NOT NULL,
                object_count INTEGER NOT NULL,
                PRIMARY KEY(dimension,value,term_id)
            ) WITHOUT ROWID;
            CREATE TABLE d.dimension_denominators(
                dimension TEXT NOT NULL,
                value TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                object_count INTEGER NOT NULL,
                PRIMARY KEY(dimension,value)
            ) WITHOUT ROWID;
            """
        )
        c.execute(
            "INSERT INTO d.term_page_stats "
            "SELECT term_id,page_rowid,COUNT(*) FROM main.token_positions GROUP BY term_id,page_rowid"
        )
        c.commit()

        for public_name, column in DIMENSIONS:
            c.execute(
                f"""
                INSERT INTO d.term_dimension_stats
                SELECT ?,CAST(p.{column} AS TEXT),s.term_id,
                       SUM(s.occurrence_count),COUNT(*),COUNT(DISTINCT p.object_id)
                FROM d.term_page_stats s
                JOIN main.pages p ON p.page_rowid=s.page_rowid
                WHERE p.{column} IS NOT NULL
                GROUP BY p.{column},s.term_id
                """,
                (public_name,),
            )
            c.execute(
                f"""
                INSERT INTO d.dimension_denominators
                SELECT ?,CAST({column} AS TEXT),COUNT(*),COUNT(DISTINCT object_id)
                FROM main.pages
                WHERE {column} IS NOT NULL
                GROUP BY {column}
                """,
                (public_name,),
            )
            c.commit()

        counts = {
            "term_page_stats_rows": int(c.execute("SELECT COUNT(*) FROM d.term_page_stats").fetchone()[0]),
            "term_dimension_stats_rows": int(c.execute("SELECT COUNT(*) FROM d.term_dimension_stats").fetchone()[0]),
            "generation_term_rows": int(c.execute("SELECT COUNT(*) FROM d.term_dimension_stats WHERE dimension='generation'").fetchone()[0]),
            "grade_term_rows": int(c.execute("SELECT COUNT(*) FROM d.term_dimension_stats WHERE dimension='grade_code'").fetchone()[0]),
            "wave_term_rows": int(c.execute("SELECT COUNT(*) FROM d.term_dimension_stats WHERE dimension='wave'").fetchone()[0]),
            "dimension_denominator_rows": int(c.execute("SELECT COUNT(*) FROM d.dimension_denominators").fetchone()[0]),
        }
        expected_term_pages = int(meta.get("term_page_relations", counts["term_page_stats_rows"]))
        if counts["term_page_stats_rows"] != expected_term_pages:
            raise RuntimeError("term-page relation count differs from lexical-position artifact")
        unique_pages = int(meta.get("unique_pages", c.execute("SELECT COUNT(*) FROM main.pages").fetchone()[0]))
        for dimension, _ in DIMENSIONS:
            total = c.execute(
                "SELECT SUM(page_count) FROM d.dimension_denominators WHERE dimension=?", (dimension,)
            ).fetchone()[0]
            if int(total or 0) != unique_pages:
                raise RuntimeError(f"{dimension} denominators do not cover all lexical pages")

        metadata = {
            "builder_version": BUILDER_VERSION,
            "artifact_version": ARTIFACT_VERSION,
            "source_version": SOURCE_VERSION,
            **counts,
            "private": True,
            "text_verified": False,
            "semantic_ready": False,
            "default_result_state": "exploratory_signal",
        }
        for k, v in metadata.items():
            c.execute("INSERT INTO d.meta VALUES(?,?)", (k, json.dumps(v, ensure_ascii=False)))
        c.commit()
        if c.execute("PRAGMA d.quick_check").fetchone()[0] != "ok":
            raise RuntimeError("lexical-dimension artifact quick_check failed")
        c.execute("PRAGMA d.wal_checkpoint(TRUNCATE)")
        c.execute("PRAGMA d.journal_mode=DELETE")
        c.commit()
    finally:
        c.close()

    return {
        "builder_version": BUILDER_VERSION,
        "artifact_version": ARTIFACT_VERSION,
        "source_version": SOURCE_VERSION,
        "counts": counts,
        "private_artifact": {
            "bytes": output_path.stat().st_size,
            "sha256": sha256_file(output_path),
            "publish": False,
        },
        "privacy": {
            "term_values_emitted_publicly": False,
            "page_identifiers_emitted_publicly": False,
            "dimension_aggregates_only": True,
        },
        "scientific_state": {
            "text_verified": False,
            "semantic_ready": False,
            "default_result_state": "exploratory_signal",
        },
    }


def run(source_path: Path, output_path: Path, *, expected_source_sha256: str | None = None, overwrite: bool = False) -> dict:
    verified = verify_source(source_path, expected_source_sha256)
    summary = build(source_path, output_path, overwrite=overwrite)
    summary["source_sha256"] = verified
    return summary


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--summary")
    p.add_argument("--expected-source-sha256")
    p.add_argument("--overwrite", action="store_true")
    a = p.parse_args(argv)
    result = run(Path(a.source), Path(a.output), expected_source_sha256=a.expected_source_sha256, overwrite=a.overwrite)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if a.summary:
        Path(a.summary).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
