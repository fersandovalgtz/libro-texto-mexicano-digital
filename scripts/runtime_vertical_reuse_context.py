#!/usr/bin/env python3
"""Runtime-safe wrapper for LTMD vertical reuse/similarity context."""
from __future__ import annotations

from pathlib import Path

from scripts.build_vertical_reuse_context import CONTEXT_VERSION, aggregate_context

CONTEXT_WARNINGS = [
    "Reuse/similarity context is computational evidence and does not create aliases or establish semantic equivalence.",
    "Counts describe candidate pages touched by corpus-wide reuse/similarity signals; they do not invalidate or validate the vertical selection.",
]


def runtime_context(index_path: Path, reuse_path: Path, page_ids: list[str]) -> dict:
    return {
        "context_version": CONTEXT_VERSION,
        "result_state": "exploratory_signal",
        "metrics": aggregate_context(index_path, reuse_path, page_ids),
        "warnings": list(CONTEXT_WARNINGS),
    }
