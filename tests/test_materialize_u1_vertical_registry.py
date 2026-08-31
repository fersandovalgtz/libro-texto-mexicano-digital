import importlib.util
import json
import sqlite3
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "materialize_u1_vertical_registry.py"
SPEC = importlib.util.spec_from_file_location("materialize_u1_vertical_registry", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_index(path):
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE index_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID")
    connection.execute("INSERT INTO index_meta VALUES(?,?)", ("builder_version", json.dumps("LTMD_U1_UNIVERSAL_INDEX_0.1")))
    connection.execute("CREATE TABLE pages(id INTEGER PRIMARY KEY,page_id TEXT,canonical_viewer_key TEXT,wave TEXT,catalog_generation INTEGER,grade_code INTEGER,search_text TEXT)")
    connection.execute("CREATE VIRTUAL TABLE pages_fts USING fts5(search_text,content='pages',content_rowid='id',tokenize='unicode61 remove_diacritics 2')")
    rows = [
        (1, "p1", "B1", "W1", 1993, 5, "democracia y ciudadanía"),
        (2, "p2", "B2", "W2", 2014, 6, "democracia ciencia"),
        (3, "p3", "B3", "W2", 2014, 6, "naturaleza"),
    ]
    connection.executemany("INSERT INTO pages VALUES(?,?,?,?,?,?,?)", rows)
    connection.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
    connection.commit()
    connection.close()


def make_reuse(path):
    connection = sqlite3.connect(path)
    connection.executescript("""
        CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID;
        CREATE TABLE exact_source_groups(group_id INTEGER PRIMARY KEY,hash TEXT,page_count INTEGER,object_count INTEGER,generation_count INTEGER,cross_object INTEGER,cross_generation INTEGER);
        CREATE TABLE exact_source_members(group_id INTEGER,page_rowid INTEGER,object_id INTEGER,generation INTEGER,PRIMARY KEY(group_id,page_rowid)) WITHOUT ROWID;
        CREATE TABLE exact_text_groups(group_id INTEGER PRIMARY KEY,hash TEXT,page_count INTEGER,object_count INTEGER,generation_count INTEGER,grade_count INTEGER,wave_count INTEGER,cross_object INTEGER,cross_generation INTEGER);
        CREATE TABLE exact_text_members(group_id INTEGER,page_rowid INTEGER,object_id INTEGER,generation INTEGER,PRIMARY KEY(group_id,page_rowid)) WITHOUT ROWID;
        CREATE TABLE similarity_candidates(page_a INTEGER,page_b INTEGER,object_a INTEGER,object_b INTEGER,jaccard REAL,shared_shingles INTEGER,shingles_a INTEGER,shingles_b INTEGER,tier TEXT,PRIMARY KEY(page_a,page_b)) WITHOUT ROWID;
    """)
    connection.execute("INSERT INTO meta VALUES(?,?)", ("artifact_version", json.dumps("LTMD_U1_REUSE_SIMILARITY_0.1")))
    connection.execute("INSERT INTO exact_text_groups VALUES(1,'h',2,2,2,2,2,1,1)")
    connection.executemany("INSERT INTO exact_text_members VALUES(?,?,?,?)", [(1, 1, 1, 1993), (1, 2, 2, 2014)])
    connection.execute("INSERT INTO similarity_candidates VALUES(1,2,1,2,.9,50,60,60,'similarity_candidate')")
    connection.commit()
    connection.close()


def write_registry(path):
    registry = {
        "registry_version": "LTMD_U1_VERTICAL_REGISTRY_0.1",
        "result_state": "exploratory_signal",
        "frozen_before_materialization": True,
        "dimensions": ["generation", "grade_code", "wave"],
        "scientific_boundaries": ["synthetic fixture"],
        "verticals": [],
    }
    for index in range(8):
        registry["verticals"].append({
            "vertical_id": f"v{index}",
            "label_es": f"Vertical {index}",
            "status": "preregistered_exploratory",
            "union_expression": "democracia",
            "probes": [
                {"probe_id": "a", "label_es": "A", "fts5_expression": "democracia"},
                {"probe_id": "b", "label_es": "B", "fts5_expression": "ciencia"},
            ],
            "interpretation_boundary": "Límite interpretativo suficientemente largo para prueba sintética del contrato.",
        })
    path.write_text(json.dumps(registry), encoding="utf-8")


def test_materializer_fixture(tmp_path):
    index = tmp_path / "index.sqlite"
    reuse = tmp_path / "reuse.sqlite"
    registry = tmp_path / "registry.json"
    make_index(index)
    make_reuse(reuse)
    write_registry(registry)
    output = mod.materialize(registry, index, reuse)
    assert len(output["verticals"]) == 8
    vertical = output["verticals"][0]
    assert vertical["metrics"]["candidate_pages"] == 2
    assert vertical["metrics"]["candidate_books"] == 2
    assert vertical["reuse_context"]["metrics"]["candidate_pages_with_exact_text_cross_generation_reuse"] == 2
    assert vertical["reuse_context"]["metrics"]["candidate_pages_with_similarity_signal"] == 2
    by_generation = {item["value"]: item["metrics"]["candidate_pages"] for item in vertical["breakdowns"]["generation"]}
    assert by_generation == {"1993": 1, "2014": 1}
    assert output["privacy"]["page_identifiers_emitted"] is False


def test_public_materialization_record_schema_and_invariants():
    schema = json.loads((ROOT / "schemas" / "ltmd_u1_vertical_materialization.schema.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data" / "analytics" / "ltmd_u1_vertical_materialization_0_1.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(data)
    ids = [vertical["vertical_id"] for vertical in data["verticals"]]
    assert len(ids) == len(set(ids)) == 8
    assert data["corpus"] == {"pages": 86549, "canonical_objects": 492}
    assert data["provenance"]["human_validation_complete"] is False
    assert data["scientific_state"] == {"text_verified": False, "semantic_ready": False, "aliases_created": False}
    assert data["full_materialization_sha256"] == "e2faab966faced48327634c4acd40a867b76add29612538736b91db8d3afb0ad"
    assert data["full_materialization_bytes"] == 120354
    for vertical in data["verticals"]:
        assert vertical["breakdown_cardinality"] == {"generation": 11, "grade_code": 6, "wave": 11}
        assert vertical["reuse_context"]["candidate_pages_with_any_reuse_similarity_signal"] <= vertical["metrics"]["candidate_pages"]
