#!/usr/bin/env python3
"""Promote LTMD-U1 completion ledger 0.8 to 0.9 after verified W10 closure.

This is a metadata-only promoter. It is deliberately unusable until both the
text-free global computational evidence and a persistent private archival
closure record for W10 exist. It promotes only the 68 source-admitted W10
identities. H2014P1ENA remains an active source retention and is never aliased,
imputed, or counted as corpus-ready.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

W10_GATE = Path("data/catalog/ltmd_u1_w10_source_admissibility.csv")
W10_GLOBAL = Path("data/research/ltmd_u1_w10_global_evidence.json")
W10_CLOSURE = Path("data/research/ltmd_u1_w10_archival_closure.json")
DEFAULT_LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
DEFAULT_SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
OLD_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.8"
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.9"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.9"
WITHHELD = {"H2014P1ENA"}
EXPECTED_HISTORICAL = 69
EXPECTED_ADMITTED = 68
EXPECTED_PAGES = 11937
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise AssertionError("refusing to write an empty completion ledger")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def no_private_locator(value) -> None:
    if isinstance(value, dict):
        forbidden = {"drive_id", "file_id", "folder_id", "drive_url", "private_url", "private_key", "passphrase"}
        overlap = forbidden & set(value)
        assert not overlap, f"public W10 evidence exposes private locator/key material: {overlap}"
        for child in value.values():
            no_private_locator(child)
    elif isinstance(value, list):
        for child in value:
            no_private_locator(child)
    elif isinstance(value, str):
        lowered = value.lower()
        assert "drive.google.com" not in lowered
        assert "docs.google.com" not in lowered
        assert "begin private key" not in lowered


def validate_gate(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    assert len(rows) == EXPECTED_HISTORICAL
    assert len({r["viewer_key"] for r in rows}) == EXPECTED_HISTORICAL
    admitted = [r for r in rows if int(r["ocr_source_admitted"]) == 1]
    withheld = [r for r in rows if int(r["ocr_source_admitted"]) == 0]
    assert len(admitted) == EXPECTED_ADMITTED
    assert len(withheld) == 1
    assert {r["viewer_key"] for r in withheld} == WITHHELD
    assert all(r["source_state"] == "admitted_direct" for r in admitted)
    assert all(int(r["internal_unserved"]) == 0 and int(r["probe_errors"]) == 0 for r in admitted)
    assert all(int(r["source_jpegs"]) > 0 for r in admitted)
    assert sum(int(r["source_jpegs"]) for r in admitted) == EXPECTED_PAGES
    retained = withheld[0]
    assert retained["source_state"] == "withheld_internal_unserved"
    assert int(retained["internal_unserved"]) > 0 and int(retained["probe_errors"]) == 0
    return ({r["viewer_key"]: r for r in admitted}, {r["viewer_key"]: r for r in withheld})


def validate_global(p: dict, admitted: dict[str, dict[str, str]]) -> dict[str, int]:
    assert p["schema"] == "LTMD_FTRL_W10_GLOBAL_EVIDENCE_0.1"
    assert p["wave"] == "W10" and p["status"] == "validated"
    assert p["historical_identities"] == EXPECTED_HISTORICAL
    assert p["canonical_processing_objects"] == EXPECTED_ADMITTED
    assert p["withheld_source_identities"] == 1
    assert set(p["withheld_viewer_keys"]) == WITHHELD
    assert p["source_pages"] == EXPECTED_PAGES
    assert p["unique_page_key_hashes"] == EXPECTED_PAGES
    assert p["sqlite_page_rows"] == EXPECTED_PAGES
    assert p["fts_rows"] == EXPECTED_PAGES
    assert p["qc_page_records"] == EXPECTED_PAGES
    assert p["source_gaps_in_admitted_canonical_objects"] == 0
    assert p["aliases_for_withheld_identities"] == 0
    assert p["archival_complete"] is False
    assert p["text_verified"] is False and p["semantic_ready"] is False
    pages = {k: int(v) for k, v in p["book_page_records"].items()}
    assert set(pages) == set(admitted)
    assert sum(pages.values()) == EXPECTED_PAGES
    for viewer, row in admitted.items():
        assert pages[viewer] == int(row["source_jpegs"])
    products = p["products"]
    assert len(products) == EXPECTED_ADMITTED * 6
    assert Counter(x["viewer_key"] for x in products) == Counter({k: 6 for k in admitted})
    assert Counter(x["class"] for x in products) == Counter({"restricted_products": EXPECTED_ADMITTED * 3, "text_free_products": EXPECTED_ADMITTED * 3})
    assert all(int(x["bytes"]) > 0 and SHA256.fullmatch(x["sha256"]) for x in products)
    no_private_locator(p)
    return pages


def validate_closure(p: dict, global_evidence: dict) -> tuple[str, str, str, str]:
    assert p["schema"] == "LTMD_FTRL_ARCHIVAL_CLOSURE_0.9"
    assert p["wave"] == "W10" and p["archival_complete"] is True
    assert p["domain"] in {"Integrados/Multiarea", "integrados_multiarea"}
    f = p["ftrl"]
    assert f["historical_identities"] == EXPECTED_HISTORICAL
    assert f["canonical_processing_objects"] == EXPECTED_ADMITTED
    assert f["withheld_source_identities"] == 1
    assert f["distributed_books"] == EXPECTED_ADMITTED
    assert f["page_records"] == EXPECTED_PAGES and f["fts_rows"] == EXPECTED_PAGES
    assert f["status"] == "validated"
    assert f["global_exact_union"] is True
    assert f["page_partition_complete"] is True and f["page_partition_unique"] is True
    assert f["sqlite_integrity"] == "ok"
    assert str(f["run_id"]).strip()
    assert SHA256.fullmatch(f["commit"])

    a = p["persistent_archive"]
    assert a["destination_shared"] is False
    assert a["encrypted_handoffs_preserved"] is True
    assert a["encrypted_handoffs_unique"] == EXPECTED_ADMITTED
    assert a["private_consolidation_validated"] is True
    assert a["archive_closure_record_preserved"] is True
    assert a["redownload_checksum_verification_complete"] is True
    assert a["restricted_plaintext_publicly_exposed"] is False
    assert a["text_free_evidence_preserved"] is True
    assert a["text_free_evidence_unique"] == EXPECTED_ADMITTED + 1
    assert int(a["consolidated_archive_bytes"]) > 0
    assert SHA256.fullmatch(a["consolidated_archive_sha256"])
    assert str(a["logical_destination"]).startswith("LTMD-U1 — corpus FTRL privado/W10")

    sr = p["source_retention"]
    assert sr["count"] == 1
    assert set(sr["viewer_keys"]) == WITHHELD
    assert sr["aliases_introduced"] == 0
    assert p["security"]["plaintext_restricted_outputs_published"] is False
    assert p["security"]["private_key_stored_outside_public_repository"] is True
    assert p["text_verified"] is False and p["semantic_ready"] is False

    # Closure and global evidence must refer to the same validated computation.
    assert global_evidence["canonical_processing_objects"] == f["canonical_processing_objects"]
    assert global_evidence["source_pages"] == f["page_records"]
    assert global_evidence["fts_rows"] == f["fts_rows"]
    no_private_locator(p)
    return str(f["run_id"]), f["commit"], a["logical_destination"], p["effective_date"]


def validate_base(rows: list[dict[str, str]], admitted: set[str], withheld: set[str]) -> set[str]:
    assert len(rows) == 542 and len({r["viewer_key"] for r in rows}) == 542
    versions = {r["ledger_version"] for r in rows}
    assert versions in ({OLD_VERSION}, {VERSION})
    dispositions = Counter(r["documentary_disposition"] for r in rows)
    assert dispositions == Counter({"required_ftrl_processing": 524, "active_retention": 13, "final_exception": 5})
    waves = Counter(r["wave"] for r in rows)
    assert waves == Counter({"W1": 40, "W2": 64, "W3": 130, "W4": 14, "W5": 18, "W6": 42, "W7": 30, "W8": 20, "W9": 4, "W10": 69, "W11": 111})

    w10 = [r for r in rows if r["wave"] == "W10"]
    assert len(w10) == EXPECTED_HISTORICAL
    assert {r["viewer_key"] for r in w10} == admitted | withheld
    retained = [r for r in w10 if r["viewer_key"] in withheld]
    assert len(retained) == 1
    assert retained[0]["documentary_disposition"] == "active_retention"
    assert retained[0]["ftrl_status"] == "blocked_active_retention"
    assert retained[0]["archival_status"] == "not_started"
    assert retained[0]["is_canonical_processing_object"] == "0"
    assert retained[0]["corpus_ready"] == "0" and retained[0]["ocr_available"] == "0"

    proc = [r for r in w10 if r["viewer_key"] in admitted]
    assert len(proc) == EXPECTED_ADMITTED
    assert all(r["documentary_disposition"] == "required_ftrl_processing" for r in proc)
    if versions == {OLD_VERSION}:
        assert all(r["ftrl_status"] == "pending" and r["archival_status"] == "not_started" for r in proc)
        assert all(r["corpus_ready"] == "0" and r["ocr_available"] == "0" for r in proc)
    else:
        assert all(r["ftrl_status"] == "validated" and r["archival_status"] == "archival_complete" for r in proc)
        assert all(r["corpus_ready"] == "1" and r["ocr_available"] == "1" for r in proc)
    return versions


def promote(rows: list[dict[str, str]], gate: dict[str, dict[str, str]], pages: dict[str, int], run_id: str, commit: str, archive: str, effective_date: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for original in rows:
        row = dict(original)
        row["ledger_version"] = VERSION
        viewer = row["viewer_key"]
        if viewer in gate:
            g = gate[viewer]
            assert row["wave"] == "W10"
            row["source_ready"] = "full"
            row["relation_type"] = "direct_canonical"
            row["canonical_processing_viewer_key"] = viewer
            row["is_canonical_processing_object"] = "1"
            row["declared_positions"] = g["declared_positions"]
            row["canonical_source_pages"] = str(pages[viewer])
            row["persistent_unresolved_source_gaps"] = "0"
            row["ftrl_status"] = "validated"
            row["ftrl_run_id"] = run_id
            row["ftrl_commit"] = commit
            row["corpus_ready"] = "1"
            row["ocr_available"] = "1"
            row["text_verified"] = "0"
            row["semantic_ready"] = "0"
            row["archival_status"] = "archival_complete"
            row["preservation_run_id"] = f"private_consolidation_{effective_date}"
            row["archive_destination_logical"] = archive
            row["interpretive_limit"] = "Computational/archival closure of source-admitted W10 only; H2014P1ENA remains retained and excluded; OCR is not human text verification or semantic evidence."
        out.append(row)
    return out


def build_summary(rows: list[dict[str, str]]) -> dict:
    dispositions = Counter(r["documentary_disposition"] for r in rows)
    assert dispositions == Counter({"required_ftrl_processing": 524, "active_retention": 13, "final_exception": 5})
    waves = Counter(r["wave"] for r in rows)
    ftrl = Counter(r["ftrl_status"] for r in rows)
    archival = Counter(r["archival_status"] for r in rows)
    assert ftrl == Counter({"validated": 357, "pending": 167, "blocked_active_retention": 13, "final_exception": 5})
    assert archival == Counter({"archival_complete": 357, "not_started": 180, "not_applicable_final_exception": 5})

    canonical = Counter()
    pages = Counter()
    for r in rows:
        if r["is_canonical_processing_object"] == "1":
            canonical[r["ftrl_status"]] += 1
            if r["canonical_source_pages"]:
                pages[r["ftrl_status"]] += int(r["canonical_source_pages"])
    assert canonical["validated"] == 329
    assert pages["validated"] == 54742

    corpus_ready = sum(int(r["corpus_ready"]) for r in rows)
    ocr_available = sum(int(r["ocr_available"]) for r in rows)
    text_verified = sum(int(r["text_verified"]) for r in rows)
    semantic_ready = sum(int(r["semantic_ready"]) for r in rows)
    assert corpus_ready == ocr_available == 357
    assert text_verified == semantic_ready == 0

    source_readiness = Counter(r["source_ready"] for r in rows)
    validated = ftrl["validated"]
    final_exceptions = dispositions["final_exception"]
    active_retentions = dispositions["active_retention"]
    terminal = validated + final_exceptions
    remaining = len(rows) - terminal
    assert terminal == 362 and remaining == 180

    pending = ftrl["pending"]
    eligible = pending == 0 and active_retentions == 0
    reason = "all required FTRL processing and archival closure complete" if eligible else "active retentions and unfinished FTRL waves remain; archival completion is incomplete outside validated waves"

    return {
        "schema": SUMMARY_SCHEMA,
        "status": "valid",
        "ledger_version": VERSION,
        "documentary_identities": len(rows),
        "documentary_dispositions": dict(sorted(dispositions.items())),
        "wave_denominators": dict(sorted(waves.items())),
        "source_readiness": dict(sorted(source_readiness.items())),
        "ftrl_identity_status": dict(sorted(ftrl.items())),
        "archival_status": dict(sorted(archival.items())),
        "known_processing_topology_identities": validated,
        "canonical_processing_objects_by_ftrl_status": dict(sorted(canonical.items())),
        "canonical_source_pages_by_ftrl_status": dict(sorted(pages.items())),
        "corpus_ready_identities": corpus_ready,
        "ocr_available_identities": ocr_available,
        "text_verified_identities": text_verified,
        "semantic_ready_identities": semantic_ready,
        "strict_identity_progress": {
            "definition": "validated FTRL identities plus documented final exceptions over the fixed 542-identity denominator",
            "terminal_identities": terminal,
            "terminal_fraction": round(terminal / len(rows), 6),
            "remaining_identities": remaining,
            "remaining_fraction": round(remaining / len(rows), 6),
            "processable_pending": pending,
            "active_retentions": active_retentions,
        },
        "global_closure": {
            "eligible": eligible,
            "active_retentions": active_retentions,
            "final_exceptions": final_exceptions,
            "reason": reason,
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = ap.parse_args()

    # Missing evidence is an intentional hard stop, not a recoverable condition.
    for required in (W10_GATE, W10_GLOBAL, W10_CLOSURE, args.ledger):
        if not required.is_file():
            raise SystemExit(f"W10 ledger 0.9 promotion blocked: missing required evidence {required}")

    gate, withheld = validate_gate(read_csv(W10_GATE))
    global_evidence = json.loads(W10_GLOBAL.read_text(encoding="utf-8"))
    closure = json.loads(W10_CLOSURE.read_text(encoding="utf-8"))
    pages = validate_global(global_evidence, gate)
    run_id, commit, archive, effective_date = validate_closure(closure, global_evidence)

    rows = read_csv(args.ledger)
    versions = validate_base(rows, set(gate), set(withheld))
    promoted = rows if versions == {VERSION} else promote(rows, gate, pages, run_id, commit, archive, effective_date)
    validate_base(promoted, set(gate), set(withheld))
    summary = build_summary(promoted)

    write_csv(args.ledger, promoted)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "ledger_version": VERSION, "validated": 357, "pending": 167, "w10_promoted": 68}, sort_keys=True))


if __name__ == "__main__":
    main()
