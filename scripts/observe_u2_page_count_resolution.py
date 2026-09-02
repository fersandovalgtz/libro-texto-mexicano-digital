#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import urllib.request
from pathlib import Path

SOURCE_HOST = "libros.conaliteg.gob.mx"
EXPECTED_OBJECTS = 39
METHOD = "targeted_tail_startxref_classic_xref_catalog_pages_count"
EVIDENCE_SCOPE = (
    "structural trailer/xref/catalog/root-/Pages-/Count only; "
    "no page enumeration, text extraction, OCR, or semantic validation"
)
USER_AGENT = "LTMD-U2-page-count-observer/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"

OUTPUT_FIELDS = [
    "source_object_id",
    "viewer_key",
    "asset_url",
    "observed_at",
    "page_count_state",
    "page_count",
    "remote_total_bytes",
    "network_bytes_fetched",
    "range_requests",
    "max_network_bytes",
    "startxref_offset",
    "xref_kind",
    "xref_sections_traversed",
    "root_ref",
    "pages_ref",
    "method",
    "source_admission_state",
    "text_verification_state",
    "evidence_scope",
    "error",
]


class BudgetExceeded(RuntimeError):
    pass


class RangeClient:
    def __init__(self, url: str, *, max_bytes: int, timeout: float):
        self.url = url
        self.max_bytes = max_bytes
        self.timeout = timeout
        self.network_bytes = 0
        self.requests = 0
        self.length = self._discover_length()

    def _open_range(self, start: int, end: int) -> tuple[bytes, str]:
        if start < 0 or end < start:
            raise RuntimeError("invalid byte range")
        requested = end - start + 1
        if self.network_bytes + requested > self.max_bytes:
            raise BudgetExceeded(
                f"budget exceeded: fetched={self.network_bytes} requested={requested} max={self.max_bytes}"
            )
        request = urllib.request.Request(
            self.url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/pdf,*/*;q=0.2",
                "Range": f"bytes={start}-{end}",
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            if int(response.status) != 206:
                raise RuntimeError(f"expected HTTP 206, got {response.status}")
            if response.geturl() != self.url:
                raise RuntimeError(f"unexpected redirect: {response.geturl()}")
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
            if content_type != "application/pdf":
                raise RuntimeError(f"expected application/pdf, got {content_type!r}")
            content_range = response.headers.get("Content-Range", "")
            body = response.read(requested + 1)
        if len(body) != requested:
            raise RuntimeError(f"range length mismatch: requested={requested} received={len(body)}")
        self.network_bytes += len(body)
        self.requests += 1
        return body, content_range

    def _discover_length(self) -> int:
        request = urllib.request.Request(
            self.url,
            headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            if int(response.status) != 206:
                raise RuntimeError(f"expected HTTP 206 for length probe, got {response.status}")
            if response.geturl() != self.url:
                raise RuntimeError(f"unexpected redirect: {response.geturl()}")
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
            content_range = response.headers.get("Content-Range", "")
            body = response.read(2)
        if content_type != "application/pdf":
            raise RuntimeError(f"expected application/pdf, got {content_type!r}")
        match = re.fullmatch(r"bytes 0-0/(\d+)", content_range)
        if not match or body != b"%":
            raise RuntimeError("unable to establish PDF length/signature")
        self.network_bytes = 1
        self.requests = 1
        return int(match.group(1))

    def get(self, start: int, end: int) -> bytes:
        end = min(end, self.length - 1)
        body, content_range = self._open_range(start, end)
        expected = f"bytes {start}-{end}/{self.length}"
        if content_range != expected:
            raise RuntimeError(f"Content-Range mismatch: expected {expected!r}, got {content_range!r}")
        return body


def last_startxref(tail: bytes) -> int:
    matches = list(re.finditer(rb"startxref\s+(\d+)\s+%%EOF", tail))
    if not matches:
        matches = list(re.finditer(rb"startxref\s+(\d+)", tail))
    if not matches:
        raise RuntimeError("startxref not found in bounded tail")
    return int(matches[-1].group(1))


def parse_classic_xref(section: bytes) -> tuple[dict[int, int], tuple[int, int] | None, int | None]:
    if not section.startswith(b"xref"):
        raise RuntimeError("xref_at_startxref_is_not_classic")
    lines = section.splitlines()
    if not lines or lines[0].strip() != b"xref":
        raise RuntimeError("malformed classic xref header")

    entries: dict[int, int] = {}
    index = 1
    trailer_start: int | None = None
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == b"trailer":
            trailer_start = index + 1
            break
        header = re.fullmatch(rb"(\d+)\s+(\d+)", line)
        if not header:
            raise RuntimeError(f"unexpected xref subsection header: {line[:80]!r}")
        first = int(header.group(1))
        count = int(header.group(2))
        index += 1
        if index + count > len(lines):
            raise RuntimeError("xref section truncated before all entries")
        for ordinal in range(count):
            entry = lines[index + ordinal].strip()
            match = re.fullmatch(rb"(\d{10})\s+(\d{5})\s+([nf])\s*", entry)
            if not match:
                raise RuntimeError(f"malformed xref entry: {entry[:80]!r}")
            if match.group(3) == b"n":
                entries[first + ordinal] = int(match.group(1))
        index += count

    if trailer_start is None:
        raise RuntimeError("trailer not found in bounded xref section")
    trailer = b"\n".join(lines[trailer_start:])
    root_match = re.search(rb"/Root\s+(\d+)\s+(\d+)\s+R\b", trailer)
    prev_match = re.search(rb"/Prev\s+(\d+)\b", trailer)
    root_ref = (int(root_match.group(1)), int(root_match.group(2))) if root_match else None
    prev = int(prev_match.group(1)) if prev_match else None
    return entries, root_ref, prev


def fetch_indirect_object(client: RangeClient, offset: int, *, window: int) -> bytes:
    body = client.get(offset, offset + window - 1)
    end = body.find(b"endobj")
    if end < 0:
        raise RuntimeError(f"indirect object at offset {offset} exceeds {window}-byte window")
    return body[: end + len(b"endobj")]


def ref_text(value: tuple[int, int] | None) -> str:
    return f"{value[0]} {value[1]} R" if value else "not_observed"


def observe_one(
    asset: dict[str, str],
    *,
    observed_at: str,
    max_bytes: int,
    xref_window: int,
    tail_bytes: int,
    object_window: int,
    timeout: float,
) -> dict[str, str]:
    source_id = asset["source_object_id"]
    key = asset["viewer_key"]
    url = asset["asset_url"]
    if asset["asset_resolution_state"] != "resolved_pdf":
        raise RuntimeError(f"{source_id}: page-count observation requires resolved_pdf")
    if not re.fullmatch(r"https://libros\.conaliteg\.gob\.mx/pdf-reader/assets/primaria/2026/[A-Z0-9]+\.pdf", url):
        raise RuntimeError(f"{source_id}: unexpected asset URL")

    state = "observed"
    page_count: int | None = None
    startxref_offset: int | None = None
    xref_kind = "not_observed"
    xref_sections = 0
    root_ref: tuple[int, int] | None = None
    pages_ref: tuple[int, int] | None = None
    error = "none"
    client: RangeClient | None = None

    try:
        client = RangeClient(url, max_bytes=max_bytes, timeout=timeout)
        if client.length != int(asset["total_bytes"]):
            raise RuntimeError(
                f"remote byte length changed: expected={asset['total_bytes']} observed={client.length}"
            )
        tail_start = max(0, client.length - tail_bytes)
        startxref_offset = last_startxref(client.get(tail_start, client.length - 1))

        merged_entries: dict[int, int] = {}
        current: int | None = startxref_offset
        seen_offsets: set[int] = set()
        while current is not None:
            if current in seen_offsets or len(seen_offsets) >= 16:
                raise RuntimeError("xref /Prev chain cycle or excessive depth")
            seen_offsets.add(current)
            section = client.get(current, min(client.length - 1, current + xref_window - 1))
            if not section.startswith(b"xref"):
                raise RuntimeError("xref_at_startxref_is_not_classic")
            xref_kind = "classic"
            entries, candidate_root, prev = parse_classic_xref(section)
            xref_sections += 1
            for objnum, offset in entries.items():
                merged_entries.setdefault(objnum, offset)
            if root_ref is None and candidate_root is not None:
                root_ref = candidate_root
            current = prev

        if root_ref is None:
            raise RuntimeError("/Root reference not found in trailer chain")
        root_offset = merged_entries.get(root_ref[0])
        if root_offset is None:
            raise RuntimeError(f"xref entry for /Root object {root_ref[0]} not found")
        root_obj = fetch_indirect_object(client, root_offset, window=object_window)
        pages_match = re.search(rb"/Pages\s+(\d+)\s+(\d+)\s+R\b", root_obj)
        if not pages_match:
            raise RuntimeError("/Pages reference not found in catalog object")
        pages_ref = (int(pages_match.group(1)), int(pages_match.group(2)))
        pages_offset = merged_entries.get(pages_ref[0])
        if pages_offset is None:
            raise RuntimeError(f"xref entry for /Pages object {pages_ref[0]} not found")
        pages_obj = fetch_indirect_object(client, pages_offset, window=object_window)
        count_match = re.search(rb"/Count\s+(\d+)\b", pages_obj)
        if not count_match:
            raise RuntimeError("/Count not found in root /Pages object")
        page_count = int(count_match.group(1))
        if page_count <= 0:
            raise RuntimeError(f"invalid /Pages /Count: {page_count}")
    except Exception as exc:
        state = "unresolved"
        error = f"{type(exc).__name__}: {exc}"

    return {
        "source_object_id": source_id,
        "viewer_key": key,
        "asset_url": url,
        "observed_at": observed_at,
        "page_count_state": state,
        "page_count": str(page_count) if page_count is not None else "not_observed",
        "remote_total_bytes": str(client.length) if client else "not_observed",
        "network_bytes_fetched": str(client.network_bytes) if client else "0",
        "range_requests": str(client.requests) if client else "0",
        "max_network_bytes": str(max_bytes),
        "startxref_offset": str(startxref_offset) if startxref_offset is not None else "not_observed",
        "xref_kind": xref_kind,
        "xref_sections_traversed": str(xref_sections),
        "root_ref": ref_text(root_ref),
        "pages_ref": ref_text(pages_ref),
        "method": METHOD,
        "source_admission_state": "not_assessed",
        "text_verification_state": "not_assessed",
        "evidence_scope": EVIDENCE_SCOPE,
        "error": error,
    }


def read_assets(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_OBJECTS:
        raise RuntimeError(f"expected {EXPECTED_OBJECTS} U2 assets, got {len(rows)}")
    if len({row["source_object_id"] for row in rows}) != len(rows):
        raise RuntimeError("asset source_object_id values must be unique")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Observe LTMD-U2 root PDF page-tree /Count values using bounded HTTP ranges; source PDFs are never persisted."
    )
    parser.add_argument("--assets", type=Path, default=Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--max-bytes", type=int, default=4194304)
    parser.add_argument("--xref-window", type=int, default=3145728)
    parser.add_argument("--tail-bytes", type=int, default=65536)
    parser.add_argument("--object-window", type=int, default=65536)
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    assets = read_assets(args.assets)
    rows = [
        observe_one(
            asset,
            observed_at=args.observed_at,
            max_bytes=args.max_bytes,
            xref_window=args.xref_window,
            tail_bytes=args.tail_bytes,
            object_window=args.object_window,
            timeout=args.timeout,
        )
        for asset in assets
    ]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    observed = [row for row in rows if row["page_count_state"] == "observed"]
    unresolved = [row for row in rows if row["page_count_state"] != "observed"]
    print(
        f"LTMD-U2 structural page-count observation: total={len(rows)} observed={len(observed)} "
        f"unresolved={len(unresolved)} network_bytes={sum(int(row['network_bytes_fetched']) for row in rows)}"
    )
    for row in unresolved:
        print(f"UNRESOLVED {row['source_object_id']}: {row['error']}")
    return 0 if not unresolved else 2


if __name__ == "__main__":
    raise SystemExit(main())
