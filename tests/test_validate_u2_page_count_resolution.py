import csv
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "validate_u2_page_count_resolution.py"
SPEC = importlib.util.spec_from_file_location("validate_u2_page_count_resolution", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

SOURCE_OBJECTS = ROOT / "data" / "catalog" / "ltmd_u2_source_objects_2026_2027.csv"
ASSET_RESOLUTION = ROOT / "data" / "catalog" / "ltmd_u2_asset_resolution_2026_09_02.csv"
PAGE_COUNTS = ROOT / "data" / "catalog" / "ltmd_u2_page_count_resolution_2026_09_02.csv"
SCHEMA = ROOT / "schemas" / "ltmd_u2_page_count_resolution.schema.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_repository_page_counts_cover_all_39_objects_and_fixed_total():
    rows = mod.validate_resolution(SOURCE_OBJECTS, ASSET_RESOLUTION, PAGE_COUNTS)
    assert len(rows) == 39
    counts = [int(row["page_count"]) for row in rows]
    assert sum(counts) == 10392
    assert min(counts) == 91
    assert max(counts) == 371
    assert {row["page_count_state"] for row in rows} == {"observed"}
    assert {row["xref_kind"] for row in rows} == {"classic"}
    assert {row["source_admission_state"] for row in rows} == {"not_assessed"}
    assert {row["text_verification_state"] for row in rows} == {"not_assessed"}


def test_reference_counts_match_known_cross_validation_points():
    rows = {row["viewer_key"]: row for row in read_rows(PAGE_COUNTS)}
    assert rows["P0CMA"]["page_count"] == "191"
    assert rows["P3MLA"]["page_count"] == "259"
    assert rows["P4PEA"]["page_count"] == "363"
    assert rows["P5LPM"]["page_count"] == "99"


def test_rows_conform_to_page_count_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for row in read_rows(PAGE_COUNTS):
        validator.validate(row)


def test_asset_identity_mismatch_is_rejected(tmp_path):
    rows = read_rows(PAGE_COUNTS)
    rows[0]["asset_url"] = rows[0]["asset_url"].replace("P0CMA.pdf", "P0SHA.pdf")
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)
    with pytest.raises(RuntimeError, match="asset_url mismatch"):
        mod.validate_resolution(SOURCE_OBJECTS, ASSET_RESOLUTION, bad)


def test_remote_length_mismatch_is_rejected(tmp_path):
    rows = read_rows(PAGE_COUNTS)
    rows[0]["remote_total_bytes"] = "1"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)
    with pytest.raises(RuntimeError, match="remote_total_bytes changed"):
        mod.validate_resolution(SOURCE_OBJECTS, ASSET_RESOLUTION, bad)


def test_page_count_evidence_cannot_promote_source_admission(tmp_path):
    rows = read_rows(PAGE_COUNTS)
    rows[0]["source_admission_state"] = "admitted"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)
    with pytest.raises(RuntimeError, match="cannot promote source admission"):
        mod.validate_resolution(SOURCE_OBJECTS, ASSET_RESOLUTION, bad)


def test_page_count_evidence_cannot_promote_text_verification(tmp_path):
    rows = read_rows(PAGE_COUNTS)
    rows[0]["text_verification_state"] = "verified"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)
    with pytest.raises(RuntimeError, match="cannot promote text verification"):
        mod.validate_resolution(SOURCE_OBJECTS, ASSET_RESOLUTION, bad)


def test_corrupted_page_total_is_rejected(tmp_path):
    rows = read_rows(PAGE_COUNTS)
    rows[0]["page_count"] = str(int(rows[0]["page_count"]) + 1)
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)
    with pytest.raises(RuntimeError, match="structural page total mismatch"):
        mod.validate_resolution(SOURCE_OBJECTS, ASSET_RESOLUTION, bad)
