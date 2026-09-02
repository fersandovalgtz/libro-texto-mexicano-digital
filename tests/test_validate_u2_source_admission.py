import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_u2_source_admission.py"
spec = importlib.util.spec_from_file_location("validate_u2_source_admission", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)

SOURCE = ROOT / "data" / "catalog" / "ltmd_u2_source_admission_2026_09_02.csv"


def rows():
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_canonical_source_admission_layer_validates_cleanly():
    assert validator.validate(SOURCE) == []


def test_source_admission_is_complete_but_does_not_promote_text_states():
    records = rows()
    assert len(records) == 39
    assert all(r["source_admission_state"] == "admitted_full_body_verified" for r in records)
    assert all(r["source_pdf_persisted"].lower() == "false" for r in records)
    assert all(r["ocr_available_state"] == "not_assessed" for r in records)
    assert all(r["text_verified_state"] == "not_assessed" for r in records)


def test_hashes_and_transport_invariants_are_materialized_for_every_object():
    records = rows()
    assert len({r["source_object_id"] for r in records}) == 39
    assert len({r["sha256"] for r in records}) == 39
    for record in records:
        assert len(record["sha256"]) == 64
        int(record["sha256"], 16)
        assert record["bytes_received"] == record["expected_bytes"]
        assert record["size_matches"].lower() == "true"
        assert record["http_status"] == "200"
        assert record["content_type"] == "application/pdf"
        assert record["pdf_signature"].lower() == "true"
        assert record["eof_marker"].lower() == "true"
        assert record["startxref_in_tail"].lower() == "true"
