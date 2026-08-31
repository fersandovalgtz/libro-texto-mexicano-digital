import json
import sqlite3
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
REGISTRY = ROOT / "data" / "analytics" / "ltmd_u1_vertical_registry_0_1.json"
SCHEMA = ROOT / "schemas" / "ltmd_u1_vertical_registry.schema.json"


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_registry_validates_against_schema():
    registry = load_registry()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(registry)


def test_registry_ids_are_unique_and_scientific_state_is_frozen():
    registry = load_registry()
    assert registry["frozen_before_materialization"] is True
    assert registry["result_state"] == "exploratory_signal"
    vertical_ids = [item["vertical_id"] for item in registry["verticals"]]
    assert len(vertical_ids) == len(set(vertical_ids))
    for vertical in registry["verticals"]:
        probe_ids = [probe["probe_id"] for probe in vertical["probes"]]
        assert len(probe_ids) == len(set(probe_ids))
        assert vertical["status"] == "preregistered_exploratory"
        rendered = json.dumps(vertical, ensure_ascii=False).lower()
        assert "semantic_ready" not in rendered
        assert "page_id" not in rendered
        assert "object_id" not in rendered


def test_all_preregistered_fts5_expressions_parse_without_corpus_data():
    registry = load_registry()
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE VIRTUAL TABLE docs USING fts5(search_text, tokenize='unicode61 remove_diacritics 2')"
    )
    try:
        for vertical in registry["verticals"]:
            expressions = [vertical["union_expression"]] + [
                probe["fts5_expression"] for probe in vertical["probes"]
            ]
            for expression in expressions:
                connection.execute("SELECT count(*) FROM docs WHERE docs MATCH ?", (expression,)).fetchone()
    finally:
        connection.close()


def test_registry_dimensions_match_corpus_query_engine_contract():
    registry = load_registry()
    assert registry["dimensions"] == ["generation", "grade_code", "wave"]
