import csv
import importlib.util
import sqlite3
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "build_u1_corpus_analytics_manifest.py"
SPEC = importlib.util.spec_from_file_location("build_u1_corpus_analytics_manifest", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_index(path: Path):
    c = sqlite3.connect(path)
    try:
        c.executescript("""
        CREATE TABLE index_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        INSERT INTO index_meta VALUES ('builder_version', '"LTMD_U1_UNIVERSAL_INDEX_0.1"');
        CREATE TABLE pages(
          id INTEGER PRIMARY KEY, page_id TEXT UNIQUE, canonical_viewer_key TEXT,
          wave TEXT, catalog_generation INTEGER, grade_code INTEGER,
          search_text TEXT, ocr_confidence_mean REAL
        );
        CREATE VIRTUAL TABLE pages_fts USING fts5(search_text, content='pages', content_rowid='id');
        """)
        rows = [
            (1, 'p1', 'B1', 'W1', 1993, 5, 'alpha', 90.0),
            (2, 'p2', 'B1', 'W1', 1993, 5, 'beta', None),
            (3, 'p3', 'B2', 'W2', 2014, 6, 'gamma', 80.0),
            (4, 'p4', 'B3', 'W2', 2014, 6, 'delta', 100.0),
        ]
        c.executemany('INSERT INTO pages VALUES (?,?,?,?,?,?,?,?)', rows)
        c.execute("INSERT INTO pages_fts(pages_fts) VALUES('rebuild')")
        c.commit()
    finally:
        c.close()


def make_coverage(path: Path, *, effective=4, objects=3):
    path.write_text(f'''# LTMD-U1 — tablero de cobertura técnica

Versión: `TEST_COVERAGE_0.1`.

## Totales

- Universo U1: **4/4** identidades catalogadas.
- Cobertura técnica efectiva cerrada o resuelta: **{effective}/4 (100%)**.
- Objetos canónicos de procesamiento cerrados: **{objects}/4 (75%)**.
- Cobertura semántica humana validada incorporada al tablero: **0/4**.

## Por ola

| ola | dominio operacional | plan | efectiva | canónicos | restantes | estado |
|---|---|---:|---:|---:|---:|---|
| W1 | `a` | 1 | 1 | 1 | 0 | `closed` |
| W2 | `b` | 1 | 1 | 1 | 0 | `closed` |
| W3 | `c` | 1 | 1 | 1 | 0 | `closed` |
| W4 | `d` | 1 | {1 if effective == 4 else 0} | 0 | {0 if effective == 4 else 1} | `closed` |
| W5 | `e` | 0 | 0 | 0 | 0 | `closed` |
| W6 | `f` | 0 | 0 | 0 | 0 | `closed` |
| W7 | `g` | 0 | 0 | 0 | 0 | `closed` |
| W8 | `h` | 0 | 0 | 0 | 0 | `closed` |
| W9 | `i` | 0 | 0 | 0 | 0 | `closed` |
| W10 | `j` | 0 | 0 | 0 | 0 | `closed` |
| W11 | `k` | 0 | 0 | 0 | 0 | `closed` |
''', encoding='utf-8')


def make_retained(path: Path, rows=None):
    fields = ['register_version','wave','operational_domain','viewer_key','catalog_generation','grade_code','retention_class','retention_detail','tracking_issue','status']
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows or []:
            w.writerow({
                'register_version':'TEST_RETENTION_0.1','wave':'W4','operational_domain':'d',
                'viewer_key':'PRIVATE_ID','catalog_generation':'2014','grade_code':'1',
                'retention_class':'x','retention_detail':'private detail','tracking_issue':'1',
                'status':row,
            })


def build_fixture(tmp_path: Path):
    index = tmp_path/'index.sqlite'
    coverage = tmp_path/'coverage.md'
    retained = tmp_path/'retained.csv'
    output = tmp_path/'manifest.json'
    make_index(index)
    make_coverage(coverage, effective=3, objects=3)
    make_retained(retained, ['active_retention'])
    manifest = mod.build(index, coverage, retained, output, expected_index_sha256=mod.sha256_file(index), expected_pages=4, expected_objects=3)
    return index, coverage, retained, output, manifest


def test_manifest_reconciles_and_builds_exact_denominators(tmp_path):
    _, _, _, _, m = build_fixture(tmp_path)
    assert m['universe']['indexed_pages'] == 4
    assert m['universe']['canonical_processing_objects'] == 3
    assert m['universe']['residual_identities'] == 1
    assert m['universe']['active_retentions'] == 1
    cells = m['dimensions']['nonempty_generation_grade_wave_cells']
    assert cells == [
        {'generation':1993,'grade_code':5,'wave':'W1','pages':2,'canonical_objects':1},
        {'generation':2014,'grade_code':6,'wave':'W2','pages':2,'canonical_objects':2},
    ]
    assert sum(row['pages'] for row in cells) == 4


def test_ocr_quality_is_engine_confidence_not_text_verification(tmp_path):
    _, _, _, _, m = build_fixture(tmp_path)
    q = m['ocr_quality']
    assert q['available_pages'] == 3
    assert q['unavailable_pages'] == 1
    assert q['mean'] == 90.0
    assert q['min'] == 80.0 and q['max'] == 100.0
    assert q['interpretation'] == 'engine_confidence_only_not_CER_WER_or_human_text_verification'
    assert m['scientific_state']['text_verified'] is False
    assert m['scientific_state']['semantic_ready'] is False


def test_public_manifest_surface_omits_private_rows_and_text(tmp_path):
    _, _, _, output, m = build_fixture(tmp_path)
    rendered = output.read_text(encoding='utf-8')
    for forbidden in ('PRIVATE_ID', 'private detail', 'alpha', 'beta', 'gamma', 'delta', 'file:/'):
        assert forbidden not in rendered
    assert m['privacy']['aggregate_only_public_surface'] is True
    assert m['privacy']['source_urls_emitted'] is False


def test_residual_mismatch_is_rejected(tmp_path):
    index = tmp_path/'index.sqlite'; make_index(index)
    coverage = tmp_path/'coverage.md'; make_coverage(coverage, effective=4, objects=3)
    retained = tmp_path/'retained.csv'; make_retained(retained, ['active_retention'])
    try:
        mod.build(index, coverage, retained, tmp_path/'out.json', expected_pages=4, expected_objects=3)
    except RuntimeError as exc:
        assert 'coverage residual does not equal retained-source register rows' in str(exc)
    else:
        raise AssertionError('expected residual mismatch gate')


def test_index_sha_mismatch_is_rejected(tmp_path):
    index, coverage, retained, _, _ = build_fixture(tmp_path)
    try:
        mod.build(index, coverage, retained, tmp_path/'out2.json', expected_index_sha256='0'*64, expected_pages=4, expected_objects=3)
    except RuntimeError as exc:
        assert str(exc) == 'Universal Index SHA-256 mismatch'
    else:
        raise AssertionError('expected SHA mismatch')
