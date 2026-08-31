import csv
import json
import sqlite3
from pathlib import Path

from jsonschema import Draft202012Validator

from analytics_api import app as api


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate(page_id, book, generation, grade, wave, explicit="0", named="0", languages="", terms=""):
    return {
        "page_id": page_id,
        "canonical_viewer_key": book,
        "wave": wave,
        "generation": generation,
        "grade_code": grade,
        "explicit_general": explicit,
        "named_language_contextual": named,
        "matched_explicit_terms": terms,
        "matched_language_groups": languages,
        "validation_status": "not_visually_validated",
    }


def fake_reuse_context(page_ids):
    n = len(page_ids)
    touched = 1 if n else 0
    return {
        "context_version": "LTMD_VERTICAL_REUSE_CONTEXT_0.1",
        "result_state": "exploratory_signal",
        "metrics": {
            "candidate_pages": n,
            "mapped_candidate_pages": n,
            "unmapped_candidate_pages": 0,
            "candidate_pages_with_exact_source_cross_object_reuse": 0,
            "candidate_pages_with_exact_source_cross_generation_reuse": 0,
            "candidate_pages_with_exact_text_cross_object_reuse": 0,
            "candidate_pages_with_exact_text_cross_generation_reuse": 0,
            "candidate_pages_with_similarity_signal": touched,
            "candidate_pages_with_near_exact_signal": 0,
            "candidate_pages_with_cross_generation_similarity_signal": touched,
            "candidate_pages_with_any_reuse_similarity_signal": touched,
            "candidate_pages_with_cross_generation_reuse_similarity_signal": touched,
            "candidate_pages_without_reuse_similarity_signal": n - touched,
            "internal_similarity_pairs": 0,
            "internal_near_exact_pairs": 0,
            "share_candidate_pages_with_any_reuse_similarity_signal": (touched / n if n else None),
        },
        "warnings": [
            "Reuse/similarity context is computational evidence.",
            "Vertical membership remains unchanged.",
        ],
    }


def reset_state():
    for key in list(api._state):
        api._state[key] = None


def configure(monkeypatch, tmp_path):
    ledger = tmp_path / "ledger.csv"
    rows = [
        candidate("p1", "B1", "1993", "5", "W3", "1", "1", "Náhuatl", "lenguas indigenas"),
        candidate("p2", "B1", "1993", "5", "W3", "0", "1", "Náhuatl;Otomí", ""),
        candidate("p3", "B2", "2014", "6", "W7", "1", "0", "", "lengua indigena"),
    ]
    write_csv(ledger, list(rows[0]), rows)
    generation = tmp_path / "generation.csv"
    write_csv(generation, ["generation", "total_pages"], [
        {"generation": "1993", "total_pages": "1000"},
        {"generation": "2014", "total_pages": "2000"},
    ])
    monkeypatch.setenv("LTMD_INDIGENOUS_LEDGER_PATH", str(ledger))
    monkeypatch.setenv("LTMD_GENERATION_SUMMARY_PATH", str(generation))
    monkeypatch.delenv("LTMD_UNIVERSAL_INDEX_PATH", raising=False)
    monkeypatch.delenv("LTMD_UNIVERSAL_INDEX_SHA256", raising=False)
    monkeypatch.delenv("LTMD_REUSE_SIMILARITY_PATH", raising=False)
    reset_state()
    return ledger


def make_corpus_index(path):
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE index_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID")
    connection.execute(
        "INSERT INTO index_meta VALUES(?,?)",
        ("builder_version", json.dumps("LTMD_U1_UNIVERSAL_INDEX_0.1")),
    )
    connection.execute(
        "CREATE TABLE pages(id INTEGER PRIMARY KEY,page_id TEXT,canonical_viewer_key TEXT,wave TEXT,catalog_generation INTEGER,grade_code INTEGER,search_text TEXT)"
    )
    connection.execute(
        "CREATE VIRTUAL TABLE pages_fts USING fts5(search_text,content='pages',content_rowid='id',tokenize='unicode61 remove_diacritics 2')"
    )
    connection.executemany(
        "INSERT INTO pages VALUES(?,?,?,?,?,?,?)",
        [
            (1, "cp1", "CB1", "W3", 1993, 5, "democracia y ciudadanía"),
            (2, "cp2", "CB2", "W7", 2014, 6, "democracia ciencia"),
            (3, "cp3", "CB3", "W7", 2014, 6, "naturaleza"),
        ],
    )
    connection.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
    connection.commit()
    connection.close()


def test_passenger_root_entry_point_exports_flask_application():
    import passenger_wsgi
    assert passenger_wsgi.application is api.app


def test_health_is_safe_and_configured(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    client = api.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["candidate_rows_loaded"] == 3
    assert payload["corpus_query_configured"] is False
    assert payload["reuse_context_configured"] is False
    assert payload["human_validation_complete"] is False
    rendered = repr(payload)
    assert str(tmp_path) not in rendered
    assert "ledger.csv" not in rendered


def test_meta_exposes_filter_vocabulary_not_private_rows(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    client = api.app.test_client()
    response = client.get("/v1/meta")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["filters"]["generation"] == ["1993", "2014"]
    assert "Náhuatl" in payload["filters"]["language_group"]
    assert payload["candidate_rows"] == 3
    assert payload["corpus_query_configured"] is False
    assert payload["corpus_index_sha256"] is None
    assert payload["reuse_context_configured"] is False
    assert "page_id" not in repr(payload)


def test_corpus_query_endpoint_uses_universal_index_and_schema(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    index = tmp_path / "corpus.sqlite"
    make_corpus_index(index)
    expected_sha = api.sha256_file(index)
    monkeypatch.setenv("LTMD_UNIVERSAL_INDEX_PATH", str(index))
    monkeypatch.setenv("LTMD_UNIVERSAL_INDEX_SHA256", expected_sha)
    reset_state()

    client = api.app.test_client()
    response = client.get(
        "/v1/corpus/query",
        query_string=[("q", "democracia"), ("group_by", "generation")],
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["metrics"]["candidate_pages"] == 2
    assert payload["metrics"]["candidate_books"] == 2
    assert payload["metrics"]["corpus_pages_in_scope"] == 3
    assert payload["metrics"]["corpus_books_in_scope"] == 3
    assert payload["result_state"] == "exploratory_signal"
    assert payload["provenance"]["index_sha256"] == expected_sha
    by_generation = {item["value"]: item["metrics"]["candidate_pages"] for item in payload["breakdown"]}
    assert by_generation == {"1993": 1, "2014": 1}

    rendered = repr(payload)
    for forbidden in ("cp1", "cp2", "page_id", "search_text", "source_asset_url", "ocr_sha256"):
        assert forbidden not in rendered

    schema = json.loads(
        (Path(__file__).parents[1] / "schemas" / "ltmd_u1_corpus_query_response.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(payload)


def test_corpus_index_without_reuse_is_valid(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    index = tmp_path / "corpus.sqlite"
    make_corpus_index(index)
    monkeypatch.setenv("LTMD_UNIVERSAL_INDEX_PATH", str(index))
    reset_state()
    client = api.app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["corpus_query_configured"] is True
    assert payload["reuse_context_configured"] is False


def test_corpus_query_invalid_input_is_400(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    index = tmp_path / "corpus.sqlite"
    make_corpus_index(index)
    monkeypatch.setenv("LTMD_UNIVERSAL_INDEX_PATH", str(index))
    reset_state()
    client = api.app.test_client()
    assert client.get("/v1/corpus/query").status_code == 400
    assert client.get("/v1/corpus/query?q=democracia&group_by=page_id").status_code == 400


def test_query_endpoint_uses_exact_unique_counts(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    client = api.app.test_client()
    response = client.get(
        "/v1/indigenous/query",
        query_string=[
            ("q", "náhuatl 1993"),
            ("generation", "1993"),
            ("language_group", "Náhuatl"),
            ("group_by", "generation"),
        ],
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["metrics"]["candidate_pages"] == 2
    assert payload["metrics"]["candidate_books"] == 1
    assert payload["metrics"]["pages_per_1000"] == 2.0
    assert payload["breakdown"][0]["value"] == "1993"
    assert payload["result_state"] == "exploratory_signal"
    assert payload["provenance"]["query_engine_version"] == "LTMD_ANALYTICS_QUERY_ENGINE_0.2"
    assert payload["provenance"]["human_validation_complete"] is False
    assert "reuse_context" not in payload
    assert "p1" not in repr(payload)
    assert "p2" not in repr(payload)


def test_query_endpoint_adds_scoped_reuse_context_when_configured(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    calls = []

    def resolver_factory():
        def resolver(page_ids):
            calls.append(tuple(page_ids))
            return fake_reuse_context(page_ids)
        return resolver

    monkeypatch.setattr(api, "_reuse_context_resolver", resolver_factory)
    client = api.app.test_client()
    response = client.get(
        "/v1/indigenous/query",
        query_string=[("q", "all candidate pages"), ("group_by", "generation")],
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["metrics"]["candidate_pages"] == 3
    assert payload["reuse_context"]["metrics"]["candidate_pages"] == 3
    assert all("reuse_context" in item for item in payload["breakdown"])
    by_generation = {item["value"]: item for item in payload["breakdown"]}
    assert by_generation["1993"]["reuse_context"]["metrics"]["candidate_pages"] == 2
    assert by_generation["2014"]["reuse_context"]["metrics"]["candidate_pages"] == 1
    assert calls[0] == ("p1", "p2", "p3")
    assert set(calls[1:]) == {("p1", "p2"), ("p3",)}
    rendered = repr(payload)
    assert "p1" not in rendered
    assert "p2" not in rendered
    assert "p3" not in rendered

    schema_path = Path(__file__).parents[1] / "schemas" / "ltmd_analytics_query_response.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(payload)


def test_reuse_without_index_degrades_service(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    monkeypatch.setenv("LTMD_REUSE_SIMILARITY_PATH", str(tmp_path / "reuse.sqlite"))
    client = api.app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    payload = response.get_json()
    assert payload["status"] == "degraded"
    assert payload["corpus_query_configured"] is False
    assert payload["reuse_context_configured"] is True
    assert str(tmp_path) not in repr(payload)


def test_invalid_group_by_is_rejected(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    client = api.app.test_client()
    response = client.get("/v1/indigenous/query?group_by=page_id")
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid group_by"


def test_service_is_read_only(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    client = api.app.test_client()
    response = client.post("/v1/indigenous/query")
    assert response.status_code == 405
    assert "read-only" in response.get_json()["error"]
    assert client.post("/v1/corpus/query").status_code == 405


def test_unconfigured_health_does_not_leak_path(monkeypatch):
    monkeypatch.delenv("LTMD_INDIGENOUS_LEDGER_PATH", raising=False)
    monkeypatch.delenv("LTMD_GENERATION_SUMMARY_PATH", raising=False)
    monkeypatch.delenv("LTMD_UNIVERSAL_INDEX_PATH", raising=False)
    monkeypatch.delenv("LTMD_UNIVERSAL_INDEX_SHA256", raising=False)
    monkeypatch.delenv("LTMD_REUSE_SIMILARITY_PATH", raising=False)
    reset_state()
    client = api.app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    payload = response.get_json()
    assert payload["status"] == "degraded"
    assert payload["private_ledger_configured"] is False
    assert "path" not in repr(payload).lower()
