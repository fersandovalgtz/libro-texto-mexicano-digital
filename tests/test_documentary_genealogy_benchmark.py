import importlib.util
import json
import sqlite3
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "run_documentary_genealogy_benchmark.py"
SPEC = importlib.util.spec_from_file_location("genealogy_benchmark", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def h(char: str) -> str:
    return char * 64


def make_index(path: Path) -> None:
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
    con.execute("INSERT INTO index_meta VALUES(?,?)", ("unique_pages", json.dumps(9)))
    rows = [
        (1, "obj_a", 1993, h("a"), h("a"), 400, 80),
        (2, "obj_a", 1993, h("b"), h("b"), 350, 70),
        (3, "obj_b", 1993, h("c"), h("c"), 50, 8),
        (4, "obj_a", 2014, h("a"), h("a"), 410, 82),
        (5, "obj_c", 2014, h("d"), h("d"), 380, 75),
        (6, "obj_b", 2014, h("c"), h("c"), 60, 9),
        (7, "obj_a", 2018, h("a"), h("a"), 420, 85),
        (8, "obj_d", 2018, h("e"), h("e"), 390, 78),
        (9, "obj_e", 2018, h("f"), h("f"), 370, 74),
    ]
    con.executemany("INSERT INTO pages VALUES(?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()


def make_reuse(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE similarity_candidates(
          page_a INTEGER NOT NULL,
          page_b INTEGER NOT NULL,
          jaccard REAL NOT NULL,
          tier TEXT NOT NULL,
          PRIMARY KEY(page_a,page_b)
        );
        """
    )
    con.execute("INSERT INTO meta VALUES(?,?)", ("artifact_version", json.dumps(mod.REUSE_VERSION)))
    con.executemany(
        "INSERT INTO similarity_candidates VALUES(?,?,?,?)",
        [
            (2, 5, 0.97, "near_exact_candidate"),
            (5, 8, 0.88, "similarity_candidate"),
            (2, 8, 0.86, "similarity_candidate"),  # non-adjacent generation pair, excluded from adjacent sensitivity
        ],
    )
    con.commit()
    con.close()


def test_exact_transition_metrics_and_privacy(tmp_path):
    index = tmp_path / "index.sqlite"
    reuse = tmp_path / "reuse.sqlite"
    make_index(index)
    make_reuse(reuse)

    result = mod.benchmark(index, reuse_path=reuse, bootstrap_reps=100, permutations=100, seed=7)
    assert result["status"] == "PASS"
    assert result["corpus"]["pages"] == 9
    assert result["corpus"]["generations"] == [1993, 2014, 2018]

    source = result["channels"]["source"]["transitions"]
    first = source[0]["distinct_representations"]
    assert first["previous"] == 3
    assert first["current"] == 3
    assert first["shared"] == 2
    assert first["previous_only"] == 1
    assert first["current_only"] == 1
    assert first["persistence_rate"] == round(2 / 3, 8)
    assert first["novelty_rate"] == round(1 / 3, 8)
    assert first["turnover_rate"] == 0.5

    second = source[1]["distinct_representations"]
    assert second["shared"] == 1
    assert second["persistence_rate"] == round(1 / 3, 8)
    assert second["novelty_rate"] == round(2 / 3, 8)
    assert second["turnover_rate"] == 0.8

    text_admissible = result["channels"]["text_admissible"]["transitions"][0]["distinct_representations"]
    assert text_admissible["previous"] == 2
    assert text_admissible["current"] == 2
    assert text_admissible["shared"] == 1

    rendered = json.dumps(result, sort_keys=True)
    for value in [h("a"), h("b"), h("c"), h("d"), h("e"), h("f")]:
        assert value not in rendered
    assert "page_a" not in rendered and "page_b" not in rendered
    assert result["privacy"] == {
        "hash_values_emitted": False,
        "page_identifiers_emitted": False,
        "object_identifiers_emitted": False,
        "ocr_text_emitted": False,
    }


def test_near_exact_is_separate_sensitivity_channel(tmp_path):
    index = tmp_path / "index.sqlite"
    reuse = tmp_path / "reuse.sqlite"
    make_index(index)
    make_reuse(reuse)
    result = mod.benchmark(index, reuse_path=reuse, bootstrap_reps=20, permutations=20, seed=9)
    sensitivity = result["near_exact_sensitivity"]
    assert sensitivity is not None
    assert sensitivity["state"] == "sensitivity_signal_only"
    transitions = {(r["previous_generation"], r["current_generation"]): r for r in sensitivity["transitions"]}
    assert transitions[(1993, 2014)]["near_exact_candidate_pairs"] == 1
    assert transitions[(2014, 2018)]["similarity_candidate_pairs"] == 1
    assert all(r["all_verified_nonexact_pairs"] == 1 for r in transitions.values())
    assert result["scientific_state"]["near_exact_is_exact_identity"] is False
    assert result["scientific_state"]["similarity_is_semantic_equivalence"] is False


def test_survival_and_temporal_negative_control_are_deterministic(tmp_path):
    index = tmp_path / "index.sqlite"
    make_index(index)
    one = mod.benchmark(index, bootstrap_reps=80, permutations=80, seed=123)
    two = mod.benchmark(index, bootstrap_reps=80, permutations=80, seed=123)
    assert one == two
    survival = one["channels"]["source"]["survival"]
    assert survival["kaplan_meier"]
    assert survival["cohorts"][0]["entry_generation"] == 1993
    control = one["channels"]["source"]["temporal_negative_control"]
    assert control["permutations"] == 80
    assert 0.0 <= control["upper_tail_p_value"] <= 1.0


def test_page_occurrence_denominator_handles_duplicate_representations(tmp_path):
    index = tmp_path / "index.sqlite"
    make_index(index)
    con = sqlite3.connect(index)
    con.execute("UPDATE index_meta SET value=? WHERE key='unique_pages'", (json.dumps(10),))
    con.execute(
        "INSERT INTO pages VALUES(?,?,?,?,?,?,?)",
        (10, "obj_extra", 1993, h("a"), h("a"), 300, 60),
    )
    con.commit()
    con.close()
    result = mod.benchmark(index, bootstrap_reps=0, permutations=0)
    page = result["channels"]["source"]["transitions"][0]["page_occurrences"]
    assert page["previous"] == 4
    assert page["current"] == 3
    # Exact A can match only one current occurrence; C also matches once: 2 matched occurrences.
    assert page["matched_by_exact_representation"] == 2
    assert page["persistence_rate"] == 0.5


def test_invalid_hash_is_rejected(tmp_path):
    index = tmp_path / "index.sqlite"
    make_index(index)
    con = sqlite3.connect(index)
    con.execute("UPDATE pages SET source_sha256='not-a-sha' WHERE id=1")
    con.commit()
    con.close()
    try:
        mod.benchmark(index, bootstrap_reps=0, permutations=0)
    except RuntimeError as exc:
        assert "invalid SHA-256" in str(exc)
    else:
        raise AssertionError("expected invalid hash rejection")
