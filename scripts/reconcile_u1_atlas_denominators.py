#!/usr/bin/env python3
"""LTMD-U1: reconcile public Indigenous candidate strata against a *private* corpus manifest.

Reads the true private manifest locally. Emits ONLY a non-reconstructive audit certificate,
never the denominator cells or per-cell rates. Not for GitHub-hosted CI with private inputs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "LTMD_U1_PRIVATE_DENOMINATOR_AUDIT_0.1"
EXPECTED_UNIVERSE = 86549
EXPECTED_CELLS = 267
EXPECTED_CANDIDATE_CELLS = 140
EXPECTED_CANDIDATE_PAGES = 1151
STRATA_FIELDS = (
    "generation", "grade_code", "wave", "candidate_pages", "explicit_general_pages",
    "named_language_contextual_pages", "candidate_books", "epistemic_state",
)
GENERATION_FIELDS = (
    "generation", "corpus_total_pages", "candidate_pages", "explicit_general_pages",
    "named_language_contextual_pages", "candidate_books",
    "candidate_pages_per_1000_corpus_pages", "epistemic_state",
)
PRIVACY_FIELDS = {
    "page_id", "canonical_viewer_key", "ocr_text", "search_text", "source_url",
    "source_asset_url", "ocr_sha256", "private_path", "source_hash", "viewer_key",
}


def fail(message: str) -> None:
    raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def loaded_json(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict):
        fail("Expected JSON object: " + path.name)
    return data, sha256(raw)


def verified_csv(path: Path, metadata: dict, fields: tuple[str, ...]) -> list[dict]:
    raw = path.read_bytes()
    expected = metadata["sha256"]
    digest_as_is = sha256(raw)
    digest_as_crlf = sha256(raw.replace(b"\n", b"\r\n")) if b"\r" not in raw else digest_as_is
    if expected not in (digest_as_is, digest_as_crlf):
        fail("Public CSV checksum mismatch: " + path.name)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != fields:
            fail("Unexpected public CSV schema/unsafe fields: " + path.name)
        if PRIVACY_FIELDS.intersection(reader.fieldnames or ()):
            fail("Prohibited fields in public CSV: " + path.name)
        rows = list(reader)
    if len(rows) != metadata["rows"] or any(
        None in row or any(value is None for value in row.values()) for row in rows
    ):
        fail("Public CSV row cardinality or row structure mismatch: " + path.name)
    return rows


def int_value(value, label: str, minimum=0) -> int:
    if type(value) is int:
        number = value
    elif isinstance(value, str) and value.isdecimal():
        number = int(value)
    else:
        fail("Noninteger value: " + label)
    if number < minimum:
        fail("Out of range integer: " + label)
    return number


def key(row: dict) -> tuple[int, int, str]:
    year = int_value(row["generation"], "generation", 1)
    grade = int_value(row["grade_code"], "grade_code", 1)
    wave = row["wave"]
    if grade not in range(1, 7) or not isinstance(wave, str) or not wave.startswith("W") or not wave[1:].isdecimal():
        fail("Malformed generation-grade-wave key")
    return year, grade, wave


def reconcile(private: dict, private_sha: str, public_summary: dict,
              public_indigenous_manifest: dict, strata: list[dict],
              generations: list[dict], *, production: bool = True) -> dict:
    """Return public-safe, schema-limited audit certificate; never leak denominator rows."""
    full = public_summary["full_manifest"]
    if private_sha != full["sha256"] or full.get("preserved_private") is not True:
        fail("Private manifest SHA-256 differs from canonical public receipt")
    if private["manifest_version"] != full["version"]:
        fail("Private manifest version does not match public receipt")
    if private["index"]["sha256"] != public_summary["index"]["sha256"]:
        fail("Index SHA differs between private manifest and public receipt")
    if private["index"].get("private") is not True or private["index"].get("publish_index_file") is not False:
        fail("Index privacy contract violated")
    if private.get("denominator_policy") != {
        "filtered_denominators_come_from_same_universal_index": True,
        "silent_imputation": False,
        "wave_is_operational_not_curricular_ontology": True,
        "zero_hits_demonstrate_absence": False,
    }:
        fail("Denominator policy contract mismatch")
    if private["scientific_state"].get("semantic_ready") is not False or \
       private["scientific_state"].get("text_verified") is not False or \
       public_summary["scientific_state"].get("semantic_ready") is not False or \
       public_indigenous_manifest["scientific_state"].get("human_validation_complete") is not False or \
       int_value(public_indigenous_manifest["scientific_state"].get("semantic_ready_promotions"), "promotions") != 0:
        fail("Semantic/human validation state altered")
    dims = private["dimensions"]
    denom_cells = dims["nonempty_generation_grade_wave_cells"]
    expected = public_summary["dimension_cardinality"]["nonempty_generation_grade_wave_cells"]
    if len(denom_cells) != expected or (production and len(denom_cells) != EXPECTED_CELLS):
        fail("Private denominator cell cardinality mismatch")
    if len(strata) != public_indigenous_manifest["cardinality"]["stratum_rows"] or \
       (production and len(strata) != EXPECTED_CANDIDATE_CELLS):
        fail("Public stratum cardinality mismatch")
    by_key = {}
    marginals = {dim: Counter() for dim in ("generation", "grade_code", "wave")}
    for cell in denom_cells:
        if set(cell) != {"generation", "grade_code", "wave", "pages", "canonical_objects"}:
            fail("Unexpected private cell schema")
        k = key(cell)
        if k in by_key:
            fail("Duplicate private denominator cell")
        pages = int_value(cell["pages"], "pages", 1)
        books = int_value(cell["canonical_objects"], "cell objects", 1)
        if books > pages:
            fail("Cell objects exceed pages")
        by_key[k] = cell
        for dim, v in zip(("generation", "grade_code", "wave"), k):
            marginals[dim][str(v)] += pages
    universe = int_value(private["universe"]["indexed_pages"], "indexed_pages", 1)
    if universe != public_summary["universe"]["indexed_pages"] or \
       universe != sum(x["pages"] for x in denom_cells) or \
       (production and universe != EXPECTED_UNIVERSE):
        fail("Corpus denominator total mismatch")
    if private["universe"].get("canonical_processing_objects") != public_summary["universe"]["canonical_processing_objects"]:
        fail("Canonical objects metadata mismatch")
    for dim, reference in (
        ("generation", "generations"), ("grade_code", "grades"), ("wave", "waves")
    ):
        published = dims[dim]
        if len(published) != public_summary["dimension_cardinality"][reference]:
            fail("Dimension cardinality mismatch: " + dim)
        rec = {}
        for value in published:
            v = value["value"]
            if v in rec:
                fail("Duplicate dimension summary value: " + dim)
            rec[v] = int_value(value["pages"], "dimension pages", 1)
        if dict(marginals[dim]) != rec:
            fail("Denominator cell marginal totals differ from original manifest for " + dim)
    by_generation = defaultdict(Counter)
    seen = set()
    for row in strata:
        k = key(row)
        if k in seen or k not in by_key:
            fail("Missing or duplicate stratum key in canonical private manifest")
        seen.add(k)
        candidate = int_value(row["candidate_pages"], "candidate_pages", 1)
        books = int_value(row["candidate_books"], "candidate_books")
        explicit = int_value(row["explicit_general_pages"], "explicit")
        named = int_value(row["named_language_contextual_pages"], "named")
        if row["epistemic_state"] != "exploratory_signal" or \
           max(candidate, books, explicit, named) > by_key[k]["pages"] or \
           max(books, explicit, named) > candidate:
            fail("Candidate count, status or books incompatible with denominator")
        for column, value in (("candidate_pages", candidate), ("explicit_general_pages", explicit),
                              ("named_language_contextual_pages", named)):
            by_generation[k[0]][column] += value
    gen_keys = set()
    for g in generations:
        year = int_value(g["generation"], "generation", 1)
        if year in gen_keys or g["epistemic_state"] != "exploratory_signal":
            fail("Generation row duplicated or has invalid state")
        gen_keys.add(year)
        if int_value(g["corpus_total_pages"], "generation corpus") != marginals["generation"][str(year)]:
            fail("Generation denominator not reconciled with private manifest")
        for column in ("candidate_pages", "explicit_general_pages", "named_language_contextual_pages"):
            if int_value(g[column], column) != by_generation[year][column]:
                fail("Candidate generation marginal mismatch for " + column)
        if int_value(g["candidate_books"], "candidate_books") > int_value(g["candidate_pages"], "candidates"):
            fail("Candidate generation book counts exceed candidate pages")
        observed_rate = float(g["candidate_pages_per_1000_corpus_pages"])
        expected_rate = round(1000 * int(g["candidate_pages"]) / int(g["corpus_total_pages"]), 4)
        if abs(observed_rate - expected_rate) > 0.00015:
            fail("Public generation rate does not use canonical denominator")
    if gen_keys != {int(row["value"]) for row in dims["generation"]}:
        fail("Generation domains do not coincide")
    all_candidate_pages = sum(by_generation[y]["candidate_pages"] for y in gen_keys)
    if all_candidate_pages != public_indigenous_manifest["cardinality"]["candidate_pages"] or \
       (production and all_candidate_pages != EXPECTED_CANDIDATE_PAGES):
        fail("Total candidate page count does not reconcile")
    other_keys = set(by_key) - seen
    # The certificate contains no generation-grade-wave denominators or stratum rates.
    return {
        "certificate_version": VERSION,
        "status": "structurally_and_numerically_reconciled",
        "source_integrity": {
            "private_manifest_sha256": private_sha,
            "private_index_sha256_from_manifest": private["index"]["sha256"],
            "indigenous_analysis_version": public_indigenous_manifest["version"],
            "public_manifest_version": public_summary["summary_version"],
        },
        "reconciliation": {
            "denominator_cells": len(denom_cells),
            "candidate_strata": len(strata),
            "matched_candidate_strata": len(seen),
            "cells_without_candidate_strata": len(other_keys),
            "missing_denominators": 0,
            "duplicate_denominators": 0,
            "candidate_count_violations": 0,
            "indexed_corpus_pages": universe,
            "candidate_page_observations": all_candidate_pages,
            "reconciled_generations": len(gen_keys),
        },
        "checks": {
            "private_sha256_matches_public_canonical_receipt": True,
            "private_manifest_dimension_marginals_reconcile": True,
            "unique_composite_cell_keys": True,
            "all_candidate_strata_found_in_private_denominators": True,
            "candidate_counts_not_greater_than_denominator": True,
            "generation_public_aggregates_reconcile": True,
            "epistemic_state_is_exploratory": True,
        },
        "scientific_boundary": {
            "human_validation_complete": False,
            "semantic_ready": False,
            "no_yearly_interpolation": True,
            "empty_candidate_cells_are_not_historical_absence": True,
            "no_private_cell_denominators_exported": True,
            "no_private_cell_rates_exported": True,
            "legality_gate_issue_2_unchanged": True,
        },
    }


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-manifest", type=Path, required=True)
    ap.add_argument("--public-summary", type=Path, default=Path(__file__).resolve().parents[1] / "data/research/ltmd_u1_corpus_analytics_manifest_summary_0_1.json")
    ap.add_argument("--public-indigenous-manifest", type=Path, default=Path(__file__).resolve().parents[1] / "data/analytics/ltmd_analytics_indigenous_manifest_0_1.json")
    ap.add_argument("--strata", type=Path, default=Path(__file__).resolve().parents[1] / "data/analytics/ltmd_analytics_indigenous_strata_0_1.csv")
    ap.add_argument("--generation", type=Path, default=Path(__file__).resolve().parents[1] / "data/analytics/ltmd_analytics_indigenous_generation_0_1.csv")
    ap.add_argument("--certificate-out", type=Path, required=True)
    args = ap.parse_args(argv)
    private, private_sha = loaded_json(args.private_manifest)
    summary, _ = loaded_json(args.public_summary)
    indigenous, _ = loaded_json(args.public_indigenous_manifest)
    rows = verified_csv(args.strata, indigenous["outputs"][args.strata.name], STRATA_FIELDS)
    generations = verified_csv(args.generation, indigenous["outputs"][args.generation.name], GENERATION_FIELDS)
    audit = reconcile(private, private_sha, summary, indigenous, rows, generations)
    args.certificate_out.parent.mkdir(parents=True, exist_ok=True)
    args.certificate_out.write_text(json.dumps(audit, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print("RECONCILED", audit["reconciliation"]["matched_candidate_strata"], "of",
          audit["reconciliation"]["candidate_strata"], "against",
          audit["reconciliation"]["denominator_cells"], "private denominator cells")
    print("Certificate excludes private per-cell denominator information")


if __name__ == "__main__":
    main()