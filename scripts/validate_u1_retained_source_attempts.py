#!/usr/bin/env python3
"""Validate the LTMD-U1 retained-source research-attempt ledger.

The ledger records bounded source-recovery work without allowing discovery
failures, OCR similarity, title similarity, or other weak signals to mutate the
canonical retained-source lifecycle. This validator is deliberately standard-
library only and performs no network access.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/catalog/ltmd_u1_retained_source_register.csv"
LEDGER = ROOT / "data/catalog/ltmd_u1_retained_source_attempts.csv"

LEDGER_VERSION = "LTMD_U1_RETAINED_SOURCE_ATTEMPTS_0.1"
EXPECTED_COLUMNS = [
    "ledger_version",
    "attempt_id",
    "attempt_date",
    "wave",
    "viewer_key",
    "tracking_issue",
    "method",
    "scope",
    "query_or_target",
    "outcome",
    "evidence_reference",
    "evidence_sha256",
    "admissibility",
    "state_before",
    "state_after",
    "notes",
]
ATTEMPT_ID_RE = re.compile(r"^RS-\d{8}-\d{3}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REFERENCE_RE = re.compile(r"^(?:repo:|issue:|search:|https?://).+")
ALLOWED_ADMISSIBILITY = {
    "discovery_only",
    "not_admissible_to_resolve",
    "admissible_to_resolve",
}
NEGATIVE_OR_DISCOVERY_OUTCOMES = {
    "no_indexed_result",
    "declared_route_unserved",
    "isolated_gap_unresolved",
    "official_subtree_unserved",
    "source_unresolved",
    "archive_inconclusive",
    "candidate_unverified",
}


def fail(message: str) -> None:
    raise SystemExit(f"retained-source attempt validation failed: {message}")


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    return fields, rows


def main() -> None:
    register_fields, register_rows = load_csv(REGISTER)
    if "viewer_key" not in register_fields or "status" not in register_fields:
        fail("retained-source register lacks viewer_key/status")

    ledger_fields, rows = load_csv(LEDGER)
    if ledger_fields != EXPECTED_COLUMNS:
        fail(f"unexpected ledger columns: {ledger_fields!r}")
    if not rows:
        fail("attempt ledger is empty")

    register = {row["viewer_key"]: row for row in register_rows}
    if len(register) != len(register_rows):
        fail("retained-source register contains duplicate viewer_key values")

    versions = {row["ledger_version"] for row in rows}
    if versions != {LEDGER_VERSION}:
        fail(f"ledger version mismatch: {sorted(versions)!r}")

    attempt_ids = [row["attempt_id"] for row in rows]
    duplicates = sorted(key for key, count in Counter(attempt_ids).items() if count > 1)
    if duplicates:
        fail(f"duplicate attempt_id values: {duplicates}")
    invalid_ids = sorted(key for key in attempt_ids if not ATTEMPT_ID_RE.fullmatch(key))
    if invalid_ids:
        fail(f"invalid attempt_id format: {invalid_ids}")

    attempts_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    methods_by_key: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        missing = [column for column in EXPECTED_COLUMNS if column != "evidence_sha256" and not row[column].strip()]
        if missing:
            fail(f"{row.get('attempt_id', '<unknown>')} has empty required fields: {missing}")

        try:
            date.fromisoformat(row["attempt_date"])
        except ValueError:
            fail(f"{row['attempt_id']} has invalid ISO date: {row['attempt_date']!r}")

        key = row["viewer_key"]
        if key not in register:
            fail(f"{row['attempt_id']} references identity absent from retained register: {key}")
        retained = register[key]
        if row["wave"] != retained["wave"]:
            fail(f"{row['attempt_id']} wave mismatch for {key}: {row['wave']} != {retained['wave']}")
        if row["tracking_issue"] != retained["tracking_issue"]:
            fail(
                f"{row['attempt_id']} issue mismatch for {key}: "
                f"{row['tracking_issue']} != {retained['tracking_issue']}"
            )
        if row["state_before"] != retained["status"]:
            fail(
                f"{row['attempt_id']} state_before must match canonical register for {key}: "
                f"{row['state_before']} != {retained['status']}"
            )

        if row["admissibility"] not in ALLOWED_ADMISSIBILITY:
            fail(f"{row['attempt_id']} has invalid admissibility: {row['admissibility']!r}")
        if not REFERENCE_RE.fullmatch(row["evidence_reference"]):
            fail(f"{row['attempt_id']} has unsupported evidence_reference: {row['evidence_reference']!r}")

        digest = row["evidence_sha256"].strip()
        if digest and not SHA256_RE.fullmatch(digest):
            fail(f"{row['attempt_id']} has invalid SHA-256: {digest!r}")

        transitioned = row["state_after"] != row["state_before"]
        if row["outcome"] in NEGATIVE_OR_DISCOVERY_OUTCOMES and transitioned:
            fail(f"{row['attempt_id']} uses a negative/discovery outcome to change lifecycle state")
        if row["admissibility"] != "admissible_to_resolve" and transitioned:
            fail(f"{row['attempt_id']} changes lifecycle without admissible_to_resolve evidence")
        if row["admissibility"] == "admissible_to_resolve" and not digest:
            fail(f"{row['attempt_id']} marks evidence admissible to resolve without a SHA-256 evidence digest")

        if retained["status"] == "final_exception" and row["method"] != "new_evidence_trigger_review":
            fail(
                f"{row['attempt_id']} reopens final exception {key} without method=new_evidence_trigger_review"
            )

        attempts_by_key[key].append(row)
        methods_by_key[key].add(row["method"])

    active_keys = {
        row["viewer_key"] for row in register_rows if row["status"] == "active_retention"
    }
    missing_active = sorted(active_keys - attempts_by_key.keys())
    if missing_active:
        fail(f"active retained identities lack research attempts: {missing_active}")

    missing_baseline = sorted(
        key for key in active_keys if "evidence_consolidation" not in methods_by_key[key]
    )
    if missing_baseline:
        fail(f"active retained identities lack evidence_consolidation baseline: {missing_baseline}")

    final_keys_in_ledger = sorted(
        key for key in attempts_by_key if register[key]["status"] == "final_exception"
    )

    print("LTMD-U1 retained-source attempt ledger: OK")
    print(f"Attempts: {len(rows)}")
    print(f"Active retained identities represented: {len(active_keys)}")
    print(f"Attempts by wave: {dict(Counter(row['wave'] for row in rows))}")
    print(f"Outcomes: {dict(Counter(row['outcome'] for row in rows))}")
    print(f"Final exceptions reopened by new evidence trigger: {len(final_keys_in_ledger)}")


if __name__ == "__main__":
    main()
