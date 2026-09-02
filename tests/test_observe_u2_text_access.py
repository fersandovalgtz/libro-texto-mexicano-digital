import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "observe_u2_text_access.py"
spec = importlib.util.spec_from_file_location("observe_u2_text_access", MODULE_PATH)
observer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(observer)


def test_parser_versions_are_pinned_to_experimental_observation():
    assert observer.REQUIRED_VERSIONS == {
        "pypdf": "6.16.2",
        "PyMuPDF": "1.28.2",
        "pikepdf": "10.12.0",
        "cryptography": "50.0.1",
    }


def test_consensus_classifies_only_the_observed_password_required_state():
    state = observer.classify_signals(
        {"encrypted": True, "blank_password_result": "NOT_DECRYPTED", "error_type": "FileNotDecryptedError"},
        {"needs_password": True, "blank_password_result": 0, "error_type": "ValueError"},
        {"blank_password_open": False, "error_type": "PasswordError"},
    )
    assert state == "blocked_by_password_required_encryption"


def test_non_consensus_remains_indeterminate_instead_of_promoting_text_or_ocr_state():
    state = observer.classify_signals(
        {"encrypted": True, "blank_password_result": "NOT_DECRYPTED", "error_type": "FileNotDecryptedError"},
        {"needs_password": True, "blank_password_result": 1, "error_type": None},
        {"blank_password_open": False, "error_type": "PasswordError"},
    )
    assert state == "indeterminate_parser_access_state"


def test_output_contract_contains_no_source_or_extracted_text_field():
    forbidden = {"pdf", "pdf_bytes", "source_bytes", "text", "extracted_text", "page_text"}
    assert forbidden.isdisjoint(set(observer.OUTPUT_FIELDS))
    assert "source_pdf_persisted" in observer.OUTPUT_FIELDS
    assert "extracted_text_persisted" in observer.OUTPUT_FIELDS
