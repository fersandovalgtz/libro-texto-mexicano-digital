#!/usr/bin/env python3
"""Build the public-safe LTMD-U1 Corpus Analytics Manifest 0.1.

Inputs:
- private LTMD-U1 Universal Index SQLite;
- public LTMD-U1 coverage Markdown;
- public retained-source register CSV.

The output contains aggregate denominators, technical coverage and OCR-engine
quality summaries only. It never emits OCR/search text, page IDs, book keys,
source URLs, page hashes or private filesystem paths.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_CORPUS_ANALYTICS_MANIFEST_0.1"
INDEX_VERSION = "LTMD_U1_UNIVERSAL_INDEX_0.1"
EXPECTED_PAGES = 86549
EXPECTED_OBJECTS = 492


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_coverage(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    version_m = re.search(r"Versión:\s*`([^`]+)`", text)
    universe_m = re.search(r"Universo U1:\s*\*\*(\d+)/(\d+)\*\*", text)
    effective_m = re.search(r"Cobertura técnica efectiva[^:]*:\s*\*\*(\d+)/(\d+)", text)
    objects_m = re.search(r"Objetos canónicos[^:]*:\s*\*\*(\d+)/(\d+)", text)
    semantic_m = re.search(r"Cobertura semántica humana[^:]*:\s*\*\*(\d+)/(\d+)", text)
    required = [version_m, universe_m, effective_m, objects_m, semantic_m]
    if not all(required):
        raise RuntimeError("coverage Markdown does not match expected LTMD-U1 structure")

    rows = []
    row_re = re.compile(
        r"^\|\s*(W\d+)\s*\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|$"
    )
    for line in text.splitlines():
        m = row_re.match(line)
        if m:
            rows.append({
                "wave": m.group(1),
                "operational_domain": m.group(2),
                "planned_identities": int(m.group(3)),
                "effective_technical_identities": int(m.group(4)),
                "canonical_processing_objects": int(m.group(5)),
                "residual_identities": int(m.group(6)),
                "technical_status": m.group(7),
            })
    if len(rows) != 11:
        raise RuntimeError(f"coverage wave table must contain 11 rows; got {len(rows)}")

    return {
        "version": version_m.group(1),
        "historical_identities": int(universe_m.group(1)),
        "universe_denominator": int(universe_m.group(2)),
        "effective_technical_identities": int(effective_m.group(1)),
        "canonical_processing_objects": int(objects_m.group(1)),
        "human_semantic_validated_identities": int(semantic_m.group(1)),
        "by_wave": rows,
    }


def parse_retained(path: Path) -> dict:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError("retained-source register is empty")
    versions = {row["register_version"] for row in rows}
    if len(versions) != 1:
        raise RuntimeError("retained-source register has multiple versions")
    status_counts = Counter(row["status"] for row in rows)
    by_wave = {}
    for row in rows:
        slot = by_wave.setdefault(row["wave"], Counter())
        slot[row["status"]] += 1
    return {
        "version": versions.pop(),
        "rows": len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "by_wave": {
            wave: dict(sorted(counts.items()))
            for wave, counts in sorted(by_wave.items(), key=lambda item: int(item[0][1:]))
        },
    }


def validate_index(connection: sqlite3.Connection) -> dict:
    meta = {}
    for key, raw in connection.execute("SELECT key, value FROM index_meta"):
        try:
            meta[key] = json.loads(raw)
        except json.JSONDecodeError:
            meta[key] = raw
    if meta.get("builder_version") != INDEX_VERSION:
        raise RuntimeError("unsupported Universal Index version")
    pages = connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    objects = connection.execute(
        "SELECT COUNT(DISTINCT canonical_viewer_key) FROM pages"
    ).fetchone()[0]
    fts = connection.execute("SELECT COUNT(*) FROM pages_fts").fetchone()[0]
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    if pages != fts or integrity != "ok":
        raise RuntimeError("Universal Index integrity/cardinality gate failed")
    return {"pages": int(pages), "canonical_objects": int(objects), "fts_rows": int(fts), "integrity": integrity}


def dimension(connection: sqlite3.Connection, column: str, *, wave: bool = False) -> list[dict]:
    order = f"CAST(SUBSTR({column},2) AS INTEGER)" if wave else column
    rows = connection.execute(
        f"""SELECT {column}, COUNT(*), COUNT(DISTINCT canonical_viewer_key)
            FROM pages GROUP BY {column} ORDER BY {order}"""
    ).fetchall()
    return [
        {"value": str(value), "pages": int(pages), "canonical_objects": int(objects)}
        for value, pages, objects in rows
    ]


def denominator_cells(connection: sqlite3.Connection) -> list[dict]:
    rows = connection.execute(
        """SELECT catalog_generation, grade_code, wave,
                  COUNT(*), COUNT(DISTINCT canonical_viewer_key)
           FROM pages
           GROUP BY catalog_generation, grade_code, wave
           ORDER BY catalog_generation, grade_code, CAST(SUBSTR(wave,2) AS INTEGER)"""
    ).fetchall()
    return [
        {
            "generation": int(generation),
            "grade_code": int(grade),
            "wave": wave,
            "pages": int(pages),
            "canonical_objects": int(objects),
        }
        for generation, grade, wave, pages, objects in rows
    ]


def percentile(sorted_values: list[float], p: float) -> float | None:
    if not sorted_values:
        return None
    pos = (len(sorted_values) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = pos - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def ocr_quality(connection: sqlite3.Connection, total_pages: int) -> dict:
    values = [
        float(row[0])
        for row in connection.execute(
            "SELECT ocr_confidence_mean FROM pages WHERE ocr_confidence_mean IS NOT NULL ORDER BY ocr_confidence_mean"
        )
    ]
    mean = sum(values) / len(values) if values else None
    return {
        "metric": "page_level_ocr_engine_confidence_mean",
        "available_pages": len(values),
        "unavailable_pages": total_pages - len(values),
        "mean": mean,
        "min": values[0] if values else None,
        "p10": percentile(values, 0.10),
        "p25": percentile(values, 0.25),
        "median": percentile(values, 0.50),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.90),
        "max": values[-1] if values else None,
        "interpretation": "engine_confidence_only_not_CER_WER_or_human_text_verification",
    }


def build(index_path: Path, coverage_path: Path, retained_path: Path, output_path: Path,
          expected_index_sha256: str | None = None,
          expected_pages: int = EXPECTED_PAGES,
          expected_objects: int = EXPECTED_OBJECTS) -> dict:
    actual_sha = sha256_file(index_path)
    if expected_index_sha256 and actual_sha != expected_index_sha256.lower():
        raise RuntimeError("Universal Index SHA-256 mismatch")

    coverage = parse_coverage(coverage_path)
    retained = parse_retained(retained_path)
    connection = sqlite3.connect(f"file:{index_path.resolve()}?mode=ro", uri=True)
    try:
        index_state = validate_index(connection)
        if index_state["pages"] != expected_pages:
            raise RuntimeError(f"page cardinality mismatch: {index_state['pages']} != {expected_pages}")
        if index_state["canonical_objects"] != expected_objects:
            raise RuntimeError(
                f"canonical object cardinality mismatch: {index_state['canonical_objects']} != {expected_objects}"
            )
        if coverage["historical_identities"] != coverage["universe_denominator"]:
            raise RuntimeError("coverage universe numerator/denominator mismatch")
        residual = coverage["historical_identities"] - coverage["effective_technical_identities"]
        wave_planned = sum(row["planned_identities"] for row in coverage["by_wave"])
        wave_effective = sum(row["effective_technical_identities"] for row in coverage["by_wave"])
        wave_objects = sum(row["canonical_processing_objects"] for row in coverage["by_wave"])
        wave_residual = sum(row["residual_identities"] for row in coverage["by_wave"])
        if wave_planned != coverage["historical_identities"]:
            raise RuntimeError("coverage wave planned identities do not reconcile with universe")
        if wave_effective != coverage["effective_technical_identities"]:
            raise RuntimeError("coverage wave effective identities do not reconcile with total")
        if wave_objects != coverage["canonical_processing_objects"]:
            raise RuntimeError("coverage wave canonical objects do not reconcile with total")
        if wave_residual != residual:
            raise RuntimeError("coverage wave residual identities do not reconcile with total")
        if residual != retained["rows"]:
            raise RuntimeError("coverage residual does not equal retained-source register rows")
        if coverage["canonical_processing_objects"] != index_state["canonical_objects"]:
            raise RuntimeError("coverage canonical objects do not match Universal Index")
        if retained["status_counts"].get("active_retention", 0) + retained["status_counts"].get("final_exception", 0) != residual:
            raise RuntimeError("retention lifecycle does not reconcile with residual")

        residual_by_wave = {row["wave"]: row["residual_identities"] for row in coverage["by_wave"] if row["residual_identities"]}
        retention_rows_by_wave = {
            wave: sum(status_counts.values())
            for wave, status_counts in retained["by_wave"].items()
        }
        if residual_by_wave != retention_rows_by_wave:
            raise RuntimeError("retention rows by wave do not reconcile with coverage residual distribution")

        manifest = {
            "manifest_version": VERSION,
            "universe": {
                "historical_identities": coverage["historical_identities"],
                "effective_technical_identities": coverage["effective_technical_identities"],
                "canonical_processing_objects": coverage["canonical_processing_objects"],
                "indexed_pages": index_state["pages"],
                "fts_rows": index_state["fts_rows"],
                "residual_identities": residual,
                "active_retentions": retained["status_counts"].get("active_retention", 0),
                "final_exceptions": retained["status_counts"].get("final_exception", 0),
                "human_semantic_validated_identities": coverage["human_semantic_validated_identities"],
            },
            "index": {
                "version": INDEX_VERSION,
                "sha256": actual_sha,
                "sqlite_integrity_check": index_state["integrity"],
                "tokenizer": "unicode61 remove_diacritics 2",
                "private": True,
                "publish_index_file": False,
            },
            "dimensions": {
                "generation": dimension(connection, "catalog_generation"),
                "grade_code": dimension(connection, "grade_code"),
                "wave": dimension(connection, "wave", wave=True),
                "nonempty_generation_grade_wave_cells": denominator_cells(connection),
            },
            "technical_coverage": {
                "coverage_version": coverage["version"],
                "retained_register_version": retained["version"],
                "by_wave": coverage["by_wave"],
                "retention_status_counts": retained["status_counts"],
                "retention_by_wave": retained["by_wave"],
            },
            "ocr_quality": ocr_quality(connection, index_state["pages"]),
            "denominator_policy": {
                "filtered_denominators_come_from_same_universal_index": True,
                "silent_imputation": False,
                "wave_is_operational_not_curricular_ontology": True,
                "zero_hits_demonstrate_absence": False,
            },
            "scientific_state": {
                "ocr_available": True,
                "text_verified": False,
                "corpus_ready_for_computational_retrieval": True,
                "semantic_ready": False,
                "default_result_state": "exploratory_signal",
                "human_validation_deferred_not_cancelled": True,
            },
            "privacy": {
                "ocr_or_search_text_emitted": False,
                "snippets_emitted": False,
                "page_ids_emitted": False,
                "book_identifiers_emitted": False,
                "source_urls_emitted": False,
                "page_or_ocr_hashes_emitted": False,
                "private_storage_paths_emitted": False,
                "aggregate_only_public_surface": True,
            },
            "inputs": {
                "index_sha256": actual_sha,
                "coverage_source": "data/catalog/ltmd_u1_coverage.md",
                "retained_source_register": "data/catalog/ltmd_u1_retained_source_register.csv",
                "private_index_path_emitted": False,
            },
        }
    finally:
        connection.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_args(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--index", required=True)
    p.add_argument("--coverage", default="data/catalog/ltmd_u1_coverage.md")
    p.add_argument("--retained-register", default="data/catalog/ltmd_u1_retained_source_register.csv")
    p.add_argument("--output", required=True)
    p.add_argument("--expected-index-sha256")
    p.add_argument("--expected-pages", type=int, default=EXPECTED_PAGES)
    p.add_argument("--expected-objects", type=int, default=EXPECTED_OBJECTS)
    return p.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    manifest = build(
        Path(a.index), Path(a.coverage), Path(a.retained_register), Path(a.output),
        expected_index_sha256=a.expected_index_sha256,
        expected_pages=a.expected_pages,
        expected_objects=a.expected_objects,
    )
    print(json.dumps({
        "manifest_version": manifest["manifest_version"],
        "indexed_pages": manifest["universe"]["indexed_pages"],
        "canonical_processing_objects": manifest["universe"]["canonical_processing_objects"],
        "denominator_cells": len(manifest["dimensions"]["nonempty_generation_grade_wave_cells"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
