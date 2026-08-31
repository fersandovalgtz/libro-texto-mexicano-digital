import importlib.util
import json
import sqlite3
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'build_u1_cooccurrences.py'
SPEC = importlib.util.spec_from_file_location('build_u1_cooccurrences', SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_source(path: Path):
    c = sqlite3.connect(path)
    c.executescript('''
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE terms(term_id INTEGER PRIMARY KEY,term TEXT,page_count INTEGER,occurrence_count INTEGER);
    CREATE TABLE pages(page_rowid INTEGER PRIMARY KEY,object_id INTEGER,generation INTEGER,grade_code INTEGER,wave TEXT);
    CREATE TABLE token_positions(term_id INTEGER,page_rowid INTEGER,token_offset INTEGER);
    CREATE TABLE term_stats(term_id INTEGER PRIMARY KEY,page_count INTEGER,occurrence_count INTEGER,object_count INTEGER,generation_count INTEGER,grade_count INTEGER,wave_count INTEGER);
    ''')
    for k, v in {'artifact_version': mod.SOURCE_VERSION, 'unique_pages': 3, 'unique_objects': 2}.items():
        c.execute('INSERT INTO meta VALUES(?,?)', (k, json.dumps(v)))
    c.executemany('INSERT INTO terms VALUES(?,?,?,?)', [(1,'secretAlpha',3,6),(2,'secretBeta',3,6),(3,'secretGamma',3,6),(4,'secretDelta',2,2)])
    c.executemany('INSERT INTO pages VALUES(?,?,?,?,?)', [(1,1,1993,5,'W1'),(2,1,1993,5,'W1'),(3,2,2014,6,'W3')])
    seqs = {1:[1,2,3,1,2,3], 2:[1,2,3,1,2,3], 3:[1,2,4,3]}
    rows=[]
    for page, seq in seqs.items(): rows.extend((term,page,offset) for offset,term in enumerate(seq))
    c.executemany('INSERT INTO token_positions VALUES(?,?,?)', rows)
    c.executemany('INSERT INTO term_stats VALUES(?,?,?,?,?,?,?)', [
        (1,3,5,2,2,2,2),(2,3,5,2,2,2,2),(3,3,5,2,2,2,2),(4,1,1,1,1,1,1)])
    c.commit(); c.close()
    return seqs


def naive_raw(seqs):
    total=0
    pair_counts={}
    pair_pages={}
    for page, seq in seqs.items():
        for i,x in enumerate(seq):
            for j in range(i+1, min(len(seq), i+1+mod.WINDOW_MAX_TOKENS)):
                y=seq[j]
                if x==y: continue
                pair=tuple(sorted((x,y)))
                total+=1
                pair_counts[pair]=pair_counts.get(pair,0)+1
                pair_pages.setdefault(pair,set()).add(page)
    return total,pair_counts,pair_pages


def test_windowed_unordered_distinct_same_page(tmp_path):
    src, out = tmp_path/'source.sqlite', tmp_path/'cooc.sqlite'
    seqs=make_source(src); expected_total, counts, pages=naive_raw(seqs)
    summary=mod.run(src,out)
    assert summary['counts']['raw_pair_occurrences']==expected_total
    c=sqlite3.connect(out)
    row=c.execute('SELECT occurrence_count,page_count,object_count FROM cooccurrences WHERE t1=1 AND t2=2').fetchone()
    assert row==(counts[(1,2)],len(pages[(1,2)]),2)
    assert c.execute('SELECT 1 FROM cooccurrences WHERE t1>=t2').fetchone() is None
    assert c.execute('SELECT 1 FROM cooccurrences WHERE t1=t2').fetchone() is None
    assert c.execute('PRAGMA quick_check').fetchone()[0]=='ok'
    c.close()


def test_protocol_fixed_and_summary_private(tmp_path):
    src,out=tmp_path/'source.sqlite',tmp_path/'cooc.sqlite'; make_source(src)
    rendered=json.dumps(mod.run(src,out),sort_keys=True)
    assert mod.WINDOW_MAX_TOKENS==5
    assert mod.PRIVATE_RETENTION=={'min_occurrences':3,'min_pages':2}
    assert mod.PUBLIC_SUPPRESSION=={'min_occurrences':75,'min_pages':25,'min_objects':10,'each_term_min_pages':20,'each_term_min_objects':10}
    assert 'secretAlpha' not in rendered and 'secretBeta' not in rendered
    assert 'page_rowid' not in rendered
    assert 'cooccurrence_is_semantic_relation' in rendered


def test_sha_gate(tmp_path):
    src=tmp_path/'source.sqlite'; make_source(src); sha=mod.sha256_file(src)
    assert mod.run(src,tmp_path/'good.sqlite',expected_source_sha256=sha)['source_lexical_sha256']==sha
    try:
        mod.run(src,tmp_path/'bad.sqlite',expected_source_sha256='f'*64)
    except RuntimeError as exc:
        assert str(exc)=='lexical-position SHA-256 mismatch'
    else:
        raise AssertionError('expected mismatch')
