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


def fake_reuse_context(page_ids: list[str]) -> dict:
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
        "warnings": ["reuse context warning", "vertical membership unchanged"],
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


def test_reuse_context_is_scoped_to_filtered_rows_and_breakdown_groups():
    rows = [
        row("p1", "B1", "1993", "5", "W3", named="1", languages="Náhuatl"),
        row("p2", "B1", "1993", "5", "W3", named="1", languages="Náhuatl"),
        row("p3", "B2", "2014", "6", "W7", named="1", languages="Náhuatl"),
    ]
    calls = []

    def resolver(page_ids):
        calls.append(tuple(page_ids))
        return fake_reuse_context(page_ids)

    response = mod.query(
        rows,
        query_label="contextualized",
        filters={"language_group": ["Náhuatl"]},
        denominators={"1993": 1000, "2014": 1000},
        group_by="generation",
        reuse_context_resolver=resolver,
    )
    assert response["reuse_context"]["metrics"]["candidate_pages"] == 3
    by_generation = {item["value"]: item for item in response["breakdown"]}
    assert by_generation["1993"]["reuse_context"]["metrics"]["candidate_pages"] == 2
    assert by_generation["2014"]["reuse_context"]["metrics"]["candidate_pages"] == 1
    assert calls[0] == ("p1", "p2", "p3")
    assert set(calls[1:]) == {("p1", "p2"), ("p3",)}


def test_response_never_contains_page_level_fields():
    rows = [row("secret-page", "B1", "1993", "5", "W3", "1", "1", "Náhuatl")]
    response = mod.query(rows, query_label="safe", filters={}, denominators={"1993": 1000})
    rendered = repr(response)
    assert "secret-page" not in rendered
    assert "page_id" not in rendered
    assert "source_asset_url" not in rendered
    assert "ocr_sha256" not in rendered


def test_reuse_context_candidate_count_mismatch_is_rejected():
    rows = [row("p1", "B1", "1993", "5", "W3")]

    def bad_resolver(_page_ids):
        context = fake_reuse_context([])
        return context

    try:
        mod.query(rows, query_label="bad-context", filters={}, reuse_context_resolver=bad_resolver)
    except RuntimeError as exc:
        assert "candidate count mismatch" in str(exc)
    else:
        raise AssertionError("expected reuse context mismatch rejection")


def test_invalid_group_by_is_rejected():
    try:
        mod.query([], query_label="bad", filters={}, group_by="page_id")
    except RuntimeError as exc:
        assert "group_by must be one of" in str(exc)
    else:
        raise AssertionError("expected invalid group_by rejection")
