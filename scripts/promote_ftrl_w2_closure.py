#!/usr/bin/env python3
"""Promote W2 Mathematics after computational and private archival closure.

Only source-admitted W2 identities are promoted. The four unresolved DMA 2018
identities remain active retentions and are never inferred from 2019 editions.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
WAVE_STATE = Path("data/research/ltmd_u1_ftrl_wave_state.json")
SCOPE = Path("data/catalog/ltmd_u1_w2_scope.csv")
RECON_SUMMARY = Path("data/catalog/ltmd_u1_w2_math_reconciled_summary.csv")
ALIASES = Path("data/catalog/ltmd_u1_w2_math_reconciled_exact_aliases.csv")
REQUEST = Path("data/research/ltmd_u1_w2_closure_promotion_request.json")
CLOSURE = Path("data/research/ltmd_u1_w2_archival_closure.json")

TARGET_LEDGER_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_1.0"
TARGET_SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_1.0"
SOURCE_RUN_ID = "33291984081"
SOURCE_COMMIT = "29f31430ab542ed3c9098446e0af9136515dc581"
PRESERVATION_RUN_ID = "private_consolidation_2026-08-30"
ARCHIVE_DESTINATION = (
    "LTMD-U1 — corpus FTRL privado/W2 — Matemáticas/"
    "run_33291984081__29f3143__2026-08-30/02_CONSOLIDATED_PRIVATE"
)
EXPECTED_WITHHELD = {"H2018P3DMA", "H2018P4DMA", "H2018P5DMA", "H2018P6DMA"}
EXPECTED_ALIAS = {
    "H1982P4MA388": "H1972P4MA083",
    "H1982P5MA394": "H1972P5MA089",
    "H1982P6MA399": "H1972P6MA094",
}
INTERPRETIVE_LIMIT = (
    "Computational/archival closure of source-admitted W2 only; four DMA 2018 "
    "identities remain documented active retentions and excluded; OCR is not "
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
    assert request["schema"] == "LTMD_U1_W2_CLOSURE_PROMOTION_REQUEST_1.0"
    assert request["wave"] == "W2"
    assert request["source_run_id"] == int(SOURCE_RUN_ID)
    assert request["source_commit"] == SOURCE_COMMIT
    assert request["computationally_validated"] is True
    assert request["archival_complete"] is True
    assert request["text_verified"] is False
    assert request["semantic_ready"] is False
    assert request["historical_identities"] == 64
    assert request["admitted_historical_identities"] == 60
    assert request["canonical_processing_objects"] == 57
    assert request["exact_source_aliases"] == 3
    assert request["source_pages"] == 11945
    assert request["active_retentions"] == 4
    assert request["private_archive"]["drive_readback_sha256_verified"] is True
    assert request["manifest_bundle"]["drive_readback_sha256_verified"] is True
    assert request["public_evidence_archive"]["drive_readback_sha256_verified"] is True

    scope_rows = read_csv(SCOPE)
    recon_rows = read_csv(RECON_SUMMARY)
    alias_rows = read_csv(ALIASES)
    assert len(scope_rows) == len(recon_rows) == 64
    scope = {r["viewer_key"]: r for r in scope_rows}
    recon = {r["viewer_key"]: r for r in recon_rows}
    assert set(scope) == set(recon)

    admitted = {k for k, r in recon.items() if n(r, "effective_asset_ready") == 1}
    withheld = set(scope) - admitted
    assert len(admitted) == 60
    assert withheld == EXPECTED_WITHHELD
    assert all(n(recon[k], "effective_unresolved") > 0 for k in withheld)

    aliases = {
        r["viewer_key"]: r["canonical_viewer_key"]
        for r in alias_rows
        if n(r, "all_effective_pages_byte_identical_aligned") == 1
    }
    assert aliases == EXPECTED_ALIAS
    canonical = admitted - set(aliases)
    assert len(canonical) == 57
    assert set(aliases.values()) <= canonical
    assert sum(n(recon[k], "effective_real_jpeg") for k in canonical) == 11945
    assert all(n(recon[k], "effective_unresolved") == 0 for k in admitted)

    with LEDGER.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    assert len(rows) == 542
    w2 = [r for r in rows if r["wave"] == "W2"]
    assert len(w2) == 64
    assert {r["viewer_key"] for r in w2} == set(scope)

    before_other = [
        {k: v for k, v in r.items() if k != "ledger_version"}
        for r in rows if r["wave"] != "W2"
    ]

    for row in rows:
        row["ledger_version"] = TARGET_LEDGER_VERSION
        if row["wave"] != "W2":
            continue
        viewer = row["viewer_key"]
        if viewer in withheld:
            assert row["documentary_disposition"] == "active_retention"
            assert row["ftrl_status"] == "blocked_active_retention"
            assert row["archival_status"] == "not_started"
            row["text_verified"] = "0"
            row["semantic_ready"] = "0"
            continue

        assert row["documentary_disposition"] == "required_ftrl_processing"
        s = recon[viewer]
        row["source_ready"] = "full"
        if viewer in aliases:
            target = aliases[viewer]
            row["relation_type"] = "exact_byte_alias"
            row["canonical_processing_viewer_key"] = target
            row["is_canonical_processing_object"] = "0"
            row["canonical_source_pages"] = str(n(recon[target], "effective_real_jpeg"))
        else:
            assert viewer in canonical
            row["relation_type"] = "direct_canonical"
            row["canonical_processing_viewer_key"] = viewer
            row["is_canonical_processing_object"] = "1"
            row["canonical_source_pages"] = str(n(s, "effective_real_jpeg"))
        row["declared_positions"] = str(n(s, "declared_rows"))
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

    after_other = [
        {k: v for k, v in r.items() if k != "ledger_version"}
        for r in rows if r["wave"] != "W2"
    ]
    assert after_other == before_other, "non-W2 records changed during W2 promotion"

    w2_after = [r for r in rows if r["wave"] == "W2"]
    assert Counter(r["ftrl_status"] for r in w2_after) == Counter({"validated": 60, "blocked_active_retention": 4})
    assert Counter(r["archival_status"] for r in w2_after) == Counter({"archival_complete": 60, "not_started": 4})
    assert sum(int(r["is_canonical_processing_object"] or 0) for r in w2_after) == 57
    assert sum(int(r["canonical_source_pages"] or 0) for r in w2_after if r["is_canonical_processing_object"] == "1") == 11945
    assert {r["viewer_key"] for r in w2_after if r["ftrl_status"] == "blocked_active_retention"} == EXPECTED_WITHHELD
    for alias, target in EXPECTED_ALIAS.items():
        r = next(x for x in w2_after if x["viewer_key"] == alias)
        assert r["relation_type"] == "exact_byte_alias"
        assert r["canonical_processing_viewer_key"] == target
        assert r["is_canonical_processing_object"] == "0"

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
    assert ftrl_status == {"blocked_active_retention": 13, "final_exception": 5, "validated": 524}
    assert archival_status == {"archival_complete": 524, "not_applicable_final_exception": 5, "not_started": 13}
    assert source_readiness == {"full": 499, "partial": 7, "unresolved": 36}
    assert dict(canonical_by_status) == {"validated": 492}
    assert dict(pages_by_status) == {"validated": 86549}
    assert validated == 524 and terminal == 529 and remaining == 13 and processable_pending == 0

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
            "reason": "all processable FTRL waves are computationally and archivally complete; 13 documented active retentions remain outside source-admitted computation",
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
    assert summary["corpus_ready_identities"] == 524
    assert summary["ocr_available_identities"] == 524
    assert summary["known_processing_topology_identities"] == 524
    assert summary["text_verified_identities"] == 0
    assert summary["semantic_ready_identities"] == 0
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    wave_state = json.loads(WAVE_STATE.read_text(encoding="utf-8"))
    wave_state["waves"]["W2"] = {
        "domain": "matematicas",
        "ftrl_status": "validated",
        "ftrl_run_id": SOURCE_RUN_ID,
        "ftrl_commit": SOURCE_COMMIT,
        "archival_status": "archival_complete",
        "preservation_run_id": PRESERVATION_RUN_ID,
        "archive_destination_logical": ARCHIVE_DESTINATION,
        "archival_closure_evidence": str(CLOSURE),
    }
    WAVE_STATE.write_text(json.dumps(wave_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    closure = {
        "schema": "LTMD_FTRL_ARCHIVAL_CLOSURE_1.0",
        "effective_date": "2026-08-30",
        "wave": "W2",
        "domain": "matematicas",
        "archival_complete": True,
        "ftrl": {
            "computationally_validated": True,
            "source_run_id": int(SOURCE_RUN_ID),
            "source_commit": SOURCE_COMMIT,
            "historical_identities": 64,
            "admitted_historical_identities": 60,
            "canonical_processing_objects": 57,
            "exact_source_aliases": 3,
            "source_pages": 11945,
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
            "status": "documented_active_retention",
        },
        "qc": {
            "source_pages": 11945,
            "unique_page_key_hashes": 11945,
            "sqlite_page_rows": 11945,
            "fts_rows": 11945,
            "qc_page_records": 11945,
            "source_gaps_in_admitted_canonical_objects": 0,
        },
        "security": {
            "private_public_pairing_exact": True,
            "plaintext_restricted_outputs_present": False,
            "private_handoffs_encrypted": True,
        },
        "text_verified": False,
        "semantic_ready": False,
        "interpretive_limit": INTERPRETIVE_LIMIT,
    }
    CLOSURE.write_text(json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "wave": "W2",
        "validated_identities": 60,
        "active_retentions": 4,
        "canonical_processing_objects": 57,
        "source_pages": 11945,
        "global_validated_identities": validated,
        "global_processable_pending": processable_pending,
        "global_active_retentions": active_retentions,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
