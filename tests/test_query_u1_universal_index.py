import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path

BUILDER_PATH = Path(__file__).parents[1] / "scripts" / "build_u1_universal_index.py"
BUILDER_SPEC = importlib.util.spec_from_file_location("build_u1_universal_index", BUILDER_PATH)
builder = importlib.util.module_from_spec(BUILDER_SPEC)
assert BUILDER_SPEC.loader is not None
BUILDER_SPEC.loader.exec_module(builder)

QUERY_PATH = Path(__file__).parents[1] / "scripts" / "query_u1_universal_index.py"
QUERY_SPEC = importlib.util.spec_from_file_location("query_u1_universal_index", QUERY_PATH)
mod = importlib.util.module_from_spec(QUERY_SPEC)
assert QUERY_SPEC.loader is not None
QUERY_SPEC.loader.exec_module(mod)


def source_row(page_id, book, generation, grade, wave, text, page_index):
    return {
        "page_id": page_id,
        "viewer_key": book,
        "canonical_viewer_key": book,
        "wave": wave,
        "catalog_generation": generation,
        "grade_code": grade,
        "title_core": f"Book {book}",
        "page_index": page_index,
        "viewer_page": page_index,
        "source_asset_url": f"https://example.invalid/{page_id}.jpg",
        "source_sha256": hashlib.sha256((page_id + "source").encode()).hexdigest(),
        "source_byte_size": 100,
        "ocr_engine": "test",
        "ocr_engine_version": "1",
        "ocr_language": "spa",
        "ocr_psm": 3,
        "ocr_sha256": hashlib.sha256((page_id + "ocr").encode()).hexdigest(),
        "search_text": text,
        "search_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "ocr_confidence_mean": 90.0,
        "ocr_char_count": len(text),
        "ocr_word_count": len(text.split()),
        "generated_at": "2026-08-30T00:00:00Z",
    }


def make_source_db(path: Path):
    rows = [
        source_row("p1", "B1", 1993, 5, "W3", "democracia y lengua rarámuri", 1),
        source_row("p2", "B1", 1993, 5, "W3", "familia y comunidad", 2),
        source_row("p3", "B2", 2014, 6, "W7", "democracia participación", 1),
        source_row("p4", "B3", 2014, 6, "W3", "tecnología y ciencia", 1),
    ]
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            CREATE TABLE pages (
                page_id TEXT, viewer_key TEXT, canonical_viewer_key TEXT, wave TEXT,
                catalog_generation INTEGER, grade_code INTEGER, title_core TEXT,
                page_index INTEGER, viewer_page INTEGER, source_asset_url TEXT,
                source_sha256 TEXT, source_byte_size INTEGER, ocr_engine TEXT,
                ocr_engine_version TEXT, ocr_language TEXT, ocr_psm INTEGER,
                ocr_sha256 TEXT, search_text TEXT, search_text_sha256 TEXT,
                ocr_confidence_mean REAL, ocr_char_count INTEGER, ocr_word_count INTEGER,
                generated_at TEXT
            )
            """
        )
        fields = list(rows[0])
        for row in rows:
            connection.execute(
                "INSERT INTO pages (" + ",".join(fields) + ") VALUES (" + ",".join("?" for _ in fields) + ")",
                [row[field] for field in fields],
            )
        connection.commit()
    finally:
        connection.close()


def make_index(tmp_path: Path) -> Path:
    source = tmp_path / "source.sqlite"
    make_source_db(source)
    index = tmp_path / "universal.sqlite"
    manifest = tmp_path / "manifest.json"
    builder.build_index([source], index, manifest, expected_pages=4, expected_objects=3)
    return index


def test_query_exact_counts_and_scope_denominator(tmp_path):
    index = make_index(tmp_path)
    response = mod.run(
        index,
        query_expression="democracia",
        filters={"generation": ["2014"], "grade_code": ["6"], "wave": None},
    )
    assert response["metrics"] == {
        "candidate_pages": 1,
        "candidate_books": 1,
        "corpus_pages_in_scope": 2,
        "corpus_books_in_scope": 2,
        "candidate_pages_per_1000": 500.0,
    }
    assert response["filters"]["generation"] == [2014]
    assert response["filters"]["grade_code"] == [6]
    assert response["result_state"] == "exploratory_signal"


def test_combined_grade_wave_denominator_is_exact(tmp_path):
    index = make_index(tmp_path)
    response = mod.run(
        index,
        query_expression="democracia",
        filters={"generation": ["2014"], "grade_code": ["6"], "wave": ["W7"]},
    )
    assert response["metrics"]["candidate_pages"] == 1
    assert response["metrics"]["corpus_pages_in_scope"] == 1
    assert response["metrics"]["candidate_pages_per_1000"] == 1000.0


def test_breakdown_uses_group_specific_denominators(tmp_path):
    index = make_index(tmp_path)
    response = mod.run(index, query_expression="democracia", group_by="generation")
    by_generation = {row["value"]: row["metrics"] for row in response["breakdown"]}
    assert by_generation["1993"]["candidate_pages"] == 1
    assert by_generation["1993"]["corpus_pages_in_scope"] == 2
    assert by_generation["1993"]["candidate_pages_per_1000"] == 500.0
    assert by_generation["2014"]["candidate_pages"] == 1
    assert by_generation["2014"]["corpus_pages_in_scope"] == 2


def test_accent_insensitive_fts_and_private_surface(tmp_path):
    index = make_index(tmp_path)
    plain = mod.run(index, query_expression="raramuri")
    accented = mod.run(index, query_expression="rarámuri")
    assert plain["metrics"]["candidate_pages"] == 1
    assert plain["metrics"] == accented["metrics"]
    rendered = json.dumps(plain, ensure_ascii=False)
    for forbidden in ("page_id", "search_text", "source_asset_url", "source_sha256", "ocr_sha256", "example.invalid", "p1"):
        assert forbidden not in rendered


def test_zero_hits_warns_that_absence_is_not_demonstrated(tmp_path):
    index = make_index(tmp_path)
    response = mod.run(index, query_expression="inexistente")
    assert response["metrics"]["candidate_pages"] == 0
    assert response["metrics"]["candidate_books"] == 0
    assert response["metrics"]["corpus_pages_in_scope"] == 4
    assert any("do not demonstrate historical absence" in warning for warning in response["warnings"])


def test_invalid_fts_expression_is_sanitized(tmp_path):
    index = make_index(tmp_path)
    try:
        mod.run(index, query_expression='"unterminated')
    except RuntimeError as exc:
        assert str(exc) == "invalid FTS5 query expression"
    else:
        raise AssertionError("expected invalid FTS expression")


def test_index_hash_verification(tmp_path):
    index = make_index(tmp_path)
    expected = mod.sha256_file(index)
    response = mod.run(index, query_expression="familia", expected_index_sha256=expected)
    assert response["provenance"]["index_sha256"] == expected
    try:
        mod.run(index, query_expression="familia", expected_index_sha256="0" * 64)
    except RuntimeError as exc:
        assert str(exc) == "Universal Index SHA-256 mismatch"
    else:
        raise AssertionError("expected SHA mismatch")


def test_filter_validation(tmp_path):
    index = make_index(tmp_path)
    for filters, expected_fragment in [
        ({"generation": ["x"]}, "generation values"),
        ({"grade_code": ["six"]}, "grade_code values"),
        ({"wave": ["history"]}, "invalid wave"),
    ]:
        try:
            mod.run(index, query_expression="familia", filters=filters)
        except RuntimeError as exc:
            assert expected_fragment in str(exc)
        else:
            raise AssertionError("expected filter validation failure")
