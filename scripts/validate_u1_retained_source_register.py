#!/usr/bin/env python3
"""Validate the LTMD-U1 retained-source register against the coverage dashboard.

This validator intentionally uses only Python's standard library. It does not
fetch source assets and does not infer documentary identity.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data/catalog/ltmd_u1_retained_source_register.csv"
COVERAGE = ROOT / "data/catalog/ltmd_u1_coverage.md"

REGISTER_VERSION = "LTMD_U1_RETAINED_SOURCE_REGISTER_0.2"
EXPECTED_COLUMNS = [
    "register_version",
    "wave",
    "operational_domain",
    "viewer_key",
    "catalog_generation",
    "grade_code",
    "retention_class",
    "retention_detail",
    "tracking_issue",
    "status",
]
EXPECTED_WAVE_COUNTS = {"W2": 4, "W7": 5, "W8": 4, "W10": 1, "W11": 4}
EXPECTED_STATUS_COUNTS = {"active_retention": 13, "final_exception": 5}
EXPECTED_ISSUES = {"4", "5", "9", "11", "13", "14"}
EXPECTED_FINAL_EXCEPTION_KEYS = {
    "H2014P1ENA",
    "H2014P1EAM",
    "H2014P2EAM",
    "H2014P3COL",
    "H2014P3MOR",
}
VIEWER_KEY_RE = re.compile(r"^H\d{4}P\d[A-Z0-9]+$")


def fail(message: str) -> None:
    raise SystemExit(f"retained-source register validation failed: {message}")


def load_register() -> list[dict[str, str]]:
    if not REGISTER.exists():
        fail(f"missing {REGISTER.relative_to(ROOT)}")
    with REGISTER.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_COLUMNS:
            fail(f"unexpected columns: {reader.fieldnames!r}")
        rows = list(reader)
    if not rows:
        fail("register is empty")
    return rows


def parse_coverage() -> tuple[int, int, dict[str, int]]:
    if not COVERAGE.exists():
        fail(f"missing {COVERAGE.relative_to(ROOT)}")
    text = COVERAGE.read_text(encoding="utf-8")

    universe_match = re.search(r"Universo U1:\s*\*\*(\d+)/(\d+)\*\*", text)
    effective_match = re.search(
        r"Cobertura técnica efectiva cerrada o resuelta:\s*\*\*(\d+)/(\d+)", text
    )
    if not universe_match or not effective_match:
        fail("could not parse U1 universe/effective coverage totals")

    universe_num, universe_den = map(int, universe_match.groups())
    effective_num, effective_den = map(int, effective_match.groups())
    if universe_num != universe_den:
        fail(f"U1 census is not closed: {universe_num}/{universe_den}")
    if effective_den != universe_den:
        fail("coverage denominator differs from U1 universe")

    remaining: dict[str, int] = {}
    for line in text.splitlines():
        if not line.startswith("| W"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 7:
            fail(f"unexpected coverage table row: {line}")
        wave = parts[0]
        try:
            remaining[wave] = int(parts[5])
        except ValueError as exc:
            fail(f"non-integer remaining count in {wave}: {parts[5]!r}")
            raise exc  # pragma: no cover

    if not remaining:
        fail("no wave rows parsed from coverage table")
    return universe_den, effective_num, remaining


def main() -> None:
    rows = load_register()
    universe, effective, coverage_remaining = parse_coverage()

    versions = {row["register_version"] for row in rows}
    if versions != {REGISTER_VERSION}:
        fail(f"register version mismatch: {sorted(versions)!r}")

    viewer_keys = [row["viewer_key"] for row in rows]
    duplicates = sorted(key for key, count in Counter(viewer_keys).items() if count > 1)
    if duplicates:
        fail(f"duplicate viewer_key values: {duplicates}")
    invalid_keys = sorted(key for key in viewer_keys if not VIEWER_KEY_RE.fullmatch(key))
    if invalid_keys:
        fail(f"invalid viewer_key format: {invalid_keys}")

    empty_required = [
        row.get("viewer_key", "")
        for row in rows
        if any(not row[column].strip() for column in EXPECTED_COLUMNS)
    ]
    if empty_required:
        fail(f"rows contain empty required fields: {empty_required}")

    status_counts = Counter(row["status"] for row in rows)
    if dict(status_counts) != EXPECTED_STATUS_COUNTS:
        fail(
            "retention lifecycle distribution mismatch: "
            f"register={dict(status_counts)}, expected={EXPECTED_STATUS_COUNTS}"
        )

    final_keys = {row["viewer_key"] for row in rows if row["status"] == "final_exception"}
    if final_keys != EXPECTED_FINAL_EXCEPTION_KEYS:
        fail(
            "final-exception identity mismatch: "
            f"register={sorted(final_keys)}, expected={sorted(EXPECTED_FINAL_EXCEPTION_KEYS)}"
        )

    issues = {row["tracking_issue"] for row in rows}
    if not issues.issubset(EXPECTED_ISSUES):
        fail(f"unexpected tracking issue(s): {sorted(issues - EXPECTED_ISSUES)}")

    register_wave_counts = Counter(row["wave"] for row in rows)
    if dict(register_wave_counts) != EXPECTED_WAVE_COUNTS:
        fail(
            "wave distribution mismatch: "
            f"register={dict(register_wave_counts)}, expected={EXPECTED_WAVE_COUNTS}"
        )

    residual = universe - effective
    if len(rows) != residual:
        fail(f"register rows ({len(rows)}) != U1 residual ({residual})")

    coverage_nonzero = {wave: count for wave, count in coverage_remaining.items() if count > 0}
    if coverage_nonzero != EXPECTED_WAVE_COUNTS:
        fail(
            "coverage-table residual distribution mismatch: "
            f"coverage={coverage_nonzero}, expected={EXPECTED_WAVE_COUNTS}"
        )

    if sum(coverage_remaining.values()) != len(rows):
        fail(
            f"sum of coverage remaining ({sum(coverage_remaining.values())}) "
            f"!= register rows ({len(rows)})"
        )

    print("LTMD-U1 retained-source register: OK")
    print(f"Universe: {universe}")
    print(f"Effective technical coverage: {effective}")
    print(f"Residual identities: {len(rows)}")
    print(f"Lifecycle: {dict(status_counts)}")
    print(f"Wave distribution: {dict(register_wave_counts)}")


if __name__ == "__main__":
    main()
