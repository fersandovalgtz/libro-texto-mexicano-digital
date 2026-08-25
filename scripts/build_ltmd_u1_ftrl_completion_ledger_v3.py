#!/usr/bin/env python3
"""Build LTMD-U1 FTRL completion ledger 0.3 after verified W3 archival closure.

Version 0.3 preserves the exhaustive 542-row denominator and W3 topology from
ledger 0.2, then promotes W3 only when public, text-free archival-closure
evidence passes exact invariants. It never reads or emits OCR text or private
Google Drive identifiers.
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
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.3"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.3"
W3_RUN = "32853375619"
W3_COMMIT = "2a55ec09124054729e9c45a2285686cf4abf8776"
W3_ARCHIVE = "LTMD-U1 — corpus FTRL privado/W3 — Español y Lengua/run_32853375619__2a55ec0__2026-08-25/02_CONSOLIDATED_PRIVATE"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def no_private_locator(value) -> None:
    if isinstance(value, dict):
        forbidden = {"drive_id", "file_id", "folder_id", "drive_url", "private_url"}
        if forbidden & set(value):
            raise AssertionError(f"public W3 closure exposes private locator: {forbidden & set(value)}")
        for child in value.values():
            no_private_locator(child)
    elif isinstance(value, list):
        for child in value:
            no_private_locator(child)
    elif isinstance(value, str):
        if "drive.google.com" in value or "docs.google.com" in value or "BEGIN PRIVATE KEY" in value:
            raise AssertionError("public W3 closure exposes forbidden private material")


def validate_w3_closure(payload: dict) -> None:
    assert payload["schema"] == "LTMD_FTRL_ARCHIVAL_CLOSURE_0.3"
    assert payload["wave"] == "W3"
    assert payload["archival_complete"] is True
    ftrl = payload["ftrl"]
    assert ftrl == {
        "canonical_processing_objects": 114,
        "commit": W3_COMMIT,
        "distributed_shards": 52,
        "fts_rows": 20765,
        "global_exact_union": True,
        "historical_identities": 130,
        "page_partition_complete": True,
        "page_partition_unique": True,
        "page_records": 20765,
        "run_id": W3_RUN,
        "sqlite_integrity": "ok",
        "status": "validated",
    }
    archive = payload["persistent_archive"]
    assert archive["destination_shared"] is False
    assert archive["encrypted_handoffs_preserved"] is True
    assert archive["text_free_evidence_preserved"] is True
    assert archive["private_consolidation_validated"] is True
    assert archive["archive_closure_record_preserved"] is True
    assert archive["redownload_checksum_verification_complete"] is True
    assert archive["restricted_plaintext_publicly_exposed"] is False
    assert payload["security"]["plaintext_restricted_outputs_published"] is False
    assert payload["text_verified"] is False
    assert payload["semantic_ready"] is False
    no_private_locator(payload)


def enrich_and_promote_w3(rows: list[dict[str, str]], processing: list[dict[str, str]]) -> list[dict[str, str]]:
    if len(processing) != 130 or len({r["viewer_key"] for r in processing}) != 130:
        raise AssertionError("W3 processing denominator must be exactly 130 unique identities")
    modes = Counter(r["processing_mode"] for r in processing)
    assert modes == Counter({"direct_canonical": 107, "partial_canonical_explicit_gap": 7, "exact_byte_alias": 8, "paired_route_alias_2018_to_2019": 8})
    assert sum(r["is_canonical_processing_object"] == "1" for r in processing) == 114
    assert sum(int(r["direct_source_jpegs"]) for r in processing if r["is_canonical_processing_object"] == "1") == 20765
    by_proc = {r["viewer_key"]: r for r in processing}
    out = []
    for row in rows:
        row = dict(row)
        row["ledger_version"] = VERSION
        if row["wave"] == "W3":
            proc = by_proc[row["viewer_key"]]
            assert row["documentary_disposition"] == "required_ftrl_processing"
            assert row["ftrl_status"] == "validated"
            assert row["ftrl_run_id"] == W3_RUN
            assert row["ftrl_commit"] == W3_COMMIT
            assert row["archival_status"] == "archival_complete"
            row["source_ready"] = "partial" if proc["processing_mode"] == "partial_canonical_explicit_gap" else "full"
            row["relation_type"] = proc["processing_mode"]
            row["canonical_processing_viewer_key"] = proc["canonical_processing_viewer_key"]
            row["is_canonical_processing_object"] = proc["is_canonical_processing_object"]
            row["declared_positions"] = proc["declared_positions"]
            row["canonical_source_pages"] = proc["direct_source_jpegs"]
            row["persistent_unresolved_source_gaps"] = proc["persistent_internal_source_gaps"]
            row["corpus_ready"] = "1"
            row["ocr_available"] = "1"
            row["text_verified"] = "0"
            row["semantic_ready"] = "0"
            row["preservation_run_id"] = "private_consolidation_2026-08-25"
            row["archive_destination_logical"] = W3_ARCHIVE
            row["interpretive_limit"] = "Computational/archival closure only; OCR is not human text verification or semantic evidence."
        out.append(row)
    if {r["viewer_key"] for r in out if r["wave"] == "W3"} != set(by_proc):
        raise AssertionError("W3 ledger denominator and processing inventory differ")
    return out


def build_summary(rows: list[dict[str, str]]) -> dict:
    assert len(rows) == 542 and len({r["viewer_key"] for r in rows}) == 542
    wave_counts = Counter(r["wave"] for r in rows)
    dispositions = Counter(r["documentary_disposition"] for r in rows)
    assert dispositions == Counter({"required_ftrl_processing": 524, "active_retention": 13, "final_exception": 5})

    w3 = [r for r in rows if r["wave"] == "W3"]
    assert len(w3) == 130
    assert Counter(r["ftrl_status"] for r in w3) == Counter({"validated": 130})
    assert Counter(r["archival_status"] for r in w3) == Counter({"archival_complete": 130})
    assert sum(int(r["corpus_ready"]) for r in w3) == 130
    assert sum(int(r["ocr_available"]) for r in w3) == 130
    assert sum(int(r["text_verified"]) for r in w3) == 0
    assert sum(int(r["semantic_ready"]) for r in w3) == 0
    assert sum(r["is_canonical_processing_object"] == "1" for r in w3) == 114
    assert sum(int(r["canonical_source_pages"] or 0) for r in w3 if r["is_canonical_processing_object"] == "1") == 20765

    canonical_by_status = Counter()
    pages_by_status = Counter()
    for row in rows:
        if row["is_canonical_processing_object"] == "1":
            canonical_by_status[row["ftrl_status"]] += 1
            if row["canonical_source_pages"]:
                pages_by_status[row["ftrl_status"]] += int(row["canonical_source_pages"])

    ftrl_identity_status = Counter(r["ftrl_status"] for r in rows)
    archival_status = Counter(r["archival_status"] for r in rows)
    validated = ftrl_identity_status["validated"]
    terminal = validated + dispositions["final_exception"]
    remaining = len(rows) - terminal
    processable_pending = ftrl_identity_status["pending"]

    assert validated == 188
    assert terminal == 193
    assert remaining == 349
    assert processable_pending == 336
    assert archival_status == Counter({"not_started": 349, "archival_complete": 188, "not_applicable_final_exception": 5})

    return {
        "schema": SUMMARY_SCHEMA,
        "ledger_version": VERSION,
        "status": "valid",
        "documentary_identities": len(rows),
        "wave_denominators": dict(sorted(wave_counts.items())),
        "documentary_dispositions": dict(sorted(dispositions.items())),
        "source_readiness": dict(sorted(Counter(r["source_ready"] for r in rows).items())),
        "known_processing_topology_identities": sum(bool(r["canonical_processing_viewer_key"]) for r in rows),
        "ftrl_identity_status": dict(sorted(ftrl_identity_status.items())),
        "canonical_processing_objects_by_ftrl_status": dict(sorted(canonical_by_status.items())),
        "canonical_source_pages_by_ftrl_status": dict(sorted(pages_by_status.items())),
        "corpus_ready_identities": sum(int(r["corpus_ready"]) for r in rows),
        "ocr_available_identities": sum(int(r["ocr_available"]) for r in rows),
        "text_verified_identities": sum(int(r["text_verified"]) for r in rows),
        "semantic_ready_identities": sum(int(r["semantic_ready"]) for r in rows),
        "archival_status": dict(sorted(archival_status.items())),
        "strict_identity_progress": {
            "terminal_identities": terminal,
            "terminal_fraction": round(terminal / len(rows), 6),
            "remaining_identities": remaining,
            "remaining_fraction": round(remaining / len(rows), 6),
            "processable_pending": processable_pending,
            "active_retentions": dispositions["active_retention"],
            "definition": "validated FTRL identities plus documented final exceptions over the fixed 542-identity denominator"
        },
        "global_closure": {
            "eligible": False,
            "reason": "active retentions and unfinished FTRL waves remain; archival completion is incomplete outside validated waves",
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

    closure = json.loads(W3_CLOSURE.read_text(encoding="utf-8"))
    validate_w3_closure(closure)

    with tempfile.TemporaryDirectory(prefix="ltmd-ledger-v3-") as tmp:
        tmp = Path(tmp)
        base_ledger = tmp / "ledger.csv"
        base_summary = tmp / "summary.json"
        subprocess.run([
            sys.executable, str(BASE_BUILDER),
            "--output", str(base_ledger),
            "--summary-output", str(base_summary),
        ], check=True, stdout=subprocess.DEVNULL)
        rows = read_csv(base_ledger)

    processing = read_csv(W3_PROCESSING)
    rows = enrich_and_promote_w3(rows, processing)
    summary = build_summary(rows)
    write_csv(args.output, rows)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
