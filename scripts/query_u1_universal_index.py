#!/usr/bin/env python3
"""Query the private LTMD-U1 Universal Index and emit aggregate-only results.

Version: LTMD_U1_CORPUS_QUERY_ENGINE_0.1

The engine executes an FTS5 expression against the private Universal Index, applies exact
corpus filters, and returns only aggregate counts/rates. It never emits OCR/search text,
page IDs, source URLs, source/OCR hashes, snippets, or private filesystem paths.

Scientific boundary:
    ocr_available != text_verified
    search_hit != historical_claim
    zero_hits != demonstrated_absence
    computational_candidate != semantic_ready
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Iterable

ENGINE_VERSION = "LTMD_U1_CORPUS_QUERY_ENGINE_0.1"
INDEX_VERSION = "LTMD_U1_UNIVERSAL_INDEX_0.1"
MAX_QUERY_LENGTH = 500
MAX_FILTER_VALUES = 50
ALLOWED_GROUP_BY = {"generation", "grade_code", "wave"}
DIMENSION_COLUMNS = {
    "generation": "catalog_generation",
    "grade_code": "grade_code",
    "wave": "wave",
}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
WAVE_RE = re.compile(r"^W\d+$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_numeric_values(name: str, values: Iterable[str] | None) -> list[int]:
    if not values:
        return []
    normalized: set[int] = set()
    for raw in values:
        value = str(raw).strip()
        if not value or not value.isdigit():
            raise RuntimeError(f"{name} values must be unsigned integers")
        normalized.add(int(value))
    if len(normalized) > MAX_FILTER_VALUES:
        raise RuntimeError(f"too many {name} values; maximum is {MAX_FILTER_VALUES}")
    return sorted(normalized)


def normalize_wave_values(values: Iterable[str] | None) -> list[str]:
    if not values:
        return []
    normalized = {str(value).strip().upper() for value in values if str(value).strip()}
    if len(normalized) > MAX_FILTER_VALUES:
        raise RuntimeError(f"too many wave values; maximum is {MAX_FILTER_VALUES}")
    invalid = sorted(value for value in normalized if not WAVE_RE.fullmatch(value))
    if invalid:
        raise RuntimeError("invalid wave value(s): " + ", ".join(invalid))
    return sorted(normalized, key=lambda value: int(value[1:]))


def normalize_filters(filters: dict[str, Iterable[str] | None]) -> dict[str, list]:
    return {
        "generation": normalize_numeric_values("generation", filters.get("generation")),
        "grade_code": normalize_numeric_values("grade_code", filters.get("grade_code")),
        "wave": normalize_wave_values(filters.get("wave")),
    }


def validate_query_expression(query_expression: str) -> str:
    value = str(query_expression or "").strip()
    if not value:
        raise RuntimeError("FTS query must not be blank")
    if len(value) > MAX_QUERY_LENGTH:
        raise RuntimeError(f"FTS query exceeds {MAX_QUERY_LENGTH} characters")
    if "\x00" in value:
        raise RuntimeError("FTS query contains a NUL byte")
    return value


def validate_index(connection: sqlite3.Connection) -> dict:
    tables = {
        row[0]
        for row in connection.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
    }
    missing = {"pages", "pages_fts", "index_meta"} - tables
    if missing:
        raise RuntimeError("not an LTMD-U1 Universal Index; missing: " + ", ".join(sorted(missing)))

    columns = {row[1] for row in connection.execute("PRAGMA table_info(pages)")}
    required = {
        "id", "page_id", "canonical_viewer_key", "wave", "catalog_generation",
        "grade_code", "search_text",
    }
    missing_columns = required - columns
    if missing_columns:
        raise RuntimeError("Universal Index pages table missing: " + ", ".join(sorted(missing_columns)))

    meta = {}
    for key, raw in connection.execute("SELECT key, value FROM index_meta"):
        try:
            meta[key] = json.loads(raw)
        except json.JSONDecodeError:
            meta[key] = raw
    if meta.get("builder_version") != INDEX_VERSION:
        raise RuntimeError(
            f"unsupported Universal Index version: {meta.get('builder_version')!r}; expected {INDEX_VERSION}"
        )
    return meta


def build_filter_clause(filters: dict[str, list], alias: str = "p") -> tuple[str, list]:
    clauses = []
    params: list = []
    for public_name in ("generation", "grade_code", "wave"):
        values = filters.get(public_name) or []
        if not values:
            continue
        column = DIMENSION_COLUMNS[public_name]
        placeholders = ",".join("?" for _ in values)
        clauses.append(f"{alias}.{column} IN ({placeholders})")
        params.extend(values)
    return (" AND ".join(clauses) if clauses else "1=1"), params


def count_scope(connection: sqlite3.Connection, filters: dict[str, list]) -> dict:
    where, params = build_filter_clause(filters)
    row = connection.execute(
        f"SELECT COUNT(*), COUNT(DISTINCT p.canonical_viewer_key) FROM pages p WHERE {where}",
        params,
    ).fetchone()
    return {"corpus_pages_in_scope": int(row[0]), "corpus_books_in_scope": int(row[1])}


def count_hits(connection: sqlite3.Connection, query_expression: str, filters: dict[str, list]) -> dict:
    where, params = build_filter_clause(filters)
    sql = f"""
        SELECT COUNT(*), COUNT(DISTINCT p.canonical_viewer_key)
        FROM pages_fts f
        JOIN pages p ON p.id = f.rowid
        WHERE pages_fts MATCH ? AND {where}
    """
    try:
        row = connection.execute(sql, [query_expression, *params]).fetchone()
    except sqlite3.OperationalError as exc:
        raise RuntimeError("invalid FTS5 query expression") from exc
    return {"candidate_pages": int(row[0]), "candidate_books": int(row[1])}


def combine_metrics(scope: dict, hits: dict) -> dict:
    corpus_pages = scope["corpus_pages_in_scope"]
    candidate_pages = hits["candidate_pages"]
    return {
        **hits,
        **scope,
        "candidate_pages_per_1000": (
            candidate_pages / corpus_pages * 1000 if corpus_pages else None
        ),
    }


def group_values(connection: sqlite3.Connection, filters: dict[str, list], group_by: str) -> list:
    if group_by not in ALLOWED_GROUP_BY:
        raise RuntimeError("group_by must be one of: " + ", ".join(sorted(ALLOWED_GROUP_BY)))
    column = DIMENSION_COLUMNS[group_by]
    where, params = build_filter_clause(filters)
    rows = connection.execute(
        f"SELECT DISTINCT p.{column} FROM pages p WHERE {where} ORDER BY p.{column}",
        params,
    ).fetchall()
    return [row[0] for row in rows]


def with_group_filter(filters: dict[str, list], group_by: str, value) -> dict[str, list]:
    result = {key: list(values) for key, values in filters.items()}
    result[group_by] = [value]
    return result


def build_breakdown(
    connection: sqlite3.Connection,
    query_expression: str,
    filters: dict[str, list],
    group_by: str,
) -> list[dict]:
    breakdown = []
    for value in group_values(connection, filters, group_by):
        group_filters = with_group_filter(filters, group_by, value)
        scope = count_scope(connection, group_filters)
        hits = count_hits(connection, query_expression, group_filters)
        breakdown.append({
            "dimension": group_by,
            "value": str(value),
            "result_state": "exploratory_signal",
            "metrics": combine_metrics(scope, hits),
        })
    return breakdown


def query_index(
    connection: sqlite3.Connection,
    *,
    query_expression: str,
    filters: dict[str, Iterable[str] | None] | None = None,
    group_by: str | None = None,
    index_sha256: str | None = None,
) -> dict:
    expression = validate_query_expression(query_expression)
    normalized_filters = normalize_filters(filters or {})
    validate_index(connection)
    if group_by is not None and group_by not in ALLOWED_GROUP_BY:
        raise RuntimeError("group_by must be one of: " + ", ".join(sorted(ALLOWED_GROUP_BY)))
    if index_sha256 is not None and not SHA256_RE.fullmatch(index_sha256):
        raise RuntimeError("index_sha256 must be a lowercase SHA-256 value")

    scope = count_scope(connection, normalized_filters)
    hits = count_hits(connection, expression, normalized_filters)
    metrics = combine_metrics(scope, hits)

    warnings = [
        "FTS5 matches are computational candidates/exploratory signals, not validated historical claims.",
        "OCR-derived search text is not human-verified text.",
    ]
    if hits["candidate_pages"] == 0:
        warnings.append("Zero FTS5 hits do not demonstrate historical absence.")

    response = {
        "query": expression,
        "filters": normalized_filters,
        "result_state": "exploratory_signal",
        "metrics": metrics,
        "provenance": {
            "query_engine_version": ENGINE_VERSION,
            "index_version": INDEX_VERSION,
            "index_sha256": index_sha256,
            "human_validation_complete": False,
        },
        "warnings": warnings,
    }
    if group_by:
        response["group_by"] = group_by
        response["breakdown"] = build_breakdown(
            connection, expression, normalized_filters, group_by
        )
    return response


def run(
    index_path: Path,
    *,
    query_expression: str,
    filters: dict[str, Iterable[str] | None] | None = None,
    group_by: str | None = None,
    expected_index_sha256: str | None = None,
) -> dict:
    path = index_path.expanduser().resolve()
    if not path.is_file():
        raise RuntimeError("Universal Index file is unavailable")

    verified_sha = None
    if expected_index_sha256 is not None:
        expected = expected_index_sha256.strip().lower()
        if not SHA256_RE.fullmatch(expected):
            raise RuntimeError("expected index SHA-256 is invalid")
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError("Universal Index SHA-256 mismatch")
        verified_sha = actual

    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        return query_index(
            connection,
            query_expression=query_expression,
            filters=filters,
            group_by=group_by,
            index_sha256=verified_sha,
        )
    finally:
        connection.close()


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True, help="Private LTMD-U1 Universal Index SQLite")
    parser.add_argument("--query", required=True, help="FTS5 MATCH expression")
    parser.add_argument("--generation", action="append")
    parser.add_argument("--grade-code", action="append")
    parser.add_argument("--wave", action="append")
    parser.add_argument("--group-by", choices=sorted(ALLOWED_GROUP_BY))
    parser.add_argument("--expected-index-sha256")
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    response = run(
        Path(args.index),
        query_expression=args.query,
        filters={
            "generation": args.generation,
            "grade_code": args.grade_code,
            "wave": args.wave,
        },
        group_by=args.group_by,
        expected_index_sha256=args.expected_index_sha256,
    )
    payload = json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
