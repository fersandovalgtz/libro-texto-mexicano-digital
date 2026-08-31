#!/usr/bin/env python3
"""Read-only HTTP adapter for LTMD Analytics 0.1.

The Indigenous-language vertical preserves its preregistered private candidate ledger.
Optional corpus-wide reuse/similarity context may be configured with a paired Universal
Index and reuse/similarity artifact. Private paths and page-level contents are never returned.
"""
from __future__ import annotations

import os
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
}


def _configured_paths() -> tuple[Path, Path]:
    ledger_value = os.environ.get("LTMD_INDIGENOUS_LEDGER_PATH", "").strip()
    if not ledger_value:
        raise RuntimeError("LTMD Analytics private ledger is not configured")
    ledger_path = Path(ledger_value).expanduser()
    generation_value = os.environ.get("LTMD_GENERATION_SUMMARY_PATH", "").strip()
    generation_path = Path(generation_value).expanduser() if generation_value else DEFAULT_GENERATION_SUMMARY
    return ledger_path, generation_path


def _configured_reuse_paths() -> tuple[Path, Path] | None:
    index_value = os.environ.get("LTMD_UNIVERSAL_INDEX_PATH", "").strip()
    reuse_value = os.environ.get("LTMD_REUSE_SIMILARITY_PATH", "").strip()
    if bool(index_value) != bool(reuse_value):
        raise RuntimeError("LTMD corpus-wide reuse context is partially configured")
    if not index_value:
        return None
    index_path = Path(index_value).expanduser()
    reuse_path = Path(reuse_value).expanduser()
    if not index_path.is_file() or not reuse_path.is_file():
        raise RuntimeError("LTMD corpus-wide reuse context is unavailable")
    return index_path, reuse_path


def _reuse_context_resolver():
    configured = _configured_reuse_paths()
    if configured is None:
        return None
    index_path, reuse_path = configured
    return lambda page_ids: runtime_context(index_path, reuse_path, page_ids)


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
    return jsonify({
        "error": message,
        "status": status,
        "service": "LTMD Analytics",
    }), status


@app.get("/health")
def health():
    try:
        rows, denominators, _ = _load_state()
        reuse_resolver = _reuse_context_resolver()
    except RuntimeError:
        return jsonify({
            "status": "degraded",
            "service": "LTMD Analytics",
            "analytics_version": ANALYTICS_VERSION,
            "query_engine_version": ENGINE_VERSION,
            "private_ledger_configured": bool(os.environ.get("LTMD_INDIGENOUS_LEDGER_PATH", "").strip()),
            "reuse_context_configured": bool(
                os.environ.get("LTMD_UNIVERSAL_INDEX_PATH", "").strip()
                and os.environ.get("LTMD_REUSE_SIMILARITY_PATH", "").strip()
            ),
        }), 503
    return jsonify({
        "status": "ok",
        "service": "LTMD Analytics",
        "analytics_version": ANALYTICS_VERSION,
        "query_engine_version": ENGINE_VERSION,
        "candidate_rows_loaded": len(rows),
        "generation_denominators_loaded": len(denominators),
        "reuse_context_configured": reuse_resolver is not None,
        "human_validation_complete": False,
    })


@app.get("/v1/meta")
def metadata():
    try:
        rows, denominators, _ = _load_state()
        reuse_resolver = _reuse_context_resolver()
    except RuntimeError:
        return _public_error("analytics data unavailable", 503)

    generations = sorted({str(row["generation"]) for row in rows}, key=lambda value: int(value) if value.isdigit() else 10**12)
    grades = sorted({str(row["grade_code"]) for row in rows})
    waves = sorted({str(row["wave"]) for row in rows})
    languages = sorted({
        language.strip()
        for row in rows
        for language in str(row.get("matched_language_groups") or "").split(";")
        if language.strip()
    })
    explicit_terms = sorted({
        term.strip()
        for row in rows
        for term in str(row.get("matched_explicit_terms") or "").split(";")
        if term.strip()
    })
    return jsonify({
        "service": "LTMD Analytics",
        "analytics_version": ANALYTICS_VERSION,
        "query_engine_version": ENGINE_VERSION,
        "source_analysis_version": SOURCE_ANALYSIS_VERSION,
        "result_state": "exploratory_signal",
        "human_validation_complete": False,
        "candidate_rows": len(rows),
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
