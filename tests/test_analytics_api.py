import csv
import json
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
    monkeypatch.delenv("LTMD_REUSE_SIMILARITY_PATH", raising=False)
    reset_state()
    return ledger


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
    assert payload["reuse_context_configured"] is False
    assert "page_id" not in repr(payload)


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
        query_string=[
            ("q", "all named languages"),
            ("language_group", "Náhuatl"),
            ("group_by", "generation"),
        ],
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["metrics"]["candidate_pages"] == 2
    assert payload["reuse_context"]["metrics"]["candidate_pages"] == 2
    assert all("reuse_context" in item for item in payload["breakdown"])
    assert {item["reuse_context"]["metrics"]["candidate_pages"] for item in payload["breakdown"]} == {1}
    assert calls[0] == ("p1", "p2")
    assert set(calls[1:]) == {("p1",), ("p2",)}
    rendered = repr(payload)
    assert "p1" not in rendered
    assert "p2" not in rendered

    schema_path = Path(__file__).parents[1] / "schemas" / "ltmd_analytics_query_response.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(payload)


def test_partial_reuse_configuration_degrades_service(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    index = tmp_path / "index.sqlite"
    index.write_bytes(b"placeholder")
    monkeypatch.setenv("LTMD_UNIVERSAL_INDEX_PATH", str(index))
    monkeypatch.delenv("LTMD_REUSE_SIMILARITY_PATH", raising=False)
    client = api.app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    payload = response.get_json()
    assert payload["status"] == "degraded"
    assert payload["reuse_context_configured"] is False
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


def test_unconfigured_health_does_not_leak_path(monkeypatch):
    monkeypatch.delenv("LTMD_INDIGENOUS_LEDGER_PATH", raising=False)
    monkeypatch.delenv("LTMD_GENERATION_SUMMARY_PATH", raising=False)
    monkeypatch.delenv("LTMD_UNIVERSAL_INDEX_PATH", raising=False)
    monkeypatch.delenv("LTMD_REUSE_SIMILARITY_PATH", raising=False)
    reset_state()
    client = api.app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    payload = response.get_json()
    assert payload["status"] == "degraded"
    assert payload["private_ledger_configured"] is False
    assert "path" not in repr(payload).lower()
