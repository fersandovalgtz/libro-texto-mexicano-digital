#!/usr/bin/env python3
"""Build private LTMD-U1 windowed co-occurrence statistics from lexical positions.

Version: LTMD_U1_COOCCURRENCES_BUILDER_0.1

Pairs are unordered distinct terms, bounded to the same page, and counted once per forward
positional pair within a five-token window. The builder consumes lexical positions only: it
never reads OCR or FTS5. Co-occurrence is an exploratory computational signal, not a semantic
relation claim.
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

BUILDER_VERSION = "LTMD_U1_COOCCURRENCES_BUILDER_0.1"
ARTIFACT_VERSION = "LTMD_U1_COOCCURRENCES_0.1"
SOURCE_VERSION = "LTMD_U1_LEXICAL_POSITIONS_0.1"
TERM_BITS = 18
TERM_MASK = (1 << TERM_BITS) - 1
BUCKETS = 64
WINDOW_MAX_TOKENS = 5
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
RECORD_DTYPE = np.dtype([("key", "<u8"), ("page", "<u4")])
PRIVATE_RETENTION = {"min_occurrences": 3, "min_pages": 2}
PUBLIC_SUPPRESSION = {
    "min_occurrences": 75,
    "min_pages": 25,
    "min_objects": 10,
    "each_term_min_pages": 20,
    "each_term_min_objects": 10,
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
        raise RuntimeError("term IDs exceed the 18-bit LTMD co-occurrence encoding")
    return meta


def _remove_sqlite_family(path: Path) -> None:
    for p in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
        if p.exists():
            p.unlink()


def _metadata_arrays(c: sqlite3.Connection):
    max_page = int(c.execute("SELECT COALESCE(MAX(page_rowid),0) FROM pages").fetchone()[0])
    max_term = int(c.execute("SELECT COALESCE(MAX(term_id),0) FROM terms").fetchone()[0])
    objects = np.zeros(max_page + 1, dtype=np.uint16)
    gen_mask = np.zeros(max_page + 1, dtype=np.uint16)
    grade_mask = np.zeros(max_page + 1, dtype=np.uint16)
    wave_mask = np.zeros(max_page + 1, dtype=np.uint16)
    term_pages = np.zeros(max_term + 1, dtype=np.uint32)
    term_objects = np.zeros(max_term + 1, dtype=np.uint16)
    generations = [r[0] for r in c.execute("SELECT DISTINCT generation FROM pages WHERE generation IS NOT NULL ORDER BY generation")]
    grades = [r[0] for r in c.execute("SELECT DISTINCT grade_code FROM pages WHERE grade_code IS NOT NULL ORDER BY grade_code")]
    waves = [r[0] for r in c.execute("SELECT DISTINCT wave FROM pages WHERE wave IS NOT NULL ORDER BY wave")]
    if max(len(generations), len(grades), len(waves)) > 16:
        raise RuntimeError("dimension cardinality exceeds compact LTMD bitmask capacity")
    gm, grm, wm = ({v: i for i, v in enumerate(x)} for x in (generations, grades, waves))
    ordered_objects = []
    for page, obj, gen, grade, wave in c.execute(
        "SELECT page_rowid,object_id,generation,grade_code,wave FROM pages ORDER BY page_rowid"
    ):
        objects[page] = obj
        ordered_objects.append(obj)
        if gen is not None: gen_mask[page] = np.uint16(1 << gm[gen])
        if grade is not None: grade_mask[page] = np.uint16(1 << grm[grade])
        if wave is not None: wave_mask[page] = np.uint16(1 << wm[wave])
    if any(a > b for a, b in zip(ordered_objects, ordered_objects[1:])):
        raise RuntimeError("lexical pages do not preserve object-contiguous page order")
    for term_id, page_count, object_count in c.execute("SELECT term_id,page_count,object_count FROM term_stats"):
        term_pages[term_id] = page_count
        term_objects[term_id] = object_count
    return objects, gen_mask, grade_mask, wave_mask, term_pages, term_objects


def _flush_bucket_chunk(bucket_paths, keys_parts, page_parts):
    if not keys_parts:
        return
    keys = np.concatenate(keys_parts)
    pages = np.concatenate(page_parts)
    bucket_ids = (keys & np.uint64(BUCKETS - 1)).astype(np.uint8)
    order = np.argsort(bucket_ids, kind="stable")
    keys, pages, bucket_ids = keys[order], pages[order], bucket_ids[order]
    boundaries = np.flatnonzero(np.r_[True, bucket_ids[1:] != bucket_ids[:-1], True])
    for start, end in zip(boundaries[:-1], boundaries[1:]):
        bucket = int(bucket_ids[start])
        arr = np.empty(end - start, dtype=RECORD_DTYPE)
        arr["key"], arr["page"] = keys[start:end], pages[start:end]
        with bucket_paths[bucket].open("ab") as f:
            arr.tofile(f)


def _partition(c: sqlite3.Connection, bucket_paths: list[Path]) -> tuple[int, int]:
    for p in bucket_paths:
        p.write_bytes(b"")
    key_parts, page_parts, buffered = [], [], 0
    raw_total, nonempty_pages = 0, 0

    def flush_page(page: int, terms: list[int], offsets: list[int]):
        nonlocal buffered, raw_total, nonempty_pages, key_parts, page_parts
        if not terms:
            return
        nonempty_pages += 1
        a = np.asarray(terms, dtype=np.uint64)
        off = np.asarray(offsets, dtype=np.int64)
        local = []
        for distance in range(1, WINDOW_MAX_TOKENS + 1):
            if a.size <= distance:
                break
            x, y = a[:-distance], a[distance:]
            valid = (off[distance:] - off[:-distance] <= WINDOW_MAX_TOKENS) & (x != y)
            if not np.any(valid):
                continue
            xv, yv = x[valid], y[valid]
            lo, hi = np.minimum(xv, yv), np.maximum(xv, yv)
            local.append((lo << np.uint64(TERM_BITS)) | hi)
        if local:
            keys = np.concatenate(local)
            pages = np.full(keys.size, page, dtype=np.uint32)
            key_parts.append(keys); page_parts.append(pages)
            buffered += int(keys.size); raw_total += int(keys.size)
        if buffered >= 500_000:
            _flush_bucket_chunk(bucket_paths, key_parts, page_parts)
            key_parts, page_parts, buffered = [], [], 0

    last_page = None
    terms: list[int] = []
    offsets: list[int] = []
    for page, term, offset in c.execute(
        "SELECT page_rowid,term_id,token_offset FROM token_positions ORDER BY page_rowid,token_offset"
    ):
        if last_page is None:
            last_page = page
        if page != last_page:
            flush_page(last_page, terms, offsets)
            terms, offsets, last_page = [], [], page
        terms.append(term); offsets.append(offset)
    if last_page is not None:
        flush_page(last_page, terms, offsets)
    _flush_bucket_chunk(bucket_paths, key_parts, page_parts)
    return raw_total, nonempty_pages


def _process_bucket(
    path: Path,
    objects: np.ndarray,
    gen_mask: np.ndarray,
    grade_mask: np.ndarray,
    wave_mask: np.ndarray,
    term_pages: np.ndarray,
    term_objects: np.ndarray,
):
    n = path.stat().st_size // RECORD_DTYPE.itemsize
    if n == 0:
        return [], {"raw_rows": 0, "unique_pairs": 0, "unique_pair_page": 0, "retained": 0, "public": 0}
    arr = np.memmap(path, dtype=RECORD_DTYPE, mode="r+", shape=(n,))
    arr.sort(order=["key", "page"]); arr.flush()
    keys, pages = arr["key"], arr["page"]
    key_start = np.empty(n, dtype=bool); key_start[0] = True; key_start[1:] = keys[1:] != keys[:-1]
    starts = np.flatnonzero(key_start); ends = np.empty_like(starts); ends[:-1], ends[-1] = starts[1:], n
    occurrence_count = (ends - starts).astype(np.uint32); group_keys = np.asarray(keys[starts], dtype=np.uint64)
    kp_start = key_start.copy(); kp_start[1:] |= pages[1:] != pages[:-1]
    unique_keys, unique_pages = np.asarray(keys[kp_start], dtype=np.uint64), np.asarray(pages[kp_start], dtype=np.uint32)
    ug_start = np.empty(unique_keys.size, dtype=bool); ug_start[0] = True; ug_start[1:] = unique_keys[1:] != unique_keys[:-1]
    ustarts = np.flatnonzero(ug_start); uends = np.empty_like(ustarts); uends[:-1], uends[-1] = ustarts[1:], unique_keys.size
    page_count = (uends - ustarts).astype(np.uint32)
    if not np.array_equal(group_keys, unique_keys[ustarts]):
        raise RuntimeError("co-occurrence key/page aggregation mismatch")
    obj_values = objects[unique_pages]
    obj_change = ug_start.copy(); obj_change[1:] |= obj_values[1:] != obj_values[:-1]
    object_count = np.add.reduceat(obj_change.astype(np.uint16), ustarts).astype(np.uint32)
    generation_count = np.bitwise_count(np.bitwise_or.reduceat(gen_mask[unique_pages], ustarts)).astype(np.uint8)
    grade_count = np.bitwise_count(np.bitwise_or.reduceat(grade_mask[unique_pages], ustarts)).astype(np.uint8)
    wave_count = np.bitwise_count(np.bitwise_or.reduceat(wave_mask[unique_pages], ustarts)).astype(np.uint8)
    t1 = (group_keys >> np.uint64(TERM_BITS)).astype(np.uint32)
    t2 = (group_keys & np.uint64(TERM_MASK)).astype(np.uint32)
    keep = (occurrence_count >= PRIVATE_RETENTION["min_occurrences"]) & (page_count >= PRIVATE_RETENTION["min_pages"])
    public = keep & (occurrence_count >= PUBLIC_SUPPRESSION["min_occurrences"]) & (
        page_count >= PUBLIC_SUPPRESSION["min_pages"]
    ) & (object_count >= PUBLIC_SUPPRESSION["min_objects"]) & (
        term_pages[t1] >= PUBLIC_SUPPRESSION["each_term_min_pages"]
    ) & (term_pages[t2] >= PUBLIC_SUPPRESSION["each_term_min_pages"]) & (
        term_objects[t1] >= PUBLIC_SUPPRESSION["each_term_min_objects"]
    ) & (term_objects[t2] >= PUBLIC_SUPPRESSION["each_term_min_objects"])
    rows = [
        (int(t1[i]), int(t2[i]), int(occurrence_count[i]), int(page_count[i]), int(object_count[i]),
         int(generation_count[i]), int(grade_count[i]), int(wave_count[i]), int(public[i]))
        for i in np.flatnonzero(keep)
    ]
    stats = {
        "raw_rows": int(n), "unique_pairs": int(group_keys.size), "unique_pair_page": int(unique_keys.size),
        "retained": int(keep.sum()), "public": int(public.sum()),
    }
    del arr
    return rows, stats


def build(source_path: Path, output_path: Path, *, overwrite: bool = False) -> dict:
    source_path = source_path.expanduser().resolve(); output_path = output_path.expanduser().resolve()
    if output_path.exists() and not overwrite:
        raise RuntimeError("output already exists; pass --overwrite to replace it")
    if overwrite: _remove_sqlite_family(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True, timeout=120)
    try:
        source_meta = load_meta(source)
        objects, gen_mask, grade_mask, wave_mask, term_pages, term_objects = _metadata_arrays(source)
        with tempfile.TemporaryDirectory(prefix="ltmd-cooc-") as tmp:
            bucket_paths = [Path(tmp) / f"bucket-{i:02d}.bin" for i in range(BUCKETS)]
            raw_pair_occurrences, nonempty_pages = _partition(source, bucket_paths)
            out = sqlite3.connect(output_path, timeout=120)
            try:
                out.executescript("""
                PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA cache_size=-200000;
                CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL) WITHOUT ROWID;
                CREATE TABLE cooccurrences(
                    t1 INTEGER NOT NULL,t2 INTEGER NOT NULL,occurrence_count INTEGER NOT NULL,
                    page_count INTEGER NOT NULL,object_count INTEGER NOT NULL,generation_count INTEGER NOT NULL,
                    grade_count INTEGER NOT NULL,wave_count INTEGER NOT NULL,public_eligible INTEGER NOT NULL,
                    PRIMARY KEY(t1,t2)) WITHOUT ROWID;
                CREATE INDEX idx_cooc_public ON cooccurrences(public_eligible,occurrence_count DESC);
                """)
                unique_pairs = unique_pair_page = retained = public = 0
                bucket_stats = []
                for bucket, path in enumerate(bucket_paths):
                    rows, stats = _process_bucket(path, objects, gen_mask, grade_mask, wave_mask, term_pages, term_objects)
                    if rows:
                        out.executemany("INSERT INTO cooccurrences VALUES(?,?,?,?,?,?,?,?,?)", rows)
                        out.commit()
                    unique_pairs += stats["unique_pairs"]
                    unique_pair_page += stats["unique_pair_page"]
                    retained += stats["retained"]
                    public += stats["public"]
                    bucket_stats.append({"bucket": bucket, **stats})
                if int(out.execute("SELECT COUNT(*) FROM cooccurrences").fetchone()[0]) != retained:
                    raise RuntimeError("co-occurrence retained-row reconciliation mismatch")
                if int(out.execute("SELECT COUNT(*) FROM cooccurrences WHERE public_eligible=1").fetchone()[0]) != public:
                    raise RuntimeError("co-occurrence public-row reconciliation mismatch")
                counts = {
                    "nonempty_tokenized_pages": nonempty_pages,
                    "raw_pair_occurrences": raw_pair_occurrences,
                    "unique_pairs_before_private_floor": unique_pairs,
                    "unique_pair_page_relations": unique_pair_page,
                    "cooccurrence_rows": retained,
                    "public_eligible_rows": public,
                }
                metadata = {
                    "builder_version": BUILDER_VERSION,
                    "artifact_version": ARTIFACT_VERSION,
                    "source_lexical_version": SOURCE_VERSION,
                    "window_max_tokens": WINDOW_MAX_TOKENS,
                    "same_page_only": True,
                    "unordered_distinct_terms": True,
                    "thresholds_preregistered_before_result_inspection": True,
                    "private_retention": PRIVATE_RETENTION,
                    "public_suppression": PUBLIC_SUPPRESSION,
                    **counts,
                    "private": True,
                    "text_verified": False,
                    "semantic_ready": False,
                    "default_result_state": "exploratory_signal",
                    "cooccurrence_is_semantic_relation": False,
                }
                for k, v in metadata.items():
                    out.execute("INSERT INTO meta VALUES(?,?)", (k, json.dumps(v, ensure_ascii=False, sort_keys=True)))
                out.commit()
                if out.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise RuntimeError("co-occurrence artifact quick_check failed")
                out.execute("PRAGMA wal_checkpoint(TRUNCATE)"); out.execute("PRAGMA journal_mode=DELETE"); out.commit()
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
            "window_max_tokens": WINDOW_MAX_TOKENS,
            "same_page_only": True,
            "unordered_distinct_terms": True,
            "bucket_count": BUCKETS,
            "thresholds_preregistered_before_result_inspection": True,
            "private_retention": PRIVATE_RETENTION,
            "public_suppression": PUBLIC_SUPPRESSION,
        },
        "private_artifact": {"bytes": output_path.stat().st_size, "sha256": sha256_file(output_path), "publish": False},
        "privacy": {
            "term_values_emitted_publicly": False,
            "pair_values_emitted_publicly": False,
            "page_identifiers_emitted_publicly": False,
            "ocr_text_emitted_publicly": False,
        },
        "scientific_state": {
            "text_verified": False,
            "semantic_ready": False,
            "default_result_state": "exploratory_signal",
            "cooccurrence_is_semantic_relation": False,
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
    p.add_argument("--output", required=True, help="Private co-occurrence SQLite output")
    p.add_argument("--summary", help="Optional public-safe aggregate JSON summary")
    p.add_argument("--expected-source-sha256")
    p.add_argument("--overwrite", action="store_true")
    a = p.parse_args(argv)
    result = run(Path(a.source), Path(a.output), expected_source_sha256=a.expected_source_sha256, overwrite=a.overwrite)
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if a.summary: Path(a.summary).write_text(payload, encoding="utf-8")
    else: print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
