#!/usr/bin/env python3
"""Validate text-free LTMD archive-closure evidence without private Drive identifiers."""
from __future__ import annotations

import json
import re
from pathlib import Path

GH = Path("data/research/ltmd_github_operational_archive_closure_2026_08_24.json")
GIT = Path("data/research/ltmd_git_history_snapshot_closure_2026_08_24.json")
GIT_SEQ8 = Path("data/research/ltmd_git_history_snapshot_closure_2026_08_24_seq8.json")
NOTION = Path("data/research/ltmd_notion_continuity_snapshot_closure_2026_08_24.json")
SHA = re.compile(r"^[0-9a-f]{64}$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_sha(value: str) -> None:
    assert SHA.fullmatch(value), value


def no_private_locator(value) -> None:
    if isinstance(value, dict):
        forbidden_keys = {"drive_id", "file_id", "folder_id", "drive_url", "private_url"}
        assert not (forbidden_keys & set(value)), forbidden_keys & set(value)
        for child in value.values():
            no_private_locator(child)
    elif isinstance(value, list):
        for child in value:
            no_private_locator(child)
    elif isinstance(value, str):
        assert "drive.google.com" not in value
        assert "docs.google.com" not in value
        assert "BEGIN PRIVATE KEY" not in value
        assert "BEGIN RSA PRIVATE KEY" not in value


def validate_git_snapshot(payload: dict, *, run_id: str, total_bytes: int, volume_bytes: list[int]) -> None:
    assert payload["schema"] == "LTMD_COMPLETE_GIT_HISTORY_ARCHIVE_CLOSURE_0.1"
    assert payload["source"]["workflow_run_id"] == run_id
    assert payload["source"]["artifact_zip_bytes"] == total_bytes
    assert_sha(payload["source"]["artifact_zip_sha256"])
    assert payload["source"]["workflow_conclusion"] == "success"
    assert payload["git_history"]["bundle_verified"] is True
    assert payload["git_history"]["independently_cloneable"] is True
    assert payload["git_history"]["branches_preserved"] is True
    assert payload["git_history"]["tags_preserved"] is True
    assert payload["git_history"]["pull_request_refs_preserved"] is True
    archive = payload["persistent_archive"]
    assert archive["volume_count"] == len(volume_bytes)
    assert [v["bytes"] for v in archive["volumes"]] == volume_bytes
    for volume in archive["volumes"]:
        assert_sha(volume["sha256"])
    assert sum(v["bytes"] for v in archive["volumes"]) == total_bytes
    assert archive["all_volumes_shared"] is False
    assert archive["all_volumes_redownload_verified"] is True
    assert archive["reconstructed_bytes"] == total_bytes
    assert_sha(archive["reconstructed_sha256"])
    assert archive["reconstructed_sha256"] == payload["source"]["artifact_zip_sha256"]
    assert archive["reconstructed_matches_origin_artifact"] is True
    assert payload["archival_complete"] is True


def main() -> None:
    gh, git, git_seq8, notion = map(load, (GH, GIT, GIT_SEQ8, NOTION))

    assert gh["schema"] == "LTMD_GITHUB_OPERATIONAL_ARCHIVE_CLOSURE_0.1"
    assert gh["source"]["workflow_run_id"] == "32791474215"
    assert gh["source"]["artifact_zip_bytes"] == 26650402
    assert_sha(gh["source"]["artifact_zip_sha256"])
    assert gh["source"]["artifact_zip_sha256"] == gh["persistent_archive"]["redownload_sha256"]
    assert gh["persistent_archive"]["destination_shared"] is False
    assert gh["persistent_archive"]["redownload_verified"] is True
    assert gh["persistent_archive"]["matches_origin_artifact"] is True
    assert gh["scope"]["restricted_ftrl_plaintext_included"] is False
    assert gh["archival_complete"] is True

    validate_git_snapshot(
        git,
        run_id="32791856141",
        total_bytes=183170565,
        volume_bytes=[90000000, 90000000, 3170565],
    )

    validate_git_snapshot(
        git_seq8,
        run_id="32806500511",
        total_bytes=183214572,
        volume_bytes=[90000000, 90000000, 3214572],
    )
    assert git_seq8["persistent_archive"]["manifest_present"] is True
    assert git_seq8["persistent_archive"]["zip_integrity_test_passed"] is True
    assert git_seq8["scope"]["repository_code_and_git_history_only"] is True
    assert git_seq8["scope"]["w1_exhaustive_distributed_run_launched"] is False
    assert git_seq8["scope"]["w1_computationally_validated"] is False
    assert git_seq8["scope"]["w1_archival_complete"] is False
    assert git_seq8["scope"]["w3_unblocked"] is False

    assert notion["schema"] == "LTMD_NOTION_CONTINUITY_ARCHIVE_CLOSURE_0.1"
    n = notion["persistent_archive"]
    assert n["immutable_text_bytes"] == 13181
    assert_sha(n["immutable_text_sha256"])
    assert n["destination_shared"] is False
    assert n["redownload_verified"] is True
    assert n["redownload_sha256"] == n["immutable_text_sha256"]
    assert n["matches_exported_source"] is True
    assert notion["continuity_rule"]["chat_is_single_source_of_truth"] is False
    assert notion["archival_complete"] is True

    for payload in (gh, git, git_seq8, notion):
        no_private_locator(payload)

    print("LTMD archive closure evidence: OK")


if __name__ == "__main__":
    main()
