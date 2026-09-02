import csv
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "validate_u2_reader_shell_resolution.py"
SPEC = importlib.util.spec_from_file_location("validate_u2_reader_shell_resolution", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

SOURCE_OBJECTS = ROOT / "data" / "catalog" / "ltmd_u2_source_objects_2026_2027.csv"
OBSERVATIONS = ROOT / "data" / "catalog" / "ltmd_u2_reader_shell_resolution_2026_09_02.csv"
SCHEMA = ROOT / "schemas" / "ltmd_u2_reader_shell_resolution.schema.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_repository_resolution_covers_exactly_39_source_objects():
    rows = mod.validate_resolution(SOURCE_OBJECTS, OBSERVATIONS)
    assert len(rows) == 39
    assert {row["reader_shell_state"] for row in rows} == {"resolved"}
    assert {row["transport_observation"] for row in rows} == {"fetch_succeeded"}
    assert {row["asset_resolution_state"] for row in rows} == {"not_observed"}
    assert {row["page_count_observation"] for row in rows} == {"not_observed"}
    assert {row["source_admission_state"] for row in rows} == {"not_assessed"}


def test_repository_rows_conform_to_reader_shell_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for row in read_rows(OBSERVATIONS):
        validator.validate(row)


def test_canonical_viewer_url_mismatch_is_rejected(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["viewer_url"] = rows[0]["viewer_url"].replace("P0CMA", "P0SHA")
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="viewer_url does not match canonical source object"):
        mod.validate_resolution(SOURCE_OBJECTS, bad)


def test_resolved_shell_requires_successful_fetch(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["transport_observation"] = "fetch_failed"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="resolved reader shell requires fetch_succeeded"):
        mod.validate_resolution(SOURCE_OBJECTS, bad)


def test_page_count_cannot_be_promoted_without_asset_resolution(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["page_count_observation"] = "256"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="page count cannot be asserted"):
        mod.validate_resolution(SOURCE_OBJECTS, bad)


def test_reader_shell_evidence_cannot_promote_source_admission(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["source_admission_state"] = "admitted"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="cannot promote source_admission_state"):
        mod.validate_resolution(SOURCE_OBJECTS, bad)
