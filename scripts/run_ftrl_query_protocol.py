#!/usr/bin/env python3
"""Execute a preregistered LTMD FTRL query protocol against a local FTS5 index."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

VERSION = "LTMD_FTRL_QUERY_PROTOCOL_0.1"
REQUIRED_COLUMNS = {
    "query_id",
    "construct",
    "query_expression",
    "role",
    "scope_wave",
    "verification_rule",
    "interpretive_rule",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_protocol(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or not REQUIRED_COLUMNS <= set(reader.fieldnames):
            raise SystemExit(
                f"query protocol lacks required columns: {sorted(REQUIRED_COLUMNS)}"
            )
        rows = [dict(row) for row in reader]
    if not rows:
        raise SystemExit("query protocol is empty")
    ids = [row["query_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("query protocol contains duplicate query_id values")
    return rows


def count_hits(conn: sqlite3.Connection, query: str, wave: str | None) -> int:
    where = ["pages_fts MATCH ?"]
    params: list[object] = [query]
    if wave:
        where.append("p.wave = ?")
        params.append(wave)
    sql = f"""
        SELECT COUNT(*)
        FROM pages_fts
        JOIN pages p ON p.id = pages_fts.rowid
        WHERE {' AND '.join(where)}
    """
    return int(conn.execute(sql, params).fetchone()[0])


def fetch_hits(
    conn: sqlite3.Connection,
    query: str,
    wave: str | None,
    max_hits: int,
    context_tokens: int,
) -> list[dict]:
    where = ["pages_fts MATCH ?"]
    params: list[object] = [query]
    if wave:
        where.append("p.wave = ?")
        params.append(wave)
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
    params.append(max_hits)
    cur = conn.execute(sql, params)
    columns = [description[0] for description in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def summarize_hits(
    row: dict[str, str], hits: list[dict], exact_count: int, max_hits: int
) -> dict:
    generations = Counter(str(hit["catalog_generation"]) for hit in hits)
    grades = Counter(str(hit["grade_code"]) for hit in hits)
    canonical = {str(hit["canonical_viewer_key"]) for hit in hits}
    historical: set[str] = set()
    for hit in hits:
        historical.update(
            key for key in str(hit.get("historical_viewers") or "").split("|") if key
        )
    return {
        "query_id": row["query_id"],
        "construct": row["construct"],
        "role": row["role"],
        "scope_wave": row["scope_wave"] or None,
        "query_expression_sha256": sha256_text(row["query_expression"]),
        "hit_pages_exact": exact_count,
        "candidate_rows_materialized": len(hits),
        "candidate_rows_truncated": exact_count > max_hits,
        "canonical_viewers_in_materialized_hits": len(canonical),
        "historical_identities_in_materialized_hits": len(historical),
        "materialized_hits_by_generation": dict(sorted(generations.items())),
        "materialized_hits_by_grade": dict(
            sorted(grades.items(), key=lambda item: int(item[0]))
        ),
        "verification_rule": row["verification_rule"],
        "interpretive_rule": row["interpretive_rule"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, required=True, help="Local candidate results JSON"
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        required=True,
        help="Text-free aggregate summary JSON",
    )
    parser.add_argument("--max-hits", type=int, default=5000)
    parser.add_argument("--context-tokens", type=int, default=24)
    args = parser.parse_args()

    if args.max_hits < 1:
        raise SystemExit("--max-hits must be >= 1")
    if args.context_tokens < 1:
        raise SystemExit("--context-tokens must be >= 1")
    if not args.db.exists():
        raise SystemExit(f"missing database: {args.db}")

    protocol = load_protocol(args.protocol)
    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        results = []
        summaries = []
        for row in protocol:
            query = row["query_expression"]
            wave = row["scope_wave"] or None
            try:
                exact_count = count_hits(conn, query, wave)
                hits = fetch_hits(conn, query, wave, args.max_hits, args.context_tokens)
            except sqlite3.OperationalError as exc:
                raise SystemExit(f"FTS query {row['query_id']} failed: {exc}") from exc
            results.append(
                {
                    "query_id": row["query_id"],
                    "construct": row["construct"],
                    "query_expression": query,
                    "role": row["role"],
                    "scope_wave": wave,
                    "verification_rule": row["verification_rule"],
                    "interpretive_rule": row["interpretive_rule"],
                    "hit_pages_exact": exact_count,
                    "hits": hits,
                }
            )
            summaries.append(summarize_hits(row, hits, exact_count, args.max_hits))
    finally:
        conn.close()

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    protocol_sha256 = hashlib.sha256(args.protocol.read_bytes()).hexdigest()
    full_payload = {
        "schema_version": VERSION,
        "generated_at": generated_at,
        "protocol_sha256": protocol_sha256,
        "rights_note": (
            "Local candidate output may contain OCR snippets and is not intended for versioning "
            "or redistribution without separate rights review."
        ),
        "queries": results,
    }
    summary_payload = {
        "schema_version": VERSION,
        "generated_at": generated_at,
        "protocol_sha256": protocol_sha256,
        "rights_note": "Text-free aggregate query summary; contains no OCR snippets.",
        "queries": summaries,
    }

    for path, payload in (
        (args.output, full_payload),
        (args.summary_output, summary_payload),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temp.replace(path)

    print(
        json.dumps(
            {
                "status": "ok",
                "queries": len(protocol),
                "total_exact_hits_across_queries": sum(
                    item["hit_pages_exact"] for item in summaries
                ),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
