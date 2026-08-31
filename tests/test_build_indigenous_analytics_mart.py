import csv
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "build_indigenous_analytics_mart.py"
SPEC = importlib.util.spec_from_file_location("build_indigenous_analytics_mart", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate(page_id: str, book: str, generation: str, grade: str, wave: str,
              explicit: str, named: str, terms: str = "", languages: str = "") -> dict:
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


def test_aggregate_counts_books_and_multivalues():
    rows = [
        candidate("p1", "B1", "1993", "5", "W3", "1", "1", "lenguas indigenas", "Náhuatl;Otomí"),
        candidate("p2", "B1", "1993", "5", "W3", "0", "1", "", "Náhuatl"),
        candidate("p3", "B2", "2014", "6", "W7", "1", "0", "derechos linguisticos", ""),
    ]
    result = mod.aggregate(rows, {"1993": 1000, "2014": 2000})
    generation = {row["generation"]: row for row in result["generation"]}
    assert generation["1993"]["candidate_pages"] == 2
    assert generation["1993"]["candidate_books"] == 1
    assert generation["1993"]["candidate_pages_per_1000_corpus_pages"] == "2.0000"
    nahuatl = [row for row in result["language"] if row["language_group"] == "Náhuatl"]
    assert nahuatl[0]["candidate_pages"] == 2
    assert nahuatl[0]["candidate_books"] == 1
    assert all(row["epistemic_state"] == "computational_candidate" for row in result["language"])


def test_duplicate_page_id_rejected(tmp_path):
    path = tmp_path / "ledger.csv"
    rows = [
        candidate("dup", "B1", "1993", "5", "W3", "1", "0"),
        candidate("dup", "B2", "2014", "6", "W7", "1", "0"),
    ]
    write_csv(path, list(rows[0]), rows)
    try:
        mod.read_ledger(path)
    except RuntimeError as exc:
        assert "duplicate page_id" in str(exc)
    else:
        raise AssertionError("expected duplicate rejection")


def test_run_emits_only_public_safe_aggregates(tmp_path):
    ledger = tmp_path / "ledger.csv"
    rows = [
        candidate("p1", "B1", "1960", "4", "W3", "1", "1", "lengua indigena", "Náhuatl"),
        candidate("p2", "B2", "2014", "6", "W7", "0", "1", "", "Tarahumara / rarámuri"),
    ]
    write_csv(ledger, list(rows[0]), rows)
    out = tmp_path / "out"
    manifest = mod.run(ledger, out)

    assert manifest["scientific_state"]["semantic_ready_promotions"] == 0
    assert manifest["privacy"]["page_ids_emitted"] is False

    for csv_path in out.glob("*.csv"):
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            fields = set(csv.DictReader(handle).fieldnames or [])
        assert not (fields & mod.FORBIDDEN_PUBLIC_FIELDS)

    saved = json.loads((out / "ltmd_analytics_indigenous_manifest_0_1.json").read_text(encoding="utf-8"))
    assert saved["scientific_state"]["human_validation_required_for_semantic_ready"] is True
    assert saved["scientific_state"]["allowed_output_states"] == [
        "computational_candidate", "exploratory_signal"
    ]


def test_generation_summary_denominator_validation(tmp_path):
    path = tmp_path / "generation.csv"
    write_csv(path, ["generation", "total_pages"], [
        {"generation": "1993", "total_pages": "100"},
        {"generation": "1993", "total_pages": "101"},
    ])
    try:
        mod.read_generation_denominators(path)
    except RuntimeError as exc:
        assert "conflicting total_pages" in str(exc)
    else:
        raise AssertionError("expected denominator conflict")
