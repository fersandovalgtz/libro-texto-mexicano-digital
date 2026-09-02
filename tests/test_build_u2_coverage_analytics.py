import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "scripts" / "build_u2_coverage_analytics.py"
VALIDATE_PATH = ROOT / "scripts" / "validate_u2_coverage_analytics.py"

build_spec = importlib.util.spec_from_file_location("build_u2_coverage_analytics", BUILD_PATH)
builder = importlib.util.module_from_spec(build_spec)
assert build_spec.loader is not None
build_spec.loader.exec_module(builder)

validate_spec = importlib.util.spec_from_file_location("validate_u2_coverage_analytics", VALIDATE_PATH)
validator = importlib.util.module_from_spec(validate_spec)
assert validate_spec.loader is not None
validate_spec.loader.exec_module(validator)

SOURCE = ROOT / "data" / "analytics" / "ltmd_u2_source_coverage_0_1.csv"
ENTRY = ROOT / "data" / "analytics" / "ltmd_u2_catalog_entry_coverage_0_1.csv"
MANIFEST = ROOT / "data" / "analytics" / "ltmd_u2_coverage_analytics_manifest_0_1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_canonical_u2_coverage_layer_validates_cleanly():
    assert validator.validate() == []


def test_denominators_remain_42_catalog_entries_and_39_source_objects():
    source = read_csv(SOURCE)
    entry = read_csv(ENTRY)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert len(source) == 39
    assert len(entry) == 42
    assert manifest["denominators"] == {"catalog_entries": 42, "source_objects": 39}
    assert manifest["separation_guards"]["catalog_entry_is_not_source_object"] is True
    assert manifest["separation_guards"]["u2_denominators_are_separate_from_u1"] is True


def test_text_and_semantic_states_are_not_promoted_by_coverage_aggregation():
    for row in read_csv(SOURCE) + read_csv(ENTRY):
        assert row["text_access_observation_state"] == "blocked_by_password_required_encryption"
        assert row["embedded_text_sample_state"] == "not_assessed_due_to_access_block"
        assert row["ocr_available_state"] == "not_assessed"
        assert row["text_verified_state"] == "not_assessed"
        assert row["semantic_ready_state"] == "not_assessed"


def test_builder_reproduces_canonical_csv_bytes(tmp_path):
    source_rows, entry_rows, _ = builder.build()
    source_out = tmp_path / "source.csv"
    entry_out = tmp_path / "entry.csv"
    builder.write_csv(source_out, builder.SOURCE_FIELDS, source_rows)
    builder.write_csv(entry_out, builder.ENTRY_FIELDS, entry_rows)
    assert digest(source_out) == digest(SOURCE)
    assert digest(entry_out) == digest(ENTRY)


def test_manifest_hashes_match_materialized_csvs():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    materialization = manifest["materialization"]
    assert materialization["source_csv_sha256"] == digest(SOURCE)
    assert materialization["entry_csv_sha256"] == digest(ENTRY)
    assert manifest["source_object_metrics"]["total_observed_pages"] == 10392
