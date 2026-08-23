#!/usr/bin/env python3
"""Query an LTMD local SQLite FTS5 full-text index."""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path


def resolve_viewer(conn: sqlite3.Connection, viewer_key: str) -> str:
    row = conn.execute(
        "SELECT canonical_viewer_key FROM identities WHERE viewer_key=?",
        (viewer_key,),
    ).fetchone()
    return row[0] if row else viewer_key


def query_rows(
    conn: sqlite3.Connection,
    query: str,
    viewer_key: str | None,
    wave: str | None,
    generation: int | None,
    grade_code: int | None,
    limit: int,
    context_tokens: int,
) -> list[dict]:
    where = ["pages_fts MATCH ?"]
    params: list[object] = [query]
    if viewer_key:
        where.append("p.viewer_key = ?")
        params.append(resolve_viewer(conn, viewer_key))
    if wave:
        where.append("p.wave = ?")
        params.append(wave)
    if generation is not None:
        where.append("p.catalog_generation = ?")
        params.append(generation)
    if grade_code is not None:
        where.append("p.grade_code = ?")
        params.append(grade_code)

    sql = f"""
        SELECT
            p.page_id,
            p.viewer_key AS canonical_viewer_key,
            p.wave,
            p.catalog_generation,
            p.grade_code,
            p.title_core,
            p.page_index,
            p.viewer_page,
            p.source_asset_url,
            p.source_sha256,
            p.ocr_sha256,
            p.ocr_confidence_mean,
            snippet(pages_fts, 0, '[', ']', ' … ', {int(context_tokens)}) AS snippet,
            bm25(pages_fts) AS rank,
            COALESCE((
                SELECT group_concat(i.viewer_key, '|')
                FROM identities i
                WHERE i.canonical_viewer_key = p.viewer_key
            ), p.viewer_key) AS historical_viewers
        FROM pages_fts
        JOIN pages p ON p.id = pages_fts.rowid
        WHERE {' AND '.join(where)}
        ORDER BY rank, p.catalog_generation, p.grade_code, p.viewer_key, p.page_index
        LIMIT ?
    """
    params.append(limit)
    cur = conn.execute(sql, params)
    columns = [description[0] for description in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def emit(rows: list[dict], output_format: str) -> None:
    if output_format == "json":
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if not rows:
        print("No matches.")
        return
    delimiter = "\t" if output_format == "tsv" else ","
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]), delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        epilog=(
            'FTS5 examples: --query \'"Benito Juárez"\' ; '
            "--query 'masonería OR masón OR masones' ; "
            "--query 'NEAR(logia yorkino, 20)'"
        )
    )
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--viewer-key")
    parser.add_argument("--wave")
    parser.add_argument("--generation", type=int)
    parser.add_argument("--grade-code", type=int)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--context-tokens", type=int, default=24)
    parser.add_argument("--format", choices=("tsv", "csv", "json"), default="tsv")
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("--limit must be >= 1")
    if args.context_tokens < 1:
        raise SystemExit("--context-tokens must be >= 1")

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        rows = query_rows(
            conn,
            args.query,
            args.viewer_key,
            args.wave,
            args.generation,
            args.grade_code,
            args.limit,
            args.context_tokens,
        )
    except sqlite3.OperationalError as exc:
        raise SystemExit(f"FTS query failed: {exc}") from exc
    finally:
        conn.close()

    emit(rows, args.format)


if __name__ == "__main__":
    main()
