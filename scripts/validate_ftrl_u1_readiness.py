#!/usr/bin/env python3
"""Validate the machine-readable FTRL U1 readiness matrix.

The validator is intentionally text-free and standard-library only. It compares
readiness counts against the canonical U1 coverage dashboard and residual
lifecycle against the retained-source register. It does not fetch source assets,
run OCR, or promote any cohort to semantic readiness.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "data/derived/ltmd_u1_ftrl_readiness.csv"
COVERAGE = ROOT / "data/catalog/ltmd_u1_coverage.md"
RETAINED = ROOT / "data/catalog/ltmd_u1_retained_source_register.csv"

SCHEMA_VERSION = "LTMD_FTRL_U1_READINESS_0.1"
EXPECTED_WAVES = {f"W{i}" for i in range(1, 12)}
EXPECTED_COLUMNS = [
    "schema_version",
    "wave",
    "domain",
    "plan_identities",
    "effective_coverage",
    "canonical_objects",
    "residual_active",
    "residual_final",
    "ftrl_status",
    "allowed_scope",
    "next_gate",
]
ALLOWED_STATUSES = {
    "REFERENCE_FULL_VALIDATION",
    "PREFLIGHT_REQUIRED",
    "PREFLIGHT_REQUIRED_WITH_EXCLUSIONS",
}


def fail(message: str) -> None:
    raise SystemExit(f"FTRL U1 readiness validation failed: {message}")


def load_readiness() -> list[dict[str, str]]:
    with READINESS.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_COLUMNS:
            fail(f"unexpected readiness columns: {reader.fieldnames!r}")
        rows = list(reader)
    if len(rows) != 11:
        fail(f"expected 11 wave rows, found {len(rows)}")
    return rows


def parse_coverage() -> dict[str, tuple[int, int, int, int]]:
    rows: dict[str, tuple[int, int, int, int]] = {}
    for line in COVERAGE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| W"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 7:
            fail(f"unexpected coverage row: {line}")
        wave, _domain, plan, effective, canonical, remaining, _status = parts
        try:
            rows[wave] = tuple(map(int, (plan, effective, canonical, remaining)))
        except ValueError:
            fail(f"non-integer coverage value in {wave}")
    if set(rows) != EXPECTED_WAVES:
        fail(f"coverage waves mismatch: {sorted(rows)}")
    return rows


def retained_lifecycle() -> tuple[Counter[str], Counter[str]]:
    wave_counts: Counter[str] = Counter()
    lifecycle: Counter[str] = Counter()
    with RETAINED.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            wave_counts[row["wave"]] += 1
            lifecycle[row["status"]] += 1
    return wave_counts, lifecycle


def main() -> None:
    rows = load_readiness()
    coverage = parse_coverage()
    retained_by_wave, lifecycle = retained_lifecycle()

    waves = [row["wave"] for row in rows]
    if len(set(waves)) != len(waves) or set(waves) != EXPECTED_WAVES:
        fail(f"readiness waves must be unique W1-W11: {waves!r}")

    versions = {row["schema_version"] for row in rows}
    if versions != {SCHEMA_VERSION}:
        fail(f"schema version mismatch: {sorted(versions)!r}")

    totals = Counter()
    active_total = 0
    final_total = 0

    for row in rows:
        wave = row["wave"]
        status = row["ftrl_status"]
        if status not in ALLOWED_STATUSES:
            fail(f"invalid FTRL status for {wave}: {status}")

        try:
            plan = int(row["plan_identities"])
            effective = int(row["effective_coverage"])
            canonical = int(row["canonical_objects"])
            active = int(row["residual_active"])
            final = int(row["residual_final"])
        except ValueError:
            fail(f"non-integer readiness count in {wave}")

        expected_plan, expected_effective, expected_canonical, expected_remaining = coverage[wave]
        if (plan, effective, canonical) != (
            expected_plan,
            expected_effective,
            expected_canonical,
        ):
            fail(
                f"{wave} diverges from canonical coverage: "
                f"readiness={(plan, effective, canonical)}, "
                f"coverage={(expected_plan, expected_effective, expected_canonical)}"
            )
        if active + final != expected_remaining:
            fail(
                f"{wave} residual mismatch: readiness={active + final}, "
                f"coverage={expected_remaining}"
            )
        if retained_by_wave.get(wave, 0) != active + final:
            fail(
                f"{wave} retained-register mismatch: register={retained_by_wave.get(wave, 0)}, "
                f"readiness={active + final}"
            )

        if expected_remaining == 0 and status == "PREFLIGHT_REQUIRED_WITH_EXCLUSIONS":
            fail(f"{wave} declares exclusions but has zero residual")
        if expected_remaining > 0 and status != "PREFLIGHT_REQUIRED_WITH_EXCLUSIONS":
            fail(f"{wave} has residual identities but does not declare exclusions")

        totals["plan"] += plan
        totals["effective"] += effective
        totals["canonical"] += canonical
        active_total += active
        final_total += final

    w5 = next(row for row in rows if row["wave"] == "W5")
    if w5["ftrl_status"] != "REFERENCE_FULL_VALIDATION":
        fail("W5 must remain the reference full-validation cohort in schema 0.1")

    if (totals["plan"], totals["effective"], totals["canonical"]) != (542, 524, 492):
        fail(f"unexpected U1 totals: {dict(totals)}")
    if (active_total, final_total) != (13, 5):
        fail(f"unexpected residual lifecycle: active={active_total}, final={final_total}")
    if lifecycle != Counter({"active_retention": 13, "final_exception": 5}):
        fail(f"retained-source lifecycle changed: {dict(lifecycle)}")

    print("LTMD FTRL U1 readiness matrix: OK")
    print("U1: plan=542 effective=524 canonical=492 residual=18")
    print("Residual lifecycle: active=13 final=5")
    print("W5 remains REFERENCE_FULL_VALIDATION")


if __name__ == "__main__":
    main()
