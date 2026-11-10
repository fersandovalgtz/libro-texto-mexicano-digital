"""Synthetic-only tests: never incorporate the private LTMD manifest into CI."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

SOURCE = Path(__file__).parents[1] / "scripts" / "reconcile_u1_atlas_denominators.py"
SPEC = importlib.util.spec_from_file_location("reconcile_u1_atlas_denominators", SOURCE)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def valid_fixture():
    cells = [
        {"generation": 1960, "grade_code": 1, "wave": "W1", "pages": 3, "canonical_objects": 1},
        {"generation": 1960, "grade_code": 2, "wave": "W2", "pages": 4, "canonical_objects": 1},
        {"generation": 1966, "grade_code": 2, "wave": "W2", "pages": 5, "canonical_objects": 1},
    ]
    private = {
        "manifest_version": "TEST_MANIFEST",
        "index": {"sha256": "a" * 64, "private": True, "publish_index_file": False},
        "denominator_policy": {
            "filtered_denominators_come_from_same_universal_index": True,
            "silent_imputation": False,
            "wave_is_operational_not_curricular_ontology": True,
            "zero_hits_demonstrate_absence": False,
        },
        "scientific_state": {"semantic_ready": False, "text_verified": False},
        "universe": {"indexed_pages": 12, "canonical_processing_objects": 3},
        "dimensions": {
            "nonempty_generation_grade_wave_cells": cells,
            "generation": [{"value": "1960", "pages": 7}, {"value": "1966", "pages": 5}],
            "grade_code": [{"value": "1", "pages": 3}, {"value": "2", "pages": 9}],
            "wave": [{"value": "W1", "pages": 3}, {"value": "W2", "pages": 9}],
        },
    }
    encoded = json.dumps(private).encode()
    summary = {
        "full_manifest": {"sha256": audit.sha256(encoded), "version": "TEST_MANIFEST", "preserved_private": True},
        "index": {"sha256": "a" * 64},
        "universe": {"indexed_pages": 12, "canonical_processing_objects": 3},
        "dimension_cardinality": {"nonempty_generation_grade_wave_cells": 3, "generations": 2, "grades": 2, "waves": 2},
        "summary_version": "TEST_SUMMARY",
        "scientific_state": {"semantic_ready": False},
    }
    indigenous = {
        "version": "TEST_INDIGENOUS",
        "scientific_state": {"human_validation_complete": False, "semantic_ready_promotions": 0},
        "cardinality": {"stratum_rows": 2, "candidate_pages": 3},
    }
    strata = [
        {"generation": "1960", "grade_code": "1", "wave": "W1", "candidate_pages": "1", "candidate_books": "1",
         "explicit_general_pages": "1", "named_language_contextual_pages": "0", "epistemic_state": "exploratory_signal"},
        {"generation": "1966", "grade_code": "2", "wave": "W2", "candidate_pages": "2", "candidate_books": "1",
         "explicit_general_pages": "0", "named_language_contextual_pages": "2", "epistemic_state": "exploratory_signal"},
    ]
    generations = [
        {"generation": "1960", "corpus_total_pages": "7", "candidate_pages": "1", "explicit_general_pages": "1",
         "named_language_contextual_pages": "0", "candidate_books": "1", "epistemic_state": "exploratory_signal",
         "candidate_pages_per_1000_corpus_pages": "142.8571"},
        {"generation": "1966", "corpus_total_pages": "5", "candidate_pages": "2", "explicit_general_pages": "0",
         "named_language_contextual_pages": "2", "candidate_books": "1", "epistemic_state": "exploratory_signal",
         "candidate_pages_per_1000_corpus_pages": "400.0000"},
    ]
    return private, summary, indigenous, strata, generations


def run_fixture(f):
    private, summary, indigenous, strata, generations = f
    raw = json.dumps(private).encode()
    return audit.reconcile(private, audit.sha256(raw), summary, indigenous, strata, generations, production=False)


def test_synthetic_reconciles_and_certificate_has_no_private_cell_details():
    result = run_fixture(valid_fixture())
    assert result["status"] == "structurally_and_numerically_reconciled"
    assert result["reconciliation"]["matched_candidate_strata"] == 2
    assert result["reconciliation"]["cells_without_candidate_strata"] == 1
    rendered = json.dumps(result)
    assert '"candidate_pages_per_1000"' not in rendered
    assert '"pages": 3' not in rendered
    assert '"grade_code"' not in rendered
    assert result["scientific_boundary"]["semantic_ready"] is False


def test_nonmatching_private_sha_is_rejected():
    f = valid_fixture()
    f[1]["full_manifest"]["sha256"] = "b" * 64
    with pytest.raises(ValueError, match="SHA-256"):
        run_fixture(f)


def test_duplicate_private_cell_is_rejected():
    f = valid_fixture()
    f[0]["dimensions"]["nonempty_generation_grade_wave_cells"][1] = deepcopy(f[0]["dimensions"]["nonempty_generation_grade_wave_cells"][0])
    f[1]["full_manifest"]["sha256"] = audit.sha256(json.dumps(f[0]).encode())
    with pytest.raises(ValueError, match="Duplicate private"):
        run_fixture(f)


def test_private_marginal_tamper_is_rejected():
    f = valid_fixture()
    f[0]["dimensions"]["grade_code"][1]["pages"] = 10
    f[1]["full_manifest"]["sha256"] = audit.sha256(json.dumps(f[0]).encode())
    with pytest.raises(ValueError, match="marginal totals"):
        run_fixture(f)


def test_missing_private_key_rejected():
    f = valid_fixture()
    f[3][0]["wave"] = "W3"
    with pytest.raises(ValueError, match="Missing or duplicate stratum key"):
        run_fixture(f)


def test_candidate_exceeding_private_denominator_rejected():
    f = valid_fixture()
    f[3][0]["candidate_pages"] = "4"
    with pytest.raises(ValueError, match="incompatible with denominator"):
        run_fixture(f)


def test_candidate_generation_mismatch_rejected():
    f = valid_fixture()
    f[4][0]["explicit_general_pages"] = "0"
    with pytest.raises(ValueError, match="generation marginal"):
        run_fixture(f)


def test_private_index_hash_mismatch_rejected():
    f = valid_fixture()
    f[0]["index"]["sha256"] = "b" * 64
    f[1]["full_manifest"]["sha256"] = audit.sha256(json.dumps(f[0]).encode())
    with pytest.raises(ValueError, match="Index SHA"):
        run_fixture(f)


def test_semantic_promotion_rejected():
    f = valid_fixture()
    f[2]["scientific_state"]["human_validation_complete"] = True
    with pytest.raises(ValueError, match="Semantic/human"):
        run_fixture(f)


def test_production_counts_dont_accept_synthetic():
    f = valid_fixture()
    private, summary, indigenous, strata, generations = f
    with pytest.raises(ValueError, match="Private denominator cell cardinality"):
        audit.reconcile(private, audit.sha256(json.dumps(private).encode()), summary, indigenous, strata, generations)


def test_strict_public_csv_rejects_unexpected_columns_and_bad_checksum(tmp_path):
    p = tmp_path / "rows.csv"
    p.write_text("generation,grade_code,page_id\n1960,1,x\n")
    meta = {"sha256": audit.sha256(p.read_bytes()), "rows": 1}
    with pytest.raises(ValueError, match="Unexpected public CSV schema"):
        audit.verified_csv(p, meta, audit.STRATA_FIELDS)
    p.write_text("generation,grade_code,wave\n1960,1,W1\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        audit.verified_csv(p, meta, ("generation", "grade_code", "wave"))


def test_lf_crlf_hash_normalization_is_safe(tmp_path):
    p = tmp_path / "rows.csv"
    p.write_bytes(b"generation,grade_code,wave\n1960,1,W1\n")
    original = p.read_bytes()
    meta = {"sha256": audit.sha256(original.replace(b"\n", b"\r\n")), "rows": 1}
    assert audit.verified_csv(p, meta, ("generation", "grade_code", "wave"))[0]["generation"] == "1960"
    p.write_bytes(original.replace(b"W1", b"W2"))
    with pytest.raises(ValueError, match="checksum mismatch"):
        audit.verified_csv(p, meta, ("generation", "grade_code", "wave"))