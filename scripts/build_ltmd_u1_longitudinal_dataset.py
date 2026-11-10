#!/usr/bin/env python3
"""Build a public-safe cohort/stratum/language atlas dataset from frozen LTMD-U1 aggregates.

No private universal index, page identifiers, OCR or document bytes are read.
Rates for grade/wave strata are deliberately null without matching corpus denominators.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "LTMD_U1_ATLAS_LONGITUDINAL_DATASET_0.2"
FILES = {
    "generation": "ltmd_analytics_indigenous_generation_0_1.csv",
    "strata": "ltmd_analytics_indigenous_strata_0_1.csv",
    "language": "ltmd_analytics_indigenous_language_matrix_0_1.csv",
    "terms": "ltmd_analytics_indigenous_explicit_terms_0_1.csv",
    "validation": "ltmd_analytics_indigenous_validation_state_0_1.csv",
}
HEADERS = {
    "generation": ("generation", "corpus_total_pages", "candidate_pages", "explicit_general_pages",
                   "named_language_contextual_pages", "candidate_books",
                   "candidate_pages_per_1000_corpus_pages", "epistemic_state"),
    "strata": ("generation", "grade_code", "wave", "candidate_pages", "explicit_general_pages",
               "named_language_contextual_pages", "candidate_books", "epistemic_state"),
    "language": ("language_group", "generation", "grade_code", "wave",
                 "candidate_pages", "candidate_books", "epistemic_state"),
    "terms": ("explicit_term", "generation", "candidate_pages", "candidate_books", "epistemic_state"),
    "validation": ("validation_status", "candidate_pages"),
}
COHORTS = (
    ("1960_1966", (1960, 1966)),
    ("1972_1988", (1972, 1982, 1988)),
    ("1993", (1993,)),
    ("2008_2011", (2008, 2011)),
    ("2014_2019", (2014, 2018, 2019)),
)
WAVES = {
    "W1": "ciencias_naturales", "W2": "matematicas", "W3": "espanol_lengua",
    "W4": "ciencias_sociales", "W5": "historia", "W6": "geografia_atlas",
    "W7": "civica_etica", "W8": "artes", "W9": "educacion_fisica",
    "W10": "integrados_multiarea", "W11": "otros_no_clasificados",
}
YEAR_TO_COHORT = {year: ident for ident, years in COHORTS for year in years}
EXPECTED_YEARS = tuple(year for _, years in COHORTS for year in years)
FORBIDDEN_FIELDS = {"page_id", "canonical_viewer_key", "ocr_text", "search_text",
                    "source_url", "source_asset_url", "ocr_sha256", "private_path"}
MANIFEST_NAME = "ltmd_analytics_indigenous_manifest_0_1.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_file(path: Path, expected: str) -> str:
    raw = path.read_bytes()
    as_is = digest(raw)
    # GitHub checkout converts the canonical CRLF bytes of these archived CSVs to LF.
    crlf = digest(raw.replace(b"\n", b"\r\n")) if b"\r" not in raw else as_is
    if expected not in (as_is, crlf):
        raise ValueError("SHA-256 mismatch for " + path.name)
    return expected


def csv_rows(path: Path, headers: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != headers:
            raise ValueError("Unexpected/unsafe columns in " + path.name)
        if FORBIDDEN_FIELDS.intersection(reader.fieldnames or []):
            raise ValueError("Private fields in " + path.name)
        rows = list(reader)
    if not rows or any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("Empty or malformed table " + path.name)
    return rows


def nonnegative(row: dict, name: str, *, positive: bool = False) -> int:
    raw = str(row[name])
    if not raw.isdecimal():
        raise ValueError("Invalid integer " + name)
    value = int(raw)
    if value < (1 if positive else 0):
        raise ValueError("Invalid nonnegative count " + name)
    return value


def validate_coverage(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for wave, domain in WAVES.items():
        if not any(line.startswith("| " + wave + " | " + chr(96) + domain + chr(96) + " |")
                   for line in text.splitlines()):
            raise ValueError("Operational domain definition changed for " + wave)
    return digest(path.read_bytes())


def build_dataset(data_dir: Path, *, coverage: Path | None = None) -> dict:
    manifest_data = (data_dir / MANIFEST_NAME).read_bytes()
    manifest = json.loads(manifest_data)
    scientific = manifest["scientific_state"]
    if scientific.get("human_validation_complete") is not False or scientific.get("semantic_ready_promotions") != 0:
        raise ValueError("Human/semantic validation promotion is not authorized")
    if manifest.get("privacy", {}).get("page_ids_emitted") is not False:
        raise ValueError("Privacy gate not satisfied")
    inputs = {}
    rows = {}
    for kind, filename in FILES.items():
        expected = manifest["outputs"][filename]["sha256"]
        inputs[filename] = verify_file(data_dir / filename, expected)
        rows[kind] = csv_rows(data_dir / filename, HEADERS[kind])
        if len(rows[kind]) != manifest["outputs"][filename]["rows"]:
            raise ValueError("Input row cardinality mismatch: " + filename)
    if len(rows["validation"]) != 1 or rows["validation"][0]["validation_status"] != "not_visually_validated":
        raise ValueError("Unexpected visual validation state")

    generation = []
    seen_years = set()
    for r in rows["generation"]:
        year = nonnegative(r, "generation", positive=True)
        if year in seen_years or year not in YEAR_TO_COHORT or r["epistemic_state"] != "exploratory_signal":
            raise ValueError("Invalid or duplicate generation")
        seen_years.add(year)
        total = nonnegative(r, "corpus_total_pages", positive=True)
        pages = nonnegative(r, "candidate_pages")
        explicit = nonnegative(r, "explicit_general_pages")
        named = nonnegative(r, "named_language_contextual_pages")
        books = nonnegative(r, "candidate_books")
        if max(explicit, named, books) > pages or pages > total:
            raise ValueError("Generation totals inconsistent")
        rate = round(pages * 1000 / total, 4)
        if abs(rate - float(r["candidate_pages_per_1000_corpus_pages"])) > 0.00015:
            raise ValueError("Invalid generation denominator/rate")
        generation.append({
            "generation": year, "cohort_id": YEAR_TO_COHORT[year], "corpus_pages": total,
            "candidate_pages": pages, "explicit_general_pages": explicit,
            "named_language_contextual_pages": named, "candidate_books_within_generation": books,
            "candidate_pages_per_1000": rate, "epistemic_state": "exploratory_signal",
        })
    if seen_years != set(EXPECTED_YEARS) or len(generation) != 11:
        raise ValueError("Missing generation coverage")
    generation.sort(key=lambda x: x["generation"])
    by_year = {r["generation"]: r for r in generation}
    total_candidates = sum(r["candidate_pages"] for r in generation)
    if total_candidates != manifest["cardinality"]["candidate_pages"] or total_candidates != nonnegative(rows["validation"][0], "candidate_pages"):
        raise ValueError("Candidate totals do not reconcile")

    stratum = []
    seen_cells = set()
    sums = defaultdict(Counter)
    for r in rows["strata"]:
        year, grade, wave = nonnegative(r, "generation"), nonnegative(r, "grade_code"), r["wave"]
        key = (year, grade, wave)
        if year not in by_year or not 1 <= grade <= 6 or wave not in WAVES or key in seen_cells or r["epistemic_state"] != "exploratory_signal":
            raise ValueError("Invalid/duplicate generation-grade-wave stratum")
        seen_cells.add(key)
        pages = nonnegative(r, "candidate_pages", positive=True)
        explicit = nonnegative(r, "explicit_general_pages")
        named = nonnegative(r, "named_language_contextual_pages")
        books = nonnegative(r, "candidate_books")
        if max(explicit, named, books) > pages:
            raise ValueError("Invalid stratum counts")
        for field, count in (("candidate_pages", pages), ("explicit_general_pages", explicit),
                             ("named_language_contextual_pages", named)):
            sums[year][field] += count
        stratum.append({
            "generation": year, "cohort_id": YEAR_TO_COHORT[year],
            "grade_code": grade, "wave": wave, "operational_domain": WAVES[wave],
            "candidate_pages": pages, "explicit_general_pages": explicit,
            "named_language_contextual_pages": named, "candidate_books_within_stratum": books,
            "corpus_pages_same_stratum": None, "candidate_pages_per_1000": None,
            "denominator_state": "private_manifest_required", "epistemic_state": "exploratory_signal",
        })
    if len(stratum) != manifest["cardinality"]["stratum_rows"]:
        raise ValueError("Unexpected number of strata")
    for year, original in by_year.items():
        for field in ("candidate_pages", "explicit_general_pages", "named_language_contextual_pages"):
            if sums[year][field] != original[field]:
                raise ValueError("Stratum/generation reconciliation failed: " + str(year) + " " + field)
    stratum.sort(key=lambda x: (x["generation"], x["grade_code"], int(x["wave"][1:])))

    languages = []
    seen_languages = set()
    for r in rows["language"]:
        year, grade, wave = nonnegative(r, "generation"), nonnegative(r, "grade_code"), r["wave"]
        label = r["language_group"].strip()
        key = (label, year, grade, wave)
        pages = nonnegative(r, "candidate_pages", positive=True)
        books = nonnegative(r, "candidate_books")
        if not label or len(label) > 120 or (year, grade, wave) not in seen_cells or key in seen_languages or r["epistemic_state"] != "computational_candidate" or books > pages:
            raise ValueError("Invalid language matrix entry")
        seen_languages.add(key)
        parent_count = next(x["candidate_pages"] for x in stratum if (x["generation"], x["grade_code"], x["wave"]) == (year, grade, wave))
        if pages > parent_count:
            raise ValueError("Language-specific count exceeds stratum")
        languages.append({
            "language_group": label, "generation": year, "cohort_id": YEAR_TO_COHORT[year],
            "grade_code": grade, "wave": wave, "operational_domain": WAVES[wave],
            "candidate_pages_for_language_in_stratum": pages,
            "candidate_books_for_language_within_stratum": books,
            "corpus_pages_same_stratum": None, "candidate_pages_per_1000": None,
            "denominator_state": "private_manifest_required", "epistemic_state": "computational_candidate",
        })
    if len(languages) != manifest["cardinality"]["language_matrix_rows"]:
        raise ValueError("Language matrix cardinality mismatch")
    languages.sort(key=lambda x: (x["language_group"], x["generation"], x["grade_code"], int(x["wave"][1:])))

    terms = []
    term_keys = set()
    for r in rows["terms"]:
        year = nonnegative(r, "generation")
        label = r["explicit_term"].strip()
        key = (label, year)
        pages = nonnegative(r, "candidate_pages", positive=True)
        books = nonnegative(r, "candidate_books")
        if year not in by_year or not label or len(label) > 120 or key in term_keys or books > pages or pages > by_year[year]["candidate_pages"] or r["epistemic_state"] != "computational_candidate":
            raise ValueError("Invalid/duplicate term entry")
        term_keys.add(key)
        terms.append({"explicit_term": label, "generation": year,
                      "cohort_id": YEAR_TO_COHORT[year], "candidate_pages_for_term": pages,
                      "candidate_books_for_term_within_generation": books,
                      "epistemic_state": "computational_candidate"})
    if len(terms) != manifest["cardinality"]["explicit_term_rows"]:
        raise ValueError("Explicit term matrix cardinality mismatch")
    terms.sort(key=lambda x: (x["explicit_term"], x["generation"]))

    cohorts = []
    for ident, years in COHORTS:
        slice_ = [by_year[year] for year in years]
        pages = sum(r["corpus_pages"] for r in slice_)
        hits = sum(r["candidate_pages"] for r in slice_)
        cohorts.append({
            "cohort_id": ident, "observed_generations": list(years),
            "corpus_pages": pages, "candidate_pages": hits,
            "explicit_general_pages": sum(r["explicit_general_pages"] for r in slice_),
            "named_language_contextual_pages": sum(r["named_language_contextual_pages"] for r in slice_),
            "candidate_pages_per_1000": round(hits * 1000 / pages, 4),
            "distinct_candidate_books_across_generations": None,
            "distinct_books_state": "not_inferable_from_public_aggregates",
            "epistemic_state": "exploratory_signal",
        })

    return {
        "version": VERSION,
        "provenance": {
            "source_analytics_version": manifest["version"],
            "source_analysis_version": manifest["source_analysis_version"],
            "public_source_manifest_sha256": digest(manifest_data),
            "public_inputs_canonical_sha256": inputs,
            "coverage_sha256": validate_coverage(coverage) if coverage is not None else None,
        },
        "scope": {
            "observed_generations": sorted(seen_years), "cohort_count": len(cohorts),
            "generation_count": len(generation), "stratum_count": len(stratum),
            "language_cells": len(languages), "explicit_term_cells": len(terms),
            "corpus_pages_indexed": sum(r["corpus_pages"] for r in generation),
            "candidate_pages": total_candidates,
            "generation_grade_wave_corpus_denominators_public": False,
        },
        "scientific_state": {
            "human_validation_complete": False, "semantic_ready": False,
            "source_visual_validation": "not_visually_validated",
            "generation_and_cohort_state": "exploratory_signal",
            "language_and_term_state": "computational_candidate",
        },
        "interpretation": {
            "cohorts": "Named sets of observed editorial cuts; not continuous annual series.",
            "rates": "Per 1,000 indexed corpus pages for the same observed generation/cohort only.",
            "strata_rates": "Null until denominator for same generation-grade-wave is retrieved from private canonical index.",
            "books": "Distinct book counts are valid inside each input group; do not add across groups.",
            "overlap": "Explicit and contextual labels, terms and languages can overlap; do not add them as disjoint populations.",
            "wave": "Operational routing domain, not validated curricular subject.",
            "status": "Automated detection and aggregates; not human-validated historical interpretations.",
        },
        "cohorts": cohorts, "generations": generation, "strata": stratum,
        "language_matrix": languages, "explicit_terms": terms,
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "analytics")
    parser.add_argument("--coverage", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "catalog" / "ltmd_u1_coverage.md")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = build_dataset(args.input_dir, coverage=args.coverage)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"version": VERSION, "cohorts": len(result["cohorts"]),
                      "generations": len(result["generations"]), "strata": len(result["strata"]),
                      "language_cells": len(result["language_matrix"]),
                      "candidates": result["scope"]["candidate_pages"]}))


if __name__ == "__main__":
    main()
