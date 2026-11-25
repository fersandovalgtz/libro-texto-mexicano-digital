"""Synthetic regression suite for private LTMD-U1 retrieval-quality evaluation.

Everything here is invented for software tests; no CONALITEG book text,
real page identifier, OCR dump, human annotation or private ledger is included.
"""
import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from scripts import evaluate_u1_search_quality as quality


def make_index(tmp_path: Path) -> Path:
    index = tmp_path / "synthetic_universal.sqlite"
    con = sqlite3.connect(index)
    try:
        con.execute("CREATE TABLE index_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID")
        con.execute(
            "INSERT INTO index_meta VALUES(?,?)",
            ("builder_version", json.dumps(quality.search.INDEX_VERSION)),
        )
        con.execute(
            "CREATE TABLE pages (id INTEGER PRIMARY KEY, page_id TEXT NOT NULL, "
            "canonical_viewer_key TEXT NOT NULL, wave TEXT NOT NULL, "
            "catalog_generation INTEGER NOT NULL, grade_code INTEGER NOT NULL, "
            "search_text TEXT NOT NULL)"
        )
        con.execute(
            "CREATE VIRTUAL TABLE pages_fts USING fts5(search_text,content='pages',"
            "content_rowid='id',tokenize='unicode61 remove_diacritics 2')"
        )
        con.executemany(
            "INSERT INTO pages VALUES(?,?,?,?,?,?,?)",
            [
                (1, "synthetic:01", "SYN-A", "W3", 1993, 5,
                 "La democracia implica participación ciudadana"),
                (2, "synthetic:02", "SYN-A", "W3", 1993, 5,
                 "La palabra democracia se imprime como ruido, fuera del concepto"),
                (3, "synthetic:03", "SYN-B", "W3", 1993, 5,
                 "Una página sobre participación política con OCR dem0cracia"),
                (4, "synthetic:04", "SYN-B", "W3", 1993, 5,
                 "La naturaleza y el agua de los ríos"),
                (5, "synthetic:05", "SYN-C", "W7", 2014, 6,
                 "La democracia se relaciona con el voto"),
                (6, "synthetic:06", "SYN-D", "W3", 1993, 5,
                 "Una frase sintética sobre lengua rarámuri"),
            ],
        )
        con.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
        con.commit()
    finally:
        con.close()
    return index


def reference(*, query="democracia", kind="synthetic_fixture",
              design="independent_scope_sample", labels=None, generation="1993"):
    if labels is None:
        labels = [
            {"page_id": "synthetic:01", "relevant": True, "source_checked": False},
            {"page_id": "synthetic:02", "relevant": False, "source_checked": False},
            {"page_id": "synthetic:03", "relevant": True, "source_checked": False},
            {"page_id": "synthetic:04", "relevant": False, "source_checked": False},
        ]
    return {
        "version": quality.VERSION,
        "reference_type": kind,
        "sampling_design": design,
        "query_expression": query,
        "filters": {"generation": [generation], "grade_code": ["5"], "wave": ["W3"]},
        "labels": labels,
    }


def test_confusion_matrix_counts_semantic_fp_and_ocr_fn(tmp_path):
    index = make_index(tmp_path)
    with sqlite3.connect(index) as con:
        report = quality.evaluate(con, reference())
    assert report["confusion_matrix"] == {"tp": 1, "fp": 1, "fn": 1, "tn": 1}
    assert report["sample_metrics"] == {
        "precision": 0.5, "recall": 0.5, "f1": 0.5, "specificity": 0.5
    }
    assert report["sample_size"] == 4
    assert report["human_validation_complete"] is False
    assert report["result_state"] == "synthetic_regression_only"


def test_diacritic_matching_and_true_negative(tmp_path):
    index = make_index(tmp_path)
    labels = [
        {"page_id": "synthetic:06", "relevant": True, "source_checked": False},
        {"page_id": "synthetic:04", "relevant": False, "source_checked": False},
    ]
    with sqlite3.connect(index) as con:
        report = quality.evaluate(con, reference(query="raramuri", labels=labels))
    assert report["confusion_matrix"] == {"tp": 1, "fp": 0, "fn": 0, "tn": 1}
    assert report["sample_metrics"]["precision"] == 1.0
    assert report["sample_metrics"]["recall"] == 1.0


def test_scope_rejects_out_of_scope_labels(tmp_path):
    index = make_index(tmp_path)
    ref = reference()
    ref["labels"][0]["page_id"] = "synthetic:05"  # 2014/W7; not selected 1993/W3
    with sqlite3.connect(index) as con, pytest.raises(ValueError, match="out-of-scope"):
        quality.evaluate(con, ref)


def test_rejects_duplicate_labels(tmp_path):
    index = make_index(tmp_path)
    ref = reference()
    ref["labels"][1]["page_id"] = "synthetic:01"
    with sqlite3.connect(index) as con, pytest.raises(ValueError, match="duplicate"):
        quality.evaluate(con, ref)


def test_human_reference_requires_visual_source_review(tmp_path):
    index = make_index(tmp_path)
    ref = reference(kind="human_adjudicated")
    with sqlite3.connect(index) as con, pytest.raises(ValueError, match="not visually checked"):
        quality.evaluate(con, ref)
    for label in ref["labels"]:
        label["source_checked"] = True
    with sqlite3.connect(index) as con:
        report = quality.evaluate(con, ref)
    assert report["result_state"] == "sample_diagnostic_not_corpus_validated"
    assert report["human_validation_complete"] is False


def test_zero_hits_remains_a_caution_not_evidence_of_absence(tmp_path):
    index = make_index(tmp_path)
    labels = [
        {"page_id": "synthetic:01", "relevant": True, "source_checked": False},
        {"page_id": "synthetic:04", "relevant": False, "source_checked": False},
    ]
    with sqlite3.connect(index) as con:
        report = quality.evaluate(con, reference(query="inexistente", labels=labels))
    assert report["confusion_matrix"] == {"tp": 0, "fp": 0, "fn": 1, "tn": 1}
    assert report["sample_metrics"]["precision"] is None
    assert report["sample_metrics"]["recall"] == 0.0
    assert any("Zero search hits" in item for item in report["warnings"])


def test_purposive_sample_is_not_generalized(tmp_path):
    index = make_index(tmp_path)
    with sqlite3.connect(index) as con:
        report = quality.evaluate(con, reference(design="purposive_sample"))
    assert any("not probabilistic" in item for item in report["warnings"])


@pytest.mark.parametrize("bad", ['"unclosed', ""])
def test_invalid_queries_are_rejected(tmp_path, bad):
    index = make_index(tmp_path)
    with sqlite3.connect(index) as con, pytest.raises((ValueError, RuntimeError)):
        quality.evaluate(con, reference(query=bad))


def test_rejects_nonboolean_or_one_class_only(tmp_path):
    index = make_index(tmp_path)
    ref = reference()
    ref["labels"][0]["relevant"] = 1
    with sqlite3.connect(index) as con, pytest.raises(ValueError, match="relevance"):
        quality.evaluate(con, ref)
    ref = reference()
    for label in ref["labels"]:
        label["relevant"] = True
    with sqlite3.connect(index) as con, pytest.raises(ValueError, match="one relevant and one non-relevant"):
        quality.evaluate(con, ref)


def test_private_run_emits_only_aggregates_and_hashes(tmp_path):
    index = make_index(tmp_path)
    path = tmp_path / "private_labels.json"
    path.write_text(json.dumps(reference(), ensure_ascii=False), encoding="utf-8")
    sha = hashlib.sha256(index.read_bytes()).hexdigest()
    report = quality.run(index, path, expected_index_sha256=sha)
    assert report["provenance"]["index_sha256"] == sha
    assert report["provenance"]["reference_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    serialized = json.dumps(report)
    for forbidden in ("synthetic:01", "synthetic:02", "page_id", "search_text",
                      "La democracia", str(tmp_path), "source_asset_url"):
        assert forbidden not in serialized
    with pytest.raises(ValueError, match="integrity"):
        quality.run(index, path, expected_index_sha256="0" * 64)


def test_reference_version_and_types_are_strict(tmp_path):
    index = make_index(tmp_path)
    ref = reference()
    ref["version"] = "LTMD_U1_SEARCH_QUALITY_999"
    with sqlite3.connect(index) as con, pytest.raises(ValueError, match="version"):
        quality.evaluate(con, ref)
    ref = reference()
    ref["sampling_design"] = "pretend_random"
    with sqlite3.connect(index) as con, pytest.raises(ValueError, match="design"):
        quality.evaluate(con, ref)
