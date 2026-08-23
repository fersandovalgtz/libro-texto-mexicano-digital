#!/usr/bin/env python3
"""Validate LTMD Full-Text Research Layer OCR JSONL and optional SQLite index."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = {
    "schema_version",
    "pipeline_version",
    "page_id",
    "viewer_key",
    "canonical_viewer_key",
    "wave",
    "catalog_generation",
    "grade_code",
    "title_core",
    "page_index",
    "source_asset_url",
    "source_sha256",
    "ocr_engine",
    "ocr_engine_version",
    "ocr_language",
    "ocr_psm",
    "ocr_text_raw",
    "ocr_sha256",
    "search_text",
    "search_text_sha256",
    "ocr_char_count",
    "ocr_word_count",
    "generated_at",
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_and_validate(path: Path) -> list[dict]:
    rows: list[dict] = []
    page_ids: set[str] = set()
    page_keys: set[tuple[str, int]] = set()
    with path.open(encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSON line {line_number}: {exc}") from exc
            missing = REQUIRED - set(row)
            if missing:
                raise SystemExit(f"line {line_number} missing fields: {sorted(missing)}")
            if row["schema_version"] != "LTMD_PAGE_OCR_0.1":
                raise SystemExit(f"line {line_number}: unexpected schema_version")
            if row["page_id"] in page_ids:
                raise SystemExit(f"duplicate page_id: {row['page_id']}")
            key = (row["viewer_key"], int(row["page_index"]))
            if key in page_keys:
                raise SystemExit(f"duplicate viewer/page: {key}")
            page_ids.add(row["page_id"])
            page_keys.add(key)
            for field in ("source_sha256", "ocr_sha256", "search_text_sha256"):
                if not SHA256_RE.fullmatch(str(row[field])):
                    raise SystemExit(f"{row['page_id']}: invalid {field}")
            if digest(row["ocr_text_raw"]) != row["ocr_sha256"]:
                raise SystemExit(f"{row['page_id']}: OCR hash mismatch")
            if digest(row["search_text"]) != row["search_text_sha256"]:
                raise SystemExit(f"{row['page_id']}: search-text hash mismatch")
            if len(row["ocr_text_raw"]) != int(row["ocr_char_count"]):
                raise SystemExit(f"{row['page_id']}: character count mismatch")
            if len(re.findall(r"\S+", row["ocr_text_raw"])) != int(row["ocr_word_count"]):
                raise SystemExit(f"{row['page_id']}: word count mismatch")
            rows.append(row)
    if not rows:
        raise SystemExit("OCR JSONL is empty")
    return rows


def validate_db(path: Path, rows: list[dict]) -> dict:
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        pages = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        fts = conn.execute("SELECT COUNT(*) FROM pages_fts").fetchone()[0]
        duplicates = conn.execute(
            "SELECT COUNT(*) FROM (SELECT page_id FROM pages GROUP BY page_id HAVING COUNT(*)>1)"
        ).fetchone()[0]
        db_hashes = {
            page_id: (ocr_sha, search_sha)
            for page_id, ocr_sha, search_sha in conn.execute(
                "SELECT page_id,ocr_sha256,search_text_sha256 FROM pages"
            )
        }
    finally:
        conn.close()

    expected = {
        row["page_id"]: (row["ocr_sha256"], row["search_text_sha256"]) for row in rows
    }
    if integrity != "ok" or pages != len(rows) or fts != pages or duplicates:
        raise SystemExit(
            f"SQLite validation failure: integrity={integrity}, pages={pages}, "
            f"fts={fts}, duplicates={duplicates}"
        )
    if db_hashes != expected:
        raise SystemExit("SQLite page/hash inventory differs from OCR JSONL")
    return {"sqlite_integrity": integrity, "sqlite_pages": pages, "fts_rows": fts}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--db", type=Path)
    args = parser.parse_args()

    rows = load_and_validate(args.input)
    summary = {
        "status": "ok",
        "page_records": len(rows),
        "canonical_viewers": len({row["viewer_key"] for row in rows}),
        "waves": sorted({row["wave"] for row in rows}),
    }
    if args.db is not None:
        summary.update(validate_db(args.db, rows))
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
