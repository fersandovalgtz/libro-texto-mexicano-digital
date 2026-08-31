import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "build_u1_universal_index.py"
SPEC = importlib.util.spec_from_file_location("build_u1_universal_index", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


def make_source_db(path: Path, rows: list[dict]):
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            CREATE TABLE pages (
                page_id TEXT,
                viewer_key TEXT,
                canonical_viewer_key TEXT,
                wave TEXT,
                catalog_generation INTEGER,
                grade_code INTEGER,
                title_core TEXT,
                page_index INTEGER,
                viewer_page INTEGER,
                source_asset_url TEXT,
                source_sha256 TEXT,
                source_byte_size INTEGER,
                ocr_engine TEXT,
                ocr_engine_version TEXT,
                ocr_language TEXT,
                ocr_psm INTEGER,
                ocr_sha256 TEXT,
                search_text TEXT,
                search_text_sha256 TEXT,
                ocr_confidence_mean REAL,
                ocr_char_count INTEGER,
                ocr_word_count INTEGER,
                generated_at TEXT
            )
            """
        )
        for row in rows:
            values = {
                "viewer_key": row.get("canonical_viewer_key"),
                "source_asset_url": "https://example.invalid/source.jpg",
                "source_byte_size": 100,
                "ocr_engine": "test",
                "ocr_engine_version": "1",
                "ocr_language": "spa",
                "ocr_psm": 3,
                "search_text_sha256": hashlib.sha256(row["search_text"].encode()).hexdigest(),
                "ocr_confidence_mean": 90.0,
                "ocr_char_count": len(row["search_text"]),
                "ocr_word_count": len(row["search_text"].split()),
                "generated_at": "2026-08-30T00:00:00Z",
                **row,
            }
            fields = list(values)
            connection.execute(
                "INSERT INTO pages (" + ",".join(fields) + ") VALUES (" + ",".join("?" for _ in fields) + ")",
                [values[field] for field in fields],
            )
        connection.commit()
    finally:
        connection.close()


def row(page_id, book, generation, grade, wave, text, page_index=1):
    return {
        "page_id": page_id,
        "canonical_viewer_key": book,
        "wave": wave,
        "catalog_generation": generation,
        "grade_code": grade,
        "title_core": f"Book {book}",
        "page_index": page_index,
        "viewer_page": page_index,
        "source_sha256": hashlib.sha256((page_id + "source").encode()).hexdigest(),
        "ocr_sha256": hashlib.sha256((page_id + "ocr").encode()).hexdigest(),
        "search_text": text,
    }


def test_build_reconciles_duplicate_and_builds_fts(tmp_path):
    db1 = tmp_path / "a.sqlite"
    db2 = tmp_path / "b.sqlite"
    p1 = row("p1", "B1", 1993, 5, "W3", "La lengua rarámuri aparece aquí")
    p2 = row("p2", "B2", 2014, 6, "W7", "Diversidad lingüística de México")
    make_source_db(db1, [p1, p2])
    make_source_db(db2, [p1])

    output = tmp_path / "universal.sqlite"
    manifest_path = tmp_path / "manifest.json"
    manifest = mod.build_index([db1, db2], output, manifest_path, expected_pages=2, expected_objects=2)

    assert manifest["reconciliation"]["unique_pages"] == 2
    assert manifest["reconciliation"]["unique_canonical_objects"] == 2
    assert manifest["reconciliation"]["identical_duplicate_rows_deduplicated"] == 1
    assert manifest["reconciliation"]["conflicts"] == 0
    assert manifest["index"]["private"] is True
    assert manifest["scientific_state"]["semantic_ready"] is False

    connection = sqlite3.connect(output)
    try:
        hit = connection.execute(
            "SELECT p.page_id FROM pages_fts f JOIN pages p ON p.id=f.rowid WHERE pages_fts MATCH ?",
            ("raramuri",),
        ).fetchall()
        assert hit == [("p1",)]
    finally:
        connection.close()


def test_conflicting_duplicate_page_id_fails(tmp_path):
    db1 = tmp_path / "a.sqlite"
    db2 = tmp_path / "b.sqlite"
    p1 = row("dup", "B1", 1993, 5, "W3", "texto")
    p2 = dict(p1)
    p2["source_sha256"] = hashlib.sha256(b"different").hexdigest()
    make_source_db(db1, [p1])
    make_source_db(db2, [p2])

    try:
        list(mod.iter_source_pages([db1, db2]))
    except RuntimeError as exc:
        assert "conflicting duplicate page_id" in str(exc)
    else:
        raise AssertionError("expected conflict gate")


def test_manifest_is_text_free_and_path_free(tmp_path):
    db = tmp_path / "private_wave.sqlite"
    make_source_db(db, [row("p1", "B1", 1993, 5, "W3", "secreto rarámuri")])
    output = tmp_path / "private_universal.sqlite"
    manifest_path = tmp_path / "manifest.json"
    mod.build_index([db], output, manifest_path, expected_pages=1, expected_objects=1)

    payload = manifest_path.read_text(encoding="utf-8")
    saved = json.loads(payload)
    assert "secreto" not in payload
    assert "example.invalid" not in payload
    assert str(tmp_path) not in payload
    assert "p1" not in payload
    assert saved["privacy"]["ocr_text_in_manifest"] is False
    assert saved["privacy"]["page_ids_in_manifest"] is False
    assert saved["input"]["private_paths_emitted"] is False


def test_u1_cardinality_gate_rejects_wrong_counts(tmp_path):
    db = tmp_path / "a.sqlite"
    make_source_db(db, [row("p1", "B1", 1993, 5, "W3", "texto")])
    output = tmp_path / "universal.sqlite"
    manifest_path = tmp_path / "manifest.json"

    try:
        mod.build_index([db], output, manifest_path, expected_pages=86549, expected_objects=492)
    except RuntimeError as exc:
        assert "page cardinality mismatch" in str(exc)
    else:
        raise AssertionError("expected U1 page cardinality gate")


def test_missing_core_column_is_rejected(tmp_path):
    db = tmp_path / "bad.sqlite"
    connection = sqlite3.connect(db)
    try:
        connection.execute("CREATE TABLE pages(page_id TEXT)")
        connection.execute("INSERT INTO pages(page_id) VALUES ('p1')")
        connection.commit()
    finally:
        connection.close()

    try:
        list(mod.iter_source_pages([db]))
    except RuntimeError as exc:
        assert "missing required columns" in str(exc)
        assert "search_text" in str(exc)
    else:
        raise AssertionError("expected schema gate")
