#!/usr/bin/env python3
"""Re-observe the LTMD-U2 password-required content-access state.

This command is intentionally narrow. It verifies each source body against the
canonical source-admission SHA-256 and byte count, then probes blank-password
content access with pinned independent PDF implementations. It does not discover,
guess, recover, or bypass passwords. It does not persist PDFs or extracted text.

Network access and the pinned parser packages are required. Ordinary CI does not
run this observer; CI validates the already materialized non-substitutive table.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

SOURCE_ADMISSION = Path("data/catalog/ltmd_u2_source_admission_2026_09_02.csv")
USER_AGENT = "LTMD-U2-text-access-observer/0.1 (+research; non-redistributive)"
REQUIRED_VERSIONS = {
    "pypdf": "6.16.2",
    "PyMuPDF": "1.28.2",
    "pikepdf": "10.12.0",
    "cryptography": "50.0.1",
}
OUTPUT_FIELDS = [
    "source_object_id",
    "viewer_key",
    "observed_at",
    "pypdf_encrypted",
    "pypdf_blank_password_result",
    "pypdf_error_type",
    "pymupdf_needs_password",
    "pymupdf_blank_password_result",
    "pymupdf_error_type",
    "pikepdf_blank_password_open",
    "pikepdf_error_type",
    "text_access_observation_state",
    "embedded_text_sample_state",
    "ocr_available_state",
    "text_verified_state",
    "source_pdf_persisted",
    "extracted_text_persisted",
]


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def assert_parser_versions() -> None:
    mismatches = {
        name: (expected, package_version(name))
        for name, expected in REQUIRED_VERSIONS.items()
        if package_version(name) != expected
    }
    if mismatches:
        raise RuntimeError(f"parser version mismatch: {mismatches}")


def read_sources() -> list[dict[str, str]]:
    with SOURCE_ADMISSION.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 39 or len({row["source_object_id"] for row in rows}) != 39:
        raise RuntimeError("canonical source-admission registry must contain 39 unique objects")
    return rows


def download_verified(row: dict[str, str], path: Path, timeout: int) -> None:
    request = urllib.request.Request(
        row["asset_url"],
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"},
    )
    digest = hashlib.sha256()
    received = 0
    with urllib.request.urlopen(request, timeout=timeout) as response, path.open("wb") as out:
        if getattr(response, "status", None) != 200:
            raise RuntimeError(f"HTTP status is not 200 for {row['viewer_key']}")
        if response.headers.get_content_type() != "application/pdf":
            raise RuntimeError(f"content type is not application/pdf for {row['viewer_key']}")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            digest.update(chunk)
            received += len(chunk)
    if received != int(row["bytes_received"]):
        raise RuntimeError(f"byte-count mismatch for {row['viewer_key']}")
    if digest.hexdigest() != row["sha256"]:
        raise RuntimeError(f"SHA-256 mismatch for {row['viewer_key']}")


def probe_pypdf(path: Path) -> dict[str, Any]:
    from pypdf import PdfReader

    reader = PdfReader(str(path), strict=False)
    encrypted = bool(reader.is_encrypted)
    blank_result = None
    error_type = None
    if encrypted:
        try:
            result = reader.decrypt("")
            blank_result = getattr(result, "name", str(result))
        except Exception as exc:
            blank_result = f"error:{type(exc).__name__}"
    try:
        _ = len(reader.pages)
    except Exception as exc:
        error_type = type(exc).__name__
    return {
        "encrypted": encrypted,
        "blank_password_result": blank_result,
        "error_type": error_type,
    }


def probe_pymupdf(path: Path) -> dict[str, Any]:
    import pymupdf

    doc = pymupdf.open(str(path))
    try:
        needs_password = bool(doc.needs_pass)
        blank_result = int(doc.authenticate("")) if needs_password else None
        error_type = None
        try:
            # Probe text access only; any returned string is discarded immediately.
            _ = doc.load_page(0).get_text("text")
        except Exception as exc:
            error_type = type(exc).__name__
        return {
            "needs_password": needs_password,
            "blank_password_result": blank_result,
            "error_type": error_type,
        }
    finally:
        doc.close()


def probe_pikepdf(path: Path) -> dict[str, Any]:
    import pikepdf

    try:
        with pikepdf.open(str(path), password="", suppress_warnings=True):
            return {"blank_password_open": True, "error_type": None}
    except Exception as exc:
        return {"blank_password_open": False, "error_type": type(exc).__name__}


def classify_signals(pypdf_state: dict[str, Any], pymupdf_state: dict[str, Any], pikepdf_state: dict[str, Any]) -> str:
    if (
        pypdf_state.get("encrypted") is True
        and pypdf_state.get("blank_password_result") == "NOT_DECRYPTED"
        and pypdf_state.get("error_type") == "FileNotDecryptedError"
        and pymupdf_state.get("needs_password") is True
        and pymupdf_state.get("blank_password_result") == 0
        and pymupdf_state.get("error_type") == "ValueError"
        and pikepdf_state.get("blank_password_open") is False
        and pikepdf_state.get("error_type") == "PasswordError"
    ):
        return "blocked_by_password_required_encryption"
    return "indeterminate_parser_access_state"


def observe(row: dict[str, str], observed_at: str, timeout: int) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="ltmd-u2-text-access-") as temp_dir:
        pdf_path = Path(temp_dir) / f"{row['viewer_key']}.pdf"
        download_verified(row, pdf_path, timeout)
        pypdf_state = probe_pypdf(pdf_path)
        pymupdf_state = probe_pymupdf(pdf_path)
        pikepdf_state = probe_pikepdf(pdf_path)
        state = classify_signals(pypdf_state, pymupdf_state, pikepdf_state)

    return {
        "source_object_id": row["source_object_id"],
        "viewer_key": row["viewer_key"],
        "observed_at": observed_at,
        "pypdf_encrypted": pypdf_state["encrypted"],
        "pypdf_blank_password_result": pypdf_state["blank_password_result"],
        "pypdf_error_type": pypdf_state["error_type"],
        "pymupdf_needs_password": pymupdf_state["needs_password"],
        "pymupdf_blank_password_result": pymupdf_state["blank_password_result"],
        "pymupdf_error_type": pymupdf_state["error_type"],
        "pikepdf_blank_password_open": pikepdf_state["blank_password_open"],
        "pikepdf_error_type": pikepdf_state["error_type"],
        "text_access_observation_state": state,
        "embedded_text_sample_state": "not_assessed_due_to_access_block" if state == "blocked_by_password_required_encryption" else "not_assessed",
        "ocr_available_state": "not_assessed",
        "text_verified_state": "not_assessed",
        "source_pdf_persisted": False,
        "extracted_text_persisted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", default="data/catalog/ltmd_u2_text_access_observation_observed.csv")
    args = parser.parse_args()

    assert_parser_versions()
    rows = []
    for index, source in enumerate(read_sources(), start=1):
        row = observe(source, args.observed_at, args.timeout)
        rows.append(row)
        print(f"[{index:02d}/39] {source['viewer_key']} state={row['text_access_observation_state']}")

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    blocked = sum(row["text_access_observation_state"] == "blocked_by_password_required_encryption" for row in rows)
    print(f"blocked_by_password_required_encryption={blocked}/{len(rows)}; PDFs persisted=0; text persisted=0")
    return 0 if blocked == len(rows) == 39 else 1


if __name__ == "__main__":
    raise SystemExit(main())
