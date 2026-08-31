import csv
import importlib.util
import json
import sqlite3
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "build_vertical_reuse_context.py"
spec = importlib.util.spec_from_file_location("ctx", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixtures(root):
    ledger = root / "ledger.csv"
    with ledger.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["page_id"])
        w.writeheader()
        w.writerows([{"page_id": "p1"}, {"page_id": "p2"}])

    idx = root / "idx.sqlite"
    c = sqlite3.connect(idx)
    c.executescript("""
    CREATE TABLE index_meta(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE pages(id INTEGER PRIMARY KEY,page_id TEXT UNIQUE,catalog_generation INTEGER);
    """)
    c.execute("INSERT INTO index_meta VALUES(?,?)", ("builder_version", json.dumps(mod.INDEX_VERSION)))
    c.executemany("INSERT INTO pages VALUES(?,?,?)", [(1, "p1", 1993), (2, "p2", 2014), (3, "p3", 2014)])
    c.commit()
    c.close()

    reuse = root / "reuse.sqlite"
    c = sqlite3.connect(reuse)
    c.executescript("""
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE exact_source_groups(group_id INTEGER PRIMARY KEY,cross_object INTEGER,cross_generation INTEGER);
    CREATE TABLE exact_source_members(group_id INTEGER,page_rowid INTEGER);
    CREATE TABLE exact_text_groups(group_id INTEGER PRIMARY KEY,cross_object INTEGER,cross_generation INTEGER);
    CREATE TABLE exact_text_members(group_id INTEGER,page_rowid INTEGER);
    CREATE TABLE similarity_candidates(page_a INTEGER,page_b INTEGER,tier TEXT);
    """)
    c.execute("INSERT INTO meta VALUES(?,?)", ("artifact_version", json.dumps(mod.REUSE_VERSION)))
    c.execute("INSERT INTO exact_source_groups VALUES(1,1,1)")
    c.executemany("INSERT INTO exact_source_members VALUES(1,?)", [(1,), (3,)])
    c.execute("INSERT INTO exact_text_groups VALUES(1,1,0)")
    c.executemany("INSERT INTO exact_text_members VALUES(1,?)", [(2,), (3,)])
    c.execute("INSERT INTO similarity_candidates VALUES(1,2,'near_exact_candidate')")
    c.commit()
    c.close()
    return ledger, idx, reuse


def test_context_counts_and_privacy(tmp_path):
    ledger, idx, reuse = fixtures(tmp_path)
    result = mod.run(ledger, idx, reuse, vertical_id="test")
    m = result["metrics"]
    assert m["candidate_pages"] == 2
    assert m["mapped_candidate_pages"] == 2
    assert m["unmapped_candidate_pages"] == 0
    assert m["candidate_pages_with_exact_source_cross_object_reuse"] == 1
    assert m["candidate_pages_with_exact_text_cross_object_reuse"] == 1
    assert m["candidate_pages_with_similarity_signal"] == 2
    assert m["candidate_pages_with_near_exact_signal"] == 2
    assert m["candidate_pages_with_any_reuse_similarity_signal"] == 2
    assert m["internal_similarity_pairs"] == 1
    assert m["internal_near_exact_pairs"] == 1
    assert result["result_state"] == "exploratory_signal"
    rendered = json.dumps(result)
    assert "p1" not in rendered and "p2" not in rendered
    assert result["privacy"]["page_identifiers_emitted"] is False


def test_missing_candidate_fails(tmp_path):
    ledger, idx, reuse = fixtures(tmp_path)
    with ledger.open("a", encoding="utf-8") as f:
        f.write("missing\n")
    try:
        mod.run(ledger, idx, reuse, vertical_id="test")
    except RuntimeError as e:
        assert "absent from Universal Index" in str(e)
    else:
        raise AssertionError("expected failure")


def test_sha_gates(tmp_path):
    ledger, idx, reuse = fixtures(tmp_path)
    result = mod.run(
        ledger, idx, reuse, vertical_id="test",
        expected_ledger_sha256=mod.sha256_file(ledger),
        expected_index_sha256=mod.sha256_file(idx),
        expected_reuse_sha256=mod.sha256_file(reuse),
    )
    assert result["provenance"]["candidate_ledger_sha256"] == mod.sha256_file(ledger)
    try:
        mod.run(ledger, idx, reuse, vertical_id="test", expected_reuse_sha256="0" * 64)
    except RuntimeError as e:
        assert str(e) == "reuse/similarity artifact SHA-256 mismatch"
    else:
        raise AssertionError("expected mismatch")
