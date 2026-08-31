import csv

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
    assert payload["provenance"]["human_validation_complete"] is False
    assert "p1" not in repr(payload)
    assert "p2" not in repr(payload)


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
    reset_state()
    client = api.app.test_client()
    response = client.get("/health")
    assert response.status_code == 503
    payload = response.get_json()
    assert payload["status"] == "degraded"
    assert payload["private_ledger_configured"] is False
    assert "path" not in repr(payload).lower()
