#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

SOURCE_HOST = "libros.conaliteg.gob.mx"
USER_AGENT = "LTMD-U2-classic-xref-page-count-probe/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"


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

    def get(self, start: int, end: int) -> bytes:
        if start < 0 or end < start:
            raise RuntimeError("invalid range")
        end = min(end, self.length - 1)
        requested = end - start + 1
        if self.network_bytes + requested > self.max_bytes:
            raise BudgetExceeded(
                f"budget exceeded: fetched={self.network_bytes} requested={requested} max={self.max_bytes}"
            )
        req = urllib.request.Request(
            self.url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/pdf,*/*;q=0.2",
                "Range": f"bytes={start}-{end}",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            if int(response.status) != 206:
                raise RuntimeError(f"expected HTTP 206, got {response.status}")
            if response.geturl() != self.url:
                raise RuntimeError(f"unexpected redirect: {response.geturl()}")
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
            if content_type != "application/pdf":
                raise RuntimeError(f"expected application/pdf, got {content_type!r}")
            content_range = response.headers.get("Content-Range", "")
            expected = f"bytes {start}-{end}/{self.length}"
            if self.length and content_range != expected:
                raise RuntimeError(f"Content-Range mismatch: expected {expected!r}, got {content_range!r}")
            body = response.read(requested + 1)
        if len(body) != requested:
            raise RuntimeError(f"range length mismatch: requested={requested} received={len(body)}")
        self.network_bytes += len(body)
        self.requests += 1
        return body

    def _discover_length(self) -> int:
        req = urllib.request.Request(
            self.url,
            headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            if int(response.status) != 206:
                raise RuntimeError(f"expected HTTP 206 for length probe, got {response.status}")
            content_range = response.headers.get("Content-Range", "")
            body = response.read(2)
        match = re.fullmatch(r"bytes 0-0/(\d+)", content_range)
        if not match or body != b"%":
            raise RuntimeError("unable to establish PDF length/signature")
        self.network_bytes = 1
        self.requests = 1
        return int(match.group(1))


def last_startxref(tail: bytes) -> int:
    matches = list(re.finditer(rb"startxref\s+(\d+)\s+%%EOF", tail))
    if not matches:
        matches = list(re.finditer(rb"startxref\s+(\d+)", tail))
    if not matches:
        raise RuntimeError("startxref not found in tail")
    return int(matches[-1].group(1))


def parse_classic_xref(section: bytes) -> tuple[dict[int, int], tuple[int, int] | None, int | None]:
    if not section.startswith(b"xref"):
        raise RuntimeError("xref_at_startxref_is_not_classic")
    lines = section.splitlines()
    if not lines or lines[0].strip() != b"xref":
        raise RuntimeError("malformed classic xref header")
    entries: dict[int, int] = {}
    i = 1
    trailer_start = None
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == b"trailer":
            trailer_start = i + 1
            break
        header = re.fullmatch(rb"(\d+)\s+(\d+)", line)
        if not header:
            raise RuntimeError(f"unexpected xref subsection header: {line[:80]!r}")
        first = int(header.group(1))
        count = int(header.group(2))
        i += 1
        if i + count > len(lines):
            raise RuntimeError("xref section truncated before all entries")
        for ordinal in range(count):
            entry = lines[i + ordinal].strip()
            match = re.fullmatch(rb"(\d{10})\s+(\d{5})\s+([nf])\s*", entry)
            if not match:
                raise RuntimeError(f"malformed xref entry: {entry[:80]!r}")
            if match.group(3) == b"n":
                entries[first + ordinal] = int(match.group(1))
        i += count
    if trailer_start is None:
        raise RuntimeError("trailer not found in xref section")
    trailer_bytes = b"\n".join(lines[trailer_start:])
    root_match = re.search(rb"/Root\s+(\d+)\s+(\d+)\s+R\b", trailer_bytes)
    prev_match = re.search(rb"/Prev\s+(\d+)\b", trailer_bytes)
    root_ref = (int(root_match.group(1)), int(root_match.group(2))) if root_match else None
    prev = int(prev_match.group(1)) if prev_match else None
    return entries, root_ref, prev


def fetch_indirect_object(client: RangeClient, offset: int, *, window: int = 65536) -> bytes:
    body = client.get(offset, offset + window - 1)
    end = body.find(b"endobj")
    if end < 0:
        raise RuntimeError(f"indirect object at offset {offset} exceeds {window}-byte window")
    return body[: end + len(b"endobj")]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Targeted classic-xref LTMD-U2 PDF structural page-count probe.")
    parser.add_argument("--viewer-key", default="P0CMA")
    parser.add_argument("--cycle", default="2026")
    parser.add_argument("--level", default="primaria")
    parser.add_argument("--tail-bytes", type=int, default=65536)
    parser.add_argument("--xref-window", type=int, default=524288)
    parser.add_argument("--object-window", type=int, default=65536)
    parser.add_argument("--max-bytes", type=int, default=4194304)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, default=Path("u2-classic-xref-page-count-pilot.json"))
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
    page_count = None
    xref_kind = None
    startxref_offset = None
    xref_sections = 0
    root_ref = None
    pages_ref = None
    error = None
    client = None
    try:
        client = RangeClient(url, max_bytes=args.max_bytes, timeout=args.timeout)
        tail_start = max(0, client.length - args.tail_bytes)
        tail = client.get(tail_start, client.length - 1)
        startxref_offset = last_startxref(tail)

        merged_entries: dict[int, int] = {}
        current = startxref_offset
        seen_offsets: set[int] = set()
        while current is not None:
            if current in seen_offsets or len(seen_offsets) >= 16:
                raise RuntimeError("xref /Prev chain cycle or excessive depth")
            seen_offsets.add(current)
            section = client.get(current, min(client.length - 1, current + args.xref_window - 1))
            if not section.startswith(b"xref"):
                xref_kind = "xref_stream_or_other"
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
        root_obj = fetch_indirect_object(client, root_offset, window=args.object_window)
        pages_match = re.search(rb"/Pages\s+(\d+)\s+(\d+)\s+R\b", root_obj)
        if not pages_match:
            raise RuntimeError("/Pages reference not found in catalog object")
        pages_ref = (int(pages_match.group(1)), int(pages_match.group(2)))
        pages_offset = merged_entries.get(pages_ref[0])
        if pages_offset is None:
            raise RuntimeError(f"xref entry for /Pages object {pages_ref[0]} not found")
        pages_obj = fetch_indirect_object(client, pages_offset, window=args.object_window)
        count_match = re.search(rb"/Count\s+(\d+)\b", pages_obj)
        if not count_match:
            raise RuntimeError("/Count not found in root /Pages object")
        page_count = int(count_match.group(1))
        if page_count <= 0:
            raise RuntimeError(f"invalid /Pages /Count: {page_count}")
    except BudgetExceeded as exc:
        state = "budget_exceeded"
        error = str(exc)
    except Exception as exc:
        state = "not_observed" if str(exc) == "xref_at_startxref_is_not_classic" else "probe_error"
        error = f"{type(exc).__name__}: {exc}"

    result = {
        "schema": "LTMD_U2_CLASSIC_XREF_PAGE_COUNT_PILOT_0.1",
        "source_object_id": f"CONALITEG:{args.cycle}:{args.level}:{args.viewer_key}",
        "asset_url": url,
        "observed_at": args.observed_at,
        "page_count_state": state,
        "page_count": page_count,
        "method": "targeted_tail_startxref_classic_xref_catalog_pages_count",
        "remote_total_bytes": client.length if client else None,
        "network_bytes_fetched": client.network_bytes if client else 0,
        "range_requests": client.requests if client else 0,
        "max_network_bytes": args.max_bytes,
        "startxref_offset": startxref_offset,
        "xref_kind": xref_kind,
        "xref_sections_traversed": xref_sections,
        "root_ref": list(root_ref) if root_ref else None,
        "pages_ref": list(pages_ref) if pages_ref else None,
        "error": error,
        "source_admission_state": "not_assessed",
        "text_verification_state": "not_assessed",
        "evidence_scope": "structural trailer/xref/catalog/root-/Pages-/Count only; no page enumeration, text extraction, OCR, or semantic validation",
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if state == "observed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
