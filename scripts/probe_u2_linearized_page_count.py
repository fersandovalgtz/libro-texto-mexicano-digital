#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

SOURCE_HOST = "libros.conaliteg.gob.mx"
USER_AGENT = "LTMD-U2-linearized-page-count-probe/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"
DEFAULT_PREFIX_BYTES = 65536


def fetch_prefix(url: str, *, prefix_bytes: int, timeout: float) -> tuple[bytes, dict[str, str], int]:
    if prefix_bytes <= 0 or prefix_bytes > 1048576:
        raise RuntimeError("prefix_bytes must be between 1 and 1048576")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,*/*;q=0.2",
            "Range": f"bytes=0-{prefix_bytes - 1}",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        status = int(response.status)
        final_url = response.geturl()
        headers = {k.lower(): v for k, v in response.headers.items()}
        body = response.read(prefix_bytes + 1)
    if status != 206:
        raise RuntimeError(f"expected HTTP 206, got {status}")
    if final_url != url:
        raise RuntimeError(f"unexpected redirect: {final_url}")
    if len(body) > prefix_bytes:
        raise RuntimeError("server returned more bytes than bounded range request")
    if not body.startswith(b"%PDF-"):
        raise RuntimeError("prefix does not begin with PDF signature")
    content_type = headers.get("content-type", "").split(";", 1)[0]
    if content_type != "application/pdf":
        raise RuntimeError(f"expected application/pdf, got {content_type!r}")
    return body, headers, status


def parse_linearization_dictionary(prefix: bytes) -> tuple[int | None, dict[str, object]]:
    # ISO 32000 linearization parameter dictionary is the first indirect object,
    # unencrypted, and includes /Linearized plus /N (number of pages).
    obj_match = re.search(rb"(?:\r?\n|\A)\s*(\d+)\s+(\d+)\s+obj\b", prefix)
    if not obj_match:
        return None, {"linearized": False, "reason": "first_indirect_object_not_found"}
    endobj = prefix.find(b"endobj", obj_match.end())
    if endobj < 0:
        return None, {"linearized": False, "reason": "first_object_not_complete_in_prefix"}
    first_object = prefix[obj_match.start():endobj + len(b"endobj")]
    if not re.search(rb"/Linearized\s+[0-9.]+", first_object):
        return None, {"linearized": False, "reason": "linearized_key_not_present_in_first_object"}
    count_match = re.search(rb"/N\s+(\d+)\b", first_object)
    if not count_match:
        return None, {"linearized": True, "reason": "N_key_not_present_in_linearization_dictionary"}
    count = int(count_match.group(1))
    if count <= 0:
        raise RuntimeError(f"invalid linearization /N page count: {count}")
    return count, {
        "linearized": True,
        "reason": "linearization_dictionary_N_observed",
        "first_object_number": int(obj_match.group(1)),
        "first_object_generation": int(obj_match.group(2)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read LTMD-U2 PDF page count from the bounded linearization dictionary prefix.")
    parser.add_argument("--viewer-key", default="P0CMA")
    parser.add_argument("--cycle", default="2026")
    parser.add_argument("--level", default="primaria")
    parser.add_argument("--prefix-bytes", type=int, default=DEFAULT_PREFIX_BYTES)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, default=Path("u2-linearized-page-count-pilot.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"[A-Z0-9]+", args.viewer_key):
        raise RuntimeError("invalid viewer key")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.level):
        raise RuntimeError("invalid level")
    if not re.fullmatch(r"[0-9]{4}", args.cycle):
        raise RuntimeError("invalid cycle")

    url = f"https://{SOURCE_HOST}/pdf-reader/assets/{args.level}/{args.cycle}/{args.viewer_key}.pdf"
    state = "observed"
    count = None
    details: dict[str, object] = {}
    error = None
    remote_total_bytes = None
    content_range = None
    try:
        prefix, headers, _status = fetch_prefix(url, prefix_bytes=args.prefix_bytes, timeout=args.timeout)
        content_range = headers.get("content-range")
        match = re.fullmatch(r"bytes 0-\d+/(\d+)", content_range or "")
        if match:
            remote_total_bytes = int(match.group(1))
        count, details = parse_linearization_dictionary(prefix)
        if count is None:
            state = "not_observed"
    except Exception as exc:
        state = "probe_error"
        error = f"{type(exc).__name__}: {exc}"
        prefix = b""

    result = {
        "schema": "LTMD_U2_LINEARIZED_PAGE_COUNT_PILOT_0.1",
        "source_object_id": f"CONALITEG:{args.cycle}:{args.level}:{args.viewer_key}",
        "asset_url": url,
        "observed_at": args.observed_at,
        "page_count_state": state,
        "page_count": count,
        "method": "pdf_linearization_dictionary_N_from_bounded_prefix",
        "prefix_bytes_requested": args.prefix_bytes,
        "prefix_bytes_received": len(prefix),
        "remote_total_bytes": remote_total_bytes,
        "content_range": content_range,
        "linearization": details,
        "error": error,
        "source_admission_state": "not_assessed",
        "text_verification_state": "not_assessed",
        "evidence_scope": "PDF linearization dictionary /N only; no page enumeration, text extraction, OCR, or semantic validation",
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if state == "observed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
