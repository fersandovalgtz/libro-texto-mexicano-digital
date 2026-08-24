#!/usr/bin/env python3
"""Validate that FTRL-U1 preserves the exhaustive 542-identity universe.

This gate validates scope and disposition, not completion of OCR/FTRL processing.
It is intentionally text-free and operates only on repository metadata.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

DEFAULT_CONTRACT = Path("data/research/ltmd_u1_exhaustive_scope_contract.json")
WAVE_RE = re.compile(r"^U1-(W(?:10|11|[1-9]))-")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def wave_from_coverage(row: dict[str, str]) -> str:
    label = row.get("wave_label", "")
    match = WAVE_RE.match(label)
    if not match:
        raise AssertionError(
            f"coverage identity {row.get('viewer_key')} lacks a valid U1-W1..W11 wave_label: {label!r}"
        )
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-global-closure",
        action="store_true",
        help="Fail unless there are zero active retentions.",
    )
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    coverage_path = Path(contract["master_inventory"])
    retained_path = Path(contract["retained_source_register"])
    coverage = read_csv(coverage_path)
    retained = read_csv(retained_path)

    expected_universe = int(contract["expected_universe_identities"])
    expected_effective = int(contract["expected_effective_technical_coverage"])
    expected_active = int(contract["expected_active_retentions"])
    expected_final = int(contract["expected_final_exceptions"])
    expected_residual = int(contract["expected_residual_identities"])

    viewer_keys = [row.get("viewer_key", "").strip() for row in coverage]
    assert all(viewer_keys), "blank viewer_key in master coverage inventory"
    assert len(viewer_keys) == expected_universe, (
        f"U1 denominator drift: {len(viewer_keys)} != {expected_universe}"
    )
    assert len(set(viewer_keys)) == expected_universe, "duplicate viewer_key in U1 universe"
    assert all(row.get("cataloged") == "1" for row in coverage), (
        "every U1 identity must remain cataloged in the master denominator"
    )

    wave_counts = Counter(wave_from_coverage(row) for row in coverage)
    expected_wave_counts = {
        str(key): int(value)
        for key, value in contract["expected_wave_denominators"].items()
    }
    assert dict(sorted(wave_counts.items())) == dict(sorted(expected_wave_counts.items())), (
        f"wave denominator drift: observed={dict(sorted(wave_counts.items()))} "
        f"expected={dict(sorted(expected_wave_counts.items()))}"
    )
    assert sum(wave_counts.values()) == expected_universe

    retained_keys = [row.get("viewer_key", "").strip() for row in retained]
    assert all(retained_keys), "blank viewer_key in retained-source register"
    assert len(retained_keys) == expected_residual, (
        f"residual register drift: {len(retained_keys)} != {expected_residual}"
    )
    assert len(set(retained_keys)) == expected_residual, (
        "duplicate viewer_key in retained-source register"
    )
    assert set(retained_keys) <= set(viewer_keys), (
        "retained-source register contains identity outside frozen U1 universe"
    )

    allowed_residual_status = {"active_retention", "final_exception"}
    observed_statuses = {row.get("status", "") for row in retained}
    assert observed_statuses <= allowed_residual_status, (
        f"unexpected retained-source lifecycle state(s): {sorted(observed_statuses - allowed_residual_status)}"
    )

    status_counts = Counter(row["status"] for row in retained)
    assert status_counts["active_retention"] == expected_active, (
        f"active-retention drift: {status_counts['active_retention']} != {expected_active}"
    )
    assert status_counts["final_exception"] == expected_final, (
        f"final-exception drift: {status_counts['final_exception']} != {expected_final}"
    )
    assert status_counts["active_retention"] + status_counts["final_exception"] == expected_residual

    retained_wave_counts = Counter(row["wave"] for row in retained)
    expected_retained_by_wave = {
        str(key): int(value)
        for key, value in contract["expected_retained_by_wave"].items()
    }
    assert dict(sorted(retained_wave_counts.items())) == dict(
        sorted(expected_retained_by_wave.items())
    ), (
        f"retained wave distribution drift: observed={dict(sorted(retained_wave_counts.items()))} "
        f"expected={dict(sorted(expected_retained_by_wave.items()))}"
    )

    required_keys = set(viewer_keys) - set(retained_keys)
    assert len(required_keys) == expected_effective, (
        f"required-FTRL identity count drift: {len(required_keys)} != {expected_effective}"
    )

    active_keys = {
        row["viewer_key"] for row in retained if row["status"] == "active_retention"
    }
    final_keys = {
        row["viewer_key"] for row in retained if row["status"] == "final_exception"
    }
    assert required_keys.isdisjoint(active_keys)
    assert required_keys.isdisjoint(final_keys)
    assert active_keys.isdisjoint(final_keys)
    assert required_keys | active_keys | final_keys == set(viewer_keys), (
        "one or more U1 identities lack an exhaustive FTRL disposition"
    )

    disposition_counts = {
        "required_ftrl_processing": len(required_keys),
        "active_retention": len(active_keys),
        "final_exception": len(final_keys),
    }
    assert sum(disposition_counts.values()) == expected_universe

    global_closure_ready = len(active_keys) == int(
        contract["global_closure_requires_active_retentions"]
    )
    result = {
        "schema_version": contract["schema_version"],
        "snapshot": contract["snapshot"],
        "status": "scope_validated",
        "universe_identities": expected_universe,
        "identity_dispositions": disposition_counts,
        "wave_denominators": dict(sorted(wave_counts.items())),
        "retained_by_wave": dict(sorted(retained_wave_counts.items())),
        "all_identities_have_disposition": True,
        "global_closure_ready": global_closure_ready,
        "global_closure_blockers": {
            "active_retentions": len(active_keys),
        },
        "interpretation": (
            "Scope validation does not assert that required_ftrl_processing identities "
            "have completed OCR/FTRL. Active retentions remain mandatory work and block "
            "global exhaustive closure."
        ),
    }

    serialized = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")

    if args.require_global_closure and not global_closure_ready:
        raise SystemExit(
            f"FTRL-U1 is not globally exhaustive yet: {len(active_keys)} active retention(s) remain"
        )


if __name__ == "__main__":
    main()
