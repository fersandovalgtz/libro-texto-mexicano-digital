import importlib.util, json, sqlite3
from pathlib import Path

SCRIPT=Path(__file__).parents[1] / 'scripts' / 'build_u1_reuse_similarity.py'
SPEC=importlib.util.spec_from_file_location('reuse',SCRIPT); mod=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)

def make_fixture(root:Path):
    idx=root/'idx.sqlite'; lex=root/'lex.sqlite'
    c=sqlite3.connect(idx)
    c.executescript('''
    CREATE TABLE index_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE pages(
      id INTEGER PRIMARY KEY,page_id TEXT,viewer_key TEXT,canonical_viewer_key TEXT,wave TEXT,catalog_generation INTEGER,grade_code INTEGER,title_core TEXT,page_index INTEGER,viewer_page INTEGER,
      source_asset_url TEXT,source_sha256 TEXT,source_byte_size INTEGER,ocr_engine TEXT,ocr_engine_version TEXT,ocr_language TEXT,ocr_psm INTEGER,ocr_sha256 TEXT,search_text TEXT,search_text_sha256 TEXT,
      ocr_confidence_mean REAL,ocr_char_count INTEGER,ocr_word_count INTEGER,generated_at TEXT);
    ''')
    c.execute('INSERT INTO index_meta VALUES(?,?)',('builder_version',json.dumps(mod.INDEX_VERSION)))
    c.execute('INSERT INTO index_meta VALUES(?,?)',('unique_pages',json.dumps(5)))
    rows=[]
    specs=[
      (1,'A',1993,5,'W1','src1','txtExact',400,80),
      (2,'B',2014,6,'W2','src2','txtExact',410,82),
      (3,'A',1993,5,'W1','src3','txt3',500,100),
      (4,'B',2014,6,'W2','src4','txt4',510,101),
      (5,'B',2014,6,'W2','src5','emptyHash',0,0),
    ]
    for pid,obj,gen,grade,wave,src,txt,chars,words in specs:
      rows.append((pid,f'p{pid}',f'v{pid}',obj,wave,gen,grade,'T',pid,pid,'u',src,1,'e','1','spa',6,'ocr'+str(pid),'x',txt,1.0,chars,words,'now'))
    c.executemany('INSERT INTO pages VALUES('+','.join('?'*24)+')',rows); c.commit(); c.close()

    c=sqlite3.connect(lex)
    c.executescript('''
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    CREATE TABLE terms(term_id INTEGER PRIMARY KEY,term TEXT,page_count INTEGER,occurrence_count INTEGER);
    CREATE TABLE pages(page_rowid INTEGER PRIMARY KEY,object_id INTEGER,generation INTEGER,grade_code INTEGER,wave TEXT);
    CREATE TABLE token_positions(term_id INTEGER,page_rowid INTEGER,token_offset INTEGER);
    ''')
    for k,v in {'artifact_version':mod.LEXICAL_VERSION,'unique_pages':5}.items(): c.execute('INSERT INTO meta VALUES(?,?)',(k,json.dumps(v)))
    c.executemany('INSERT INTO terms VALUES(?,?,?,?)',[(i,f't{i}',5,10) for i in range(1,201)])
    c.executemany('INSERT INTO pages VALUES(?,?,?,?,?)',[(1,1,1993,5,'W1'),(2,2,2014,6,'W2'),(3,1,1993,5,'W1'),(4,2,2014,6,'W2'),(5,2,2014,6,'W2')])
    seq1=list(range(1,81)); seq2=list(range(1,81)); seq3=list(range(1,101)); seq4=list(range(1,91))+list(range(101,111)); seq5=list(range(1,10))
    pos=[]
    for pid,seq in enumerate([seq1,seq2,seq3,seq4,seq5],1): pos.extend((t,pid,o) for o,t in enumerate(seq))
    c.executemany('INSERT INTO token_positions VALUES(?,?,?)',pos); c.commit(); c.close()
    return idx,lex

def test_hierarchy_and_privacy(tmp_path):
    idx,lex=make_fixture(tmp_path); out=tmp_path/'out.sqlite'
    summary=mod.run(idx,lex,out)
    assert summary['counts']['text_admissible_pages']==4
    c=sqlite3.connect(out)
    assert c.execute("SELECT COUNT(*) FROM exact_text_groups WHERE cross_object=1").fetchone()[0]==1
    assert c.execute("SELECT COUNT(*) FROM similarity_candidates WHERE object_a!=object_b").fetchone()[0]>=1
    assert c.execute('SELECT COUNT(*) FROM similarity_candidates s JOIN exact_text_members a ON s.page_a=a.page_rowid JOIN exact_text_members b ON s.page_b=b.page_rowid AND a.group_id=b.group_id').fetchone()[0]==0
    assert c.execute('PRAGMA quick_check').fetchone()[0]=='ok'; c.close()
    rendered=json.dumps(summary)
    assert 'txtExact' not in rendered and 'page_rowid' not in rendered
    assert summary['scientific_state']['similarity_creates_alias'] is False

def test_protocol_frozen():
    assert (mod.TEXT_MIN_CHARS,mod.TEXT_MIN_WORDS)==(200,30)
    assert (mod.SHINGLE_N,mod.MIN_DISTINCT_SHINGLES)==(5,50)
    assert (mod.MINHASH_COMPONENTS,mod.LSH_BANDS,mod.LSH_ROWS)==(96,12,8)
    assert mod.SIMILARITY_MIN_JACCARD==0.80 and mod.NEAR_EXACT_MIN_JACCARD==0.95
    assert mod.SIMILARITY_MIN_SHARED_SHINGLES==40

def test_sha_gates(tmp_path):
    idx,lex=make_fixture(tmp_path)
    assert mod.run(idx,lex,tmp_path/'good.sqlite',expected_index_sha256=mod.sha256_file(idx),expected_lexical_sha256=mod.sha256_file(lex))['sources']['universal_index_sha256']==mod.sha256_file(idx)
    try: mod.run(idx,lex,tmp_path/'bad.sqlite',expected_index_sha256='0'*64)
    except RuntimeError as e: assert str(e)=='Universal Index SHA-256 mismatch'
    else: raise AssertionError('expected mismatch')
