#!/usr/bin/env python3
"""Validate LTMD private FTRL storage under preservation canon 0.2.

Metadata-only/public-safety gate. It never reads restricted OCR content under local/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

CONTRACT = Path("data/research/ltmd_private_corpus_storage_contract.json")
CANON = Path("docs/LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md")
TOTAL_CANON = Path("docs/LTMD_TOTAL_PRESERVATION_CANON_0_1.md")
PRESERVATION_CANON = Path("docs/PRESERVATION_CANON_0_2.md")
W1_CLOSURE = Path("data/research/ltmd_u1_w1_archival_closure.json")
PUBLIC_KEY = Path("security/ltmd_archive_public.pem")
EXPECTED_PUBLIC_KEY_SHA256 = "78852eafbaa332247f99e23508ac157b5b906c6c3bf3aeb0af1dfe8d57579c2d"
EXPECTED_SECTIONS = [
    "01_OCR_por_pagina",
    "02_SQLite_FTS5",
    "03_QC_detallado",
    "04_Manifiestos_y_procedencia",
    "05_Checksums_y_evidencia",
]
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yml", ".yaml", ".py", ".sh", ".toml", ".ini", ".cfg", ".pem"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_for_private_keys() -> list[str]:
    hits: list[str] = []
    generic_marker = "-----BEGIN " + "PRIVATE KEY-----"
    rsa_marker = "-----BEGIN RSA " + "PRIVATE KEY-----"
    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        posix = path.as_posix().lstrip("./")
        if posix.startswith(".git/") or posix.startswith("local/") or posix.startswith("private/"):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if generic_marker in text or rsa_marker in text:
            hits.append(posix)
    return sorted(hits)


def main() -> None:
    required = (CONTRACT, CANON, TOTAL_CANON, PRESERVATION_CANON, W1_CLOSURE, PUBLIC_KEY)
    if any(not path.exists() for path in required):
        missing = [str(path) for path in required if not path.exists()]
        raise SystemExit(f"private corpus preservation canon is incomplete: {missing}")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["schema"] == "LTMD_PRIVATE_CORPUS_STORAGE_0.3"
    assert contract["canonical_document"] == PRESERVATION_CANON.as_posix()
    assert contract["legacy_total_canon_document"] == TOTAL_CANON.as_posix()
    assert contract["private_corpus_canonical_document"] == CANON.as_posix()

    storage = contract["persistent_private_storage"]
    assert storage["provider"] == "google_drive"
    assert storage["visibility"] == "private_owner_controlled"
    assert storage["required_sections"] == EXPECTED_SECTIONS
    assert storage["repository_snapshot_policy"] == {
        "current_complete_history_snapshots": 1,
        "replace_only_at_major_archival_milestones": True,
        "delete_superseded_after_verification": True,
    }
    final_text = storage["u1_final_textual_corpus_policy"]
    assert final_text["exactly_one_integral_canonical_copy"] is True
    assert final_text["private"] is True
    assert final_text["verified_by_manifest_and_checksums"] is True
    assert final_text["independent_of_actions_artifacts"] is True

    policy = contract["public_repository_policy"]
    assert policy["full_ocr_allowed"] is False
    assert policy["sqlite_allowed"] is False
    assert policy["detailed_qc_allowed"] is False
    assert policy["private_drive_ids_allowed"] is False
    assert policy["private_keys_allowed"] is False
    assert policy["text_free_evidence_allowed"] is True
    assert policy["archive_public_key"] == PUBLIC_KEY.as_posix()

    total = contract["project_total_preservation"]
    assert total["required"] is True
    assert total["chat_is_never_single_source_of_truth"] is True
    assert total["actions_artifacts_are_never_persistent_archive"] is True

    inv = contract["invariants"]
    required_true = {
        "computational_validation_does_not_imply_archival_completion",
        "archival_completion_requires_private_persistent_copy",
        "encrypted_actions_artifact_is_temporary_handoff_only",
        "plaintext_restricted_outputs_must_not_be_uploaded_to_public_actions",
        "drive_copy_must_be_bound_to_run_id_and_commit",
        "drive_copy_integrity_must_be_verified",
        "private_key_must_never_enter_public_repository",
        "prior_validated_runs_without_persistent_copy_are_archival_debt",
        "github_only_is_not_sufficient_for_project_preservation",
        "drive_only_is_not_sufficient_for_versioned_scientific_truth",
        "notion_only_is_not_sufficient_for_data_or_code_preservation",
        "major_archival_milestones_require_current_complete_history_snapshot",
        "superseded_repository_snapshots_are_removed_after_verified_replacement",
        "u1_final_textual_corpus_has_exactly_one_integral_canonical_private_copy",
    }
    assert required_true <= set(inv)
    assert all(inv[k] is True for k in required_true)

    w1 = json.loads(W1_CLOSURE.read_text(encoding="utf-8"))
    assert w1["schema"] == "LTMD_FTRL_ARCHIVAL_CLOSURE_0.2"
    assert w1["wave"] == "W1"
    assert w1["archival_complete"] is True
    assert w1["persistent_archive"]["single_canonical_consolidated_copy"] is True
    assert w1["persistent_archive"]["redownload_verified"] is True
    assert w1["persistent_archive"]["temporary_encrypted_handoff_absorbed_and_removed"] is True
    assert w1["security"]["plaintext_restricted_outputs_published"] is False
    assert w1["text_verified"] is False
    assert w1["semantic_ready"] is False

    public_key_text = PUBLIC_KEY.read_text(encoding="utf-8")
    assert "-----BEGIN PUBLIC KEY-----" in public_key_text
    assert "PRIVATE KEY" not in public_key_text
    actual_key_sha = sha256(PUBLIC_KEY)
    assert actual_key_sha == EXPECTED_PUBLIC_KEY_SHA256, actual_key_sha

    private_key_hits = scan_for_private_keys()
    if private_key_hits:
        raise SystemExit(f"private key material detected in public repository paths: {private_key_hits}")

    canon_text = CANON.read_text(encoding="utf-8")
    total_text = TOTAL_CANON.read_text(encoding="utf-8")
    preservation_text = PRESERVATION_CANON.read_text(encoding="utf-8")
    for phrase in (
        "Google Drive",
        "archival_complete",
        "computationally_validated",
        "security/ltmd_archive_public.pem",
        "nunca se versionará la clave privada",
    ):
        assert phrase in canon_text, phrase
    for phrase in ("preservación total", "GitHub", "Google Drive", "Notion", "chat", "artefactos de GitHub Actions"):
        assert phrase in total_text, phrase
    for phrase in (
        "una sola versión completa",
        "un único snapshot integral vigente",
        "handoffs temporales",
        "text_verified",
        "semantic_ready",
    ):
        assert phrase in preservation_text, phrase

    result = {
        "schema": contract["schema"],
        "status": "valid",
        "provider": storage["provider"],
        "required_sections": len(EXPECTED_SECTIONS),
        "public_key_sha256": actual_key_sha,
        "private_key_material_in_public_tree": 0,
        "retroactive_scope_entries": len(contract["retroactive_scope"]),
        "total_preservation_required": total["required"],
        "current_complete_history_snapshots": storage["repository_snapshot_policy"]["current_complete_history_snapshots"],
        "u1_single_integral_textual_copy_required": final_text["exactly_one_integral_canonical_copy"],
        "w1_archival_complete": w1["archival_complete"],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
