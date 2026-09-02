import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_u2_text_access_observation.py"
spec = importlib.util.spec_from_file_location("validate_u2_text_access_observation", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)

SOURCE = ROOT / "data" / "catalog" / "ltmd_u2_text_access_observation_2026_09_02.csv"


def rows():
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_canonical_text_access_layer_validates_cleanly():
    assert validator.validate(SOURCE) == []


def test_all_39_objects_are_blocked_without_text_state_promotion():
    records = rows()
    assert len(records) == 39
    assert len({r["source_object_id"] for r in records}) == 39
    assert all(r["text_access_observation_state"] == "blocked_by_password_required_encryption" for r in records)
    assert all(r["embedded_text_sample_state"] == "not_assessed_due_to_access_block" for r in records)
    assert all(r["ocr_available_state"] == "not_assessed" for r in records)
    assert all(r["text_verified_state"] == "not_assessed" for r in records)


def test_parser_consensus_and_non_persistence_are_materialized_for_every_object():
    for record in rows():
        assert record["pypdf_encrypted"].lower() == "true"
        assert record["pypdf_blank_password_result"] == "NOT_DECRYPTED"
        assert record["pypdf_error_type"] == "FileNotDecryptedError"
        assert record["pymupdf_needs_password"].lower() == "true"
        assert record["pymupdf_blank_password_result"] == "0"
        assert record["pymupdf_error_type"] == "ValueError"
        assert record["pikepdf_blank_password_open"].lower() == "false"
        assert record["pikepdf_error_type"] == "PasswordError"
        assert record["source_pdf_persisted"].lower() == "false"
        assert record["extracted_text_persisted"].lower() == "false"
