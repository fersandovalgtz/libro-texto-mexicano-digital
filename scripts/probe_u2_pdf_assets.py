#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE_HOST = "libros.conaliteg.gob.mx"
DEFAULT_SOURCE_OBJECTS = Path("data/catalog/ltmd_u2_source_objects_2026_2027.csv")
DEFAULT_OUTPUT = Path("u2-pdf-asset-probe.csv")
SAMPLE_BYTES = 32
USER_AGENT = "LTMD-U2-pdf-asset-probe/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"

OUTPUT_FIELDS = [
    "source_object_id",
    "viewer_key",
    "candidate_pdf_url",
    "candidate_basis",
    "observed_at",
    "probe_method",
    "http_status",
    "asset_resolution_state",
    "final_url",
    "content_type",
    "content_length_header",
    "content_range",
    "accept_ranges",
    "etag",
    "last_modified",
    "sample_bytes",
    "sample_sha256",
    "pdf_signature",
    "evidence_scope",
    "observation_note",
]


def candidate_url(row: dict[str, str]) -> str:
    cycle = row["source_cycle"]
    key = row["viewer_key"]
    if not (cycle.isdigit() and len(cycle) == 4):
        raise RuntimeError(f"{row['source_object_id']}: invalid source_cycle")
    if not re.fullmatch(r"[A-Z0-9]+", key):
        raise RuntimeError(f"{row['source_object_id']}: invalid viewer_key")
    return f"https://{SOURCE_HOST}/{cycle}/{key}.pdf"


def classify(status: int | None, is_pdf: bool) -> str:
    if status is None:
        return "transport_error"
    if status in {200, 206}:
        return "resolved_pdf" if is_pdf else "resolved_non_pdf"
    if status == 404:
        return "not_found"
    if status in {401, 403}:
        return "forbidden"
    if 500 <= status < 600:
        return "server_error"
    return "http_other"


def clean_header(value: str | None) -> str:
    return value.strip() if value else "not_exposed"


def probe(row: dict[str, str], observed_at: str, timeout: float) -> dict[str, str]:
    url = candidate_url(row)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/pdf,*/*;q=0.2",
            "Range": f"bytes=0-{SAMPLE_BYTES - 1}",
        },
        method="GET",
    )

    status: int | None = None
    final_url = url
    headers = None
    body = b""
    transport_note = ""

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            final_url = response.geturl()
            parsed_final = urllib.parse.urlparse(final_url)
            if parsed_final.scheme != "https" or parsed_final.hostname != SOURCE_HOST:
                raise RuntimeError(f"redirected outside institutional host: {final_url}")
            headers = response.headers
            body = response.read(SAMPLE_BYTES)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        final_url = exc.geturl() or url
        headers = exc.headers
        try:
            body = exc.read(SAMPLE_BYTES)
        except Exception:
            body = b""
        transport_note = f"HTTPError {status}"
    except (urllib.error.URLError, TimeoutError, socket.timeout, RuntimeError) as exc:
        transport_note = f"{type(exc).__name__}: {exc}"

    content_type = clean_header(headers.get("Content-Type") if headers else None).split(";", 1)[0]
    content_length = clean_header(headers.get("Content-Length") if headers else None)
    content_range = clean_header(headers.get("Content-Range") if headers else None)
    accept_ranges = clean_header(headers.get("Accept-Ranges") if headers else None)
    etag = clean_header(headers.get("ETag") if headers else None)
    last_modified = clean_header(headers.get("Last-Modified") if headers else None)

    is_pdf = body.startswith(b"%PDF-")
    state = classify(status, is_pdf)
    sample_hash = hashlib.sha256(body).hexdigest() if body else "not_observed"

    notes = [
        "Bounded 32-byte HTTP Range probe only; source PDF bytes are not persisted.",
        "Candidate URL is derived from the current CONALITEG reader.bundle.js rule: cycle/key -> /<cycle>/<key>.pdf.",
        "resolved_pdf establishes transport-level PDF asset resolution only; it does not establish open licensing, OCR availability, text verification, semantic readiness, or historical validity.",
    ]
    if status == 200:
        notes.append("Server returned 200 rather than 206; probe still read only the first 32 bytes and closed the response.")
    if transport_note:
        notes.append(transport_note)

    return {
        "source_object_id": row["source_object_id"],
        "viewer_key": row["viewer_key"],
        "candidate_pdf_url": url,
        "candidate_basis": "current CONALITEG pdf-reader/reader.bundle.js constructs /<ciclo>/<clave>.pdf when ciclo is present",
        "observed_at": observed_at,
        "probe_method": "http_get_range_bytes_0_31_read_max_32",
        "http_status": str(status) if status is not None else "not_exposed",
        "asset_resolution_state": state,
        "final_url": final_url,
        "content_type": content_type,
        "content_length_header": content_length,
        "content_range": content_range,
        "accept_ranges": accept_ranges,
        "etag": etag,
        "last_modified": last_modified,
        "sample_bytes": str(len(body)),
        "sample_sha256": sample_hash,
        "pdf_signature": "true" if is_pdf else "false",
        "evidence_scope": "transport_headers_and_first_32_bytes_pdf_signature_only",
        "observation_note": " ".join(notes),
    }


def read_source_objects(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 39:
        raise RuntimeError(f"expected 39 U2 source objects, got {len(rows)}")
    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe LTMD-U2 CONALITEG PDF asset candidates with a bounded 32-byte range read.")
    parser.add_argument("--source-objects", type=Path, default=DEFAULT_SOURCE_OBJECTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--timeout", type=float, default=15.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [probe(row, args.observed_at, args.timeout) for row in read_source_objects(args.source_objects)]
    write_rows(args.output, rows)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["asset_resolution_state"]] = counts.get(row["asset_resolution_state"], 0) + 1
    print(f"LTMD-U2 PDF asset probe: total={len(rows)} states={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
