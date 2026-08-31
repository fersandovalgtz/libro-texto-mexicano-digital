import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "query_indigenous_analytics.py"
SPEC = importlib.util.spec_from_file_location("query_indigenous_analytics", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def row(page_id: str, book: str, generation: str, grade: str, wave: str,
        explicit: str = "0", named: str = "0", languages: str = "", terms: str = "") -> dict:
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


def test_exact_unique_page_and_book_aggregation():
    rows = [
        row("p1", "B1", "1993", "5", "W3", "1", "1", "Náhuatl", "lenguas indigenas"),
        row("p2", "B1", "1993", "5", "W3", "0", "1", "Náhuatl;Otomí", ""),
        row("p3", "B2", "2014", "6", "W7", "1", "0", "", "lengua indigena"),
    ]
    response = mod.query(
        rows,
        query_label="náhuatl",
        filters={"language_group": ["Náhuatl"], "generation": ["1993"]},
        denominators={"1993": 1000, "2014": 2000},
        source_ledger_sha256="a" * 64,
    )
    assert response["metrics"]["candidate_pages"] == 2
    assert response["metrics"]["candidate_books"] == 1
    assert response["metrics"]["explicit_general_pages"] == 1
    assert response["metrics"]["named_language_contextual_pages"] == 2
    assert response["metrics"]["pages_per_1000"] == 2.0
    assert response["result_state"] == "exploratory_signal"
    assert response["provenance"]["human_validation_complete"] is False


def test_grade_or_wave_filter_refuses_invalid_rate_denominator():
    rows = [row("p1", "B1", "2014", "6", "W7", "1", "0")]
    response = mod.query(
        rows,
        query_label="filtered",
        filters={"generation": ["2014"], "grade_code": ["6"]},
        denominators={"2014": 1000},
    )
    assert response["metrics"]["candidate_pages"] == 1
    assert response["metrics"]["pages_per_1000"] is None
    assert any("only generation-level corpus denominators" in warning for warning in response["warnings"])


def test_breakdown_uses_unique_books_inside_each_group():
    rows = [
        row("p1", "B1", "1993", "5", "W3", named="1", languages="Náhuatl;Otomí"),
        row("p2", "B1", "1993", "5", "W3", named="1", languages="Náhuatl"),
        row("p3", "B2", "2014", "6", "W7", named="1", languages="Náhuatl"),
    ]
    response = mod.query(
        rows,
        query_label="languages",
        filters={},
        denominators={"1993": 1000, "2014": 1000},
        group_by="generation",
    )
    assert response["group_by"] == "generation"
    by_generation = {item["value"]: item for item in response["breakdown"]}
    assert by_generation["1993"]["metrics"]["candidate_pages"] == 2
    assert by_generation["1993"]["metrics"]["candidate_books"] == 1
    assert by_generation["2014"]["metrics"]["candidate_books"] == 1


def test_response_never_contains_page_level_fields():
    rows = [row("secret-page", "B1", "1993", "5", "W3", "1", "1", "Náhuatl")]
    response = mod.query(rows, query_label="safe", filters={}, denominators={"1993": 1000})
    rendered = repr(response)
    assert "secret-page" not in rendered
    assert "page_id" not in rendered
    assert "source_asset_url" not in rendered
    assert "ocr_sha256" not in rendered


def test_invalid_group_by_is_rejected():
    try:
        mod.query([], query_label="bad", filters={}, group_by="page_id")
    except RuntimeError as exc:
        assert "group_by must be one of" in str(exc)
    else:
        raise AssertionError("expected invalid group_by rejection")
