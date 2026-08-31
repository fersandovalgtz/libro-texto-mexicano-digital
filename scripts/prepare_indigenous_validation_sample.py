#!/usr/bin/env python3
"""Prepare a deterministic, text-free validation queue for LTMD-U1 Indigenous-language study 0.2.

Version: LTMD_U1_INDIGENOUS_LANGUAGES_VALIDATION_STAGE1_0.1

Input is the private candidate ledger emitted by analyze_indigenous_languages.py.
Only rows marked explicit_general are admitted. No OCR text or snippets are read or emitted.

The output queue preserves source identity/hash fields required for visual verification and
marks every row as pending. A deterministic subset is flagged for independent double coding.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "LTMD_U1_INDIGENOUS_LANGUAGES_VALIDATION_STAGE1_0.1"

REQUIRED_FIELDS = {
    "page_id",
    "canonical_viewer_key",
    "generation",
    "grade_code",
    "page_index",
    "viewer_page",
    "source_asset_url",
    "source_sha256",
    "ocr_sha256",
    "explicit_general",
    "matched_explicit_terms",
    "matched_language_groups",
    "validation_status",
}

OUTPUT_FIELDS = [
    "validation_id",
    "page_id",
    "canonical_viewer_key",
    "generation",
    "grade_code",
    "page_index",
    "viewer_page",
    "source_asset_url",
    "source_sha256",
    "ocr_sha256",
    "query_family",
    "matched_explicit_terms",
    "matched_language_groups",
    "validation_status",
    "double_code_required",
    "coder_a_id",
    "coder_b_id",
    "reference_type",
    "named_language",
    "status_label",
    "temporality",
    "speaker_agency",
    "relation_to_spanish",
    "territorial_function",
    "pedagogical_function",
    "normative_frame",
    "risk_frame",
    "evaluative_polarity",
    "false_positive_cause",
    "adjudication_status",
    "validation_date",
    "notes_nonexpressive",
]


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def stable_score(seed: str, page_id: str) -> str:
    return hashlib.sha256(f"{seed}\0{page_id}".encode("utf-8")).hexdigest()


def read_candidates(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_FIELDS - fields
        if missing:
            raise RuntimeError("candidate ledger missing fields: " + ", ".join(sorted(missing)))
        rows = [dict(row) for row in reader]

    seen = {}
    unique_rows = []
    for row in rows:
        page_id = row["page_id"].strip()
        if not page_id:
            raise RuntimeError("candidate ledger contains blank page_id")
        fingerprint = (
            row["canonical_viewer_key"],
            row["source_sha256"],
            row["ocr_sha256"],
            row["generation"],
            row["page_index"],
            row["viewer_page"],
        )
        prior = seen.get(page_id)
        if prior is not None:
            if prior != fingerprint:
                raise RuntimeError(f"conflicting duplicate page_id: {page_id}")
            continue
        seen[page_id] = fingerprint
        unique_rows.append(row)

    explicit = [row for row in unique_rows if as_bool(row["explicit_general"])]
    explicit.sort(key=lambda row: (
        int(row["generation"]) if str(row["generation"]).isdigit() else str(row["generation"]),
        row["canonical_viewer_key"],
        int(row["page_index"] or 0),
        row["page_id"],
    ))
    return explicit


def double_code_quota(n: int, rate: float, minimum: int) -> int:
    if n <= 0:
        return 0
    quota = max(minimum, math.ceil(n * rate))
    return min(n, quota)


def select_double_code(rows: list[dict], seed: str, rate: float, minimum: int) -> set[str]:
    strata = defaultdict(list)
    for row in rows:
        strata[str(row["generation"])].append(row)

    selected = set()
    for generation in sorted(strata, key=lambda value: int(value) if value.isdigit() else value):
        group = sorted(
            strata[generation],
            key=lambda row: (stable_score(seed, row["page_id"]), row["page_id"]),
        )
        quota = double_code_quota(len(group), rate, minimum)
        selected.update(row["page_id"] for row in group[:quota])
    return selected


def build_queue(rows: list[dict], selected: set[str]) -> list[dict]:
    queue = []
    for index, row in enumerate(rows, start=1):
        queue.append({
            "validation_id": f"ILV02-{index:04d}",
            "page_id": row["page_id"],
            "canonical_viewer_key": row["canonical_viewer_key"],
            "generation": row["generation"],
            "grade_code": row["grade_code"],
            "page_index": row["page_index"],
            "viewer_page": row["viewer_page"],
            "source_asset_url": row["source_asset_url"],
            "source_sha256": row["source_sha256"],
            "ocr_sha256": row["ocr_sha256"],
            "query_family": "explicit_general_0_2",
            "matched_explicit_terms": row["matched_explicit_terms"],
            "matched_language_groups": row["matched_language_groups"],
            "validation_status": "pending_visual_validation",
            "double_code_required": "1" if row["page_id"] in selected else "0",
            "coder_a_id": "",
            "coder_b_id": "",
            "reference_type": "",
            "named_language": "",
            "status_label": "",
            "temporality": "",
            "speaker_agency": "",
            "relation_to_spanish": "",
            "territorial_function": "",
            "pedagogical_function": "",
            "normative_frame": "",
            "risk_frame": "",
            "evaluative_polarity": "",
            "false_positive_cause": "",
            "adjudication_status": "pending",
            "validation_date": "",
            "notes_nonexpressive": "",
        })
    return queue


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(candidate_ledger: Path, output_csv: Path, manifest_json: Path,
        expected_explicit: int | None, double_code_rate: float,
        double_code_min_per_generation: int, seed: str) -> dict:
    if not 0 < double_code_rate <= 1:
        raise RuntimeError("double-code rate must be in (0, 1]")
    if double_code_min_per_generation < 1:
        raise RuntimeError("double-code minimum per generation must be >= 1")

    rows = read_candidates(candidate_ledger)
    if expected_explicit is not None and len(rows) != expected_explicit:
        raise RuntimeError(
            f"explicit cardinality mismatch: got {len(rows)}, expected {expected_explicit}"
        )

    selected = select_double_code(
        rows, seed=seed, rate=double_code_rate, minimum=double_code_min_per_generation
    )
    queue = build_queue(rows, selected)
    write_csv(output_csv, queue)

    by_generation = Counter(row["generation"] for row in rows)
    double_by_generation = Counter(
        row["generation"] for row in rows if row["page_id"] in selected
    )
    manifest = {
        "version": VERSION,
        "input_candidate_ledger_sha256": sha256_file(candidate_ledger),
        "explicit_pages": len(rows),
        "double_coded_pages": len(selected),
        "selection": {
            "method": "generation-stratified deterministic SHA-256 ranking",
            "seed": seed,
            "rate": double_code_rate,
            "minimum_per_generation": double_code_min_per_generation,
            "by_generation": {
                generation: {
                    "explicit_pages": by_generation[generation],
                    "double_coded_pages": double_by_generation[generation],
                }
                for generation in sorted(
                    by_generation, key=lambda value: int(value) if value.isdigit() else value
                )
            },
        },
        "scientific_state": {
            "visual_validation_complete": False,
            "semantic_ready_promotions": 0,
            "publication_note": (
                "Queue contains identifiers, source URLs, hashes and coding fields only; "
                "no OCR text or source-page bytes are emitted."
            ),
        },
        "output": {
            "filename": output_csv.name,
            "sha256": sha256_file(output_csv),
        },
    }
    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-ledger", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--manifest-json", required=True)
    parser.add_argument("--expected-explicit", type=int, default=457)
    parser.add_argument("--double-code-rate", type=float, default=0.10)
    parser.add_argument("--double-code-min-per-generation", type=int, default=2)
    parser.add_argument(
        "--seed",
        default="LTMD_U1_INDIGENOUS_LANGUAGES_VALIDATION_STAGE1_0.1",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    candidate = Path(args.candidate_ledger)
    if not candidate.is_file():
        raise SystemExit(f"missing candidate ledger: {candidate}")
    manifest = run(
        candidate_ledger=candidate,
        output_csv=Path(args.output_csv),
        manifest_json=Path(args.manifest_json),
        expected_explicit=args.expected_explicit,
        double_code_rate=args.double_code_rate,
        double_code_min_per_generation=args.double_code_min_per_generation,
        seed=args.seed,
    )
    print(json.dumps(
        {
            "explicit_pages": manifest["explicit_pages"],
            "double_coded_pages": manifest["double_coded_pages"],
        },
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
