#!/usr/bin/env python3
"""Build public-safe LTMD Analytics aggregates from the private Indigenous-language candidate ledger.

Version: LTMD_ANALYTICS_INDIGENOUS_0.1

The input ledger may contain private page-level identifiers and source URLs. This script never
copies those fields to its outputs. It emits only aggregated counts and a provenance manifest.
All outputs remain computational/exploratory until a separate human-validation process promotes
a result to a stronger epistemic state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "LTMD_ANALYTICS_INDIGENOUS_0.1"

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

FORBIDDEN_PUBLIC_FIELDS = {
    "page_id",
    "source_asset_url",
    "source_sha256",
    "ocr_sha256",
    "matched_language_forms",
    "title_core",
    "viewer_page",
    "page_index",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def split_multi(value: str) -> list[str]:
    return sorted({part.strip() for part in str(value or "").split(";") if part.strip()})


def read_ledger(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_FIELDS - fields
        if missing:
            raise RuntimeError("candidate ledger missing fields: " + ", ".join(sorted(missing)))
        rows = [dict(row) for row in reader]

    page_ids = set()
    for row in rows:
        page_id = row["page_id"].strip()
        if not page_id:
            raise RuntimeError("candidate ledger contains blank page_id")
        if page_id in page_ids:
            raise RuntimeError(f"duplicate page_id in candidate ledger: {page_id}")
        page_ids.add(page_id)
    return rows


def read_generation_denominators(path: Path | None) -> dict[str, int]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"generation", "total_pages"}
        missing = required - set(reader.fieldnames or [])
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


def generation_key(value: str):
    return (0, int(value)) if str(value).isdigit() else (1, str(value))


def aggregate(rows: list[dict], denominators: dict[str, int]) -> dict[str, list[dict]]:
    generation_pages = Counter()
    generation_explicit = Counter()
    generation_named = Counter()
    generation_books = defaultdict(set)

    stratum_pages = Counter()
    stratum_explicit = Counter()
    stratum_named = Counter()
    stratum_books = defaultdict(set)

    language_pages = Counter()
    language_books = defaultdict(set)
    term_pages = Counter()
    term_books = defaultdict(set)

    validation_states = Counter()

    for row in rows:
        generation = str(row["generation"])
        grade = str(row["grade_code"])
        wave = str(row["wave"])
        book = row["canonical_viewer_key"]
        explicit = as_bool(row["explicit_general"])
        named = as_bool(row["named_language_contextual"])
        validation_states[str(row["validation_status"] or "").strip() or "blank"] += 1

        generation_pages[generation] += 1
        generation_books[generation].add(book)
        if explicit:
            generation_explicit[generation] += 1
        if named:
            generation_named[generation] += 1

        stratum = (generation, grade, wave)
        stratum_pages[stratum] += 1
        stratum_books[stratum].add(book)
        if explicit:
            stratum_explicit[stratum] += 1
        if named:
            stratum_named[stratum] += 1

        for language in split_multi(row["matched_language_groups"]):
            key = (language, generation, grade, wave)
            language_pages[key] += 1
            language_books[key].add(book)

        for term in split_multi(row["matched_explicit_terms"]):
            key = (term, generation)
            term_pages[key] += 1
            term_books[key].add(book)

    generation_rows = []
    for generation in sorted(generation_pages, key=generation_key):
        total_pages = denominators.get(generation)
        candidate_pages = generation_pages[generation]
        row = {
            "generation": generation,
            "corpus_total_pages": total_pages if total_pages is not None else "",
            "candidate_pages": candidate_pages,
            "explicit_general_pages": generation_explicit[generation],
            "named_language_contextual_pages": generation_named[generation],
            "candidate_books": len(generation_books[generation]),
            "candidate_pages_per_1000_corpus_pages": (
                f"{candidate_pages / total_pages * 1000:.4f}" if total_pages else ""
            ),
            "epistemic_state": "exploratory_signal",
        }
        generation_rows.append(row)

    stratum_rows = []
    for generation, grade, wave in sorted(
        stratum_pages,
        key=lambda item: (generation_key(item[0]), item[1], item[2]),
    ):
        key = (generation, grade, wave)
        stratum_rows.append({
            "generation": generation,
            "grade_code": grade,
            "wave": wave,
            "candidate_pages": stratum_pages[key],
            "explicit_general_pages": stratum_explicit[key],
            "named_language_contextual_pages": stratum_named[key],
            "candidate_books": len(stratum_books[key]),
            "epistemic_state": "exploratory_signal",
        })

    language_rows = []
    for language, generation, grade, wave in sorted(
        language_pages,
        key=lambda item: (item[0], generation_key(item[1]), item[2], item[3]),
    ):
        key = (language, generation, grade, wave)
        language_rows.append({
            "language_group": language,
            "generation": generation,
            "grade_code": grade,
            "wave": wave,
            "candidate_pages": language_pages[key],
            "candidate_books": len(language_books[key]),
            "epistemic_state": "computational_candidate",
        })

    term_rows = []
    for term, generation in sorted(term_pages, key=lambda item: (item[0], generation_key(item[1]))):
        key = (term, generation)
        term_rows.append({
            "explicit_term": term,
            "generation": generation,
            "candidate_pages": term_pages[key],
            "candidate_books": len(term_books[key]),
            "epistemic_state": "computational_candidate",
        })

    return {
        "generation": generation_rows,
        "stratum": stratum_rows,
        "language": language_rows,
        "term": term_rows,
        "validation_states": [
            {"validation_status": status, "candidate_pages": count}
            for status, count in sorted(validation_states.items())
        ],
    }


def write_csv(path: Path, rows: list[dict], fallback_fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else fallback_fields
    forbidden = FORBIDDEN_PUBLIC_FIELDS & set(fields)
    if forbidden:
        raise RuntimeError("refusing to emit forbidden public fields: " + ", ".join(sorted(forbidden)))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(candidate_ledger: Path, output_dir: Path, generation_summary: Path | None = None) -> dict:
    rows = read_ledger(candidate_ledger)
    denominators = read_generation_denominators(generation_summary)
    aggregates = aggregate(rows, denominators)

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "generation": output_dir / "ltmd_analytics_indigenous_generation_0_1.csv",
        "stratum": output_dir / "ltmd_analytics_indigenous_strata_0_1.csv",
        "language": output_dir / "ltmd_analytics_indigenous_language_matrix_0_1.csv",
        "term": output_dir / "ltmd_analytics_indigenous_explicit_terms_0_1.csv",
        "validation_states": output_dir / "ltmd_analytics_indigenous_validation_state_0_1.csv",
    }
    write_csv(outputs["generation"], aggregates["generation"], ["generation"])
    write_csv(outputs["stratum"], aggregates["stratum"], ["generation", "grade_code", "wave"])
    write_csv(outputs["language"], aggregates["language"], ["language_group", "generation"])
    write_csv(outputs["term"], aggregates["term"], ["explicit_term", "generation"])
    write_csv(outputs["validation_states"], aggregates["validation_states"], ["validation_status"])

    manifest = {
        "version": VERSION,
        "input": {
            "candidate_ledger_sha256": sha256_file(candidate_ledger),
            "generation_summary_sha256": sha256_file(generation_summary) if generation_summary else None,
            "candidate_rows": len(rows),
        },
        "privacy": {
            "page_ids_emitted": False,
            "source_urls_emitted": False,
            "source_or_ocr_hashes_emitted": False,
            "ocr_text_or_snippets_emitted": False,
        },
        "scientific_state": {
            "human_validation_required_for_semantic_ready": True,
            "semantic_ready_promotions": 0,
            "allowed_output_states": ["computational_candidate", "exploratory_signal"],
            "note": (
                "Aggregates are suitable for LTMD Analytics exploration and product workflows, "
                "not for validated historical prevalence claims."
            ),
        },
        "outputs": {
            path.name: {"sha256": sha256_file(path), "rows": len(aggregates[key])}
            for key, path in outputs.items()
        },
    }
    manifest_path = output_dir / "ltmd_analytics_indigenous_manifest_0_1.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["outputs"][manifest_path.name] = {"sha256": sha256_file(manifest_path), "rows": 1}
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-ledger", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--generation-summary")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    manifest = run(
        candidate_ledger=Path(args.candidate_ledger),
        output_dir=Path(args.output_dir),
        generation_summary=Path(args.generation_summary) if args.generation_summary else None,
    )
    print(json.dumps({
        "version": manifest["version"],
        "candidate_rows": manifest["input"]["candidate_rows"],
        "semantic_ready_promotions": manifest["scientific_state"]["semantic_ready_promotions"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
