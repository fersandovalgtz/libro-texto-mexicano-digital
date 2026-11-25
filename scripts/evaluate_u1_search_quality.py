#!/usr/bin/env python3
"""Evaluate LTMD-U1 search recovery against PRIVATE, page-level reference labels.

This is a sample-based diagnostic, not corpus-wide scientific validation.
Run inside a controlled environment; reference JSON and index stay under local/.
Only aggregate metrics and cryptographic digests may leave this process.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from scripts import query_u1_universal_index as search

VERSION = "LTMD_U1_SEARCH_QUALITY_0.1"
REFERENCE_TYPES = {"synthetic_fixture", "human_adjudicated"}
SAMPLING_DESIGNS = {"independent_scope_sample", "purposive_sample"}
MAX_LABELS = 10000


def _sha256(path: Path) -> str:
    return search.sha256_file(path)


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _read_reference(path: Path) -> dict:
    reference = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(reference, dict) or reference.get("version") != VERSION:
        raise ValueError("unsupported reference version")
    if reference.get("reference_type") not in REFERENCE_TYPES:
        raise ValueError("invalid reference type")
    if reference.get("sampling_design") not in SAMPLING_DESIGNS:
        raise ValueError("invalid sampling design")
    labels = reference.get("labels")
    if not isinstance(labels, list) or not 2 <= len(labels) <= MAX_LABELS:
        raise ValueError("reference requires between 2 and 10000 labels")
    return reference


def evaluate(connection: sqlite3.Connection, reference: dict, *, index_digest: str | None = None,
             reference_digest: str | None = None) -> dict:
    """Score exact FTS5 retrieval only for adjudicated pages in the declared scope.

    Neither page IDs nor OCR text are returned. Human relevance is supplied
    externally and is NEVER inferred from the search engine's own matches.
    """
    search.validate_index(connection)
    if reference.get("version") != VERSION:
        raise ValueError("unsupported reference version")
    reference_type = reference.get("reference_type")
    sampling_design = reference.get("sampling_design")
    if reference_type not in REFERENCE_TYPES or sampling_design not in SAMPLING_DESIGNS:
        raise ValueError("invalid evaluation design")
    expression = search.validate_query_expression(reference.get("query_expression", ""))
    raw_filters = reference.get("filters", {})
    if not isinstance(raw_filters, dict) or set(raw_filters) - set(search.DIMENSION_COLUMNS):
        raise ValueError("invalid filter dimensions")
    filters = search.normalize_filters(raw_filters)
    labels = reference.get("labels")
    if not isinstance(labels, list) or not 2 <= len(labels) <= MAX_LABELS:
        raise ValueError("reference requires between 2 and 10000 labels")

    filter_sql, filter_params = search.build_filter_clause(filters)
    seen = set()
    counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for label in labels:
        if not isinstance(label, dict):
            raise ValueError("invalid reference entry")
        page_id = label.get("page_id")
        relevant = label.get("relevant")
        source_checked = label.get("source_checked")
        if not isinstance(page_id, str) or not page_id.strip() or len(page_id) > 300:
            raise ValueError("invalid private page identifier")
        if page_id in seen:
            raise ValueError("duplicate private page identifier")
        seen.add(page_id)
        if type(relevant) is not bool or type(source_checked) is not bool:
            raise ValueError("labels must explicitly record relevance and source-check status")
        if reference_type == "human_adjudicated" and not source_checked:
            raise ValueError("human reference contains a page not visually checked")

        scope_rows = connection.execute(
            f"SELECT p.id FROM pages p WHERE p.page_id = ? AND {filter_sql}",
            [page_id, *filter_params],
        ).fetchall()
        if len(scope_rows) != 1:
            raise ValueError("private reference has a missing, repeated or out-of-scope page")
        try:
            hit = connection.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM pages_fts f
                    JOIN pages p ON p.id = f.rowid
                    WHERE pages_fts MATCH ? AND p.id = ?
                )
                """,
                [expression, scope_rows[0][0]],
            ).fetchone()[0]
        except sqlite3.OperationalError as exc:
            raise ValueError("invalid FTS5 query expression") from exc

        counts["tp" if hit and relevant else
               "fp" if hit else
               "fn" if relevant else "tn"] += 1

    if not (counts["tp"] + counts["fn"]) or not (counts["fp"] + counts["tn"]):
        raise ValueError("reference must contain at least one relevant and one non-relevant page")

    tp, fp, fn, tn = (counts[key] for key in ("tp", "fp", "fn", "tn"))
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    result = {
        "version": VERSION,
        "result_state": ("synthetic_regression_only" if reference_type == "synthetic_fixture"
                         else "sample_diagnostic_not_corpus_validated"),
        "sampling_design": sampling_design,
        "sample_size": len(labels),
        "sample_relevant": tp + fn,
        "sample_not_relevant": fp + tn,
        "confusion_matrix": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "sample_metrics": {
            "precision": precision,
            "recall": recall,
            "f1": _ratio(2 * tp, 2 * tp + fp + fn),
            "specificity": _ratio(tn, tn + fp),
        },
        "provenance": {
            "index_version": search.INDEX_VERSION,
            "query_engine_version": search.ENGINE_VERSION,
            "index_sha256": index_digest,
            "reference_sha256": reference_digest,
        },
        "human_validation_complete": False,
        "warnings": [
            "Metrics refer only to labeled sample pages, never the full LTMD corpus.",
            "Index retrieval quality and historical/semantic validity are different questions.",
            "Zero search hits cannot establish historical absence.",
        ],
    }
    if sampling_design == "purposive_sample":
        result["warnings"].append(
            "Purposive sampling is not probabilistic; do not extrapolate these metrics to the corpus."
        )
    if reference_type == "synthetic_fixture":
        result["warnings"].append(
            "Synthetic fixtures test software behavior; they provide no empirical quality estimate."
        )
    return result


def run(index_path: Path, reference_path: Path, *, expected_index_sha256: str | None = None) -> dict:
    """Evaluate entirely within the private environment; never export reference labels."""
    index_path = index_path.expanduser().resolve()
    reference_path = reference_path.expanduser().resolve()
    if not index_path.is_file() or not reference_path.is_file():
        raise ValueError("private index or reference file unavailable")
    reference = _read_reference(reference_path)
    index_digest = _sha256(index_path)
    if expected_index_sha256 is not None:
        expected = expected_index_sha256.lower().strip()
        if not search.SHA256_RE.fullmatch(expected) or expected != index_digest:
            raise ValueError("index integrity verification failed")
    connection = sqlite3.connect(f"file:{index_path}?mode=ro", uri=True)
    try:
        return evaluate(connection, reference, index_digest=index_digest,
                        reference_digest=_sha256(reference_path))
    finally:
        connection.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True,
                        help="Private, locally reconstructed Universal Index")
    parser.add_argument("--reference", type=Path, required=True,
                        help="Private, expert-annotated JSON; never commit")
    parser.add_argument("--expected-index-sha256")
    parser.add_argument("--output", type=Path,
                        help="Optional aggregate-only report path (no per-page data)")
    args = parser.parse_args(argv)
    report = run(args.index, args.reference,
                 expected_index_sha256=args.expected_index_sha256)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
