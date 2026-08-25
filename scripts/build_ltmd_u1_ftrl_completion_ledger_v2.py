#!/usr/bin/env python3
"""Build LTMD-U1 FTRL completion ledger 0.2 with W3 topology and closure state.

Version 0.2 preserves the exhaustive 542-row documentary denominator and the
verified FTRL states from ledger 0.1, while incorporating the versioned W3
Español/Lengua processing topology. When the text-free W3 archival-closure
record exists and validates, it deterministically promotes all 130 W3
historical identities to validated/corpus-ready/OCR-available/archive-complete.
It never reads or emits OCR text or private Drive locators.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

BASE_BUILDER = Path("scripts/build_ltmd_u1_ftrl_completion_ledger.py")
W3_PROCESSING = Path("data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv")
W3_CLOSURE = Path("data/research/ltmd_u1_w3_archival_closure.json")
DEFAULT_LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
DEFAULT_SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.2"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.2"
EXPECTED_W3_MODES = Counter({
    "direct_canonical": 107,
    "partial_canonical_explicit_gap": 7,
    "exact_byte_alias": 8,
    "paired_route_alias_2018_to_2019": 8,
})
W3_RUN_ID = "32853375619"
W3_COMMIT = "2a55ec09124054729e9c45a2285686cf4abf8776"
W3_PRESERVATION_RUN = "private_consolidation_2026-08-25"
W3_ARCHIVE_LOGICAL = (
    "LTMD-U1 — corpus FTRL privado/W3 — Español y Lengua/"
    "run_32853375619__2a55ec0__2026-08-25/02_CONSOLIDATED_PRIVATE"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def validate_w3(rows: list[dict[str, str]]) -> None:
    if len(rows) != 130 or len({r["viewer_key"] for r in rows}) != 130:
        raise AssertionError("W3 processing denominator must be exactly 130 unique identities")
    modes = Counter(r["processing_mode"] for r in rows)
    if modes != EXPECTED_W3_MODES:
        raise AssertionError(f"W3 processing topology drift: {modes}")
    canonical = [r for r in rows if r["is_canonical_processing_object"] == "1"]
    if len(canonical) != 114:
        raise AssertionError(f"W3 canonical object drift: {len(canonical)} != 114")
    if sum(int(r["direct_source_jpegs"]) for r in canonical) != 20765:
        raise AssertionError("W3 canonical source-page cardinality drift")
    if sum(int(r["persistent_internal_source_gaps"]) for r in canonical) != 8:
        raise AssertionError("W3 internal source-gap cardinality drift")
    if not all(r["ocr_identity_eligible"] == "1" for r in rows):
        raise AssertionError("W3 contains an OCR-ineligible identity")
    if any((r.get("block_reason") or "").strip() for r in rows):
        raise AssertionError("W3 contains a blocked identity")


def read_w3_closure() -> dict | None:
    if not W3_CLOSURE.exists():
        return None
    c = json.loads(W3_CLOSURE.read_text(encoding="utf-8"))
    assert c["schema"] == "LTMD_U1_W3_ARCHIVAL_CLOSURE_0.1"
    assert c["wave"] == "W3"
    assert c["distributed_run_id"] == W3_RUN_ID
    assert c["distributed_source_commit"] == W3_COMMIT
    assert c["historical_identities"] == 130
    assert c["canonical_processing_objects"] == 114
    assert c["page_records"] == 20765
    assert c["shard_count"] == 52
    assert c["computational_validation"]["status"] == "distributed_computationally_validated"
    assert c["computational_validation"]["page_partition_complete"] is True
    assert c["computational_validation"]["page_partition_unique"] is True
    assert c["persistent_archive"]["private_consolidation_validated"] is True
    assert c["persistent_archive"]["consolidated_products_roundtrip_sha256_verified"] is True
    assert c["persistent_archive"]["consolidated_products_shared_false"] is True
    assert c["persistent_archive"]["private_closure_roundtrip_sha256_verified"] is True
    assert c["persistent_archive"]["private_closure_shared_false"] is True
    assert c["state"]["ftrl_status"] == "validated"
    assert c["state"]["corpus_ready"] is True
    assert c["state"]["ocr_available"] is True
    assert c["state"]["archival_complete"] is True
    assert c["state"]["text_verified"] is False
    assert c["state"]["semantic_ready"] is False
    return c


def enrich_w3(base_rows: list[dict[str, str]], processing: list[dict[str, str]], closure: dict | None) -> list[dict[str, str]]:
    by_proc = {r["viewer_key"]: r for r in processing}
    w3_base = [r for r in base_rows if r["wave"] == "W3"]
    if len(w3_base) != 130 or {r["viewer_key"] for r in w3_base} != set(by_proc):
        raise AssertionError("W3 ledger denominator and processing inventory differ")

    out = []
    for row in base_rows:
        row = dict(row)
        row["ledger_version"] = VERSION
        if row["wave"] == "W3":
            proc = by_proc[row["viewer_key"]]
            if row["documentary_disposition"] != "required_ftrl_processing":
                raise AssertionError(f"unexpected W3 documentary disposition: {row['viewer_key']}")
            row["source_ready"] = "partial" if proc["processing_mode"] == "partial_canonical_explicit_gap" else "full"
            row["relation_type"] = proc["processing_mode"]
            row["canonical_processing_viewer_key"] = proc["canonical_processing_viewer_key"]
            row["is_canonical_processing_object"] = proc["is_canonical_processing_object"]
            row["declared_positions"] = proc["declared_positions"]
            row["canonical_source_pages"] = proc["direct_source_jpegs"]
            row["persistent_unresolved_source_gaps"] = proc["persistent_internal_source_gaps"]
            if closure is None:
                if row["ftrl_status"] != "pending" or row["corpus_ready"] != "0" or row["ocr_available"] != "0":
                    raise AssertionError(f"W3 pre-closure state drift: {row['viewer_key']}")
            else:
                row["ftrl_status"] = "validated"
                row["ftrl_run_id"] = W3_RUN_ID
                row["ftrl_commit"] = W3_COMMIT
                row["corpus_ready"] = "1"
                row["ocr_available"] = "1"
                row["text_verified"] = "0"
                row["semantic_ready"] = "0"
                row["archival_status"] = "archival_complete"
                row["preservation_run_id"] = W3_PRESERVATION_RUN
                row["archive_destination_logical"] = W3_ARCHIVE_LOGICAL
        out.append(row)
    return out


def build_summary(rows: list[dict[str, str]], closure: dict | None) -> dict:
    if len(rows) != 542 or len({r["viewer_key"] for r in rows}) != 542:
        raise AssertionError("ledger 0.2 must preserve exactly 542 unique identities")

    wave_counts = Counter(r["wave"] for r in rows)
    dispositions = Counter(r["documentary_disposition"] for r in rows)
    if dispositions != Counter({"required_ftrl_processing": 524, "active_retention": 13, "final_exception": 5}):
        raise AssertionError(f"documentary disposition drift: {dispositions}")

    canonical_by_status = Counter()
    pages_by_status = Counter()
    for row in rows:
        if row["is_canonical_processing_object"] == "1":
            canonical_by_status[row["ftrl_status"]] += 1
            if row["canonical_source_pages"]:
                pages_by_status[row["ftrl_status"]] += int(row["canonical_source_pages"])

    w3 = [r for r in rows if r["wave"] == "W3"]
    expected_w3_status = Counter({"validated": 130}) if closure else Counter({"pending": 130})
    if Counter(r["ftrl_status"] for r in w3) != expected_w3_status:
        raise AssertionError("W3 closure-dependent FTRL status drift")
    if sum(r["is_canonical_processing_object"] == "1" for r in w3) != 114:
        raise AssertionError("W3 ledger canonical count drift")
    if sum(int(r["canonical_source_pages"] or 0) for r in w3 if r["is_canonical_processing_object"] == "1") != 20765:
        raise AssertionError("W3 ledger source-page total drift")
    if sum(int(r["persistent_unresolved_source_gaps"] or 0) for r in w3 if r["is_canonical_processing_object"] == "1") != 8:
        raise AssertionError("W3 ledger gap total drift")
    if closure:
        assert sum(int(r["corpus_ready"]) for r in w3) == 130
        assert sum(int(r["ocr_available"]) for r in w3) == 130
        assert sum(int(r["text_verified"]) for r in w3) == 0
        assert sum(int(r["semantic_ready"]) for r in w3) == 0
        assert Counter(r["archival_status"] for r in w3) == Counter({"archival_complete": 130})

    return {
        "schema": SUMMARY_SCHEMA,
        "ledger_version": VERSION,
        "status": "valid",
        "documentary_identities": len(rows),
        "wave_denominators": dict(sorted(wave_counts.items())),
        "documentary_dispositions": dict(sorted(dispositions.items())),
        "source_readiness": dict(sorted(Counter(r["source_ready"] for r in rows).items())),
        "known_processing_topology_identities": sum(bool(r["canonical_processing_viewer_key"]) for r in rows),
        "ftrl_identity_status": dict(sorted(Counter(r["ftrl_status"] for r in rows).items())),
        "canonical_processing_objects_by_ftrl_status": dict(sorted(canonical_by_status.items())),
        "canonical_source_pages_by_ftrl_status": dict(sorted(pages_by_status.items())),
        "corpus_ready_identities": sum(int(r["corpus_ready"]) for r in rows),
        "ocr_available_identities": sum(int(r["ocr_available"]) for r in rows),
        "text_verified_identities": sum(int(r["text_verified"]) for r in rows),
        "semantic_ready_identities": sum(int(r["semantic_ready"]) for r in rows),
        "archival_status": dict(sorted(Counter(r["archival_status"] for r in rows).items())),
        "global_closure": {
            "eligible": False,
            "reason": "active retentions and unfinished FTRL waves remain; global archival completion is incomplete",
            "active_retentions": dispositions["active_retention"],
            "final_exceptions": dispositions["final_exception"],
        },
        "epistemic_guards": [
            "topology_ready != corpus_ready",
            "preflight_ready != ftrl_validated",
            "corpus_ready != semantic_ready",
            "ocr_available != text_verified",
            "search_hit != historical_claim",
            "zero_hits != demonstrated_absence",
            "computationally_validated != archival_complete",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="ltmd-ledger-v2-") as tmp:
        tmp = Path(tmp)
        base_ledger = tmp / "ledger.csv"
        base_summary = tmp / "summary.json"
        subprocess.run([
            sys.executable, str(BASE_BUILDER),
            "--output", str(base_ledger),
            "--summary-output", str(base_summary),
        ], check=True, stdout=subprocess.DEVNULL)
        base_rows = read_csv(base_ledger)

    w3_processing = read_csv(W3_PROCESSING)
    validate_w3(w3_processing)
    closure = read_w3_closure()
    rows = enrich_w3(base_rows, w3_processing, closure)
    summary = build_summary(rows, closure)

    write_csv(args.output, rows)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
