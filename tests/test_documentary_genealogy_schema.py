import importlib.util
import json
import sqlite3
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "run_documentary_genealogy_benchmark.py"
SPEC = importlib.util.spec_from_file_location("genealogy_schema_target", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_minimal_index(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE index_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE pages(
          id INTEGER PRIMARY KEY,
          canonical_viewer_key TEXT NOT NULL,
          catalog_generation INTEGER,
          source_sha256 TEXT,
          search_text_sha256 TEXT,
          ocr_char_count INTEGER,
          ocr_word_count INTEGER
        );
        """
    )
    con.execute("INSERT INTO index_meta VALUES(?,?)", ("builder_version", json.dumps(mod.INDEX_VERSION)))
    con.execute("INSERT INTO index_meta VALUES(?,?)", ("unique_pages", json.dumps(4)))
    a, b, c = "a" * 64, "b" * 64, "c" * 64
    con.executemany(
        "INSERT INTO pages VALUES(?,?,?,?,?,?,?)",
        [
            (1, "o1", 1993, a, a, 400, 80),
            (2, "o2", 1993, b, b, 400, 80),
            (3, "o3", 2014, a, a, 400, 80),
            (4, "o4", 2014, c, c, 400, 80),
        ],
    )
    con.commit()
    con.close()


def test_output_matches_draft_2020_12_contract(tmp_path):
    index = tmp_path / "index.sqlite"
    make_minimal_index(index)
    result = mod.benchmark(index, bootstrap_reps=20, permutations=0, seed=1)
    schema = json.loads((ROOT / "schemas" / "ltmd_documentary_genealogy_benchmark_0_2.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(result)
    assert result["scientific_state"]["human_validation"] is False
    assert result["scientific_state"]["semantic_ready"] is False
    assert result["scientific_state"]["historical_truth_claimed"] is False
