#!/usr/bin/env python3
"""Promote W3 only from verified public archival-closure evidence.

This transition is metadata-only. It never reads OCR text, private Drive IDs,
private keys, or restricted bytes. All private-integrity facts must already be
represented by the text-free archival closure record.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

CLOSURE = Path("data/research/ltmd_u1_w3_archival_closure.json")
WAVE_STATE = Path("data/research/ltmd_u1_ftrl_wave_state.json")
READINESS = Path("data/research/ltmd_u1_w3_runtime_readiness.json")
LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
RUN_ID = "32853375619"
COMMIT = "2a55ec09124054729e9c45a2285686cf4abf8776"
LOGICAL_ARCHIVE = (
    "LTMD-U1 — corpus FTRL privado/W3 — Español y Lengua/"
    "run_32853375619__2a55ec0__2026-08-25/02_CONSOLIDATED_PRIVATE"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def validate_closure(c: dict) -> None:
    assert c["schema"] == "LTMD_U1_W3_ARCHIVAL_CLOSURE_0.1"
    assert c["distributed_run_id"] == RUN_ID
    assert c["distributed_source_commit"] == COMMIT
    assert c["historical_identities"] == 130
    assert c["canonical_processing_objects"] == 114
    assert c["page_records"] == 20765
    assert c["shard_count"] == 52
    assert c["shard_page_count_distribution"] == {"399": 35, "400": 17}
    assert c["computational_validation"]["page_partition_complete"] is True
    assert c["computational_validation"]["page_partition_unique"] is True
    assert c["persistent_archive"]["encrypted_handoff_artifacts_preserved"] == 52
    assert c["persistent_archive"]["text_free_evidence_artifacts_preserved"] == 53
    assert c["persistent_archive"]["exact_handoff_bundles_roundtrip_sha256_verified"] is True
    assert c["persistent_archive"]["private_consolidation_validated"] is True
    assert c["persistent_archive"]["consolidated_page_records"] == 20765
    assert c["persistent_archive"]["consolidated_sqlite_integrity"] == "ok"
    assert c["persistent_archive"]["consolidated_fts_rows"] == 20765
    assert c["persistent_archive"]["consolidated_products_roundtrip_sha256_verified"] is True
    assert c["persistent_archive"]["consolidated_products_shared_false"] is True
    assert c["persistent_archive"]["private_closure_roundtrip_sha256_verified"] is True
    assert c["persistent_archive"]["private_closure_shared_false"] is True
    assert c["state"] == {
        "archival_complete": True,
        "corpus_ready": True,
        "ftrl_status": "validated",
        "ocr_available": True,
        "semantic_ready": False,
        "text_verified": False,
    }


def update_wave_state() -> None:
    state = load_json(WAVE_STATE)
    state["effective_date"] = "2026-08-25"
    w3 = state["waves"]["W3"]
    w3.update({
        "ftrl_status": "validated",
        "ftrl_run_id": RUN_ID,
        "ftrl_commit": COMMIT,
        "archival_status": "archival_complete",
        "preservation_run_id": "private_consolidation_2026-08-25",
        "archive_destination_logical": LOGICAL_ARCHIVE,
        "archival_closure_evidence": str(CLOSURE),
    })
    write_json(WAVE_STATE, state)


def update_readiness() -> None:
    r = load_json(READINESS)
    r["effective_date"] = "2026-08-25"
    r["runtime"]["full_execution_activated"] = True
    r["runtime"]["full_execution_topology_frozen"] = True
    r["runtime"]["full_execution_run_id"] = RUN_ID
    r["runtime"]["full_execution_commit"] = COMMIT
    r["runtime"]["distributed_shard_count"] = 52
    r["runtime"]["shard_page_count_distribution"] = {"399": 35, "400": 17}
    r["runtime"]["topology_decision_basis"] = (
        "Frozen after successful 100-page W3 pilot and W1 observed shard runtime; "
        "exhaustive W3 run completed as 52 deterministic shards with exact 20,765/20,765 union."
    )
    r["preservation"]["archival_complete"] = True
    r["preservation"]["archival_closure_evidence"] = str(CLOSURE)
    write_json(READINESS, r)


def validate_generated() -> None:
    rows = list(csv.DictReader(LEDGER.open(encoding="utf-8", newline="")))
    w3 = [r for r in rows if r["wave"] == "W3"]
    assert len(w3) == 130
    assert Counter(r["ftrl_status"] for r in w3) == Counter({"validated": 130})
    assert Counter(r["archival_status"] for r in w3) == Counter({"archival_complete": 130})
    assert sum(int(r["corpus_ready"]) for r in w3) == 130
    assert sum(int(r["ocr_available"]) for r in w3) == 130
    assert sum(int(r["text_verified"]) for r in w3) == 0
    assert sum(int(r["semantic_ready"]) for r in w3) == 0
    assert {r["ftrl_run_id"] for r in w3} == {RUN_ID}
    assert {r["ftrl_commit"] for r in w3} == {COMMIT}
    summary = load_json(SUMMARY)
    assert summary["ftrl_identity_status"]["validated"] == 188
    assert summary["ftrl_identity_status"]["pending"] == 336
    assert summary["canonical_processing_objects_by_ftrl_status"] == {"validated": 165}
    assert summary["canonical_source_pages_by_ftrl_status"] == {"validated": 29934}
    assert summary["corpus_ready_identities"] == 188
    assert summary["ocr_available_identities"] == 188
    assert summary["text_verified_identities"] == 0
    assert summary["semantic_ready_identities"] == 0
    assert summary["archival_status"] == {
        "archival_complete": 188,
        "not_applicable_final_exception": 5,
        "not_started": 349,
    }


def main() -> None:
    closure = load_json(CLOSURE)
    validate_closure(closure)
    subprocess.run([sys.executable, "scripts/build_ltmd_u1_ftrl_completion_ledger_v2.py"], check=True)
    update_wave_state()
    update_readiness()
    validate_generated()
    print(json.dumps({"status": "ok", "wave": "W3", "archival_complete": True, "validated_identities": 130}, sort_keys=True))


if __name__ == "__main__":
    main()
