#!/usr/bin/env python3
"""Audit the exact LTMD-U1 W10 source state without downloading textbook assets.

This is a metadata-only discovery step. It reads the exhaustive completion ledger,
coverage catalog, and retained-source register already versioned in the repository.
It does not perform OCR, infer aliases, or promote any FTRL/archival status.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
COVERAGE = Path("data/catalog/ltmd_u1_coverage.csv")
RETAINED = Path("data/catalog/ltmd_u1_retained_source_register.csv")
FINAL_EXCEPTION = "H2014P1ENA"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def intval(value: str | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=Path("/tmp/w10-source-audit"))
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    ledger = rows(LEDGER)
    coverage = rows(COVERAGE)
    retained = rows(RETAINED)

    assert len(ledger) == 542 and len({r["viewer_key"] for r in ledger}) == 542
    w10 = [r for r in ledger if r["wave"] == "W10"]
    assert len(w10) == 69 and len({r["viewer_key"] for r in w10}) == 69

    dispositions = Counter(r["documentary_disposition"] for r in w10)
    assert dispositions == Counter({"required_ftrl_processing": 68, "final_exception": 1})
    exceptions = [r for r in w10 if r["documentary_disposition"] == "final_exception"]
    assert [r["viewer_key"] for r in exceptions] == [FINAL_EXCEPTION]
    assert not [r for r in w10 if r["documentary_disposition"] == "active_retention"]

    required = [r for r in w10 if r["documentary_disposition"] == "required_ftrl_processing"]
    assert all(r["ftrl_status"] == "pending" for r in required)
    assert all(r["archival_status"] == "not_started" for r in required)
    assert all(r["text_verified"] == "0" and r["semantic_ready"] == "0" for r in required)

    cov = {r["viewer_key"]: r for r in coverage}
    missing_cov = sorted(r["viewer_key"] for r in w10 if r["viewer_key"] not in cov)
    assert not missing_cov, missing_cov

    retained_by_viewer = {r.get("viewer_key", ""): r for r in retained if r.get("viewer_key")}
    retained_w10 = [retained_by_viewer[v] for v in sorted({r["viewer_key"] for r in w10} & set(retained_by_viewer))]

    generations = Counter(cov[r["viewer_key"]].get("catalog_generation", "") for r in w10)
    grade_codes = Counter(cov[r["viewer_key"]].get("grade_code", "") for r in w10)
    asset_status = Counter(cov[r["viewer_key"]].get("asset_status", "") for r in required)
    queue_status = Counter(cov[r["viewer_key"]].get("queue_status", "") for r in required)
    full_resolved = sum(intval(cov[r["viewer_key"]].get("asset_resolved_full")) for r in required)
    partial_resolved = sum(intval(cov[r["viewer_key"]].get("asset_resolved_partial")) for r in required)
    manifest_ready = sum(intval(cov[r["viewer_key"]].get("page_manifest_ready")) for r in required)
    ocr_ready = sum(intval(cov[r["viewer_key"]].get("ocr_ready")) for r in required)

    source_ready = Counter(r.get("source_ready", "") for r in required)
    relation_type = Counter(r.get("relation_type", "") for r in required)
    known_declared_positions = [intval(r.get("declared_positions")) for r in required if r.get("declared_positions")]
    known_source_pages = [intval(r.get("canonical_source_pages")) for r in required if r.get("canonical_source_pages")]

    # A source URL is only a candidate endpoint here. Presence does not establish source admissibility.
    candidates = []
    for r in sorted(required, key=lambda x: x["viewer_key"]):
        c = cov[r["viewer_key"]]
        candidates.append({
            "viewer_key": r["viewer_key"],
            "catalog_generation": c.get("catalog_generation", ""),
            "grade_code": c.get("grade_code", ""),
            "tail_code": c.get("tail_code", ""),
            "title_core": c.get("title_core", ""),
            "source_url": c.get("source_url", ""),
            "asset_status": c.get("asset_status", ""),
            "asset_resolved_full": c.get("asset_resolved_full", ""),
            "asset_resolved_partial": c.get("asset_resolved_partial", ""),
            "page_manifest_ready": c.get("page_manifest_ready", ""),
            "coverage_queue_status": c.get("queue_status", ""),
            "ledger_source_ready": r.get("source_ready", ""),
            "ledger_relation_type": r.get("relation_type", ""),
            "ledger_declared_positions": r.get("declared_positions", ""),
            "ledger_canonical_source_pages": r.get("canonical_source_pages", ""),
            "ftrl_status": r.get("ftrl_status", ""),
            "archival_status": r.get("archival_status", ""),
        })

    with (args.out_dir / "w10_source_candidates.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(candidates[0]))
        writer.writeheader(); writer.writerows(candidates)

    family_members: dict[str, list[str]] = defaultdict(list)
    for r in w10:
        family_members[cov[r["viewer_key"]].get("catalog_generation", "")].append(r["viewer_key"])

    summary = {
        "schema": "LTMD_U1_W10_SOURCE_STATE_AUDIT_0.1",
        "wave": "W10",
        "domain": "integrados_multiarea",
        "status": "discovery_only_not_source_admissibility",
        "historical_identities": 69,
        "required_ftrl_processing": 68,
        "active_retention": 0,
        "final_exception": 1,
        "final_exception_viewer_keys": [FINAL_EXCEPTION],
        "aliases_introduced": 0,
        "coverage_rows_present": 69,
        "catalog_generation_counts": dict(sorted(generations.items())),
        "grade_code_counts": dict(sorted(grade_codes.items())),
        "required_asset_status_counts": dict(sorted(asset_status.items())),
        "required_queue_status_counts": dict(sorted(queue_status.items())),
        "required_asset_resolved_full": full_resolved,
        "required_asset_resolved_partial": partial_resolved,
        "required_page_manifest_ready": manifest_ready,
        "required_ocr_ready": ocr_ready,
        "ledger_source_ready_counts": dict(sorted(source_ready.items())),
        "ledger_relation_type_counts": dict(sorted(relation_type.items())),
        "required_with_known_declared_positions": len(known_declared_positions),
        "required_known_declared_positions_sum": sum(known_declared_positions),
        "required_with_known_canonical_source_pages": len(known_source_pages),
        "required_known_canonical_source_pages_sum": sum(known_source_pages),
        "retained_register_rows_matching_w10": len(retained_w10),
        "generation_members": {k: sorted(v) for k, v in sorted(family_members.items())},
        "interpretive_limit": "Candidate source URLs and coverage flags are metadata only. They do not establish source admissibility, page cardinality, OCR completeness, text verification, or semantic readiness.",
        "next_gate": "probe the 68 required candidate source endpoints and freeze exact admitted/retained/page denominators before any distributed OCR run",
    }
    (args.out_dir / "w10_source_state_audit.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        k: summary[k] for k in (
            "historical_identities", "required_ftrl_processing", "active_retention",
            "final_exception", "catalog_generation_counts", "required_asset_status_counts",
            "required_asset_resolved_full", "required_asset_resolved_partial",
            "required_page_manifest_ready", "required_ocr_ready",
            "ledger_source_ready_counts", "required_with_known_declared_positions",
            "required_with_known_canonical_source_pages", "retained_register_rows_matching_w10",
            "next_gate"
        )
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
