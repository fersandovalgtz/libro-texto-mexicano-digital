#!/usr/bin/env python3
"""Audit the exhaustive LTMD-U1 W1 denominator against current FTRL inputs.

This is a metadata-only gate. It never downloads assets or emits OCR text.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

COVERAGE = Path("data/catalog/ltmd_u1_coverage.csv")
READINESS = Path("data/catalog/ciencias_naturales_family_asset_readiness.csv")
RETAINED = Path("data/catalog/ltmd_u1_retained_source_register.csv")
EXPECTED_W1 = 40


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    coverage = read_csv(COVERAGE)
    readiness = read_csv(READINESS)
    retained = read_csv(RETAINED)

    w1 = [r for r in coverage if r.get("operational_domain") == "ciencias_naturales"]
    if len(w1) != EXPECTED_W1:
        raise AssertionError(f"W1 denominator drift: {len(w1)} != {EXPECTED_W1}")

    w1_keys = {r["viewer_key"] for r in w1}
    readiness_keys = {r["viewer_key"] for r in readiness}
    if len(readiness_keys) != len(readiness):
        raise AssertionError("duplicate viewer_key in W1 readiness")
    if not readiness_keys <= w1_keys:
        raise AssertionError(
            f"readiness contains non-W1 identities: {sorted(readiness_keys - w1_keys)}"
        )

    retained_w1 = [r for r in retained if r.get("viewer_key") in w1_keys]
    missing = [r for r in w1 if r["viewer_key"] not in readiness_keys]

    result = {
        "schema_version": "LTMD_FTRL_W1_EXHAUSTIVE_AUDIT_0.1",
        "w1_denominator": len(w1),
        "current_ftrl_readiness_identities": len(readiness),
        "retained_w1_identities": len(retained_w1),
        "identities_not_in_current_ftrl_readiness": len(missing),
        "missing": [
            {
                "viewer_key": r["viewer_key"],
                "catalog_generation": r["catalog_generation"],
                "grade_code": r["grade_code"],
                "tail_code": r["tail_code"],
                "book_id": r.get("book_id", ""),
                "asset_status": r.get("asset_status", ""),
                "asset_resolved_full": r.get("asset_resolved_full", ""),
                "asset_resolved_partial": r.get("asset_resolved_partial", ""),
                "page_manifest_ready": r.get("page_manifest_ready", ""),
                "ocr_ready": r.get("ocr_ready", ""),
                "coverage_inherited_from_viewer": r.get("coverage_inherited_from_viewer", ""),
                "wave_label": r.get("wave_label", ""),
                "queue_status": r.get("queue_status", ""),
            }
            for r in missing
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    # Under the exhaustive protocol, W1 cannot be called complete until every one
    # of its 40 historical identities has an explicit FTRL disposition.
    if missing:
        raise SystemExit(
            f"W1 FTRL denominator is not exhaustive: {len(missing)} of {EXPECTED_W1} "
            "historical identities are absent from the current FTRL readiness cohort"
        )


if __name__ == "__main__":
    main()
