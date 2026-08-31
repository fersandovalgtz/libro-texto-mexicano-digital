import importlib.util
import json
import sqlite3
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'build_u1_lexical_positions.py'
SPEC = importlib.util.spec_from_file_location('build_u1_lexical_positions', SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_index(path: Path):
    c = sqlite3.connect(path)
    c.executescript('''
    CREATE TABLE pages(
      id INTEGER PRIMARY KEY, page_id TEXT NOT NULL, canonical_viewer_key TEXT NOT NULL,
      wave TEXT, catalog_generation INTEGER, grade_code INTEGER, search_text TEXT NOT NULL
    );
    CREATE TABLE index_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE VIRTUAL TABLE pages_fts USING fts5(search_text,content='pages',content_rowid='id',tokenize='unicode61 remove_diacritics 2');
    ''')
    rows = [
      (1,'p1','B1','W1',1993,5,'lengua rarámuri comunidad'),
      (2,'p2','B1','W1',1993,5,'comunidad y familia'),
      (3,'p3','B2','W3',2014,6,'Raramuri familia democracia'),
    ]
    c.executemany('insert into pages values(?,?,?,?,?,?,?)',rows)
    c.execute("insert into pages_fts(pages_fts) values('rebuild')")
    meta = {'builder_version':mod.INDEX_VERSION,'unique_pages':3,'unique_canonical_objects':2,'text_verified':False,'semantic_ready':False}
    for k,v in meta.items():
        c.execute('insert into index_meta values(?,?)',(k,json.dumps(v)))
    c.commit()
    c.close()


def test_materialization_counts_and_normalization(tmp_path):
    src=tmp_path/'index.sqlite'
    out=tmp_path/'lex.sqlite'
    make_index(src)
    summary=mod.run(src,out)
    assert summary['counts']['unique_pages']==3
    assert summary['counts']['unique_objects']==2
    assert summary['counts']['token_instances']==9
    c=sqlite3.connect(out)
    terms=dict(c.execute('select term,term_id from terms'))
    assert 'raramuri' in terms
    assert 'rarámuri' not in terms
    tid=terms['raramuri']
    assert c.execute('select occurrence_count,page_count from terms where term_id=?',(tid,)).fetchone()==(2,2)
    assert c.execute('select object_count,generation_count from term_stats where term_id=?',(tid,)).fetchone()==(2,2)
    assert c.execute('pragma quick_check').fetchone()[0]=='ok'
    c.close()


def test_positions_preserve_page_order_for_downstream_ngrams(tmp_path):
    src=tmp_path/'index.sqlite'
    out=tmp_path/'lex.sqlite'
    make_index(src)
    mod.run(src,out)
    c=sqlite3.connect(out)
    page1=c.execute('''select t.term,x.token_offset from token_positions x join terms t using(term_id) where page_rowid=1 order by token_offset''').fetchall()
    assert page1==[('lengua',0),('raramuri',1),('comunidad',2)]
    c.close()


def test_public_summary_does_not_emit_term_values(tmp_path):
    src=tmp_path/'index.sqlite'
    out=tmp_path/'lex.sqlite'
    make_index(src)
    summary=mod.run(src,out)
    rendered=json.dumps(summary,ensure_ascii=False)
    for forbidden in ('raramuri','comunidad','B1','p1'):
        assert forbidden not in rendered
    assert summary['privacy']['rare_terms_publish_by_default'] is False
    assert summary['scientific_state']['semantic_ready'] is False


def test_sha_gate(tmp_path):
    src=tmp_path/'index.sqlite'
    out=tmp_path/'lex.sqlite'
    make_index(src)
    actual=mod.sha256_file(src)
    assert mod.run(src,out,expected_index_sha256=actual)['source_index_sha256']==actual
    out2=tmp_path/'lex2.sqlite'
    try:
        mod.run(src,out2,expected_index_sha256='0'*64)
    except RuntimeError as exc:
        assert str(exc)=='Universal Index SHA-256 mismatch'
    else:
        raise AssertionError('expected SHA mismatch')
