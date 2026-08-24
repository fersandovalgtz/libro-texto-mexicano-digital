#!/usr/bin/env python3
"""Audit the exhaustive LTMD-U1 W1 denominator against explicit FTRL inputs.

This metadata-only gate preserves the historical 37-identity family-readiness
register and verifies that the three additional master-denominator identities
have explicit, versioned FTRL source dispositions. It never downloads assets or
emits OCR text.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

COVERAGE = Path("data/catalog/ltmd_u1_coverage.csv")
READINESS = Path("data/catalog/ciencias_naturales_family_asset_readiness.csv")
W1966_SUMMARY = Path("data/catalog/ltmd_u1_w1_1966_page_manifest_summary.csv")
CN46_SUMMARY = Path("data/expansion/cn46_page_manifest_summary.csv")
RETAINED = Path("data/catalog/ltmd_u1_retained_source_register.csv")
EXPECTED_W1 = 40
EXPECTED_LEGACY = 37
EXPECTED_SUPPLEMENTAL = {"H1966P6CI374", "H1966P6CI375", "H1993P6CI209"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    coverage = read_csv(COVERAGE)
    readiness = read_csv(READINESS)
    w1966 = read_csv(W1966_SUMMARY)
    cn46 = read_csv(CN46_SUMMARY)
    retained = read_csv(RETAINED)

    w1 = [r for r in coverage if r.get("operational_domain") == "ciencias_naturales"]
    if len(w1) != EXPECTED_W1:
        raise AssertionError(f"W1 denominator drift: {len(w1)} != {EXPECTED_W1}")

    w1_keys = {r["viewer_key"] for r in w1}
    readiness_keys = {r["viewer_key"] for r in readiness}
    if len(readiness) != EXPECTED_LEGACY:
        raise AssertionError(
            f"legacy W1 readiness drift: {len(readiness)} != {EXPECTED_LEGACY}"
        )
    if len(readiness_keys) != len(readiness):
        raise AssertionError("duplicate viewer_key in W1 readiness")
    if not readiness_keys <= w1_keys:
        raise AssertionError(
            f"readiness contains non-W1 identities: {sorted(readiness_keys - w1_keys)}"
        )

    missing_from_legacy = w1_keys - readiness_keys
    if missing_from_legacy != EXPECTED_SUPPLEMENTAL:
        raise AssertionError(
            "unexpected master/readiness difference: "
            f"{sorted(missing_from_legacy)}"
        )

    w1966_keys = {r["viewer_key"] for r in w1966}
    if w1966_keys != {"H1966P6CI374", "H1966P6CI375"}:
        raise AssertionError(f"unexpected W1-1966 summary set: {sorted(w1966_keys)}")
    for row in w1966:
        if int(row["asset_layer_ready"]) != 1:
            raise AssertionError(f"W1-1966 asset layer not ready: {row['viewer_key']}")
        if int(row["source_jpegs"]) != int(row["unique_source_hashes"]):
            raise AssertionError(f"W1-1966 SHA coverage mismatch: {row['viewer_key']}")

    dh_rows = [r for r in cn46 if r["viewer_key"] == "H1993P6CI209"]
    if len(dh_rows) != 1:
        raise AssertionError("expected one CN46 disposition for H1993P6CI209")
    dh = dh_rows[0]
    if dh["book_id"] != "LTMD-CN6-G1993-DH":
        raise AssertionError("H1993P6CI209 book_id drift")
    if int(dh["source_jpegs"]) != int(dh["unique_source_hashes"]):
        raise AssertionError("H1993P6CI209 SHA coverage mismatch")

    supplemental_keys = w1966_keys | {dh["viewer_key"]}
    explicit_ftrl_keys = readiness_keys | supplemental_keys
    missing = sorted(w1_keys - explicit_ftrl_keys)
    extra = sorted(explicit_ftrl_keys - w1_keys)

    retained_w1 = [r for r in retained if r.get("viewer_key") in w1_keys]
    result = {
        "schema_version": "LTMD_FTRL_W1_EXHAUSTIVE_AUDIT_0.2",
        "w1_denominator": len(w1),
        "legacy_family_readiness_identities": len(readiness),
        "supplemental_ftrl_identities": len(supplemental_keys),
        "explicit_ftrl_dispositions": len(explicit_ftrl_keys),
        "retained_w1_identities": len(retained_w1),
        "identities_without_ftrl_disposition": len(missing),
        "missing": missing,
        "extra": extra,
        "supplemental": sorted(supplemental_keys),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    if missing or extra or len(explicit_ftrl_keys) != EXPECTED_W1:
        raise SystemExit(
            "W1 FTRL denominator is not exhaustive: every one of the 40 historical "
            "identities must have one explicit FTRL disposition"
        )


if __name__ == "__main__":
    main()
