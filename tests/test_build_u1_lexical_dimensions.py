import importlib.util
import json
import sqlite3
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'build_u1_lexical_dimensions.py'
SPEC = importlib.util.spec_from_file_location('build_u1_lexical_dimensions', SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_source(path: Path):
    c = sqlite3.connect(path)
    c.executescript('''
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE terms(term_id INTEGER PRIMARY KEY,term TEXT,page_count INTEGER,occurrence_count INTEGER);
    CREATE TABLE objects(object_id INTEGER PRIMARY KEY,canonical_viewer_key TEXT);
    CREATE TABLE pages(page_rowid INTEGER PRIMARY KEY,object_id INTEGER,generation INTEGER,grade_code INTEGER,wave TEXT);
    CREATE TABLE token_positions(term_id INTEGER,page_rowid INTEGER,token_offset INTEGER);
    CREATE TABLE term_pages(term_id INTEGER,page_rowid INTEGER,PRIMARY KEY(term_id,page_rowid));
    CREATE TABLE term_stats(term_id INTEGER PRIMARY KEY,page_count INTEGER,occurrence_count INTEGER,object_count INTEGER,generation_count INTEGER,grade_count INTEGER,wave_count INTEGER);
    ''')
    for k, v in {'version': mod.SOURCE_VERSION, 'term_page_relations': 4, 'unique_pages': 3}.items():
        c.execute('insert into meta values(?,?)', (k, json.dumps(v)))
    c.executemany('insert into terms values(?,?,?,?)', [(1,'a',2,3),(2,'b',2,2)])
    c.executemany('insert into objects values(?,?)', [(1,'B1'),(2,'B2')])
    c.executemany('insert into pages values(?,?,?,?,?)', [(1,1,1993,5,'W1'),(2,1,1993,5,'W1'),(3,2,2014,6,'W3')])
    c.executemany('insert into token_positions values(?,?,?)', [(1,1,0),(1,1,1),(2,1,2),(1,3,0),(2,3,1)])
    c.executemany('insert into term_pages values(?,?)', [(1,1),(1,3),(2,1),(2,3)])
    c.executemany('insert into term_stats values(?,?,?,?,?,?,?)', [(1,2,3,2,2,2,2),(2,2,2,2,2,2,2)])
    c.commit()
    c.close()


def test_dimension_counts_and_denominators(tmp_path):
    src = tmp_path / 'source.sqlite'
    out = tmp_path / 'dims.sqlite'
    make_source(src)
    summary = mod.run(src, out)
    assert summary['counts']['term_page_stats_rows'] == 4
    c = sqlite3.connect(out)
    assert c.execute("select page_count,object_count from dimension_denominators where dimension='generation' and value='1993'").fetchone() == (2,1)
    assert c.execute("select occurrence_count,page_count,object_count from term_dimension_stats where dimension='generation' and value='1993' and term_id=1").fetchone() == (2,1,1)
    assert c.execute('pragma quick_check').fetchone()[0] == 'ok'
    c.close()


def test_summary_has_no_term_values_or_page_ids(tmp_path):
    src = tmp_path / 'source.sqlite'
    out = tmp_path / 'dims.sqlite'
    make_source(src)
    rendered = json.dumps(mod.run(src, out))
    assert 'B1' not in rendered
    assert '1993' not in rendered
    assert mod.SOURCE_VERSION in rendered


def test_sha_gate(tmp_path):
    src = tmp_path / 'source.sqlite'
    out = tmp_path / 'dims.sqlite'
    make_source(src)
    sha = mod.sha256_file(src)
    assert mod.run(src, out, expected_source_sha256=sha)['source_sha256'] == sha
    try:
        mod.run(src, tmp_path / 'bad.sqlite', expected_source_sha256='0' * 64)
    except RuntimeError as exc:
        assert str(exc) == 'lexical-position SHA-256 mismatch'
    else:
        raise AssertionError('expected mismatch')
