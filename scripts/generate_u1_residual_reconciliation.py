#!/usr/bin/env python3
"""Generate the deterministic LTMD-U1 residual reconciliation report.

The report reconciles the canonical U1 coverage table, the retained-source
register, and the research-attempt ledger. It never promotes evidence or
changes lifecycle state; it only renders the canonical residual surface and
fails when the three inputs disagree on core invariants.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERAGE_CSV = ROOT / "data/catalog/ltmd_u1_coverage.csv"
COVERAGE_MD = ROOT / "data/catalog/ltmd_u1_coverage.md"
REGISTER = ROOT / "data/catalog/ltmd_u1_retained_source_register.csv"
LEDGER = ROOT / "data/catalog/ltmd_u1_retained_source_attempts.csv"
OUTPUT = ROOT / "data/catalog/ltmd_u1_residual_reconciliation.json"
REPORT_VERSION = "LTMD_U1_RESIDUAL_RECONCILIATION_0.1"
ALLOWED_STATUSES = {"active_retention", "final_exception"}


def fail(message: str) -> None:
    raise SystemExit(f"U1 residual reconciliation failed: {message}")


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def extract(pattern: str, text: str, label: str) -> tuple[int, ...]:
    match = re.search(pattern, text)
    if not match:
        fail(f"could not parse {label} from data/catalog/ltmd_u1_coverage.md")
    return tuple(int(value) for value in match.groups())


def build_report() -> dict[str, object]:
    coverage_rows = load_csv(COVERAGE_CSV)
    register_rows = load_csv(REGISTER)
    attempt_rows = load_csv(LEDGER)
    coverage_md = COVERAGE_MD.read_text(encoding="utf-8")

    coverage_keys = [row["viewer_key"] for row in coverage_rows]
    if len(set(coverage_keys)) != len(coverage_keys):
        fail("coverage table contains duplicate viewer_key values")

    register_keys = [row["viewer_key"] for row in register_rows]
    if len(set(register_keys)) != len(register_keys):
        fail("retained-source register contains duplicate viewer_key values")

    unknown_statuses = sorted(set(row["status"] for row in register_rows) - ALLOWED_STATUSES)
    if unknown_statuses:
        fail(f"unsupported retained-source statuses: {unknown_statuses}")

    missing_from_coverage = sorted(set(register_keys) - set(coverage_keys))
    if missing_from_coverage:
        fail(f"retained identities absent from U1 coverage: {missing_from_coverage}")

    universe_numerator, universe_denominator = extract(
        r"Universo U1:\s*\*\*(\d+)/(\d+)\*\*",
        coverage_md,
        "U1 universe",
    )
    effective_numerator, effective_denominator = extract(
        r"Cobertura técnica efectiva cerrada o resuelta:\s*\*\*(\d+)/(\d+)",
        coverage_md,
        "effective technical coverage",
    )
    semantic_numerator, semantic_denominator = extract(
        r"Cobertura semántica humana validada incorporada al tablero:\s*\*\*(\d+)/(\d+)\*\*",
        coverage_md,
        "human semantic coverage",
    )

    if universe_numerator != universe_denominator:
        fail("coverage dashboard does not report a fully cataloged U1 universe")
    if universe_denominator != len(coverage_rows):
        fail(
            f"coverage dashboard universe ({universe_denominator}) != coverage CSV rows ({len(coverage_rows)})"
        )
    if effective_denominator != universe_denominator or semantic_denominator != universe_denominator:
        fail("coverage dashboard denominators are not aligned")

    residual_count = len(register_rows)
    if universe_denominator - effective_numerator != residual_count:
        fail(
            "effective technical coverage and retained-source register disagree: "
            f"{universe_denominator} - {effective_numerator} != {residual_count}"
        )

    status_counts = Counter(row["status"] for row in register_rows)
    if sum(status_counts.values()) != residual_count:
        fail("retained-source status counts do not sum to residual identities")

    attempts_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in attempt_rows:
        key = row["viewer_key"]
        if key not in set(register_keys):
            fail(f"attempt {row['attempt_id']} references non-residual identity {key}")
        attempts_by_key[key].append(row)

    active_keys = {row["viewer_key"] for row in register_rows if row["status"] == "active_retention"}
    active_without_attempt = sorted(active_keys - set(attempts_by_key))
    if active_without_attempt:
        fail(f"active retentions lack attempts: {active_without_attempt}")

    final_reopened = sorted(
        key
        for key in attempts_by_key
        if next(row for row in register_rows if row["viewer_key"] == key)["status"] == "final_exception"
    )

    per_wave: dict[str, dict[str, int]] = {}
    wave_status = defaultdict(Counter)
    for row in register_rows:
        wave_status[row["wave"]][row["status"]] += 1
    for wave in sorted(wave_status, key=lambda value: int(value[1:])):
        counts = wave_status[wave]
        per_wave[wave] = {
            "residual_identities": sum(counts.values()),
            "active_retention": counts["active_retention"],
            "final_exception": counts["final_exception"],
            "attempts": sum(len(attempts_by_key[row["viewer_key"]]) for row in register_rows if row["wave"] == wave),
        }

    residuals: list[dict[str, object]] = []
    for retained in sorted(register_rows, key=lambda row: (int(row["wave"][1:]), row["viewer_key"])):
        attempts = sorted(
            attempts_by_key.get(retained["viewer_key"], []),
            key=lambda row: (row["attempt_date"], row["attempt_id"]),
        )
        latest = attempts[-1] if attempts else None
        status = retained["status"]
        residuals.append(
            {
                "viewer_key": retained["viewer_key"],
                "wave": retained["wave"],
                "operational_domain": retained["operational_domain"],
                "catalog_generation": int(retained["catalog_generation"]),
                "grade_code": int(retained["grade_code"]),
                "retention_class": retained["retention_class"],
                "retention_detail": retained["retention_detail"],
                "tracking_issue": int(retained["tracking_issue"]),
                "status": status,
                "resolution_gate": (
                    "requires_admissible_reproducible_source_evidence"
                    if status == "active_retention"
                    else "requires_new_evidence_trigger_review"
                ),
                "attempt_count": len(attempts),
                "latest_attempt": (
                    {
                        "attempt_id": latest["attempt_id"],
                        "attempt_date": latest["attempt_date"],
                        "method": latest["method"],
                        "outcome": latest["outcome"],
                        "admissibility": latest["admissibility"],
                        "state_after": latest["state_after"],
                    }
                    if latest
                    else None
                ),
            }
        )

    attempt_dates = [row["attempt_date"] for row in attempt_rows]
    snapshot_date = max(attempt_dates) if attempt_dates else None
    effective_percent = round((effective_numerator / universe_denominator) * 100, 2)

    return {
        "report_version": REPORT_VERSION,
        "snapshot_date": snapshot_date,
        "sources": {
            "coverage_csv": "data/catalog/ltmd_u1_coverage.csv",
            "coverage_dashboard": "data/catalog/ltmd_u1_coverage.md",
            "retained_source_register": "data/catalog/ltmd_u1_retained_source_register.csv",
            "research_attempt_ledger": "data/catalog/ltmd_u1_retained_source_attempts.csv",
        },
        "summary": {
            "universe_identities": universe_denominator,
            "effective_technical_identities": effective_numerator,
            "effective_technical_coverage_percent": effective_percent,
            "residual_identities": residual_count,
            "active_retention": status_counts["active_retention"],
            "final_exception": status_counts["final_exception"],
            "research_attempts": len(attempt_rows),
            "final_exceptions_reopened_by_new_evidence": len(final_reopened),
            "human_semantic_validated_identities": semantic_numerator,
        },
        "per_wave": per_wave,
        "residuals": residuals,
    }


def rendered_report() -> str:
    return json.dumps(build_report(), ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed JSON differs from the deterministic render",
    )
    args = parser.parse_args()

    rendered = rendered_report()
    if args.check:
        if not OUTPUT.exists():
            fail(f"missing generated report {OUTPUT.relative_to(ROOT)}")
        committed = OUTPUT.read_text(encoding="utf-8")
        if committed != rendered:
            fail(
                "committed residual reconciliation is stale; run "
                "python scripts/generate_u1_residual_reconciliation.py"
            )
        print("LTMD-U1 residual reconciliation report: OK")
        return

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
