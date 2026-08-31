#!/usr/bin/env python3
"""Build private page-bounded LTMD-U1 bigram/trigram statistics from lexical positions.

Version: LTMD_U1_NGRAMS_BUILDER_0.1

This builder never reads OCR or FTS5. It consumes LTMD_U1_LEXICAL_POSITIONS_0.1,
uses the already materialized token positions, and keeps all sequence values private.
Publication eligibility is computed from preregistered suppression thresholds; eligibility
is not itself a claim of semantic validity or permission to redistribute source text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import tempfile
from pathlib import Path

import numpy as np

BUILDER_VERSION = "LTMD_U1_NGRAMS_BUILDER_0.1"
ARTIFACT_VERSION = "LTMD_U1_NGRAMS_0.1"
SOURCE_VERSION = "LTMD_U1_LEXICAL_POSITIONS_0.1"
TERM_BITS = 18
TERM_MASK = (1 << TERM_BITS) - 1
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
RECORD_DTYPE = np.dtype([("key", "<u8"), ("page", "<u4")])

PRIVATE_RETENTION = {
    "bigram_min_occurrences": 2,
    "bigram_min_pages": 2,
    "trigram_min_occurrences": 3,
    "trigram_min_pages": 2,
}
PUBLIC_SUPPRESSION = {
    "bigram_min_occurrences": 50,
    "bigram_min_pages": 20,
    "bigram_min_objects": 10,
    "trigram_min_occurrences": 75,
    "trigram_min_pages": 25,
    "trigram_min_objects": 10,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_source(path: Path, expected_sha256: str | None) -> str | None:
    if not path.is_file():
        raise RuntimeError("lexical-position artifact is unavailable")
    if expected_sha256 is None:
        return None
    expected = expected_sha256.strip().lower()
    if not SHA256_RE.fullmatch(expected):
        raise RuntimeError("expected lexical-position SHA-256 is invalid")
    actual = sha256_file(path)
    if actual != expected:
        raise RuntimeError("lexical-position SHA-256 mismatch")
    return actual


def _decode_json(raw: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def load_meta(c: sqlite3.Connection) -> dict:
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required = {"meta", "pages", "terms", "token_positions", "term_stats"}
    missing = required - tables
    if missing:
        raise RuntimeError("not an LTMD lexical-position artifact; missing: " + ", ".join(sorted(missing)))
    meta = {k: _decode_json(v) for k, v in c.execute("SELECT key,value FROM meta")}
    version = meta.get("artifact_version", meta.get("version"))
    if version != SOURCE_VERSION:
        raise RuntimeError("unsupported lexical-position artifact version")
    max_term = int(c.execute("SELECT COALESCE(MAX(term_id),0) FROM terms").fetchone()[0])
    if max_term > TERM_MASK:
        raise RuntimeError("term IDs exceed the 18-bit LTMD n-gram encoding")
    return meta


def _remove_sqlite_family(path: Path) -> None:
    for p in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
        if p.exists():
            p.unlink()


def _page_metadata(c: sqlite3.Connection):
    max_page = int(c.execute("SELECT COALESCE(MAX(page_rowid),0) FROM pages").fetchone()[0])
    objects = np.zeros(max_page + 1, dtype=np.uint16)
    gen_mask = np.zeros(max_page + 1, dtype=np.uint16)
    grade_mask = np.zeros(max_page + 1, dtype=np.uint16)
    wave_mask = np.zeros(max_page + 1, dtype=np.uint16)
    generations = [r[0] for r in c.execute("SELECT DISTINCT generation FROM pages WHERE generation IS NOT NULL ORDER BY generation")]
    grades = [r[0] for r in c.execute("SELECT DISTINCT grade_code FROM pages WHERE grade_code IS NOT NULL ORDER BY grade_code")]
    waves = [r[0] for r in c.execute("SELECT DISTINCT wave FROM pages WHERE wave IS NOT NULL ORDER BY wave")]
    if max(len(generations), len(grades), len(waves)) > 16:
        raise RuntimeError("dimension cardinality exceeds compact LTMD bitmask capacity")
    gm = {v: i for i, v in enumerate(generations)}
    grm = {v: i for i, v in enumerate(grades)}
    wm = {v: i for i, v in enumerate(waves)}
    ordered_objects = []
    for page, obj, gen, grade, wave in c.execute(
        "SELECT page_rowid,object_id,generation,grade_code,wave FROM pages ORDER BY page_rowid"
    ):
        objects[page] = obj
        ordered_objects.append(obj)
        if gen is not None:
            gen_mask[page] = np.uint16(1 << gm[gen])
        if grade is not None:
            grade_mask[page] = np.uint16(1 << grm[grade])
        if wave is not None:
            wave_mask[page] = np.uint16(1 << wm[wave])
    if any(a > b for a, b in zip(ordered_objects, ordered_objects[1:])):
        raise RuntimeError("lexical pages do not preserve object-contiguous page order")
    return objects, gen_mask, grade_mask, wave_mask


def _append_records(path: Path, keys: np.ndarray, page: int) -> None:
    if keys.size == 0:
        return
    arr = np.empty(keys.size, dtype=RECORD_DTYPE)
    arr["key"] = keys
    arr["page"] = page
    with path.open("ab") as f:
        arr.tofile(f)


def _materialize_raw(c: sqlite3.Connection, bigram_path: Path, trigram_path: Path) -> tuple[int, int, int]:
    bigram_path.write_bytes(b"")
    trigram_path.write_bytes(b"")
    bigram_instances = 0
    trigram_instances = 0
    nonempty_pages = 0

    def flush(page: int, terms: list[int], offsets: list[int]):
        nonlocal bigram_instances, trigram_instances, nonempty_pages
        if not terms:
            return
        nonempty_pages += 1
        a = np.asarray(terms, dtype=np.uint64)
        off = np.asarray(offsets, dtype=np.int64)
        if a.size >= 2:
            valid = off[1:] == off[:-1] + 1
            keys = ((a[:-1] << np.uint64(TERM_BITS)) | a[1:])[valid]
            _append_records(bigram_path, keys, page)
            bigram_instances += int(keys.size)
        if a.size >= 3:
            valid = (off[1:-1] == off[:-2] + 1) & (off[2:] == off[1:-1] + 1)
            keys = (
                (a[:-2] << np.uint64(TERM_BITS * 2))
                | (a[1:-1] << np.uint64(TERM_BITS))
                | a[2:]
            )[valid]
            _append_records(trigram_path, keys, page)
            trigram_instances += int(keys.size)

    last_page = None
    terms: list[int] = []
    offsets: list[int] = []
    for page, term, offset in c.execute(
        "SELECT page_rowid,term_id,token_offset FROM token_positions ORDER BY page_rowid,token_offset"
    ):
        if last_page is None:
            last_page = page
        if page != last_page:
            flush(last_page, terms, offsets)
            terms, offsets, last_page = [], [], page
        terms.append(term)
        offsets.append(offset)
    if last_page is not None:
        flush(last_page, terms, offsets)
    return bigram_instances, trigram_instances, nonempty_pages


def _aggregate(
    raw_path: Path,
    kind: str,
    objects: np.ndarray,
    gen_mask: np.ndarray,
    grade_mask: np.ndarray,
    wave_mask: np.ndarray,
):
    n = raw_path.stat().st_size // RECORD_DTYPE.itemsize
    if n == 0:
        empty = np.array([], dtype=np.uint64)
        return empty, *(np.array([], dtype=np.uint32) for _ in range(3)), *(np.array([], dtype=np.uint8) for _ in range(4)), 0, 0
    arr = np.memmap(raw_path, dtype=RECORD_DTYPE, mode="r+", shape=(n,))
    arr.sort(order=["key", "page"])
    arr.flush()
    keys, pages = arr["key"], arr["page"]

    key_start = np.empty(n, dtype=bool)
    key_start[0] = True
    key_start[1:] = keys[1:] != keys[:-1]
    starts = np.flatnonzero(key_start)
    ends = np.empty_like(starts)
    ends[:-1], ends[-1] = starts[1:], n
    occurrence_count = (ends - starts).astype(np.uint32)
    group_keys = np.asarray(keys[starts], dtype=np.uint64)

    key_page_start = key_start.copy()
    key_page_start[1:] |= pages[1:] != pages[:-1]
    unique_keys = np.asarray(keys[key_page_start], dtype=np.uint64)
    unique_pages = np.asarray(pages[key_page_start], dtype=np.uint32)
    unique_group_start = np.empty(unique_keys.size, dtype=bool)
    unique_group_start[0] = True
    unique_group_start[1:] = unique_keys[1:] != unique_keys[:-1]
    ustarts = np.flatnonzero(unique_group_start)
    uends = np.empty_like(ustarts)
    uends[:-1], uends[-1] = ustarts[1:], unique_keys.size
    page_count = (uends - ustarts).astype(np.uint32)
    if not np.array_equal(group_keys, unique_keys[ustarts]):
        raise RuntimeError("n-gram key/page aggregation mismatch")

    obj_values = objects[unique_pages]
    object_change = unique_group_start.copy()
    object_change[1:] |= obj_values[1:] != obj_values[:-1]
    object_count = np.add.reduceat(object_change.astype(np.uint16), ustarts).astype(np.uint32)
    generation_count = np.bitwise_count(np.bitwise_or.reduceat(gen_mask[unique_pages], ustarts)).astype(np.uint8)
    grade_count = np.bitwise_count(np.bitwise_or.reduceat(grade_mask[unique_pages], ustarts)).astype(np.uint8)
    wave_count = np.bitwise_count(np.bitwise_or.reduceat(wave_mask[unique_pages], ustarts)).astype(np.uint8)

    if kind == "bigram":
        keep = (occurrence_count >= PRIVATE_RETENTION["bigram_min_occurrences"]) & (
            page_count >= PRIVATE_RETENTION["bigram_min_pages"]
        )
        public = keep & (occurrence_count >= PUBLIC_SUPPRESSION["bigram_min_occurrences"]) & (
            page_count >= PUBLIC_SUPPRESSION["bigram_min_pages"]
        ) & (object_count >= PUBLIC_SUPPRESSION["bigram_min_objects"])
    else:
        keep = (occurrence_count >= PRIVATE_RETENTION["trigram_min_occurrences"]) & (
            page_count >= PRIVATE_RETENTION["trigram_min_pages"]
        )
        public = keep & (occurrence_count >= PUBLIC_SUPPRESSION["trigram_min_occurrences"]) & (
            page_count >= PUBLIC_SUPPRESSION["trigram_min_pages"]
        ) & (object_count >= PUBLIC_SUPPRESSION["trigram_min_objects"])

    result = (
        group_keys[keep], occurrence_count[keep], page_count[keep], object_count[keep],
        generation_count[keep], grade_count[keep], wave_count[keep], public[keep].astype(np.uint8),
        int(group_keys.size), int(unique_keys.size),
    )
    del arr
    return result


def _insert_rows(c: sqlite3.Connection, table: str, aggregated) -> None:
    keys, occ, pages, objects, generations, grades, waves, public, _, _ = aggregated
    rows = []
    if table == "bigrams":
        for key, a, b, d, e, f, g, h in zip(keys, occ, pages, objects, generations, grades, waves, public):
            k = int(key)
            rows.append((k >> TERM_BITS, k & TERM_MASK, int(a), int(b), int(d), int(e), int(f), int(g), int(h)))
            if len(rows) >= 50_000:
                c.executemany("INSERT INTO bigrams VALUES(?,?,?,?,?,?,?,?,?)", rows)
                c.commit(); rows = []
    else:
        for key, a, b, d, e, f, g, h in zip(keys, occ, pages, objects, generations, grades, waves, public):
            k = int(key)
            rows.append((k >> (TERM_BITS * 2), (k >> TERM_BITS) & TERM_MASK, k & TERM_MASK, int(a), int(b), int(d), int(e), int(f), int(g), int(h)))
            if len(rows) >= 50_000:
                c.executemany("INSERT INTO trigrams VALUES(?,?,?,?,?,?,?,?,?,?)", rows)
                c.commit(); rows = []
    if rows:
        placeholders = "?,?,?,?,?,?,?,?,?" if table == "bigrams" else "?,?,?,?,?,?,?,?,?,?"
        c.executemany(f"INSERT INTO {table} VALUES({placeholders})", rows)
        c.commit()


def build(source_path: Path, output_path: Path, *, overwrite: bool = False) -> dict:
    source_path = source_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    if output_path.exists() and not overwrite:
        raise RuntimeError("output already exists; pass --overwrite to replace it")
    if overwrite:
        _remove_sqlite_family(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True, timeout=120)
    try:
        source_meta = load_meta(source)
        objects, gen_mask, grade_mask, wave_mask = _page_metadata(source)
        with tempfile.TemporaryDirectory(prefix="ltmd-ngrams-") as tmp:
            tmpdir = Path(tmp)
            braw, traw = tmpdir / "bigrams.bin", tmpdir / "trigrams.bin"
            raw_bigram_instances, raw_trigram_instances, nonempty_pages = _materialize_raw(source, braw, traw)
            bagg = _aggregate(braw, "bigram", objects, gen_mask, grade_mask, wave_mask)
            tagg = _aggregate(traw, "trigram", objects, gen_mask, grade_mask, wave_mask)

            out = sqlite3.connect(output_path, timeout=120)
            try:
                out.executescript("""
                PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA cache_size=-200000;
                CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID;
                CREATE TABLE bigrams(
                    t1 INTEGER NOT NULL,t2 INTEGER NOT NULL,occurrence_count INTEGER NOT NULL,
                    page_count INTEGER NOT NULL,object_count INTEGER NOT NULL,generation_count INTEGER NOT NULL,
                    grade_count INTEGER NOT NULL,wave_count INTEGER NOT NULL,public_eligible INTEGER NOT NULL,
                    PRIMARY KEY(t1,t2)) WITHOUT ROWID;
                CREATE TABLE trigrams(
                    t1 INTEGER NOT NULL,t2 INTEGER NOT NULL,t3 INTEGER NOT NULL,occurrence_count INTEGER NOT NULL,
                    page_count INTEGER NOT NULL,object_count INTEGER NOT NULL,generation_count INTEGER NOT NULL,
                    grade_count INTEGER NOT NULL,wave_count INTEGER NOT NULL,public_eligible INTEGER NOT NULL,
                    PRIMARY KEY(t1,t2,t3)) WITHOUT ROWID;
                CREATE INDEX idx_bigrams_public ON bigrams(public_eligible,occurrence_count DESC);
                CREATE INDEX idx_trigrams_public ON trigrams(public_eligible,occurrence_count DESC);
                """)
                _insert_rows(out, "bigrams", bagg)
                _insert_rows(out, "trigrams", tagg)
                counts = {
                    "nonempty_tokenized_pages": nonempty_pages,
                    "raw_bigram_instances": raw_bigram_instances,
                    "raw_trigram_instances": raw_trigram_instances,
                    "unique_bigrams_before_private_floor": bagg[-2],
                    "unique_trigrams_before_private_floor": tagg[-2],
                    "unique_bigram_page_relations": bagg[-1],
                    "unique_trigram_page_relations": tagg[-1],
                    "bigram_rows": int(len(bagg[0])),
                    "trigram_rows": int(len(tagg[0])),
                    "bigram_public_eligible_rows": int(bagg[7].sum()),
                    "trigram_public_eligible_rows": int(tagg[7].sum()),
                }
                metadata = {
                    "builder_version": BUILDER_VERSION,
                    "artifact_version": ARTIFACT_VERSION,
                    "source_lexical_version": SOURCE_VERSION,
                    "page_bounded": True,
                    "thresholds_preregistered_before_result_inspection": True,
                    "private_retention": PRIVATE_RETENTION,
                    "public_suppression": PUBLIC_SUPPRESSION,
                    **counts,
                    "private": True,
                    "text_verified": False,
                    "semantic_ready": False,
                    "default_result_state": "exploratory_signal",
                    "frequency_is_semantic_claim": False,
                }
                for k, v in metadata.items():
                    out.execute("INSERT INTO meta VALUES(?,?)", (k, json.dumps(v, ensure_ascii=False, sort_keys=True)))
                out.commit()
                if out.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise RuntimeError("n-gram artifact quick_check failed")
                out.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                out.execute("PRAGMA journal_mode=DELETE")
                out.commit()
            finally:
                out.close()
    finally:
        source.close()

    return {
        "builder_version": BUILDER_VERSION,
        "artifact_version": ARTIFACT_VERSION,
        "source_lexical_version": SOURCE_VERSION,
        "counts": counts,
        "method": {
            "page_bounded": True,
            "thresholds_preregistered_before_result_inspection": True,
            "private_retention": PRIVATE_RETENTION,
            "public_suppression": PUBLIC_SUPPRESSION,
        },
        "private_artifact": {"bytes": output_path.stat().st_size, "sha256": sha256_file(output_path), "publish": False},
        "privacy": {
            "term_values_emitted_publicly": False,
            "sequence_values_emitted_publicly": False,
            "page_identifiers_emitted_publicly": False,
            "ocr_text_emitted_publicly": False,
        },
        "scientific_state": {
            "text_verified": False,
            "semantic_ready": False,
            "default_result_state": "exploratory_signal",
            "frequency_is_semantic_claim": False,
        },
        "source_meta_cardinality": {
            "unique_pages": source_meta.get("unique_pages"),
            "unique_objects": source_meta.get("unique_objects", source_meta.get("unique_canonical_objects")),
        },
    }


def run(source_path: Path, output_path: Path, *, expected_source_sha256: str | None = None, overwrite: bool = False) -> dict:
    verified = verify_source(source_path, expected_source_sha256)
    summary = build(source_path, output_path, overwrite=overwrite)
    summary["source_lexical_sha256"] = verified
    return summary


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="Private LTMD_U1_LEXICAL_POSITIONS_0.1 SQLite")
    p.add_argument("--output", required=True, help="Private n-gram SQLite output")
    p.add_argument("--summary", help="Optional public-safe aggregate JSON summary")
    p.add_argument("--expected-source-sha256")
    p.add_argument("--overwrite", action="store_true")
    a = p.parse_args(argv)
    result = run(Path(a.source), Path(a.output), expected_source_sha256=a.expected_source_sha256, overwrite=a.overwrite)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if a.summary:
        Path(a.summary).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
