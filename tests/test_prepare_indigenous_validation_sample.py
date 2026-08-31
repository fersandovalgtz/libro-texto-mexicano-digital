import csv
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "prepare_indigenous_validation_sample.py"
SPEC = importlib.util.spec_from_file_location("prepare_indigenous_validation_sample", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_ledger(path: Path, rows: list[dict]) -> None:
    fieldnames = sorted(mod.REQUIRED_FIELDS)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate(page_id: str, generation: str, explicit: str = "1") -> dict:
    return {
        "page_id": page_id,
        "canonical_viewer_key": f"K-{generation}",
        "generation": generation,
        "grade_code": "P5",
        "page_index": "1",
        "viewer_page": "2",
        "source_asset_url": f"https://example.invalid/{page_id}.jpg",
        "source_sha256": f"source-{page_id}",
        "ocr_sha256": f"ocr-{page_id}",
        "explicit_general": explicit,
        "matched_explicit_terms": "lenguas indigenas",
        "matched_language_groups": "",
        "validation_status": "not_visually_validated",
    }


def test_read_candidates_filters_to_explicit(tmp_path):
    ledger = tmp_path / "candidate.csv"
    make_ledger(ledger, [candidate("p1", "1993", "1"), candidate("p2", "1993", "0")])
    rows = mod.read_candidates(ledger)
    assert [row["page_id"] for row in rows] == ["p1"]


def test_double_code_selection_is_deterministic_and_stratified():
    rows = [candidate(f"a{i}", "1960") for i in range(2)]
    rows += [candidate(f"b{i}", "1993") for i in range(20)]
    first = mod.select_double_code(rows, seed="fixed", rate=0.10, minimum=2)
    second = mod.select_double_code(list(reversed(rows)), seed="fixed", rate=0.10, minimum=2)
    assert first == second
    assert len([page_id for page_id in first if page_id.startswith("a")]) == 2
    assert len([page_id for page_id in first if page_id.startswith("b")]) == 2


def test_build_queue_emits_no_text_fields():
    rows = [candidate("p1", "2014")]
    queue = mod.build_queue(rows, {"p1"})
    assert queue[0]["validation_status"] == "pending_visual_validation"
    assert queue[0]["double_code_required"] == "1"
    assert "search_text" not in queue[0]
    assert "ocr_text" not in queue[0]
    assert "snippet" not in queue[0]


def test_run_checks_expected_cardinality(tmp_path):
    ledger = tmp_path / "candidate.csv"
    make_ledger(ledger, [candidate("p1", "2014")])
    try:
        mod.run(
            ledger,
            tmp_path / "queue.csv",
            tmp_path / "manifest.json",
            expected_explicit=457,
            double_code_rate=0.10,
            double_code_min_per_generation=2,
            seed="fixed",
        )
    except RuntimeError as exc:
        assert "explicit cardinality mismatch" in str(exc)
    else:
        raise AssertionError("expected cardinality mismatch")


def test_conflicting_duplicate_page_id_is_rejected(tmp_path):
    ledger = tmp_path / "candidate.csv"
    first = candidate("dup", "1993")
    second = candidate("dup", "1993")
    second["source_sha256"] = "different"
    make_ledger(ledger, [first, second])
    try:
        mod.read_candidates(ledger)
    except RuntimeError as exc:
        assert "conflicting duplicate page_id" in str(exc)
    else:
        raise AssertionError("expected duplicate conflict")
