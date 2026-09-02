import csv
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "validate_u2_asset_resolution.py"
SPEC = importlib.util.spec_from_file_location("validate_u2_asset_resolution", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

SOURCE_OBJECTS = ROOT / "data" / "catalog" / "ltmd_u2_source_objects_2026_2027.csv"
OBSERVATIONS = ROOT / "data" / "catalog" / "ltmd_u2_asset_resolution_2026_09_02.csv"
SCHEMA = ROOT / "schemas" / "ltmd_u2_asset_resolution.schema.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_repository_asset_resolution_covers_exactly_39_source_objects():
    rows = mod.validate_asset_resolution(SOURCE_OBJECTS, OBSERVATIONS)
    assert len(rows) == 39
    assert {row["asset_resolution_state"] for row in rows} == {"resolved_pdf"}
    assert {row["http_status"] for row in rows} == {"206"}
    assert {row["content_type"] for row in rows} == {"application/pdf"}
    assert {row["accept_ranges"] for row in rows} == {"bytes"}
    assert {row["pdf_signature"] for row in rows} == {"true"}
    assert {row["source_admission_state"] for row in rows} == {"not_assessed"}
    assert {row["page_count_observation"] for row in rows} == {"not_observed"}


def test_repository_rows_conform_to_asset_resolution_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for row in read_rows(OBSERVATIONS):
        validator.validate(row)


def test_asset_url_must_follow_current_reader_route(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["asset_url"] = rows[0]["asset_url"].replace("/pdf-reader/assets/primaria/", "/")
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="asset_url does not match current-reader route"):
        mod.validate_asset_resolution(SOURCE_OBJECTS, bad)


def test_resolved_pdf_requires_pdf_transport_evidence(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["content_type"] = "text/html"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="requires application/pdf"):
        mod.validate_asset_resolution(SOURCE_OBJECTS, bad)


def test_asset_evidence_cannot_promote_source_admission(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["source_admission_state"] = "admitted"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="cannot promote source_admission_state"):
        mod.validate_asset_resolution(SOURCE_OBJECTS, bad)


def test_asset_evidence_cannot_promote_page_count(tmp_path):
    rows = read_rows(OBSERVATIONS)
    rows[0]["page_count_observation"] = "256"
    bad = tmp_path / "bad.csv"
    write_rows(bad, rows)

    with pytest.raises(RuntimeError, match="cannot assert page_count_observation"):
        mod.validate_asset_resolution(SOURCE_OBJECTS, bad)
