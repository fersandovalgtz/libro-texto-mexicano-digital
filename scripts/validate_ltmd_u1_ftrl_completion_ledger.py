#!/usr/bin/env python3
"""Validate the committed LTMD U1 FTRL completion state without rewriting it.

This validator is intentionally read-only. Historical builders remain provenance for
older ledger schemas; canonical closure states are validated in place so a later
wave promotion cannot be silently rolled back by an obsolete builder.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/research/ltmd_u1_ftrl_completion_ledger.csv"
SUMMARY = ROOT / "data/research/ltmd_u1_ftrl_completion_summary.json"
STATE = ROOT / "data/research/ltmd_u1_ftrl_wave_state.json"
W11_CLOSURE = ROOT / "data/research/ltmd_u1_w11_archival_closure.json"

LEDGER_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_1.0"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_1.0"
WAVE_DENOMINATORS = {
    "W1": 40,
    "W2": 64,
    "W3": 130,
    "W4": 14,
    "W5": 18,
    "W6": 42,
    "W7": 30,
    "W8": 20,
    "W9": 4,
    "W10": 69,
    "W11": 111,
}
W11_FINAL_EXCEPTIONS = {"H2014P1EAM", "H2014P2EAM", "H2014P3COL", "H2014P3MOR"}


def load_rows() -> list[dict[str, str]]:
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def jload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count(rows: list[dict[str, str]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(r[key] for r in rows).items()))


def int_flag(row: dict[str, str], key: str) -> int:
    return int(row[key] or 0)


def main() -> None:
    rows = load_rows()
    summary = jload(SUMMARY)
    state = jload(STATE)
    closure = jload(W11_CLOSURE)

    # Fixed documentary universe and schema.
    assert len(rows) == 542
    assert len({r["viewer_key"] for r in rows}) == 542
    assert {r["ledger_version"] for r in rows} == {LEDGER_VERSION}
    assert Counter(r["wave"] for r in rows) == Counter(WAVE_DENOMINATORS)
    assert count(rows, "documentary_disposition") == {
        "active_retention": 13,
        "final_exception": 5,
        "required_ftrl_processing": 524,
    }

    # Summary must be a faithful projection of the committed ledger.
    assert summary["schema"] == SUMMARY_SCHEMA
    assert summary["ledger_version"] == LEDGER_VERSION
    assert summary["documentary_identities"] == len(rows)
    assert summary["wave_denominators"] == WAVE_DENOMINATORS
    assert summary["documentary_dispositions"] == count(rows, "documentary_disposition")
    assert summary["ftrl_identity_status"] == count(rows, "ftrl_status")
    assert summary["archival_status"] == count(rows, "archival_status")
    assert summary["source_readiness"] == count(rows, "source_ready")

    canonical_validated = [
        r for r in rows
        if int_flag(r, "is_canonical_processing_object") == 1 and r["ftrl_status"] == "validated"
    ]
    assert summary["canonical_processing_objects_by_ftrl_status"] == {
        "validated": len(canonical_validated)
    }
    assert summary["canonical_source_pages_by_ftrl_status"] == {
        "validated": sum(int(r["canonical_source_pages"] or 0) for r in canonical_validated)
    }

    corpus_ready = sum(int_flag(r, "corpus_ready") for r in rows)
    ocr_available = sum(int_flag(r, "ocr_available") for r in rows)
    text_verified = sum(int_flag(r, "text_verified") for r in rows)
    semantic_ready = sum(int_flag(r, "semantic_ready") for r in rows)
    topology_ready = sum(bool(r["canonical_processing_viewer_key"]) for r in rows)
    assert summary["corpus_ready_identities"] == corpus_ready
    assert summary["ocr_available_identities"] == ocr_available
    assert summary["text_verified_identities"] == text_verified
    assert summary["semantic_ready_identities"] == semantic_ready
    assert summary["known_processing_topology_identities"] == topology_ready

    statuses = Counter(r["ftrl_status"] for r in rows)
    terminal = statuses["validated"] + statuses["final_exception"]
    remaining = len(rows) - terminal
    assert summary["strict_identity_progress"]["terminal_identities"] == terminal
    assert summary["strict_identity_progress"]["remaining_identities"] == remaining
    assert summary["strict_identity_progress"]["processable_pending"] == statuses["pending"]
    assert summary["strict_identity_progress"]["active_retentions"] == statuses["blocked_active_retention"]

    # Scientific/epistemic guards: computational availability is never upgraded
    # into human text verification or semantic evidence by this pipeline.
    assert corpus_ready == ocr_available
    assert text_verified == 0
    assert semantic_ready == 0
    for row in rows:
        if row["ftrl_status"] == "validated":
            assert row["corpus_ready"] == "1"
            assert row["ocr_available"] == "1"
            assert row["text_verified"] == "0"
            assert row["semantic_ready"] == "0"
            assert row["archival_status"] == "archival_complete"
        if row["ftrl_status"] == "final_exception":
            assert row["archival_status"] == "not_applicable_final_exception"
        if row["ftrl_status"] == "blocked_active_retention":
            assert row["documentary_disposition"] == "active_retention"
            assert row["archival_status"] == "not_started"

    # W11 is a closed historical fact after its canonical promotion.
    w11 = [r for r in rows if r["wave"] == "W11"]
    assert len(w11) == 111
    assert Counter(r["ftrl_status"] for r in w11) == Counter({"validated": 107, "final_exception": 4})
    assert {r["viewer_key"] for r in w11 if r["ftrl_status"] == "final_exception"} == W11_FINAL_EXCEPTIONS
    w11_canonical = [r for r in w11 if int_flag(r, "is_canonical_processing_object") == 1]
    assert len(w11_canonical) == 106
    assert sum(int(r["canonical_source_pages"] or 0) for r in w11_canonical) == 19862
    assert all(r["persistent_unresolved_source_gaps"] == "0" for r in w11_canonical)
    assert sum(r["relation_type"] == "exact_source_alias" for r in w11) == 1

    w11_state = state["waves"]["W11"]
    assert w11_state["ftrl_status"] == "validated"
    assert w11_state["archival_status"] == "archival_complete"
    assert closure["archival_complete"] is True
    assert closure["ftrl"]["computationally_validated"] is True
    assert closure["text_verified"] is False
    assert closure["semantic_ready"] is False

    # W2 gate is version-aware: prior to activation it must remain pristine;
    # after a future W2 promotion, this validator will not force a rollback.
    w2 = [r for r in rows if r["wave"] == "W2"]
    w2_state = state["waves"]["W2"]
    if w2_state["archival_status"] == "not_started":
        assert Counter(r["ftrl_status"] for r in w2) == Counter({"pending": 60, "blocked_active_retention": 4})
        assert w2_state["ftrl_status"] == "pending"
        assert all(r["archival_status"] == "not_started" for r in w2)

    # Current post-W11 checkpoint. These assertions intentionally apply only
    # while W2 is still unopened; once W2 is promoted the dynamic checks above
    # remain valid and these checkpoint numbers cease to apply.
    if w2_state["archival_status"] == "not_started":
        assert statuses == Counter({
            "validated": 464,
            "pending": 60,
            "blocked_active_retention": 13,
            "final_exception": 5,
        })
        assert len(canonical_validated) == 435
        assert sum(int(r["canonical_source_pages"] or 0) for r in canonical_validated) == 74604
        assert terminal == 469 and remaining == 73

    print(
        "canonical FTRL-U1 ledger valid:",
        f"validated={statuses['validated']}",
        f"terminal={terminal}",
        f"remaining={remaining}",
        f"canonical_objects={len(canonical_validated)}",
    )


if __name__ == "__main__":
    main()
