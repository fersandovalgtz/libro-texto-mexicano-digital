#!/usr/bin/env python3
"""Validate the LTMD private FTRL corpus preservation canon.

Metadata-only/public-safety gate. It never reads restricted OCR content under local/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

CONTRACT = Path("data/research/ltmd_private_corpus_storage_contract.json")
CANON = Path("docs/LTMD_PRIVATE_CORPUS_PRESERVATION_CANON_0_1.md")
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
SKIP_TOP = {".git", "local", "private", "data/raw", "data/work"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_for_private_keys() -> list[str]:
    hits: list[str] = []
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
        if "-----BEGIN PRIVATE KEY-----" in text or "-----BEGIN RSA PRIVATE KEY-----" in text:
            hits.append(posix)
    return sorted(hits)


def main() -> None:
    if not CONTRACT.exists() or not CANON.exists() or not PUBLIC_KEY.exists():
        raise SystemExit("private corpus preservation canon is incomplete")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["schema"] == "LTMD_PRIVATE_CORPUS_STORAGE_0.1"
    assert contract["persistent_private_storage"]["provider"] == "google_drive"
    assert contract["persistent_private_storage"]["visibility"] == "private_owner_controlled"
    assert contract["persistent_private_storage"]["required_sections"] == EXPECTED_SECTIONS

    policy = contract["public_repository_policy"]
    assert policy["full_ocr_allowed"] is False
    assert policy["sqlite_allowed"] is False
    assert policy["detailed_qc_allowed"] is False
    assert policy["private_drive_ids_allowed"] is False
    assert policy["private_keys_allowed"] is False
    assert policy["text_free_evidence_allowed"] is True
    assert policy["archive_public_key"] == PUBLIC_KEY.as_posix()

    inv = contract["invariants"]
    required_true = {
        "computational_validation_does_not_imply_archival_completion",
        "archival_completion_requires_private_persistent_copy",
        "encrypted_actions_artifact_is_temporary_handoff_only",
        "plaintext_restricted_outputs_must_not_be_uploaded_to_public_actions",
        "drive_copy_must_be_bound_to_run_id_and_commit",
        "private_key_must_never_enter_public_repository",
        "prior_validated_runs_without_persistent_copy_are_archival_debt",
    }
    assert required_true <= set(inv)
    assert all(inv[k] is True for k in required_true)

    public_key_text = PUBLIC_KEY.read_text(encoding="utf-8")
    assert "-----BEGIN PUBLIC KEY-----" in public_key_text
    assert "PRIVATE KEY" not in public_key_text
    actual_key_sha = sha256(PUBLIC_KEY)
    assert actual_key_sha == EXPECTED_PUBLIC_KEY_SHA256, actual_key_sha

    private_key_hits = scan_for_private_keys()
    if private_key_hits:
        raise SystemExit(f"private key material detected in public repository paths: {private_key_hits}")

    canon_text = CANON.read_text(encoding="utf-8")
    for phrase in (
        "Google Drive",
        "archival_complete",
        "computationally_validated",
        "security/ltmd_archive_public.pem",
        "nunca se versionará la clave privada",
    ):
        assert phrase in canon_text, phrase

    result = {
        "schema": contract["schema"],
        "status": "valid",
        "provider": contract["persistent_private_storage"]["provider"],
        "required_sections": len(EXPECTED_SECTIONS),
        "public_key_sha256": actual_key_sha,
        "private_key_material_in_public_tree": 0,
        "retroactive_archival_debt_entries": len(contract["retroactive_scope"]),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
