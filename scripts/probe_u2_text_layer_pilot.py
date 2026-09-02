#!/usr/bin/env python3
"""Bounded LTMD-U2 pilot for observing an embedded PDF text layer.

The pilot downloads three already-admitted CONALITEG PDF sources to a temporary
file, verifies exact byte count and SHA-256 against the canonical source-admission
registry, then inspects five sampled pages with independent PDF implementations.

Only technical counts and parser states are emitted. Source PDFs and extracted
text are deleted/not persisted. This probe does NOT assess OCR availability,
text verification, licensing, or semantic readiness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import re
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

SOURCE_ADMISSION = Path("data/catalog/ltmd_u2_source_admission_2026_09_02.csv")
PILOT_KEYS = ("P5LPM", "P4PEA", "P0CMA")
USER_AGENT = "LTMD-U2-text-layer-pilot/0.1 (+research; non-redistributive)"
MEANINGFUL_TEXT_THRESHOLD = 20


def read_registry() -> dict[str, dict[str, str]]:
    with SOURCE_ADMISSION.open(newline="", encoding="utf-8") as fh:
        rows = {row["viewer_key"]: row for row in csv.DictReader(fh)}
    missing = [key for key in PILOT_KEYS if key not in rows]
    if missing:
        raise RuntimeError(f"pilot keys absent from canonical registry: {missing}")
    return rows


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def sample_indices(page_count: int) -> list[int]:
    if page_count < 1:
        return []
    candidates = [
        0,
        round((page_count - 1) * 0.25),
        round((page_count - 1) * 0.50),
        round((page_count - 1) * 0.75),
        page_count - 1,
    ]
    return sorted(set(int(i) for i in candidates))


def text_counts(text: str | None) -> dict[str, int]:
    value = text or ""
    return {
        "chars": len(value),
        "non_whitespace_chars": len(re.sub(r"\s+", "", value)),
    }


def download_verified(row: dict[str, str], path: Path, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        row["asset_url"],
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"},
    )
    digest = hashlib.sha256()
    received = 0
    first = bytearray()
    tail = bytearray()
    with urllib.request.urlopen(request, timeout=timeout) as response, path.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            digest.update(chunk)
            received += len(chunk)
            if len(first) < 16:
                first.extend(chunk[: 16 - len(first)])
            tail.extend(chunk)
            if len(tail) > 65536:
                del tail[:-65536]
        status = getattr(response, "status", None)
        content_type = response.headers.get_content_type()

    observed_sha = digest.hexdigest()
    expected_bytes = int(row["bytes_received"])
    expected_sha = row["sha256"]
    checks = {
        "http_status": status,
        "content_type": content_type,
        "bytes_received": received,
        "expected_bytes": expected_bytes,
        "size_matches": received == expected_bytes,
        "sha256": observed_sha,
        "expected_sha256": expected_sha,
        "sha256_matches": observed_sha == expected_sha,
        "pdf_signature": bytes(first).startswith(b"%PDF-"),
        "eof_marker": b"%%EOF" in tail,
    }
    checks["canonical_body_verified"] = all(
        [
            checks["http_status"] == 200,
            checks["content_type"] == "application/pdf",
            checks["size_matches"],
            checks["sha256_matches"],
            checks["pdf_signature"],
            checks["eof_marker"],
        ]
    )
    if not checks["canonical_body_verified"]:
        raise RuntimeError(f"canonical source body mismatch for {row['viewer_key']}: {checks}")
    return checks


def inspect_pypdf(path: Path, samples: list[int]) -> dict[str, Any]:
    from pypdf import PdfReader

    result: dict[str, Any] = {
        "parser": "pypdf",
        "version": package_version("pypdf"),
        "open_state": "not_opened",
        "encrypted": None,
        "blank_password_result": None,
        "page_count": None,
        "sample_counts": [],
        "error_type": None,
    }
    try:
        reader = PdfReader(str(path), strict=False)
        result["encrypted"] = bool(reader.is_encrypted)
        if reader.is_encrypted:
            try:
                decrypt_result = reader.decrypt("")
                result["blank_password_result"] = getattr(decrypt_result, "name", str(decrypt_result))
            except Exception as exc:  # parser-specific diagnostic only
                result["blank_password_result"] = f"error:{type(exc).__name__}"
        try:
            result["page_count"] = len(reader.pages)
            result["open_state"] = "page_tree_accessible"
            for index in samples:
                try:
                    counts = text_counts(reader.pages[index].extract_text())
                    result["sample_counts"].append({"page_index": index, **counts, "state": "observed"})
                except Exception as exc:
                    result["sample_counts"].append(
                        {"page_index": index, "chars": 0, "non_whitespace_chars": 0, "state": f"error:{type(exc).__name__}"}
                    )
        except Exception as exc:
            result["open_state"] = "blocked_after_open"
            result["error_type"] = type(exc).__name__
    except Exception as exc:
        result["open_state"] = "open_error"
        result["error_type"] = type(exc).__name__
    return result


def inspect_pymupdf(path: Path, samples: list[int]) -> dict[str, Any]:
    import fitz

    result: dict[str, Any] = {
        "parser": "PyMuPDF",
        "version": package_version("PyMuPDF"),
        "open_state": "not_opened",
        "needs_password": None,
        "blank_password_result": None,
        "page_count": None,
        "sample_counts": [],
        "error_type": None,
    }
    doc = None
    try:
        doc = fitz.open(str(path))
        result["needs_password"] = bool(doc.needs_pass)
        if doc.needs_pass:
            try:
                result["blank_password_result"] = int(doc.authenticate(""))
            except Exception as exc:
                result["blank_password_result"] = f"error:{type(exc).__name__}"
        result["page_count"] = int(doc.page_count)
        try:
            for index in samples:
                page = doc.load_page(index)
                counts = text_counts(page.get_text("text"))
                result["sample_counts"].append({"page_index": index, **counts, "state": "observed"})
            result["open_state"] = "sample_text_inspected"
        except Exception as exc:
            result["open_state"] = "text_access_blocked"
            result["error_type"] = type(exc).__name__
    except Exception as exc:
        result["open_state"] = "open_error"
        result["error_type"] = type(exc).__name__
    finally:
        if doc is not None:
            doc.close()
    return result


def inspect_pikepdf(path: Path) -> dict[str, Any]:
    import pikepdf

    result: dict[str, Any] = {
        "parser": "pikepdf",
        "version": package_version("pikepdf"),
        "open_state": "not_opened",
        "encrypted": None,
        "blank_password_open": False,
        "page_count": None,
        "error_type": None,
    }
    try:
        with pikepdf.open(str(path), password="", suppress_warnings=True) as pdf:
            result["encrypted"] = bool(pdf.is_encrypted)
            result["blank_password_open"] = True
            result["page_count"] = len(pdf.pages)
            result["open_state"] = "page_tree_accessible"
    except Exception as exc:
        result["open_state"] = "open_error"
        result["error_type"] = type(exc).__name__
    return result


def classify(parsers: list[dict[str, Any]], samples: list[int]) -> tuple[str, str]:
    extractors = [p for p in parsers if p["parser"] in {"pypdf", "PyMuPDF"}]
    observed = [
        item
        for parser in extractors
        for item in parser.get("sample_counts", [])
        if item.get("state") == "observed"
    ]
    if any(item["non_whitespace_chars"] >= MEANINGFUL_TEXT_THRESHOLD for item in observed):
        return "embedded_text_observed_sample", "not_indicated_by_sample"

    successful_extractors = [
        parser
        for parser in extractors
        if len([x for x in parser.get("sample_counts", []) if x.get("state") == "observed"]) == len(samples)
    ]
    if successful_extractors:
        return "no_meaningful_embedded_text_observed_sample", "candidate_ocr_needed_for_searchable_text"

    encryption_signals = []
    for parser in parsers:
        if parser["parser"] == "pypdf":
            encryption_signals.append(parser.get("encrypted") is True and parser.get("open_state") != "page_tree_accessible")
        elif parser["parser"] == "PyMuPDF":
            encryption_signals.append(parser.get("needs_password") is True and parser.get("open_state") != "sample_text_inspected")
        elif parser["parser"] == "pikepdf":
            encryption_signals.append(parser.get("open_state") == "open_error")
    if encryption_signals and all(encryption_signals):
        return "text_extraction_blocked_by_encryption", "not_assessed"
    return "indeterminate_parser_error", "not_assessed"


def inspect_object(row: dict[str, str], timeout: int) -> dict[str, Any]:
    page_count = int(row["page_count"])
    samples = sample_indices(page_count)
    with tempfile.TemporaryDirectory(prefix="ltmd-u2-text-pilot-") as temp_dir:
        pdf_path = Path(temp_dir) / f"{row['viewer_key']}.pdf"
        transport = download_verified(row, pdf_path, timeout)
        parsers = [
            inspect_pypdf(pdf_path, samples),
            inspect_pymupdf(pdf_path, samples),
            inspect_pikepdf(pdf_path),
        ]
        text_state, potential_ocr_need_state = classify(parsers, samples)

    return {
        "source_object_id": row["source_object_id"],
        "viewer_key": row["viewer_key"],
        "expected_page_count": page_count,
        "sample_page_indices_zero_based": samples,
        "transport_verification": transport,
        "parsers": parsers,
        "text_layer_observation_state": text_state,
        "potential_ocr_need_state": potential_ocr_need_state,
        "ocr_available_state": "not_assessed",
        "text_verified_state": "not_assessed",
        "source_pdf_persisted": False,
        "extracted_text_persisted": False,
        "evidence_scope": "five-page bounded sample; character counts only; no extracted text retained or emitted",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--output", default="u2-text-layer-pilot.json")
    args = parser.parse_args()

    registry = read_registry()
    results = []
    for key in PILOT_KEYS:
        result = inspect_object(registry[key], args.timeout)
        result["observed_at"] = args.observed_at
        results.append(result)
        max_chars = max(
            [
                item["non_whitespace_chars"]
                for p in result["parsers"]
                for item in p.get("sample_counts", [])
                if item.get("state") == "observed"
            ]
            or [0]
        )
        print(
            f"{key}: state={result['text_layer_observation_state']} "
            f"potential_ocr={result['potential_ocr_need_state']} max_sample_non_ws_chars={max_chars}"
        )

    payload = {
        "schema": "LTMD_U2_TEXT_LAYER_PILOT_0.1",
        "observed_at": args.observed_at,
        "pilot_keys": list(PILOT_KEYS),
        "meaningful_text_threshold_non_whitespace_chars": MEANINGFUL_TEXT_THRESHOLD,
        "packages": {
            "pypdf": package_version("pypdf"),
            "PyMuPDF": package_version("PyMuPDF"),
            "pikepdf": package_version("pikepdf"),
            "cryptography": package_version("cryptography"),
        },
        "source_pdf_bytes_persisted": False,
        "extracted_text_persisted": False,
        "ocr_available_state": "not_assessed",
        "text_verified_state": "not_assessed",
        "epistemic_guards": [
            "source_admitted != embedded_text_observed",
            "embedded_text_observed != ocr_available",
            "ocr_available != text_verified",
            "text_verified != semantic_ready",
            "publicly_accessible != openly_licensed",
        ],
        "objects": results,
    }
    Path(args.output).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
