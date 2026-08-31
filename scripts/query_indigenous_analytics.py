#!/usr/bin/env python3
"""Query the private LTMD Indigenous-language candidate ledger and emit safe aggregates only.

Version: LTMD_ANALYTICS_QUERY_ENGINE_0.2

This module preserves the preregistered Indigenous-language candidate selection. When the
corpus-wide reuse context is configured, filtered candidate sets and breakdown groups are
contextualized without changing membership or epistemic state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable

ENGINE_VERSION = "LTMD_ANALYTICS_QUERY_ENGINE_0.2"
ANALYTICS_VERSION = "LTMD_ANALYTICS_INDIGENOUS_0.1"
SOURCE_ANALYSIS_VERSION = "LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2"

REQUIRED_FIELDS = {
    "page_id", "canonical_viewer_key", "wave", "generation", "grade_code",
    "explicit_general", "named_language_contextual", "matched_explicit_terms",
    "matched_language_groups", "validation_status",
}
ALLOWED_GROUP_BY = {"generation", "grade_code", "wave", "language_group", "explicit_term"}
ReuseContextResolver = Callable[[list[str]], dict]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def split_multi(value: str) -> set[str]:
    return {part.strip() for part in str(value or "").split(";") if part.strip()}


def load_ledger(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_FIELDS - fields
        if missing:
            raise RuntimeError("candidate ledger missing fields: " + ", ".join(sorted(missing)))
        rows = [dict(row) for row in reader]
    seen = set()
    for row in rows:
        page_id = row["page_id"].strip()
        if not page_id:
            raise RuntimeError("candidate ledger contains blank page_id")
        if page_id in seen:
            raise RuntimeError(f"duplicate page_id in candidate ledger: {page_id}")
        seen.add(page_id)
    return rows


def load_generation_denominators(path: Path | None) -> dict[str, int]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        required = {"generation", "total_pages"}
        missing = required - fields
        if missing:
            raise RuntimeError("generation summary missing fields: " + ", ".join(sorted(missing)))
        result = {}
        for row in reader:
            generation = str(row["generation"]).strip()
            total = int(row["total_pages"])
            if generation in result and result[generation] != total:
                raise RuntimeError(f"conflicting total_pages for generation {generation}")
            result[generation] = total
        return result


def normalize_filters(filters: dict[str, Iterable[str] | None]) -> dict[str, list[str]]:
    normalized = {}
    for key in ("generation", "grade_code", "wave", "language_group", "explicit_term"):
        values = filters.get(key)
        if values:
            normalized[key] = sorted({str(value).strip() for value in values if str(value).strip()})
    return normalized


def row_matches(row: dict, filters: dict[str, list[str]]) -> bool:
    if filters.get("generation") and str(row["generation"]) not in filters["generation"]:
        return False
    if filters.get("grade_code") and str(row["grade_code"]) not in filters["grade_code"]:
        return False
    if filters.get("wave") and str(row["wave"]) not in filters["wave"]:
        return False
    if filters.get("language_group") and not (split_multi(row["matched_language_groups"]) & set(filters["language_group"])):
        return False
    if filters.get("explicit_term") and not (split_multi(row["matched_explicit_terms"]) & set(filters["explicit_term"])):
        return False
    return True


def aggregate_metrics(rows: list[dict], denominator: int | None = None) -> dict:
    books = {row["canonical_viewer_key"] for row in rows}
    explicit = sum(as_bool(row["explicit_general"]) for row in rows)
    named = sum(as_bool(row["named_language_contextual"]) for row in rows)
    pages = len(rows)
    return {
        "candidate_pages": pages,
        "candidate_books": len(books),
        "explicit_general_pages": explicit,
        "named_language_contextual_pages": named,
        "pages_per_1000": (pages / denominator * 1000) if denominator else None,
    }


def corpus_denominator(filters: dict[str, list[str]], denominators: dict[str, int]) -> tuple[int | None, list[str]]:
    if not denominators:
        return None, ["No corpus denominator supplied; pages_per_1000 is null."]
    if filters.get("grade_code") or filters.get("wave"):
        return None, [
            "Grade/wave filters are active but only generation-level corpus denominators are available; "
            "pages_per_1000 is null rather than using an invalid denominator."
        ]
    generations = filters.get("generation") or sorted(denominators)
    missing = [generation for generation in generations if generation not in denominators]
    if missing:
        return None, ["Missing corpus denominator for generation(s): " + ", ".join(missing) + "; pages_per_1000 is null."]
    return sum(denominators[generation] for generation in generations), []


def group_values(row: dict, group_by: str) -> set[str]:
    if group_by in {"generation", "grade_code", "wave"}:
        return {str(row[group_by])}
    if group_by == "language_group":
        return split_multi(row["matched_language_groups"])
    if group_by == "explicit_term":
        return split_multi(row["matched_explicit_terms"])
    raise RuntimeError(f"unsupported group_by: {group_by}")


def _sort_dimension_value(value: str) -> tuple[int, int | str, str]:
    if value.isdigit():
        return (0, int(value), value)
    return (1, value, value)


def _resolve_reuse_context(rows: list[dict], resolver: ReuseContextResolver | None) -> dict | None:
    if resolver is None:
        return None
    context = resolver([row["page_id"] for row in rows])
    metrics = context.get("metrics") if isinstance(context, dict) else None
    if not isinstance(metrics, dict) or metrics.get("candidate_pages") != len(rows):
        raise RuntimeError("reuse context candidate count mismatch")
    if context.get("result_state") != "exploratory_signal":
        raise RuntimeError("reuse context must remain exploratory_signal")
    return context


def build_breakdown(rows: list[dict], group_by: str, reuse_context_resolver: ReuseContextResolver | None = None) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        for value in group_values(row, group_by):
            groups[value].append(row)
    result = []
    for value in sorted(groups, key=_sort_dimension_value):
        item = {
            "dimension": group_by,
            "value": value,
            "result_state": "exploratory_signal",
            "metrics": aggregate_metrics(groups[value]),
        }
        context = _resolve_reuse_context(groups[value], reuse_context_resolver)
        if context is not None:
            item["reuse_context"] = context
        result.append(item)
    return result


def query(rows: list[dict], *, query_label: str, filters: dict[str, Iterable[str] | None],
          denominators: dict[str, int] | None = None, group_by: str | None = None,
          source_ledger_sha256: str | None = None,
          reuse_context_resolver: ReuseContextResolver | None = None) -> dict:
    normalized = normalize_filters(filters)
    if group_by is not None and group_by not in ALLOWED_GROUP_BY:
        raise RuntimeError("group_by must be one of: " + ", ".join(sorted(ALLOWED_GROUP_BY)))

    matched = [row for row in rows if row_matches(row, normalized)]
    denominator, warnings = corpus_denominator(normalized, denominators or {})
    validation_states = sorted({str(row["validation_status"]) for row in matched})
    if validation_states and validation_states != ["not_visually_validated"]:
        warnings.append("Matched rows contain mixed validation states: " + ", ".join(validation_states))

    response = {
        "query": query_label,
        "filters": normalized,
        "result_state": "exploratory_signal",
        "metrics": aggregate_metrics(matched, denominator),
        "provenance": {
            "analytics_version": ANALYTICS_VERSION,
            "source_analysis_version": SOURCE_ANALYSIS_VERSION,
            "human_validation_complete": False,
            "source_ledger_sha256": source_ledger_sha256,
            "query_engine_version": ENGINE_VERSION,
        },
        "warnings": warnings + [
            "Results are computational candidates/exploratory signals, not validated historical prevalence claims."
        ],
    }
    context = _resolve_reuse_context(matched, reuse_context_resolver)
    if context is not None:
        response["reuse_context"] = context
    if group_by:
        response["group_by"] = group_by
        response["breakdown"] = build_breakdown(matched, group_by, reuse_context_resolver)
    return response


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-ledger", required=True)
    parser.add_argument("--generation-summary")
    parser.add_argument("--universal-index")
    parser.add_argument("--reuse-similarity")
    parser.add_argument("--query", default="LTMD Analytics query")
    parser.add_argument("--generation", action="append")
    parser.add_argument("--grade-code", action="append")
    parser.add_argument("--wave", action="append")
    parser.add_argument("--language-group", action="append")
    parser.add_argument("--explicit-term", action="append")
    parser.add_argument("--group-by", choices=sorted(ALLOWED_GROUP_BY))
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    ledger = Path(args.candidate_ledger)
    rows = load_ledger(ledger)
    denominators = load_generation_denominators(Path(args.generation_summary)) if args.generation_summary else {}
    resolver = None
    if bool(args.universal_index) != bool(args.reuse_similarity):
        raise RuntimeError("--universal-index and --reuse-similarity must be supplied together")
    if args.universal_index:
        from scripts.runtime_vertical_reuse_context import runtime_context
        index_path = Path(args.universal_index)
        reuse_path = Path(args.reuse_similarity)
        resolver = lambda page_ids: runtime_context(index_path, reuse_path, page_ids)
    response = query(
        rows,
        query_label=args.query,
        filters={
            "generation": args.generation,
            "grade_code": args.grade_code,
            "wave": args.wave,
            "language_group": args.language_group,
            "explicit_term": args.explicit_term,
        },
        denominators=denominators,
        group_by=args.group_by,
        source_ledger_sha256=sha256_file(ledger),
        reuse_context_resolver=resolver,
    )
    payload = json.dumps(response, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
