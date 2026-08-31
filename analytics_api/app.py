#!/usr/bin/env python3
"""Read-only HTTP adapter for LTMD Analytics 0.1.

The service exposes aggregate-only corpus-wide search plus the preregistered Indigenous-
language vertical. Private paths, OCR/search text, page identifiers and source material are
never returned. Corpus-wide reuse/similarity context is optional and never creates aliases.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path
from threading import RLock

from flask import Flask, jsonify, request

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.query_indigenous_analytics import (  # noqa: E402
    ALLOWED_GROUP_BY,
    ANALYTICS_VERSION,
    ENGINE_VERSION,
    SOURCE_ANALYSIS_VERSION,
    load_generation_denominators,
    load_ledger,
    query,
    sha256_file,
)
from scripts.query_u1_universal_index import (  # noqa: E402
    ALLOWED_GROUP_BY as CORPUS_ALLOWED_GROUP_BY,
    ENGINE_VERSION as CORPUS_ENGINE_VERSION,
    INDEX_VERSION as CORPUS_INDEX_VERSION,
    SHA256_RE,
    normalize_filters as normalize_corpus_filters,
    query_index as query_corpus_index,
    validate_query_expression as validate_corpus_query_expression,
)
from scripts.runtime_vertical_reuse_context import runtime_context  # noqa: E402

DEFAULT_GENERATION_SUMMARY = REPO_ROOT / "data" / "research" / "ltmd_u1_indigenous_languages_generation_summary_0_2.csv"
MAX_FILTER_VALUES = 20
MAX_FILTER_VALUE_LENGTH = 120
MAX_QUERY_LABEL_LENGTH = 240

app = Flask(__name__)
app.json.ensure_ascii = False

_state_lock = RLock()
_state = {
    "ledger_path": None,
    "ledger_mtime_ns": None,
    "rows": None,
    "ledger_sha256": None,
    "generation_path": None,
    "generation_mtime_ns": None,
    "denominators": None,
    "corpus_index_path": None,
    "corpus_index_mtime_ns": None,
    "corpus_index_sha256": None,
}


def _configured_paths() -> tuple[Path, Path]:
    ledger_value = os.environ.get("LTMD_INDIGENOUS_LEDGER_PATH", "").strip()
    if not ledger_value:
        raise RuntimeError("LTMD Analytics private ledger is not configured")
    ledger_path = Path(ledger_value).expanduser()
    generation_value = os.environ.get("LTMD_GENERATION_SUMMARY_PATH", "").strip()
    generation_path = Path(generation_value).expanduser() if generation_value else DEFAULT_GENERATION_SUMMARY
    return ledger_path, generation_path


def _configured_corpus_index_path() -> Path | None:
    value = os.environ.get("LTMD_UNIVERSAL_INDEX_PATH", "").strip()
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_file():
        raise RuntimeError("LTMD Universal Index is unavailable")
    return path


def _configured_reuse_paths() -> tuple[Path, Path] | None:
    index_path = _configured_corpus_index_path()
    reuse_value = os.environ.get("LTMD_REUSE_SIMILARITY_PATH", "").strip()
    if not reuse_value:
        return None
    if index_path is None:
        raise RuntimeError("LTMD reuse context requires the Universal Index")
    reuse_path = Path(reuse_value).expanduser()
    if not reuse_path.is_file():
        raise RuntimeError("LTMD reuse/similarity artifact is unavailable")
    return index_path, reuse_path


def _reuse_context_resolver():
    configured = _configured_reuse_paths()
    if configured is None:
        return None
    index_path, reuse_path = configured
    return lambda page_ids: runtime_context(index_path, reuse_path, page_ids)


def _load_corpus_index_state() -> tuple[Path | None, str | None]:
    path = _configured_corpus_index_path()
    if path is None:
        return None, None
    mtime = path.stat().st_mtime_ns
    with _state_lock:
        changed = (
            _state["corpus_index_sha256"] is None
            or _state["corpus_index_path"] != path
            or _state["corpus_index_mtime_ns"] != mtime
        )
        if changed:
            _state["corpus_index_sha256"] = sha256_file(path)
            _state["corpus_index_path"] = path
            _state["corpus_index_mtime_ns"] = mtime
        actual = _state["corpus_index_sha256"]

    expected = os.environ.get("LTMD_UNIVERSAL_INDEX_SHA256", "").strip().lower()
    if expected:
        if not SHA256_RE.fullmatch(expected):
            raise RuntimeError("configured Universal Index SHA-256 is invalid")
        if actual != expected:
            raise RuntimeError("Universal Index SHA-256 mismatch")
    return path, actual


def _load_state() -> tuple[list[dict], dict[str, int], str]:
    ledger_path, generation_path = _configured_paths()
    if not ledger_path.is_file():
        raise RuntimeError("LTMD Analytics private ledger is unavailable")
    if not generation_path.is_file():
        raise RuntimeError("LTMD Analytics generation summary is unavailable")

    ledger_mtime = ledger_path.stat().st_mtime_ns
    generation_mtime = generation_path.stat().st_mtime_ns
    with _state_lock:
        ledger_changed = (
            _state["rows"] is None
            or _state["ledger_path"] != ledger_path
            or _state["ledger_mtime_ns"] != ledger_mtime
        )
        if ledger_changed:
            _state["rows"] = load_ledger(ledger_path)
            _state["ledger_sha256"] = sha256_file(ledger_path)
            _state["ledger_path"] = ledger_path
            _state["ledger_mtime_ns"] = ledger_mtime

        generation_changed = (
            _state["denominators"] is None
            or _state["generation_path"] != generation_path
            or _state["generation_mtime_ns"] != generation_mtime
        )
        if generation_changed:
            _state["denominators"] = load_generation_denominators(generation_path)
            _state["generation_path"] = generation_path
            _state["generation_mtime_ns"] = generation_mtime

        return _state["rows"], _state["denominators"], _state["ledger_sha256"]


def _clean_values(name: str) -> list[str] | None:
    values = [value.strip() for value in request.args.getlist(name) if value.strip()]
    if not values:
        return None
    if len(values) > MAX_FILTER_VALUES:
        raise ValueError(f"too many values for {name}; maximum is {MAX_FILTER_VALUES}")
    if any(len(value) > MAX_FILTER_VALUE_LENGTH for value in values):
        raise ValueError(f"one or more {name} values exceed {MAX_FILTER_VALUE_LENGTH} characters")
    return values


def _public_error(message: str, status: int):
    return jsonify({"error": message, "status": status, "service": "LTMD Analytics"}), status


@app.get("/health")
def health():
    try:
        rows, denominators, _ = _load_state()
        corpus_path, _ = _load_corpus_index_state()
        reuse_resolver = _reuse_context_resolver()
    except RuntimeError:
        return jsonify({
            "status": "degraded",
            "service": "LTMD Analytics",
            "analytics_version": ANALYTICS_VERSION,
            "query_engine_version": ENGINE_VERSION,
            "corpus_query_engine_version": CORPUS_ENGINE_VERSION,
            "private_ledger_configured": bool(os.environ.get("LTMD_INDIGENOUS_LEDGER_PATH", "").strip()),
            "corpus_query_configured": bool(os.environ.get("LTMD_UNIVERSAL_INDEX_PATH", "").strip()),
            "reuse_context_configured": bool(os.environ.get("LTMD_REUSE_SIMILARITY_PATH", "").strip()),
        }), 503
    return jsonify({
        "status": "ok",
        "service": "LTMD Analytics",
        "analytics_version": ANALYTICS_VERSION,
        "query_engine_version": ENGINE_VERSION,
        "corpus_query_engine_version": CORPUS_ENGINE_VERSION,
        "candidate_rows_loaded": len(rows),
        "generation_denominators_loaded": len(denominators),
        "corpus_query_configured": corpus_path is not None,
        "reuse_context_configured": reuse_resolver is not None,
        "human_validation_complete": False,
    })


@app.get("/v1/meta")
def metadata():
    try:
        rows, denominators, _ = _load_state()
        corpus_path, corpus_sha = _load_corpus_index_state()
        reuse_resolver = _reuse_context_resolver()
    except RuntimeError:
        return _public_error("analytics data unavailable", 503)

    generations = sorted({str(row["generation"]) for row in rows}, key=lambda value: int(value) if value.isdigit() else 10**12)
    grades = sorted({str(row["grade_code"]) for row in rows})
    waves = sorted({str(row["wave"]) for row in rows})
    languages = sorted({language.strip() for row in rows for language in str(row.get("matched_language_groups") or "").split(";") if language.strip()})
    explicit_terms = sorted({term.strip() for row in rows for term in str(row.get("matched_explicit_terms") or "").split(";") if term.strip()})
    return jsonify({
        "service": "LTMD Analytics",
        "analytics_version": ANALYTICS_VERSION,
        "query_engine_version": ENGINE_VERSION,
        "corpus_query_engine_version": CORPUS_ENGINE_VERSION,
        "corpus_index_version": CORPUS_INDEX_VERSION,
        "source_analysis_version": SOURCE_ANALYSIS_VERSION,
        "result_state": "exploratory_signal",
        "human_validation_complete": False,
        "candidate_rows": len(rows),
        "corpus_query_configured": corpus_path is not None,
        "corpus_index_sha256": corpus_sha,
        "reuse_context_configured": reuse_resolver is not None,
        "filters": {
            "generation": generations,
            "grade_code": grades,
            "wave": waves,
            "language_group": languages,
            "explicit_term": explicit_terms,
        },
        "denominator_generations": sorted(denominators, key=lambda value: int(value) if value.isdigit() else 10**12),
    })


@app.get("/v1/corpus/query")
def corpus_query():
    try:
        expression = validate_corpus_query_expression(request.args.get("q", ""))
        group_by = request.args.get("group_by", "").strip() or None
        if group_by is not None and group_by not in CORPUS_ALLOWED_GROUP_BY:
            raise RuntimeError("group_by must be one of: " + ", ".join(sorted(CORPUS_ALLOWED_GROUP_BY)))
        filters = {
            "generation": _clean_values("generation"),
            "grade_code": _clean_values("grade_code"),
            "wave": _clean_values("wave"),
        }
        normalize_corpus_filters(filters)
    except (ValueError, RuntimeError) as exc:
        return _public_error(str(exc), 400)

    try:
        index_path, index_sha = _load_corpus_index_state()
        if index_path is None:
            return _public_error("corpus analytics data unavailable", 503)
        connection = sqlite3.connect(f"file:{index_path}?mode=ro", uri=True)
        try:
            response = query_corpus_index(
                connection,
                query_expression=expression,
                filters=filters,
                group_by=group_by,
                index_sha256=index_sha,
            )
        finally:
            connection.close()
    except RuntimeError:
        return _public_error("corpus analytics data unavailable", 503)

    return jsonify(response)


@app.get("/v1/indigenous/query")
def indigenous_query():
    try:
        query_label = request.args.get("q", "LTMD Analytics query").strip() or "LTMD Analytics query"
        if len(query_label) > MAX_QUERY_LABEL_LENGTH:
            raise ValueError(f"q exceeds {MAX_QUERY_LABEL_LENGTH} characters")
        group_by = request.args.get("group_by", "").strip() or None
        if group_by is not None and group_by not in ALLOWED_GROUP_BY:
            raise ValueError("invalid group_by")
        filters = {
            "generation": _clean_values("generation"),
            "grade_code": _clean_values("grade_code"),
            "wave": _clean_values("wave"),
            "language_group": _clean_values("language_group"),
            "explicit_term": _clean_values("explicit_term"),
        }
    except ValueError as exc:
        return _public_error(str(exc), 400)

    try:
        rows, denominators, ledger_sha256 = _load_state()
        response = query(
            rows,
            query_label=query_label,
            filters=filters,
            denominators=denominators,
            group_by=group_by,
            source_ledger_sha256=ledger_sha256,
            reuse_context_resolver=_reuse_context_resolver(),
        )
    except RuntimeError:
        return _public_error("analytics data unavailable", 503)
    return jsonify(response)


@app.errorhandler(404)
def not_found(_error):
    return _public_error("endpoint not found", 404)


@app.errorhandler(405)
def method_not_allowed(_error):
    return _public_error("method not allowed; LTMD Analytics 0.1 is read-only", 405)


application = app


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")), debug=False)
