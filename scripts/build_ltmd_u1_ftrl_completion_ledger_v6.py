#!/usr/bin/env python3
"""Promote LTMD-U1 completion ledger 0.5 to 0.6 after verified W9 closure.

Metadata-only promotion. It consumes the canonical 0.5 ledger, versioned W9
processing topology, public text-free global evidence, and public archival
closure evidence. It never reads or emits OCR text, private Drive identifiers,
or key material.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

W9_PROCESSING = Path("data/catalog/ltmd_u1_w9_processing_inventory.csv")
W9_GLOBAL = Path("data/research/ltmd_u1_w9_global_evidence.json")
W9_CLOSURE = Path("data/research/ltmd_u1_w9_archival_closure.json")
DEFAULT_LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
DEFAULT_SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
OLD_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.5"
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.6"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.6"
W9_RUN = "33124903433"
W9_COMMIT = "ac1cb91220cb09aeb24cce11c1f9a44f303fdacc"
W9_ARCHIVE = "LTMD-U1 — corpus FTRL privado/W9 — Educación Física/run_33124903433__ac1cb91__2026-08-27/02_CONSOLIDATED_PRIVATE"
W9_PAGES = {"H2008P1ED252":114, "H2008P2ED260":106, "H2008P5ED280":114, "H2008P6ED287":114}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def no_private_locator(value) -> None:
    if isinstance(value, dict):
        forbidden = {"drive_id", "file_id", "folder_id", "drive_url", "private_url", "private_key"}
        if forbidden & set(value):
            raise AssertionError(f"public W9 evidence exposes private locator/material: {forbidden & set(value)}")
        for child in value.values():
            no_private_locator(child)
    elif isinstance(value, list):
        for child in value:
            no_private_locator(child)
    elif isinstance(value, str):
        lowered = value.lower()
        if "drive.google.com" in lowered or "docs.google.com" in lowered or "begin private key" in lowered:
            raise AssertionError("public W9 evidence exposes forbidden private material")


def validate_global(p: dict) -> None:
    assert p["schema"] == "LTMD_FTRL_W9_GLOBAL_EVIDENCE_0.1"
    assert p["wave"] == "W9" and p["status"] == "validated"
    assert p["historical_identities"] == 4
    assert p["canonical_processing_objects"] == 4
    assert p["source_pages"] == 448
    assert p["book_page_records"] == W9_PAGES
    assert p["unique_page_key_hashes"] == 448
    assert p["sqlite_page_rows"] == 448 and p["fts_rows"] == 448 and p["qc_page_records"] == 448
    assert p["source_gaps"] == 0 and p["aliases"] == 0
    assert p["archival_complete"] is False
    assert p["text_verified"] is False and p["semantic_ready"] is False
    products = p["products"]
    assert len(products) == 24
    assert Counter(x["viewer_key"] for x in products) == Counter({k:6 for k in W9_PAGES})
    assert Counter(x["class"] for x in products) == Counter({"restricted_products":12,"text_free_products":12})
    assert all(int(x["bytes"]) > 0 and len(x["sha256"]) == 64 for x in products)
    no_private_locator(p)


def validate_closure(p: dict) -> None:
    assert p["schema"] == "LTMD_FTRL_ARCHIVAL_CLOSURE_0.6"
    assert p["wave"] == "W9" and p["archival_complete"] is True
    assert p["ftrl"] == {
        "canonical_processing_objects": 4,
        "commit": W9_COMMIT,
        "distributed_books": 4,
        "fts_rows": 448,
        "global_exact_union": True,
        "historical_identities": 4,
        "page_partition_complete": True,
        "page_partition_unique": True,
        "page_records": 448,
        "run_id": W9_RUN,
        "sqlite_integrity": "ok",
        "status": "validated",
    }
    a = p["persistent_archive"]
    assert a["destination_shared"] is False
    assert a["encrypted_handoffs_preserved"] is True and a["encrypted_handoffs_unique"] == 4
    assert a["private_consolidation_validated"] is True
    assert a["archive_closure_record_preserved"] is True
    assert a["redownload_checksum_verification_complete"] is True
    assert a["restricted_plaintext_publicly_exposed"] is False
    assert a["text_free_evidence_preserved"] is True
    assert a["consolidated_archive_bytes"] == 684934
    assert a["consolidated_archive_sha256"] == "3e34f01c24ebde8f2ad9f7eeac2137234440710f50e04f0d0b62b71b6b9245e3"
    assert a["logical_destination"] == W9_ARCHIVE
    q = p["qc"]
    assert q["page_records"] == 448
    assert q["pages_flagged_for_technical_review"] == 58
    assert q["pages_unflagged"] == 390
    assert q["zero_search_text_pages"] == 20
    assert q["pages_flagged_for_technical_review"] + q["pages_unflagged"] == 448
    assert p["security"]["plaintext_restricted_outputs_published"] is False
    assert p["security"]["private_key_stored_outside_public_repository"] is True
    assert p["text_verified"] is False and p["semantic_ready"] is False
    no_private_locator(p)


def validate_processing(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    assert len(rows) == 4 and {r["viewer_key"] for r in rows} == set(W9_PAGES)
    assert all(r["source_status"] == "SOURCE_ADMISSIBLE" for r in rows)
    assert all(r["processing_mode"] == "direct_canonical" for r in rows)
    assert all(r["is_canonical_processing_object"] == "1" for r in rows)
    assert all(r["ocr_identity_eligible"] == "1" for r in rows)
    assert all(int(r["persistent_internal_source_gaps"]) == 0 for r in rows)
    assert all(int(r["probe_errors"]) == 0 for r in rows)
    assert all(r["semantic_state"] == "WAITING_HUMAN_REFERENCE" for r in rows)
    assert all(r["alias_state"] == "no_alias" for r in rows)
    for r in rows:
        viewer = r["viewer_key"]
        assert int(r["source_page_count"]) == W9_PAGES[viewer]
        assert int(r["declared_positions"]) == W9_PAGES[viewer] + 1
    return {r["viewer_key"]: r for r in rows}


def validate_base(rows: list[dict[str, str]]) -> set[str]:
    assert len(rows) == 542 and len({r["viewer_key"] for r in rows}) == 542
    versions = {r["ledger_version"] for r in rows}
    assert versions in ({OLD_VERSION}, {VERSION})
    for wave, count in (("W1",40),("W3",130),("W4",14),("W5",18),("W6",42)):
        wr = [r for r in rows if r["wave"] == wave]
        assert len(wr) == count
        assert Counter(r["ftrl_status"] for r in wr) == Counter({"validated":count})
        assert Counter(r["archival_status"] for r in wr) == Counter({"archival_complete":count})
    w9 = [r for r in rows if r["wave"] == "W9"]
    assert len(w9) == 4
    if versions == {OLD_VERSION}:
        assert Counter(r["ftrl_status"] for r in w9) == Counter({"pending":4})
        assert Counter(r["archival_status"] for r in w9) == Counter({"not_started":4})
    else:
        assert Counter(r["ftrl_status"] for r in w9) == Counter({"validated":4})
        assert Counter(r["archival_status"] for r in w9) == Counter({"archival_complete":4})
    return versions


def promote(rows: list[dict[str, str]], by: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for original in rows:
        row = dict(original)
        row["ledger_version"] = VERSION
        if row["wave"] == "W9":
            p = by[row["viewer_key"]]
            assert row["documentary_disposition"] == "required_ftrl_processing"
            row["source_ready"] = "full"
            row["relation_type"] = "direct_canonical"
            row["canonical_processing_viewer_key"] = row["viewer_key"]
            row["is_canonical_processing_object"] = "1"
            row["declared_positions"] = p["declared_positions"]
            row["canonical_source_pages"] = p["source_page_count"]
            row["persistent_unresolved_source_gaps"] = "0"
            row["ftrl_status"] = "validated"
            row["ftrl_run_id"] = W9_RUN
            row["ftrl_commit"] = W9_COMMIT
            row["corpus_ready"] = "1"
            row["ocr_available"] = "1"
            row["text_verified"] = "0"
            row["semantic_ready"] = "0"
            row["archival_status"] = "archival_complete"
            row["preservation_run_id"] = "private_consolidation_2026-08-27"
            row["archive_destination_logical"] = W9_ARCHIVE
            row["interpretive_limit"] = "Computational/archival closure only; OCR is not human text verification or semantic evidence."
        out.append(row)
    assert {r["viewer_key"] for r in out if r["wave"] == "W9"} == set(by)
    return out


def build_summary(rows: list[dict[str, str]]) -> dict:
    dispositions = Counter(r["documentary_disposition"] for r in rows)
    assert dispositions == Counter({"required_ftrl_processing":524,"active_retention":13,"final_exception":5})
    waves = Counter(r["wave"] for r in rows)
    assert waves == Counter({"W1":40,"W2":64,"W3":130,"W4":14,"W5":18,"W6":42,"W7":30,"W8":20,"W9":4,"W10":69,"W11":111})
    w9 = [r for r in rows if r["wave"] == "W9"]
    assert Counter(r["ftrl_status"] for r in w9) == Counter({"validated":4})
    assert Counter(r["archival_status"] for r in w9) == Counter({"archival_complete":4})
    assert Counter(r["source_ready"] for r in w9) == Counter({"full":4})
    assert Counter(r["relation_type"] for r in w9) == Counter({"direct_canonical":4})
    assert sum(r["is_canonical_processing_object"] == "1" for r in w9) == 4
    assert sum(int(r["canonical_source_pages"] or 0) for r in w9) == 448
    assert sum(int(r["persistent_unresolved_source_gaps"] or 0) for r in w9) == 0

    canonical = Counter(); pages = Counter()
    for r in rows:
        if r["is_canonical_processing_object"] == "1":
            canonical[r["ftrl_status"]] += 1
            if r["canonical_source_pages"]:
                pages[r["ftrl_status"]] += int(r["canonical_source_pages"])
    ftrl = Counter(r["ftrl_status"] for r in rows)
    archival = Counter(r["archival_status"] for r in rows)
    validated = ftrl["validated"]
    terminal = validated + dispositions["final_exception"]
    remaining = len(rows) - terminal
    pending = ftrl["pending"]
    assert validated == 248 and terminal == 253 and remaining == 289 and pending == 276
    assert canonical == Counter({"validated":220})
    assert pages == Counter({"validated":38054})
    assert archival == Counter({"not_started":289,"archival_complete":248,"not_applicable_final_exception":5})
    return {
      "schema": SUMMARY_SCHEMA,
      "ledger_version": VERSION,
      "status": "valid",
      "documentary_identities": len(rows),
      "wave_denominators": dict(sorted(waves.items())),
      "documentary_dispositions": dict(sorted(dispositions.items())),
      "source_readiness": dict(sorted(Counter(r["source_ready"] for r in rows).items())),
      "known_processing_topology_identities": sum(bool(r["canonical_processing_viewer_key"]) for r in rows),
      "ftrl_identity_status": dict(sorted(ftrl.items())),
      "canonical_processing_objects_by_ftrl_status": dict(sorted(canonical.items())),
      "canonical_source_pages_by_ftrl_status": dict(sorted(pages.items())),
      "corpus_ready_identities": sum(int(r["corpus_ready"]) for r in rows),
      "ocr_available_identities": sum(int(r["ocr_available"]) for r in rows),
      "text_verified_identities": sum(int(r["text_verified"]) for r in rows),
      "semantic_ready_identities": sum(int(r["semantic_ready"]) for r in rows),
      "archival_status": dict(sorted(archival.items())),
      "strict_identity_progress": {
        "terminal_identities": terminal,
        "terminal_fraction": round(terminal/len(rows), 6),
        "remaining_identities": remaining,
        "remaining_fraction": round(remaining/len(rows), 6),
        "processable_pending": pending,
        "active_retentions": 13,
        "definition": "validated FTRL identities plus documented final exceptions over the fixed 542-identity denominator"
      },
      "global_closure": {
        "eligible": False,
        "reason": "active retentions and unfinished FTRL waves remain; archival completion is incomplete outside validated waves",
        "active_retentions": 13,
        "final_exceptions": 5
      },
      "epistemic_guards": [
        "topology_ready != corpus_ready",
        "preflight_ready != ftrl_validated",
        "corpus_ready != semantic_ready",
        "ocr_available != text_verified",
        "search_hit != historical_claim",
        "zero_hits != demonstrated_absence",
        "computationally_validated != archival_complete"
      ]
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--output", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    args = ap.parse_args()
    validate_global(json.loads(W9_GLOBAL.read_text(encoding="utf-8")))
    validate_closure(json.loads(W9_CLOSURE.read_text(encoding="utf-8")))
    by = validate_processing(read_csv(W9_PROCESSING))
    rows = read_csv(args.input)
    validate_base(rows)
    rows = promote(rows, by)
    summary = build_summary(rows)
    write_csv(args.output, rows)
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
