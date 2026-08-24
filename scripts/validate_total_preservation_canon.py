#!/usr/bin/env python3
"""Validate LTMD total-preservation canon and W5 archival closure evidence."""
from __future__ import annotations

import json
from pathlib import Path

CONTRACT = Path("data/research/ltmd_private_corpus_storage_contract.json")
STATE = Path("data/research/ltmd_u1_ftrl_wave_state.json")
W5 = Path("data/research/ltmd_u1_w5_archival_closure.json")
TOTAL_CANON = Path("docs/LTMD_TOTAL_PRESERVATION_CANON_0_1.md")
PRIVATE_CANON = Path("docs/LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md")

REQUIRED_CATEGORIES = {
    "repository_snapshots",
    "source_inventories_and_manifests",
    "restricted_run_products",
    "github_operational_metadata",
    "issues_prs_releases_tags_and_control_comments",
    "workflow_logs_or_auditable_summaries",
    "rights_and_source_exceptions",
    "preservation_audits",
    "notion_continuity",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for path in (CONTRACT, STATE, W5, TOTAL_CANON, PRIVATE_CANON):
        if not path.exists():
            raise AssertionError(f"missing preservation control file: {path}")

    contract = load(CONTRACT)
    state = load(STATE)
    w5 = load(W5)

    assert contract["schema"] == "LTMD_PRIVATE_CORPUS_STORAGE_0.2"
    assert contract["canonical_document"] == str(TOTAL_CANON)
    assert contract["private_corpus_canonical_document"] == str(PRIVATE_CANON)
    total = contract["project_total_preservation"]
    assert total["required"] is True
    assert total["chat_is_never_single_source_of_truth"] is True
    assert total["actions_artifacts_are_never_persistent_archive"] is True
    assert REQUIRED_CATEGORIES <= set(total["required_categories"])
    assert total["systems"]["github"]
    assert total["systems"]["google_drive"]
    assert total["systems"]["notion"]

    storage = contract["persistent_private_storage"]
    assert storage["provider"] == "google_drive"
    assert storage["visibility"] == "private_owner_controlled"
    assert storage["repository_snapshot_folder"].endswith("01_REPO_SNAPSHOTS")
    assert storage["github_metadata_folder"].endswith("02_GITHUB_METADATA_EXPORTS")
    assert len(storage["required_sections"]) == 5

    inv = contract["invariants"]
    for key in (
        "computational_validation_does_not_imply_archival_completion",
        "archival_completion_requires_private_persistent_copy",
        "drive_copy_integrity_must_be_verified",
        "substantive_main_changes_require_persistent_repository_snapshot",
        "github_only_is_not_sufficient_for_project_preservation",
        "drive_only_is_not_sufficient_for_versioned_scientific_truth",
        "notion_only_is_not_sufficient_for_data_or_code_preservation",
    ):
        assert inv[key] is True, key

    assert w5["schema"] == "LTMD_FTRL_ARCHIVAL_CLOSURE_0.1"
    assert w5["wave"] == "W5"
    assert w5["ftrl"]["run_id"] == "32748987531"
    assert w5["ftrl"]["historical_identities"] == 18
    assert w5["ftrl"]["canonical_processing_objects"] == 15
    assert w5["ftrl"]["page_records"] == 2653
    assert w5["preservation"]["run_id"] == "32784373399"
    assert w5["preservation"]["workflow_conclusion"] == "success"
    assert w5["preservation"]["artifact_zip_bytes"] == 6740331
    assert len(w5["preservation"]["artifact_zip_sha256"]) == 64
    archive = w5["persistent_archive"]
    assert archive["provider"] == "google_drive"
    assert archive["copied"] is True
    assert archive["destination_shared"] is False
    assert archive["destination_bytes"] == w5["preservation"]["artifact_zip_bytes"]
    assert archive["redownload_verified"] is True
    assert archive["redownload_sha256"] == w5["preservation"]["artifact_zip_sha256"]
    assert archive["matches_origin_artifact"] is True
    assert w5["security"]["plaintext_restricted_outputs_published"] is False
    assert w5["archival_complete"] is True

    assert state["schema"] == "LTMD_U1_FTRL_WAVE_STATE_0.1"
    sw5 = state["waves"]["W5"]
    assert sw5["ftrl_status"] == "validated"
    assert sw5["ftrl_run_id"] == "32748987531"
    assert sw5["preservation_run_id"] == "32784373399"
    assert sw5["archival_status"] == "archival_complete"
    assert sw5["archival_closure_evidence"] == str(W5)

    combined_public = TOTAL_CANON.read_text(encoding="utf-8") + PRIVATE_CANON.read_text(encoding="utf-8")
    forbidden_markers = ("drive.google.com/drive/folders/1", "BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY")
    for marker in forbidden_markers:
        assert marker not in combined_public, f"private/sensitive marker leaked into public canon: {marker}"

    print("LTMD total-preservation canon and W5 archival closure: OK")


if __name__ == "__main__":
    main()
