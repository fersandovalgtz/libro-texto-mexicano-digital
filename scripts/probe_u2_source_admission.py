#!/usr/bin/env python3
"""Bounded LTMD-U2 source-admission probe.

Downloads one institutional PDF to a temporary file, computes a full-body SHA-256,
checks basic PDF integrity, confirms the canonical structural page count, and
samples whether an embedded text layer is technically extractable. The source
PDF and extracted text are deleted/not persisted; only non-substitutive metrics
are written to JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import urllib.request
from pathlib import Path

from pypdf import PdfReader

BASE = "https://libros.conaliteg.gob.mx/pdf-reader/assets/primaria/2026/{key}.pdf"
UA = "LTMD-U2-source-admission-probe/0.1 (+research; non-redistributive)"


def download_and_hash(url: str, target: Path, timeout: int) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/pdf"})
    sha = hashlib.sha256()
    first = bytearray()
    tail = bytearray()
    received = 0
    with urllib.request.urlopen(req, timeout=timeout) as response, target.open("wb") as fh:
        status = getattr(response, "status", None)
        content_type = response.headers.get_content_type()
        content_length = response.headers.get("Content-Length")
        etag = response.headers.get("ETag")
        last_modified = response.headers.get("Last-Modified")
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)
            sha.update(chunk)
            received += len(chunk)
            if len(first) < 16:
                first.extend(chunk[: 16 - len(first)])
            tail.extend(chunk)
            if len(tail) > 65536:
                del tail[:-65536]
    return {
        "http_status": status,
        "content_type": content_type,
        "content_length_header": int(content_length) if content_length and content_length.isdigit() else None,
        "etag": etag,
        "last_modified": last_modified,
        "bytes_received": received,
        "sha256": sha.hexdigest(),
        "pdf_signature": bytes(first).startswith(b"%PDF-"),
        "eof_marker": b"%%EOF" in tail,
        "startxref_in_tail": bool(re.search(rb"startxref\s+\d+\s+%%EOF", bytes(tail), flags=re.S)),
    }


def inspect_pdf(path: Path, expected_pages: int) -> dict:
    reader = PdfReader(str(path), strict=False)
    page_count = len(reader.pages)
    if page_count <= 0:
        sample_indices = []
    else:
        sample_indices = sorted({0, page_count // 4, page_count // 2, (3 * page_count) // 4, page_count - 1})
    char_counts = []
    for idx in sample_indices:
        text = reader.pages[idx].extract_text() or ""
        char_counts.append(len(text.strip()))
        # Do not persist extracted text.
        del text
    return {
        "parser": "pypdf",
        "parser_page_count": page_count,
        "expected_page_count": expected_pages,
        "page_count_matches": page_count == expected_pages,
        "text_sample_page_indices": sample_indices,
        "text_sample_char_counts": char_counts,
        "text_sample_pages_with_text": sum(1 for n in char_counts if n > 0),
        "embedded_text_sample_state": "detected_in_sample" if any(n > 0 for n in char_counts) else "not_detected_in_sample",
        "ocr_available_state": "not_assessed",
        "text_verified_state": "not_assessed",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viewer-key", required=True)
    ap.add_argument("--expected-bytes", required=True, type=int)
    ap.add_argument("--expected-pages", required=True, type=int)
    ap.add_argument("--observed-at", default="2026-09-02")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    url = BASE.format(key=args.viewer_key)
    result = {
        "schema": "LTMD_U2_SOURCE_ADMISSION_PILOT_0.1",
        "source_object_id": f"CONALITEG:2026:primaria:{args.viewer_key}",
        "viewer_key": args.viewer_key,
        "asset_url": url,
        "observed_at": args.observed_at,
        "expected_bytes": args.expected_bytes,
        "expected_page_count": args.expected_pages,
        "source_pdf_persisted": False,
        "extracted_text_persisted": False,
        "rights_state": "third_party_source_not_redistributable_by_default",
    }

    try:
        with tempfile.TemporaryDirectory(prefix="ltmd-u2-source-") as td:
            pdf_path = Path(td) / f"{args.viewer_key}.pdf"
            transport = download_and_hash(url, pdf_path, args.timeout)
            result.update(transport)
            result.update(inspect_pdf(pdf_path, args.expected_pages))
            result["size_matches"] = transport["bytes_received"] == args.expected_bytes
            admission_ok = all([
                transport["http_status"] == 200,
                transport["content_type"] == "application/pdf",
                result["size_matches"],
                transport["pdf_signature"],
                transport["eof_marker"],
                transport["startxref_in_tail"],
                result["page_count_matches"],
            ])
            result["source_admission_state"] = "admitted_full_body_verified" if admission_ok else "not_admitted"
            result["evidence_scope"] = (
                "full-body SHA-256 + transport/size/PDF markers + parser page-count consistency; "
                "embedded-text sample is technical detection only; no OCR or semantic verification"
            )
    except Exception as exc:
        result["source_admission_state"] = "probe_error"
        result["error"] = f"{type(exc).__name__}: {exc}"

    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result.get(k) for k in [
        "viewer_key", "source_admission_state", "bytes_received", "sha256", "parser_page_count",
        "embedded_text_sample_state", "text_sample_pages_with_text", "error"
    ]}, ensure_ascii=False))
    return 0 if result.get("source_admission_state") == "admitted_full_body_verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
