#!/usr/bin/env python3
"""Build aggregate-only reuse/similarity context for an LTMD vertical candidate ledger.

Version: LTMD_VERTICAL_REUSE_CONTEXT_BUILDER_0.1

The vertical selection itself is not recomputed. Candidate page_ids are mapped to the
private LTMD-U1 Universal Index and contextualized against the private U1 reuse/similarity
artifact. Only aggregate counts are emitted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
from pathlib import Path

BUILDER_VERSION = "LTMD_VERTICAL_REUSE_CONTEXT_BUILDER_0.1"
CONTEXT_VERSION = "LTMD_VERTICAL_REUSE_CONTEXT_0.1"
INDEX_VERSION = "LTMD_U1_UNIVERSAL_INDEX_0.1"
REUSE_VERSION = "LTMD_U1_REUSE_SIMILARITY_0.1"
SHA_RE = re.compile(r"^[a-f0-9]{64}$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha(path: Path, expected: str | None, label: str) -> str:
    if not path.is_file():
        raise RuntimeError(f"{label} is unavailable")
    actual = sha256_file(path)
    if expected is not None:
        exp = expected.strip().lower()
        if not SHA_RE.fullmatch(exp):
            raise RuntimeError(f"expected {label} SHA-256 is invalid")
        if actual != exp:
            raise RuntimeError(f"{label} SHA-256 mismatch")
    return actual


def decode_meta(c: sqlite3.Connection, table: str) -> dict:
    meta = {}
    for key, raw in c.execute(f"SELECT key,value FROM {table}"):
        try:
            meta[key] = json.loads(raw)
        except json.JSONDecodeError:
            meta[key] = raw
    return meta


def validate_index(c: sqlite3.Connection) -> None:
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
    if not {"pages", "index_meta"}.issubset(tables):
        raise RuntimeError("not an LTMD Universal Index")
    meta = decode_meta(c, "index_meta")
    if meta.get("builder_version") != INDEX_VERSION:
        raise RuntimeError("unsupported Universal Index version")


def validate_reuse(c: sqlite3.Connection) -> None:
    required = {
        "meta", "exact_source_groups", "exact_source_members", "exact_text_groups",
        "exact_text_members", "similarity_candidates",
    }
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not required.issubset(tables):
        raise RuntimeError("not an LTMD reuse/similarity artifact")
    meta = decode_meta(c, "meta")
    if meta.get("artifact_version") != REUSE_VERSION:
        raise RuntimeError("unsupported reuse/similarity artifact version")


def load_candidate_page_ids(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "page_id" not in set(reader.fieldnames or []):
            raise RuntimeError("candidate ledger missing page_id")
        page_ids = []
        seen = set()
        for row in reader:
            page_id = str(row.get("page_id") or "").strip()
            if not page_id:
                raise RuntimeError("candidate ledger contains blank page_id")
            if page_id in seen:
                raise RuntimeError("candidate ledger contains duplicate page_id")
            seen.add(page_id)
            page_ids.append(page_id)
    return page_ids


def map_candidates(index: sqlite3.Connection, page_ids: list[str]) -> list[tuple[int, str, int | None]]:
    index.execute("CREATE TEMP TABLE vertical_page_ids(page_id TEXT PRIMARY KEY) WITHOUT ROWID")
    index.executemany("INSERT INTO vertical_page_ids VALUES(?)", ((p,) for p in page_ids))
    rows = index.execute("""
        SELECT p.id,p.page_id,p.catalog_generation
        FROM pages p JOIN vertical_page_ids v ON v.page_id=p.page_id
        ORDER BY p.id
    """).fetchall()
    if len(rows) != len(page_ids):
        mapped = {r[1] for r in rows}
        missing = [p for p in page_ids if p not in mapped]
        raise RuntimeError(f"{len(missing)} candidate page_id values are absent from Universal Index")
    return rows


def _count_distinct(reuse: sqlite3.Connection, sql: str, params=()) -> int:
    return int(reuse.execute(sql, params).fetchone()[0])


def aggregate_context(index_path: Path, reuse_path: Path, page_ids: list[str]) -> dict:
    index = sqlite3.connect(f"file:{index_path}?mode=ro", uri=True)
    reuse = sqlite3.connect(f"file:{reuse_path}?mode=ro", uri=True)
    try:
        validate_index(index)
        validate_reuse(reuse)
        mapped = map_candidates(index, page_ids)
        rowids = [r[0] for r in mapped]
        generation = {r[0]: r[2] for r in mapped}

        reuse.execute("CREATE TEMP TABLE vertical_candidates(page_rowid INTEGER PRIMARY KEY) WITHOUT ROWID")
        reuse.executemany("INSERT INTO vertical_candidates VALUES(?)", ((r,) for r in rowids))

        exact_source_cross_object = _count_distinct(reuse, """
          SELECT COUNT(DISTINCT m.page_rowid)
          FROM exact_source_members m JOIN vertical_candidates v ON v.page_rowid=m.page_rowid
          JOIN exact_source_groups g ON g.group_id=m.group_id WHERE g.cross_object=1
        """)
        exact_source_cross_generation = _count_distinct(reuse, """
          SELECT COUNT(DISTINCT m.page_rowid)
          FROM exact_source_members m JOIN vertical_candidates v ON v.page_rowid=m.page_rowid
          JOIN exact_source_groups g ON g.group_id=m.group_id WHERE g.cross_generation=1
        """)
        exact_text_cross_object = _count_distinct(reuse, """
          SELECT COUNT(DISTINCT m.page_rowid)
          FROM exact_text_members m JOIN vertical_candidates v ON v.page_rowid=m.page_rowid
          JOIN exact_text_groups g ON g.group_id=m.group_id WHERE g.cross_object=1
        """)
        exact_text_cross_generation = _count_distinct(reuse, """
          SELECT COUNT(DISTINCT m.page_rowid)
          FROM exact_text_members m JOIN vertical_candidates v ON v.page_rowid=m.page_rowid
          JOIN exact_text_groups g ON g.group_id=m.group_id WHERE g.cross_generation=1
        """)

        sim_rows = reuse.execute("""
          SELECT s.page_a,s.page_b,s.tier
          FROM similarity_candidates s
          WHERE EXISTS(SELECT 1 FROM vertical_candidates v WHERE v.page_rowid=s.page_a)
             OR EXISTS(SELECT 1 FROM vertical_candidates v WHERE v.page_rowid=s.page_b)
        """).fetchall()
        candidate_set = set(rowids)
        similarity_pages = set()
        near_pages = set()
        cross_gen_similarity_pages = set()
        internal_pairs = 0
        internal_near_pairs = 0
        counterpart_ids = {p for a, b, _ in sim_rows for p in (a, b) if p not in generation}
        if counterpart_ids:
            index.execute("CREATE TEMP TABLE counterpart_ids(id INTEGER PRIMARY KEY) WITHOUT ROWID")
            index.executemany("INSERT INTO counterpart_ids VALUES(?)", ((p,) for p in counterpart_ids))
            generation.update({r[0]: r[1] for r in index.execute(
                "SELECT p.id,p.catalog_generation FROM pages p JOIN counterpart_ids c ON c.id=p.id"
            )})
        for a, b, tier in sim_rows:
            touched = {p for p in (a, b) if p in candidate_set}
            similarity_pages.update(touched)
            if tier == "near_exact_candidate":
                near_pages.update(touched)
            if generation.get(a) != generation.get(b):
                cross_gen_similarity_pages.update(touched)
            if a in candidate_set and b in candidate_set:
                internal_pairs += 1
                internal_near_pairs += int(tier == "near_exact_candidate")

        any_pages = set()
        cross_generation_any = set(cross_gen_similarity_pages)
        for table, groups, cross_col, target in (
            ("exact_source_members", "exact_source_groups", "cross_object", any_pages),
            ("exact_text_members", "exact_text_groups", "cross_object", any_pages),
            ("exact_source_members", "exact_source_groups", "cross_generation", cross_generation_any),
            ("exact_text_members", "exact_text_groups", "cross_generation", cross_generation_any),
        ):
            rows = reuse.execute(f"""
              SELECT DISTINCT m.page_rowid FROM {table} m
              JOIN vertical_candidates v ON v.page_rowid=m.page_rowid
              JOIN {groups} g ON g.group_id=m.group_id WHERE g.{cross_col}=1
            """)
            target.update(r[0] for r in rows)
        any_pages.update(similarity_pages)

        n = len(page_ids)
        return {
            "candidate_pages": n,
            "mapped_candidate_pages": len(mapped),
            "unmapped_candidate_pages": n - len(mapped),
            "candidate_pages_with_exact_source_cross_object_reuse": exact_source_cross_object,
            "candidate_pages_with_exact_source_cross_generation_reuse": exact_source_cross_generation,
            "candidate_pages_with_exact_text_cross_object_reuse": exact_text_cross_object,
            "candidate_pages_with_exact_text_cross_generation_reuse": exact_text_cross_generation,
            "candidate_pages_with_similarity_signal": len(similarity_pages),
            "candidate_pages_with_near_exact_signal": len(near_pages),
            "candidate_pages_with_cross_generation_similarity_signal": len(cross_gen_similarity_pages),
            "candidate_pages_with_any_reuse_similarity_signal": len(any_pages),
            "candidate_pages_with_cross_generation_reuse_similarity_signal": len(cross_generation_any),
            "candidate_pages_without_reuse_similarity_signal": n - len(any_pages),
            "internal_similarity_pairs": internal_pairs,
            "internal_near_exact_pairs": internal_near_pairs,
            "share_candidate_pages_with_any_reuse_similarity_signal": (len(any_pages) / n if n else None),
        }
    finally:
        index.close()
        reuse.close()


def run(candidate_ledger: Path, index_path: Path, reuse_path: Path, *, vertical_id: str,
        expected_ledger_sha256=None, expected_index_sha256=None, expected_reuse_sha256=None) -> dict:
    ledger_sha = verify_sha(candidate_ledger, expected_ledger_sha256, "candidate ledger")
    index_sha = verify_sha(index_path, expected_index_sha256, "Universal Index")
    reuse_sha = verify_sha(reuse_path, expected_reuse_sha256, "reuse/similarity artifact")
    page_ids = load_candidate_page_ids(candidate_ledger)
    metrics = aggregate_context(index_path, reuse_path, page_ids)
    return {
        "context_version": CONTEXT_VERSION,
        "builder_version": BUILDER_VERSION,
        "vertical_id": vertical_id,
        "result_state": "exploratory_signal",
        "metrics": metrics,
        "provenance": {
            "candidate_ledger_sha256": ledger_sha,
            "universal_index_sha256": index_sha,
            "reuse_similarity_sha256": reuse_sha,
            "human_validation_complete": False,
        },
        "warnings": [
            "Reuse/similarity context is computational evidence and does not create aliases or establish semantic equivalence.",
            "Counts describe candidate pages touched by corpus-wide reuse/similarity signals; they do not invalidate or validate the vertical selection.",
        ],
        "privacy": {
            "page_identifiers_emitted": False,
            "object_identifiers_emitted": False,
            "pair_identifiers_emitted": False,
            "ocr_text_emitted": False,
        },
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--candidate-ledger", required=True)
    p.add_argument("--universal-index", required=True)
    p.add_argument("--reuse-similarity", required=True)
    p.add_argument("--vertical-id", required=True)
    p.add_argument("--expected-ledger-sha256")
    p.add_argument("--expected-index-sha256")
    p.add_argument("--expected-reuse-sha256")
    p.add_argument("--output")
    a = p.parse_args(argv)
    result = run(
        Path(a.candidate_ledger), Path(a.universal_index), Path(a.reuse_similarity),
        vertical_id=a.vertical_id,
        expected_ledger_sha256=a.expected_ledger_sha256,
        expected_index_sha256=a.expected_index_sha256,
        expected_reuse_sha256=a.expected_reuse_sha256,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if a.output:
        Path(a.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
