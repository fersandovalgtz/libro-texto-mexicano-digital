#!/usr/bin/env python3
"""Find cross-page snippet contamination in PRIVATE LTMD Research text exports.

This diagnostic never reads source books or downloads anything. It reports only
book identifiers, result ordinals, viewer-page positions and overlap lengths.
A flag is evidence for human inspection, NOT proof of mis-indexing or a repair.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from difflib import SequenceMatcher
import json
from itertools import combinations
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

REPORT_VERSION = "LTMD_SEARCH_EXPORT_PAGE_AUDIT_0.1"
TOKEN_RE = re.compile(r"[^\W_]+", flags=re.UNICODE)
RESULTS_RE = re.compile(r"(?m)^Resultados\s+(\d+)[–-](\d+)\s+de\s+(\d+)\s*$")
RECORD_RE = re.compile(
    r"(?ms)^(?P<number>\d+)\. (?P<title>[^\n]+)\n"
    r"(?P<scope>Ciclo escolar[^\n]+Página del visor \d+)\n\n"
    r"(?P<snippet>.*?)\n\nSEP/CONALITEG\.[^\n]*?"
    r"Posición del visor:\s*(?P<page>\d+)\.\n"
    r"(?P<url>https://[^\s]+)"
)
MAX_RECORDS = 10000
MAX_SNIPPET_WORDS = 5000
DEFAULT_MIN_SHARED_WORDS = 32


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(TOKEN_RE.findall(value.casefold()))


def _book_key(url: str) -> tuple[str, str, str]:
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname != "libros.conaliteg.gob.mx"
            or parsed.path != "/pdf-reader/reader.html"):
        raise ValueError("export contains a noncanonical book link")
    query = parse_qs(parsed.query)
    parts = (query.get("nivel", []), query.get("ciclo", []), query.get("clave", []))
    if any(len(values) != 1 or not values[0] for values in parts):
        raise ValueError("book link is missing a single canonical identifier")
    return tuple(values[0] for values in parts)


def parse_export(text: str) -> tuple[list[dict], dict]:
    """Parse only the LTMD Research TXT export format; keep excerpts in memory."""
    header = RESULTS_RE.search(text)
    if not header:
        raise ValueError("not an LTMD result-range TXT export")
    first, last, total = map(int, header.groups())
    if not (1 <= first <= last <= total) or last - first + 1 > MAX_RECORDS:
        raise ValueError("invalid export range")
    rows = []
    for match in RECORD_RE.finditer(text):
        book = _book_key(match.group("url"))
        tokens = _tokens(match.group("snippet"))
        if len(tokens) > MAX_SNIPPET_WORDS:
            raise ValueError("export snippet exceeds safety limit")
        rows.append({
            "number": int(match.group("number")),
            "page": int(match.group("page")),
            "book": book,
            "tokens": tokens,
        })
    if len(rows) != last - first + 1:
        raise ValueError("result export was incomplete or had unrecognized record structure")
    if [row["number"] for row in rows] != list(range(first, last + 1)):
        raise ValueError("result ordinals are not contiguous or match a different range")
    return rows, {"first": first, "last": last, "total": total}


def audit_export(text: str, min_shared_words: int = DEFAULT_MIN_SHARED_WORDS) -> dict:
    """Detect long exact contiguous token spans reused on different viewer pages.

    Duplicate prose can be legitimate (indexes, illustrations, reprinted pages).
    Flags therefore MUST NOT change page data or infer the correct page.
    """
    if not 16 <= min_shared_words <= 150:
        raise ValueError("min_shared_words must be between 16 and 150")
    rows, rng = parse_export(text)
    shingles: dict[tuple, set[int]] = defaultdict(set)
    for index, row in enumerate(rows):
        words = row["tokens"]
        for offset in range(len(words) - min_shared_words + 1):
            shingles[(row["book"], words[offset:offset + min_shared_words])].add(index)

    candidates: set[tuple[int, int]] = set()
    for row_indices in shingles.values():
        if len(row_indices) > 1:
            candidates.update(combinations(sorted(row_indices), 2))

    flags = []
    for first, second in sorted(candidates):
        a, b = rows[first], rows[second]
        if a["page"] == b["page"]:
            continue
        longest = SequenceMatcher(
            None, a["tokens"], b["tokens"], autojunk=False
        ).find_longest_match(0, len(a["tokens"]), 0, len(b["tokens"])).size
        if longest < min_shared_words:
            continue
        shorter = min(len(a["tokens"]), len(b["tokens"]))
        flags.append({
            "state": "cross_page_overlap_requires_source_review",
            "book": {"level": a["book"][0], "cycle": a["book"][1],
                     "viewer_key": a["book"][2]},
            "result_ordinals": [a["number"], b["number"]],
            "viewer_pages": [a["page"], b["page"]],
            "longest_contiguous_overlap_words": longest,
            "fraction_of_shorter_snippet": round(longest / shorter, 4),
            "possible_front_matter_contamination": (
                min(a["page"], b["page"]) <= 12
                and abs(a["page"] - b["page"]) >= 20
            ),
        })
    flags.sort(key=lambda x: (-x["longest_contiguous_overlap_words"], x["result_ordinals"]))
    return {
        "version": REPORT_VERSION,
        "state": "private_export_screening_not_source_validation",
        "query_not_exported": True,
        "exported_results": len(rows),
        "result_range": {"first": rng["first"], "last": rng["last"]},
        "reported_total_results": rng["total"],
        "report_is_partial_if_export_is_paginated": len(rows) < rng["total"],
        "min_shared_words": min_shared_words,
        "review_flags": flags,
        "flag_count": len(flags),
        "evidence_scope": "within_this_export_only",
        "warnings": [
            "Long repeated spans can be legitimate. Inspect the official source before assigning a cause.",
            "No original page, OCR text, snippet, file path or search term is included in this report.",
            "This screening cannot validate retrieval precision or recall and does not repair a website.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="Private LTMD Research result export (.txt)")
    parser.add_argument("--output", type=Path, help="Optional aggregate-only local JSON report")
    parser.add_argument("--min-shared-words", type=int, default=DEFAULT_MIN_SHARED_WORDS)
    args = parser.parse_args(argv)
    report = audit_export(args.input.read_text(encoding="utf-8"),
                          min_shared_words=args.min_shared_words)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
