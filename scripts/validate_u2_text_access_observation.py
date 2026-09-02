#!/usr/bin/env python3
"""Validate the materialized LTMD-U2 text-access observation layer."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

DEFAULT_SOURCE = Path("data/catalog/ltmd_u2_text_access_observation_2026_09_02.csv")
SOURCE_ADMISSION = Path("data/catalog/ltmd_u2_source_admission_2026_09_02.csv")
MANIFEST = Path("data/catalog/ltmd_u2_text_access_observation_0_1.manifest.json")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_true(value: str) -> bool:
    return value.strip().lower() == "true"


def is_false(value: str) -> bool:
    return value.strip().lower() == "false"


def validate(source: Path = DEFAULT_SOURCE) -> list[str]:
    errors: list[str] = []
    rows = read_csv(source)
    admitted = {row["source_object_id"]: row for row in read_csv(SOURCE_ADMISSION)}

    if len(rows) != 39:
        errors.append(f"text-access cardinality must be 39, got {len(rows)}")
    ids = [row["source_object_id"] for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("source_object_id values must be unique")
    if set(ids) != set(admitted):
        errors.append("text-access IDs must exactly match source-admission IDs")

    for row in rows:
        sid = row["source_object_id"]
        admission = admitted.get(sid)
        if admission is None:
            continue
        prefix = f"{sid}: "
        if row["viewer_key"] != admission["viewer_key"]:
            errors.append(prefix + "viewer_key mismatch")
        if admission["source_admission_state"] != "admitted_full_body_verified":
            errors.append(prefix + "input source must remain admitted_full_body_verified")
        if not is_true(row["pypdf_encrypted"]):
            errors.append(prefix + "pypdf_encrypted must be true")
        if row["pypdf_blank_password_result"] != "NOT_DECRYPTED":
            errors.append(prefix + "pypdf blank-password result must be NOT_DECRYPTED")
        if row["pypdf_error_type"] != "FileNotDecryptedError":
            errors.append(prefix + "pypdf error type mismatch")
        if not is_true(row["pymupdf_needs_password"]):
            errors.append(prefix + "pymupdf_needs_password must be true")
        if row["pymupdf_blank_password_result"] != "0":
            errors.append(prefix + "pymupdf blank-password result must be 0")
        if row["pymupdf_error_type"] != "ValueError":
            errors.append(prefix + "pymupdf error type mismatch")
        if not is_false(row["pikepdf_blank_password_open"]):
            errors.append(prefix + "pikepdf blank-password open must be false")
        if row["pikepdf_error_type"] != "PasswordError":
            errors.append(prefix + "pikepdf error type mismatch")
        if row["text_access_observation_state"] != "blocked_by_password_required_encryption":
            errors.append(prefix + "text_access_observation_state mismatch")
        if row["embedded_text_sample_state"] != "not_assessed_due_to_access_block":
            errors.append(prefix + "embedded-text state must remain not assessed due to access block")
        if row["ocr_available_state"] != "not_assessed":
            errors.append(prefix + "OCR availability must remain not_assessed")
        if row["text_verified_state"] != "not_assessed":
            errors.append(prefix + "text verification must remain not_assessed")
        if not is_false(row["source_pdf_persisted"]):
            errors.append(prefix + "source_pdf_persisted must be false")
        if not is_false(row["extracted_text_persisted"]):
            errors.append(prefix + "extracted_text_persisted must be false")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("total_source_objects") != 39:
        errors.append("manifest total_source_objects must be 39")
    if manifest.get("observed_source_objects") != 39:
        errors.append("manifest observed_source_objects must be 39")
    if manifest.get("failed_source_objects") != 0:
        errors.append("manifest failed_source_objects must be 0")
    if manifest.get("objects_in_state") != 39:
        errors.append("manifest objects_in_state must be 39")
    if manifest.get("text_access_observation_state") != "blocked_by_password_required_encryption":
        errors.append("manifest text-access state mismatch")
    if manifest.get("embedded_text_sample_state") != "not_assessed_due_to_access_block":
        errors.append("manifest embedded-text state mismatch")
    if manifest.get("ocr_available_state") != "not_assessed":
        errors.append("manifest OCR state must remain not_assessed")
    if manifest.get("text_verified_state") != "not_assessed":
        errors.append("manifest text state must remain not_assessed")
    if manifest.get("source_pdf_bytes_persisted") is not False:
        errors.append("manifest source_pdf_bytes_persisted must be false")
    if manifest.get("extracted_text_persisted") is not False:
        errors.append("manifest extracted_text_persisted must be false")

    expected_hash = manifest.get("materialization", {}).get("canonical_csv_sha256")
    actual_hash = file_sha256(source)
    if expected_hash != actual_hash:
        errors.append(
            f"canonical CSV SHA-256 mismatch: manifest={expected_hash} actual={actual_hash}"
        )

    print(
        f"objects={len(rows)} blocked={sum(r['text_access_observation_state'] == 'blocked_by_password_required_encryption' for r in rows)} "
        f"csv_sha256={actual_hash} errors={len(errors)}"
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    errors = validate(args.source)
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
