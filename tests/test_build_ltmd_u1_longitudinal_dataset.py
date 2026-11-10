"""Integrity and disclosure tests for the public-safe cohort/stratum atlas build."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SRC = Path(__file__).parents[1] / "scripts" / "build_ltmd_u1_longitudinal_dataset.py"
SPEC = importlib.util.spec_from_file_location("ltmd_u1_longitudinal_dataset", SRC)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def fixture(tmp_path):
    items = {}
    years = sorted(mod.YEAR_TO_COHORT)
    gr = [list(mod.HEADERS["generation"])]
    st = [list(mod.HEADERS["strata"])]
    lg = [list(mod.HEADERS["language"])]
    tr = [list(mod.HEADERS["terms"])]
    total = 0
    for year in years:
        n = 2 if year == 1993 else 1
        total += n
        gr.append([year, 1000, n, 1, 0, 1, str(float(n)), "exploratory_signal"])
        st.append([year, 3, "W3", n, 1, 0, 1, "exploratory_signal"])
    lg.append(["Maya", 1993, 3, "W3", 1, 1, "computational_candidate"])
    tr.append(["lenguas indigenas", 1993, 1, 1, "computational_candidate"])
    val = [list(mod.HEADERS["validation"]), ["not_visually_validated", total]]
    tables = {"generation": gr, "strata": st, "language": lg, "terms": tr, "validation": val}
    manifest = {
        "version": "LTMD_ANALYTICS_INDIGENOUS_0.1",
        "source_analysis_version": "fixture",
        "privacy": {"page_ids_emitted": False},
        "scientific_state": {"human_validation_complete": False, "semantic_ready_promotions": 0},
        "cardinality": {"candidate_pages": total, "stratum_rows": 11,
                        "language_matrix_rows": 1, "explicit_term_rows": 1},
        "outputs": {},
    }
    for kind, table in tables.items():
        name = mod.FILES[kind]
        with (tmp_path / name).open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(table)
        manifest["outputs"][name] = {"sha256": mod.digest((tmp_path / name).read_bytes()),
                                     "rows": len(table) - 1}
    (tmp_path / mod.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    cov = tmp_path / "coverage.md"
    cov.write_text("\n".join("| " + wave + " | " + chr(96) + domain + chr(96) + " | 0 |"
                             for wave, domain in mod.WAVES.items()), encoding="utf-8")
    return tmp_path, cov, manifest


def refresh_hash(path, manifest):
    manifest["outputs"][path.name]["sha256"] = mod.digest(path.read_bytes())
    (path.parent / mod.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")


def test_reconciles_cohorts_and_disallows_false_rates(tmp_path):
    d, cov, _ = fixture(tmp_path)
    p = mod.build_dataset(d, coverage=cov)
    assert len(p["generations"]) == 11
    assert len(p["cohorts"]) == 5
    assert len(p["strata"]) == 11
    assert p["scope"]["candidate_pages"] == 12
    assert sum(x["candidate_pages"] for x in p["cohorts"]) == 12
    assert p["cohorts"][0]["observed_generations"] == [1960, 1966]
    assert p["cohorts"][0]["candidate_pages_per_1000"] == 1.0
    assert all(x["candidate_pages_per_1000"] is None for x in p["strata"])
    assert all(x["corpus_pages_same_stratum"] is None for x in p["language_matrix"])
    assert all(x["distinct_candidate_books_across_generations"] is None for x in p["cohorts"])
    assert p["scientific_state"]["human_validation_complete"] is False
    assert p["scientific_state"]["semantic_ready"] is False
    rendered = json.dumps(p, ensure_ascii=False)
    for key in mod.FORBIDDEN_FIELDS:
        assert '"' + key + '"' not in rendered


def test_deterministic_payload(tmp_path):
    d, cov, _ = fixture(tmp_path)
    x = mod.build_dataset(d, coverage=cov)
    assert json.dumps(x, ensure_ascii=False, sort_keys=True) == json.dumps(
        mod.build_dataset(d, coverage=cov), ensure_ascii=False, sort_keys=True)


def test_fails_on_upstream_sha_mismatch(tmp_path):
    d, cov, _ = fixture(tmp_path)
    file = d / mod.FILES["strata"]
    file.write_bytes(file.read_bytes() + b"x")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        mod.build_dataset(d, coverage=cov)


def test_refuses_private_columns_even_if_fingerprint_updated(tmp_path):
    d, cov, manifest = fixture(tmp_path)
    f = d / mod.FILES["strata"]
    f.write_text(f.read_text().replace("generation,grade_code", "page_id,generation,grade_code"),
                 encoding="utf-8")
    refresh_hash(f, manifest)
    with pytest.raises(ValueError, match="Unexpected/unsafe columns"):
        mod.build_dataset(d, coverage=cov)


def test_refuses_stratum_generation_reconciliation_error(tmp_path):
    d, cov, manifest = fixture(tmp_path)
    f = d / mod.FILES["strata"]
    original = f.read_text()
    f.write_text(original.replace("1993,3,W3,2,1,0,1", "1993,3,W3,1,1,0,1"),
                 encoding="utf-8")
    refresh_hash(f, manifest)
    with pytest.raises(ValueError, match="Stratum/generation reconciliation"):
        mod.build_dataset(d, coverage=cov)


def test_refuses_wrong_language_parent_count(tmp_path):
    d, cov, manifest = fixture(tmp_path)
    f = d / mod.FILES["language"]
    f.write_text(f.read_text().replace("Maya,1993,3,W3,1,1", "Maya,1993,3,W3,3,1"),
                 encoding="utf-8")
    refresh_hash(f, manifest)
    with pytest.raises(ValueError, match="exceeds stratum"):
        mod.build_dataset(d, coverage=cov)


def test_rejects_semantic_ready_promotion(tmp_path):
    d, cov, manifest = fixture(tmp_path)
    manifest["scientific_state"]["human_validation_complete"] = True
    (d / mod.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="Human/semantic validation"):
        mod.build_dataset(d, coverage=cov)


def test_rejects_wrong_wave_mapping(tmp_path):
    d, cov, _ = fixture(tmp_path)
    cov.write_text(cov.read_text().replace("espanol_lengua", "materia_inventada"),
                   encoding="utf-8")
    with pytest.raises(ValueError, match="Operational domain"):
        mod.build_dataset(d, coverage=cov)


def test_lf_crlf_checkout_is_accepted_only_with_matching_hash(tmp_path):
    d, cov, manifest = fixture(tmp_path)
    name = mod.FILES["generation"]
    raw = (d / name).read_bytes()
    manifest["outputs"][name]["sha256"] = hashlib.sha256(raw.replace(b"\n", b"\r\n")).hexdigest()
    (d / mod.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    assert mod.build_dataset(d, coverage=cov)["scope"]["candidate_pages"] == 12
    file = d / name
    file.write_bytes(raw.replace(b"1960,1000,1", b"1960,999,1"))
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        mod.build_dataset(d, coverage=cov)
