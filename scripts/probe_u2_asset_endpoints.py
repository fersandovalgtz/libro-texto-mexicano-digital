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
DEFAULT_OUTPUT = Path("u2-asset-probe.csv")
MAX_SAMPLE_BYTES = 262_144
USER_AGENT = "LTMD-U2-asset-probe/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"

OUTPUT_FIELDS = [
    "source_object_id",
    "viewer_key",
    "candidate_endpoint_url",
    "candidate_basis",
    "observed_at",
    "probe_method",
    "http_status",
    "endpoint_state",
    "final_url",
    "content_type",
    "content_length_header",
    "sample_bytes",
    "sample_truncated",
    "sample_sha256",
    "same_host_link_count",
    "same_host_pdf_links",
    "page_count_candidates",
    "evidence_scope",
    "observation_note",
]

LINK_RE = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
PAGE_COUNT_PATTERNS = [
    re.compile(r"(?:pageCount|numPages|totalPages|pages)\s*[:=]\s*[\"']?(\d{1,5})", re.IGNORECASE),
    re.compile(r"data-page-count\s*=\s*[\"'](\d{1,5})[\"']", re.IGNORECASE),
]


def candidate_url(row: dict[str, str]) -> str:
    cycle = row["source_cycle"]
    key = row["viewer_key"]
    if not (cycle.isdigit() and len(cycle) == 4):
        raise RuntimeError(f"{row['source_object_id']}: invalid source_cycle")
    if not re.fullmatch(r"[A-Z0-9]+", key):
        raise RuntimeError(f"{row['source_object_id']}: invalid viewer_key")
    return f"https://{SOURCE_HOST}/{cycle}/{key}.htm"


def classify_status(status: int | None) -> str:
    if status is None:
        return "transport_error"
    if 200 <= status < 400:
        return "resolved"
    if status == 404:
        return "not_found"
    if status in {401, 403}:
        return "forbidden"
    if 500 <= status < 600:
        return "server_error"
    return "http_other"


def bounded_read(response) -> tuple[bytes, bool]:
    data = response.read(MAX_SAMPLE_BYTES + 1)
    return data[:MAX_SAMPLE_BYTES], len(data) > MAX_SAMPLE_BYTES


def scan_text(base_url: str, body: bytes, content_type: str) -> tuple[list[str], list[str]]:
    if not ("html" in content_type.lower() or "text" in content_type.lower()):
        return [], []
    text = body.decode("utf-8", errors="replace")
    links: set[str] = set()
    for raw in LINK_RE.findall(text):
        url = urllib.parse.urljoin(base_url, raw)
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme == "https" and parsed.hostname == SOURCE_HOST:
            links.add(url)
    page_counts: set[str] = set()
    for pattern in PAGE_COUNT_PATTERNS:
        page_counts.update(pattern.findall(text))
    return sorted(links), sorted(page_counts, key=int)


def probe(row: dict[str, str], observed_at: str, timeout: float) -> dict[str, str]:
    url = candidate_url(row)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.8,*/*;q=0.5",
            "Range": f"bytes=0-{MAX_SAMPLE_BYTES - 1}",
        },
        method="GET",
    )

    status: int | None = None
    final_url = url
    content_type = "not_exposed"
    content_length = "not_exposed"
    body = b""
    truncated = False
    transport_note = ""

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
            final_url = response.geturl()
            parsed_final = urllib.parse.urlparse(final_url)
            if parsed_final.scheme != "https" or parsed_final.hostname != SOURCE_HOST:
                raise RuntimeError(f"redirected outside institutional host: {final_url}")
            content_type = response.headers.get("Content-Type", "not_exposed").split(";", 1)[0].strip()
            content_length = response.headers.get("Content-Length", "not_exposed")
            body, truncated = bounded_read(response)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        final_url = exc.geturl() or url
        content_type = exc.headers.get("Content-Type", "not_exposed").split(";", 1)[0].strip()
        content_length = exc.headers.get("Content-Length", "not_exposed")
        try:
            body, truncated = bounded_read(exc)
        except Exception:
            body = b""
            truncated = False
        transport_note = f"HTTPError {status}"
    except (urllib.error.URLError, TimeoutError, socket.timeout, RuntimeError) as exc:
        transport_note = f"{type(exc).__name__}: {exc}"

    links, page_counts = scan_text(final_url, body, content_type)
    pdf_links = [link for link in links if urllib.parse.urlparse(link).path.lower().endswith(".pdf")]

    state = classify_status(status)
    status_text = str(status) if status is not None else "not_exposed"
    sample_hash = hashlib.sha256(body).hexdigest() if body else "not_observed"

    note_parts = [
        "Bounded metadata/content probe only; response body is not persisted.",
        "Candidate endpoint derives from the current CONALITEG cycle/key .htm convention observed in reader behavior; resolution must be measured per object.",
    ]
    if transport_note:
        note_parts.append(transport_note)
    if page_counts:
        note_parts.append("Page-count values are parser candidates only, not validated page counts.")

    return {
        "source_object_id": row["source_object_id"],
        "viewer_key": row["viewer_key"],
        "candidate_endpoint_url": url,
        "candidate_basis": "CONALITEG current reader observed requesting /<source_cycle>/<viewer_key>.htm; tested independently per object",
        "observed_at": observed_at,
        "probe_method": f"bounded_get_range_0_{MAX_SAMPLE_BYTES - 1}",
        "http_status": status_text,
        "endpoint_state": state,
        "final_url": final_url,
        "content_type": content_type,
        "content_length_header": content_length,
        "sample_bytes": str(len(body)),
        "sample_truncated": "true" if truncated else "false",
        "sample_sha256": sample_hash,
        "same_host_link_count": str(len(links)),
        "same_host_pdf_links": "|".join(pdf_links),
        "page_count_candidates": "|".join(page_counts),
        "evidence_scope": "endpoint_transport_and_bounded_html_metadata_only",
        "observation_note": " ".join(note_parts),
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
    parser = argparse.ArgumentParser(description="Probe bounded LTMD-U2 CONALITEG asset endpoint candidates without persisting source bodies.")
    parser.add_argument("--source-objects", type=Path, default=DEFAULT_SOURCE_OBJECTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--timeout", type=float, default=15.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_rows = read_source_objects(args.source_objects)
    results = [probe(row, args.observed_at, args.timeout) for row in source_rows]
    write_rows(args.output, results)
    counts: dict[str, int] = {}
    for row in results:
        counts[row["endpoint_state"]] = counts.get(row["endpoint_state"], 0) + 1
    print(f"LTMD-U2 bounded asset endpoint probe: total={len(results)} states={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
