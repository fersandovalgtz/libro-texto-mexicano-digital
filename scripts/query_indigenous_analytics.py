#!/usr/bin/env python3
"""Query the private LTMD Indigenous-language candidate ledger and emit safe aggregates only.

Version: LTMD_ANALYTICS_QUERY_ENGINE_0.1

This module is the query core for LTMD Analytics 0.1. It may read a private page-level
candidate ledger, but its public response contains aggregates and provenance only. It never
returns page IDs, source URLs, OCR text, snippets, or source/OCR hashes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ENGINE_VERSION = "LTMD_ANALYTICS_QUERY_ENGINE_0.1"
ANALYTICS_VERSION = "LTMD_ANALYTICS_INDIGENOUS_0.1"
SOURCE_ANALYSIS_VERSION = "LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2"

REQUIRED_FIELDS = {
    "page_id",
    "canonical_viewer_key",
    "wave",
    "generation",
    "grade_code",
    "explicit_general",
    "named_language_contextual",
    "matched_explicit_terms",
    "matched_language_groups",
    "validation_status",
}

ALLOWED_GROUP_BY = {
    "generation",
    "grade_code",
    "wave",
    "language_group",
    "explicit_term",
}


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
    if filters.get("language_group"):
        if not (split_multi(row["matched_language_groups"]) & set(filters["language_group"])):
            return False
    if filters.get("explicit_term"):
        if not (split_multi(row["matched_explicit_terms"]) & set(filters["explicit_term"])):
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
    warnings = []
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
        return None, [
            "Missing corpus denominator for generation(s): " + ", ".join(missing) + "; pages_per_1000 is null."
        ]
    return sum(denominators[generation] for generation in generations), warnings


def group_values(row: dict, group_by: str) -> set[str]:
    if group_by in {"generation", "grade_code", "wave"}:
        return {str(row[group_by])}
    if group_by == "language_group":
        return split_multi(row["matched_language_groups"])
    if group_by == "explicit_term":
        return split_multi(row["matched_explicit_terms"])
    raise RuntimeError(f"unsupported group_by: {group_by}")


def build_breakdown(rows: list[dict], group_by: str) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        for value in group_values(row, group_by):
            groups[value].append(row)
    result = []
    for value in sorted(groups, key=lambda item: (int(item) if item.isdigit() else 10**12, item)):
        result.append({
            "dimension": group_by,
            "value": value,
            "result_state": "exploratory_signal",
            "metrics": aggregate_metrics(groups[value]),
        })
    return result


def query(rows: list[dict], *, query_label: str, filters: dict[str, Iterable[str] | None],
          denominators: dict[str, int] | None = None, group_by: str | None = None,
          source_ledger_sha256: str | None = None) -> dict:
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
            "source_manifest_sha256": source_ledger_sha256,
            "query_engine_version": ENGINE_VERSION,
        },
        "warnings": warnings + [
            "Results are computational candidates/exploratory signals, not validated historical prevalence claims."
        ],
    }
    if group_by:
        response["group_by"] = group_by
        response["breakdown"] = build_breakdown(matched, group_by)
    return response


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-ledger", required=True)
    parser.add_argument("--generation-summary")
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
    )
    payload = json.dumps(response, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
