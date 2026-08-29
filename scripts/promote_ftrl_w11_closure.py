#!/usr/bin/env python3
"""Promote W11 FTRL after computational and private archival closure.

This script only mutates W11 rows plus global version/summary metadata. W2 and
all other wave records must remain semantically unchanged.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
WAVE_STATE = Path("data/research/ltmd_u1_ftrl_wave_state.json")
SOURCE_GATE = Path("data/catalog/ltmd_u1_w11_source_admissibility.csv")
TOPOLOGY = Path("data/catalog/ltmd_u1_w11_processing_inventory.csv")
REQUEST = Path("data/research/ltmd_u1_w11_closure_promotion_request.json")
CLOSURE = Path("data/research/ltmd_u1_w11_archival_closure.json")

TARGET_LEDGER_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_1.0"
TARGET_SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_1.0"
SOURCE_RUN_ID = "33266902987"
SOURCE_COMMIT = "e46290d5f06b29d7a48a728037816e9f2cfb1bb5"
PRESERVATION_RUN_ID = "private_consolidation_2026-08-29"
ARCHIVE_DESTINATION = (
    "LTMD-U1 — corpus FTRL privado/W11 — Otros y No clasificados/"
    "run_33266902987__e46290d__2026-08-29/02_CONSOLIDATED_PRIVATE"
)
EXPECTED_WITHHELD = {"H2014P1EAM", "H2014P2EAM", "H2014P3COL", "H2014P3MOR"}
EXPECTED_ALIAS = {"H2008P4CI270": "H1993P4CI192"}
INTERPRETIVE_LIMIT = (
    "Computational/archival closure of source-admitted W11 only; four retained "
    "identities remain documented final exceptions and excluded; OCR is not "
    "human text verification or semantic evidence."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def n(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value in {"", None}:
        raise AssertionError(f"missing {key}: {row}")
    return int(float(value))


def counter_dict(values) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def main() -> None:
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    assert request["wave"] == "W11"
    assert request["source_run_id"] == int(SOURCE_RUN_ID)
    assert request["source_commit"] == SOURCE_COMMIT
    assert request["computationally_validated"] is True
    assert request["archival_complete"] is True
    assert request["text_verified"] is False
    assert request["semantic_ready"] is False
    assert request["canonical_processing_objects"] == 106
    assert request["admitted_historical_identities"] == 107
    assert request["source_pages"] == 19862
    assert request["private_archive"]["drive_readback_sha256_verified"] is True
    assert request["manifest_bundle"]["drive_readback_sha256_verified"] is True
    assert request["public_evidence_archive"]["drive_readback_sha256_verified"] is True

    gate_rows = read_csv(SOURCE_GATE)
    topology_rows = read_csv(TOPOLOGY)
    assert len(gate_rows) == len(topology_rows) == 111
    gate = {r["viewer_key"]: r for r in gate_rows}
    topology = {r["viewer_key"]: r for r in topology_rows}
    assert set(gate) == set(topology)

    admitted = {k for k, r in gate.items() if n(r, "ocr_source_admitted") == 1}
    withheld = set(gate) - admitted
    assert len(admitted) == 107
    assert withheld == EXPECTED_WITHHELD

    canonical = {
        k for k in admitted
        if topology[k]["processing_mode"] == "direct_canonical"
        and n(topology[k], "is_canonical_processing_object") == 1
    }
    aliases = {
        k: topology[k]["canonical_viewer_key"] for k in admitted
        if topology[k]["processing_mode"] == "exact_source_alias"
        and n(topology[k], "is_canonical_processing_object") == 0
    }
    assert len(canonical) == 106
    assert aliases == EXPECTED_ALIAS
    assert sum(n(topology[k], "source_pages") for k in canonical) == 19862
    assert all(n(gate[k], "internal_unserved") == 0 for k in admitted)
    assert all(n(gate[k], "probe_errors") == 0 for k in admitted)

    with LEDGER.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    assert len(rows) == 542
    before_w2 = [dict(r) for r in rows if r["wave"] == "W2"]
    w11 = [r for r in rows if r["wave"] == "W11"]
    assert len(w11) == 111
    assert {r["viewer_key"] for r in w11} == set(gate)

    for row in rows:
        row["ledger_version"] = TARGET_LEDGER_VERSION
        if row["wave"] != "W11":
            continue
        viewer = row["viewer_key"]
        if viewer in withheld:
            assert row["documentary_disposition"] == "final_exception"
            assert row["ftrl_status"] == "final_exception"
            assert row["archival_status"] == "not_applicable_final_exception"
            continue

        g = gate[viewer]
        t = topology[viewer]
        row["source_ready"] = "full"
        if viewer in aliases:
            target = aliases[viewer]
            row["relation_type"] = "exact_byte_alias"
            row["canonical_processing_viewer_key"] = target
            row["is_canonical_processing_object"] = "0"
            row["canonical_source_pages"] = str(n(topology[target], "source_pages"))
        else:
            assert viewer in canonical
            row["relation_type"] = "direct_canonical"
            row["canonical_processing_viewer_key"] = viewer
            row["is_canonical_processing_object"] = "1"
            row["canonical_source_pages"] = str(n(t, "source_pages"))
        row["declared_positions"] = str(n(g, "declared_positions"))
        row["persistent_unresolved_source_gaps"] = "0"
        row["ftrl_status"] = "validated"
        row["ftrl_run_id"] = SOURCE_RUN_ID
        row["ftrl_commit"] = SOURCE_COMMIT
        row["corpus_ready"] = "1"
        row["ocr_available"] = "1"
        row["text_verified"] = "0"
        row["semantic_ready"] = "0"
        row["archival_status"] = "archival_complete"
        row["preservation_run_id"] = PRESERVATION_RUN_ID
        row["archive_destination_logical"] = ARCHIVE_DESTINATION
        row["interpretive_limit"] = INTERPRETIVE_LIMIT

    after_w2 = [{k: v for k, v in r.items() if k != "ledger_version"} for r in rows if r["wave"] == "W2"]
    before_w2_cmp = [{k: v for k, v in r.items() if k != "ledger_version"} for r in before_w2]
    assert after_w2 == before_w2_cmp, "W2 changed during W11 promotion"

    w11_after = [r for r in rows if r["wave"] == "W11"]
    assert Counter(r["ftrl_status"] for r in w11_after) == Counter({"validated": 107, "final_exception": 4})
    assert Counter(r["archival_status"] for r in w11_after) == Counter({"archival_complete": 107, "not_applicable_final_exception": 4})
    assert sum(int(r["is_canonical_processing_object"] or 0) for r in w11_after) == 106
    assert sum(int(r["canonical_source_pages"] or 0) for r in w11_after if r["is_canonical_processing_object"] == "1") == 19862
    alias_row = next(r for r in w11_after if r["viewer_key"] == "H2008P4CI270")
    assert alias_row["relation_type"] == "exact_byte_alias"
    assert alias_row["canonical_processing_viewer_key"] == "H1993P4CI192"
    assert alias_row["canonical_source_pages"] == "66"

    write_csv(LEDGER, rows, fields)

    dispositions = counter_dict(r["documentary_disposition"] for r in rows)
    ftrl_status = counter_dict(r["ftrl_status"] for r in rows)
    archival_status = counter_dict(r["archival_status"] for r in rows)
    source_readiness = counter_dict(r["source_ready"] for r in rows)
    wave_denominators = counter_dict(r["wave"] for r in rows)
    canonical_by_status: defaultdict[str, int] = defaultdict(int)
    pages_by_status: defaultdict[str, int] = defaultdict(int)
    for r in rows:
        if r["is_canonical_processing_object"] == "1":
            canonical_by_status[r["ftrl_status"]] += 1
            pages_by_status[r["ftrl_status"]] += int(r["canonical_source_pages"] or 0)

    validated = ftrl_status.get("validated", 0)
    final_exceptions = ftrl_status.get("final_exception", 0)
    terminal = validated + final_exceptions
    remaining = len(rows) - terminal
    processable_pending = ftrl_status.get("pending", 0)
    active_retentions = dispositions.get("active_retention", 0)

    assert dispositions == {"active_retention": 13, "final_exception": 5, "required_ftrl_processing": 524}
    assert ftrl_status == {"blocked_active_retention": 13, "final_exception": 5, "pending": 60, "validated": 464}
    assert archival_status == {"archival_complete": 464, "not_applicable_final_exception": 5, "not_started": 73}
    assert source_readiness == {"full": 499, "partial": 7, "unresolved": 36}
    assert dict(canonical_by_status) == {"validated": 435}
    assert dict(pages_by_status) == {"validated": 74604}
    assert validated == 464 and terminal == 469 and remaining == 73 and processable_pending == 60

    summary = {
        "archival_status": archival_status,
        "canonical_processing_objects_by_ftrl_status": dict(sorted(canonical_by_status.items())),
        "canonical_source_pages_by_ftrl_status": dict(sorted(pages_by_status.items())),
        "corpus_ready_identities": sum(int(r["corpus_ready"] or 0) for r in rows),
        "documentary_dispositions": dispositions,
        "documentary_identities": len(rows),
        "epistemic_guards": [
            "topology_ready != corpus_ready",
            "preflight_ready != ftrl_validated",
            "corpus_ready != semantic_ready",
            "ocr_available != text_verified",
            "search_hit != historical_claim",
            "zero_hits != demonstrated_absence",
            "computationally_validated != archival_complete",
        ],
        "ftrl_identity_status": ftrl_status,
        "global_closure": {
            "active_retentions": active_retentions,
            "eligible": False,
            "final_exceptions": final_exceptions,
            "reason": "active retentions and unfinished FTRL wave W2 remain; W11 is computationally and archivally complete",
        },
        "known_processing_topology_identities": sum(1 for r in rows if r["canonical_processing_viewer_key"]),
        "ledger_version": TARGET_LEDGER_VERSION,
        "ocr_available_identities": sum(int(r["ocr_available"] or 0) for r in rows),
        "schema": TARGET_SUMMARY_SCHEMA,
        "semantic_ready_identities": sum(int(r["semantic_ready"] or 0) for r in rows),
        "source_readiness": source_readiness,
        "status": "valid",
        "strict_identity_progress": {
            "active_retentions": active_retentions,
            "definition": "validated FTRL identities plus documented final exceptions over the fixed 542-identity denominator",
            "processable_pending": processable_pending,
            "remaining_fraction": round(remaining / len(rows), 6),
            "remaining_identities": remaining,
            "terminal_fraction": round(terminal / len(rows), 6),
            "terminal_identities": terminal,
        },
        "text_verified_identities": sum(int(r["text_verified"] or 0) for r in rows),
        "wave_denominators": wave_denominators,
    }
    assert summary["corpus_ready_identities"] == 464
    assert summary["ocr_available_identities"] == 464
    assert summary["known_processing_topology_identities"] == 464
    assert summary["text_verified_identities"] == 0
    assert summary["semantic_ready_identities"] == 0
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    wave_state = json.loads(WAVE_STATE.read_text(encoding="utf-8"))
    before_w2_state = json.loads(json.dumps(wave_state["waves"]["W2"]))
    wave_state["waves"]["W11"] = {
        "domain": "otros_no_clasificados",
        "ftrl_status": "validated",
        "ftrl_run_id": SOURCE_RUN_ID,
        "ftrl_commit": SOURCE_COMMIT,
        "archival_status": "archival_complete",
        "preservation_run_id": PRESERVATION_RUN_ID,
        "archive_destination_logical": ARCHIVE_DESTINATION,
        "archival_closure_evidence": str(CLOSURE),
    }
    assert wave_state["waves"]["W2"] == before_w2_state
    WAVE_STATE.write_text(json.dumps(wave_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    closure = {
        "schema": "LTMD_FTRL_ARCHIVAL_CLOSURE_1.0",
        "effective_date": "2026-08-29",
        "wave": "W11",
        "domain": "otros_no_clasificados",
        "archival_complete": True,
        "ftrl": {
            "computationally_validated": True,
            "source_run_id": int(SOURCE_RUN_ID),
            "source_commit": SOURCE_COMMIT,
            "historical_identities": 111,
            "admitted_historical_identities": 107,
            "canonical_processing_objects": 106,
            "exact_source_aliases": 1,
            "source_pages": 19862,
            "global_evidence_artifact_id": request["global_evidence_artifact_id"],
            "global_evidence_artifact_sha256": request["global_evidence_artifact_sha256"],
        },
        "persistent_archive": {
            "provider": "google_drive_private",
            "run_folder_id": request["drive_run_folder_id"],
            "private_archive": request["private_archive"],
            "manifest_bundle": request["manifest_bundle"],
            "public_evidence_archive": request["public_evidence_archive"],
            "all_drive_readbacks_verified": True,
            "partial_checkpoint_removed": True,
            "individual_handoff_folder_empty": True,
        },
        "source_exceptions": {
            "count": 4,
            "viewer_keys": sorted(EXPECTED_WITHHELD),
            "status": "documented_final_exception",
        },
        "security": {
            "private_public_pairing_exact": True,
            "plaintext_restricted_outputs_present": False,
            "private_handoffs_encrypted": True,
        },
        "qc": {
            "source_pages": 19862,
            "sqlite_page_rows": 19862,
            "fts_rows": 19862,
            "qc_page_records": 19862,
            "unique_page_key_hashes": 19862,
            "source_gaps_in_admitted_canonical_objects": 0,
        },
        "text_verified": False,
        "semantic_ready": False,
        "interpretive_limit": INTERPRETIVE_LIMIT,
    }
    CLOSURE.write_text(json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "promoted",
        "w11_validated_identities": 107,
        "w11_canonical_objects": 106,
        "w11_source_pages": 19862,
        "global_validated_identities": validated,
        "remaining_identities": remaining,
        "next_wave": "W2",
        "w2_unchanged": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
