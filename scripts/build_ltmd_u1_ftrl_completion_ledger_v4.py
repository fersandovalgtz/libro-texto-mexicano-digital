#!/usr/bin/env python3
"""Promote LTMD-U1 completion ledger 0.3 to 0.4 after verified W6 closure.

This metadata-only promotion consumes the canonical 0.3 ledger, the frozen W6
processing inventory, and public text-free archival-closure evidence. It never
reads or emits OCR text or private Google Drive identifiers. The operation is
idempotent so CI can validate an already-generated 0.4 ledger.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

W6_PROCESSING = Path("data/catalog/ltmd_u1_w6_geography_atlas_processing_inventory.csv")
W6_CLOSURE = Path("data/research/ltmd_u1_w6_archival_closure.json")
DEFAULT_LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
DEFAULT_SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
OLD_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.3"
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.4"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.4"
W6_RUN = "32908105382"
W6_COMMIT = "ae785d821e86fcd10f400280eda590b0bbc729f9"
W6_ARCHIVE = "LTMD-U1 — corpus FTRL privado/W6 — Geografía y Atlas/run_32908105382__ae785d8__2026-08-25/02_CONSOLIDATED_PRIVATE"


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
            raise AssertionError(f"public W6 closure exposes private locator: {forbidden & set(value)}")
        for child in value.values():
            no_private_locator(child)
    elif isinstance(value, list):
        for child in value:
            no_private_locator(child)
    elif isinstance(value, str):
        if "drive.google.com" in value or "docs.google.com" in value or "BEGIN PRIVATE KEY" in value:
            raise AssertionError("public W6 closure exposes forbidden private material")


def validate_w6_closure(payload: dict) -> None:
    assert payload["schema"] == "LTMD_FTRL_ARCHIVAL_CLOSURE_0.4"
    assert payload["wave"] == "W6"
    assert payload["archival_complete"] is True
    assert payload["ftrl"] == {
        "canonical_processing_objects": 37,
        "commit": W6_COMMIT,
        "distributed_shards": 16,
        "fts_rows": 5258,
        "global_exact_union": True,
        "historical_identities": 42,
        "page_partition_complete": True,
        "page_partition_unique": True,
        "page_records": 5258,
        "run_id": W6_RUN,
        "sqlite_integrity": "ok",
        "status": "validated",
    }
    archive = payload["persistent_archive"]
    assert archive["destination_shared"] is False
    assert archive["encrypted_handoffs_preserved"] is True
    assert archive["encrypted_handoffs_unique"] == 16
    assert archive["private_consolidation_validated"] is True
    assert archive["archive_closure_record_preserved"] is True
    assert archive["redownload_checksum_verification_complete"] is True
    assert archive["restricted_plaintext_publicly_exposed"] is False
    assert archive["text_free_evidence_preserved"] is True
    assert archive["resume_duplicate_copies_removed"] == 12
    assert payload["security"]["plaintext_restricted_outputs_published"] is False
    assert payload["text_verified"] is False
    assert payload["semantic_ready"] is False
    no_private_locator(payload)


def validate_processing(processing: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    if len(processing) != 42 or len({r["viewer_key"] for r in processing}) != 42:
        raise AssertionError("W6 processing denominator must be exactly 42 unique identities")
    assert Counter(r["processing_mode"] for r in processing) == Counter({
        "direct_canonical": 36,
        "direct_canonical_reconciled_gap": 1,
        "route_alias_to_2019": 5,
    })
    assert sum(r["is_canonical_processing_object"] == "1" for r in processing) == 37
    assert sum(int(r["persistent_source_gaps"]) for r in processing) == 0
    assert sum(int(r["recovered_source_pages_for_processing"]) for r in processing) == 2
    pages = sum(
        int(r["direct_source_pages_for_processing"]) + int(r["recovered_source_pages_for_processing"])
        for r in processing if r["is_canonical_processing_object"] == "1"
    )
    assert pages == 5258
    return {r["viewer_key"]: r for r in processing}


def validate_base(rows: list[dict[str, str]]) -> None:
    assert len(rows) == 542 and len({r["viewer_key"] for r in rows}) == 542
    versions = {r["ledger_version"] for r in rows}
    assert versions in ({OLD_VERSION}, {VERSION})
    for wave, count in (("W1", 40), ("W3", 130), ("W5", 18)):
        wr = [r for r in rows if r["wave"] == wave]
        assert len(wr) == count
        assert Counter(r["ftrl_status"] for r in wr) == Counter({"validated": count})
        assert Counter(r["archival_status"] for r in wr) == Counter({"archival_complete": count})
    w6 = [r for r in rows if r["wave"] == "W6"]
    assert len(w6) == 42
    if versions == {OLD_VERSION}:
        assert Counter(r["ftrl_status"] for r in w6) == Counter({"pending": 42})
        assert Counter(r["archival_status"] for r in w6) == Counter({"not_started": 42})


def promote(rows: list[dict[str, str]], by_proc: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for original in rows:
        row = dict(original)
        row["ledger_version"] = VERSION
        if row["wave"] == "W6":
            proc = by_proc[row["viewer_key"]]
            assert row["documentary_disposition"] == "required_ftrl_processing"
            row["source_ready"] = "full"
            row["relation_type"] = proc["processing_mode"]
            row["canonical_processing_viewer_key"] = proc["canonical_processing_viewer_key"]
            row["is_canonical_processing_object"] = proc["is_canonical_processing_object"]
            row["declared_positions"] = proc["declared_positions"]
            row["canonical_source_pages"] = (
                str(int(proc["direct_source_pages_for_processing"]) + int(proc["recovered_source_pages_for_processing"]))
                if proc["is_canonical_processing_object"] == "1" else ""
            )
            row["persistent_unresolved_source_gaps"] = proc["persistent_source_gaps"]
            row["ftrl_status"] = "validated"
            row["ftrl_run_id"] = W6_RUN
            row["ftrl_commit"] = W6_COMMIT
            row["corpus_ready"] = "1"
            row["ocr_available"] = "1"
            row["text_verified"] = "0"
            row["semantic_ready"] = "0"
            row["archival_status"] = "archival_complete"
            row["preservation_run_id"] = "private_consolidation_2026-08-25"
            row["archive_destination_logical"] = W6_ARCHIVE
            row["interpretive_limit"] = "Computational/archival closure only; OCR is not human text verification or semantic evidence."
        out.append(row)
    if {r["viewer_key"] for r in out if r["wave"] == "W6"} != set(by_proc):
        raise AssertionError("W6 ledger denominator and processing inventory differ")
    return out


def build_summary(rows: list[dict[str, str]]) -> dict:
    assert len(rows) == 542 and len({r["viewer_key"] for r in rows}) == 542
    dispositions = Counter(r["documentary_disposition"] for r in rows)
    assert dispositions == Counter({"required_ftrl_processing": 524, "active_retention": 13, "final_exception": 5})
    wave_counts = Counter(r["wave"] for r in rows)
    assert wave_counts == Counter({"W1": 40, "W2": 64, "W3": 130, "W4": 14, "W5": 18, "W6": 42, "W7": 30, "W8": 20, "W9": 4, "W10": 69, "W11": 111})

    w6 = [r for r in rows if r["wave"] == "W6"]
    assert Counter(r["ftrl_status"] for r in w6) == Counter({"validated": 42})
    assert Counter(r["archival_status"] for r in w6) == Counter({"archival_complete": 42})
    assert Counter(r["source_ready"] for r in w6) == Counter({"full": 42})
    assert Counter(r["relation_type"] for r in w6) == Counter({"direct_canonical": 36, "direct_canonical_reconciled_gap": 1, "route_alias_to_2019": 5})
    assert sum(r["is_canonical_processing_object"] == "1" for r in w6) == 37
    assert sum(int(r["canonical_source_pages"] or 0) for r in w6 if r["is_canonical_processing_object"] == "1") == 5258
    assert sum(int(r["persistent_unresolved_source_gaps"] or 0) for r in w6) == 0
    assert sum(int(r["corpus_ready"]) for r in w6) == 42
    assert sum(int(r["ocr_available"]) for r in w6) == 42
    assert sum(int(r["text_verified"]) for r in w6) == 0
    assert sum(int(r["semantic_ready"]) for r in w6) == 0

    canonical_by_status = Counter()
    pages_by_status = Counter()
    for row in rows:
        if row["is_canonical_processing_object"] == "1":
            canonical_by_status[row["ftrl_status"]] += 1
            if row["canonical_source_pages"]:
                pages_by_status[row["ftrl_status"]] += int(row["canonical_source_pages"])

    ftrl = Counter(r["ftrl_status"] for r in rows)
    archival = Counter(r["archival_status"] for r in rows)
    validated = ftrl["validated"]
    terminal = validated + dispositions["final_exception"]
    remaining = len(rows) - terminal
    processable_pending = ftrl["pending"]
    assert validated == 230
    assert terminal == 235
    assert remaining == 307
    assert processable_pending == 294
    assert canonical_by_status == Counter({"validated": 202})
    assert pages_by_status == Counter({"validated": 35192})
    assert archival == Counter({"not_started": 307, "archival_complete": 230, "not_applicable_final_exception": 5})

    return {
        "schema": SUMMARY_SCHEMA,
        "ledger_version": VERSION,
        "status": "valid",
        "documentary_identities": len(rows),
        "wave_denominators": dict(sorted(wave_counts.items())),
        "documentary_dispositions": dict(sorted(dispositions.items())),
        "source_readiness": dict(sorted(Counter(r["source_ready"] for r in rows).items())),
        "known_processing_topology_identities": sum(bool(r["canonical_processing_viewer_key"]) for r in rows),
        "ftrl_identity_status": dict(sorted(ftrl.items())),
        "canonical_processing_objects_by_ftrl_status": dict(sorted(canonical_by_status.items())),
        "canonical_source_pages_by_ftrl_status": dict(sorted(pages_by_status.items())),
        "corpus_ready_identities": sum(int(r["corpus_ready"]) for r in rows),
        "ocr_available_identities": sum(int(r["ocr_available"]) for r in rows),
        "text_verified_identities": sum(int(r["text_verified"]) for r in rows),
        "semantic_ready_identities": sum(int(r["semantic_ready"]) for r in rows),
        "archival_status": dict(sorted(archival.items())),
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
    parser.add_argument("--input", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--output", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    closure = json.loads(W6_CLOSURE.read_text(encoding="utf-8"))
    validate_w6_closure(closure)
    processing = read_csv(W6_PROCESSING)
    by_proc = validate_processing(processing)
    rows = read_csv(args.input)
    validate_base(rows)
    rows = promote(rows, by_proc)
    summary = build_summary(rows)
    write_csv(args.output, rows)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
