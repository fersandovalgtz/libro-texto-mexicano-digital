#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import re
import urllib.error
import urllib.request
from collections import OrderedDict
from pathlib import Path

from pypdf import PdfReader, __version__ as pypdf_version

SOURCE_HOST = "libros.conaliteg.gob.mx"
USER_AGENT = "LTMD-U2-page-count-range-probe/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"


class BudgetExceeded(RuntimeError):
    pass


class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url: str, *, chunk_size: int, max_bytes: int, timeout: float):
        super().__init__()
        self.url = url
        self.chunk_size = chunk_size
        self.max_bytes = max_bytes
        self.timeout = timeout
        self.pos = 0
        self.requests = 0
        self.fetched_bytes = 0
        self.cache: OrderedDict[int, bytes] = OrderedDict()
        self.length = self._discover_length()

    def _request_range(self, start: int, end: int) -> tuple[bytes, str]:
        if start < 0 or end < start:
            raise ValueError("invalid byte range")
        requested = end - start + 1
        if self.fetched_bytes + requested > self.max_bytes:
            raise BudgetExceeded(
                f"range budget exceeded before request: fetched={self.fetched_bytes} requested={requested} max={self.max_bytes}"
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
            body = response.read(requested + 1)
        if len(body) > requested:
            raise RuntimeError("server returned more bytes than bounded range request")
        self.requests += 1
        self.fetched_bytes += len(body)
        return body, content_range

    def _discover_length(self) -> int:
        body, content_range = self._request_range(0, 0)
        if body != b"%":
            raise RuntimeError("first-byte probe does not match PDF signature prefix")
        match = re.fullmatch(r"bytes 0-0/(\d+)", content_range)
        if not match:
            raise RuntimeError(f"unexpected Content-Range: {content_range!r}")
        length = int(match.group(1))
        if length <= 0:
            raise RuntimeError("invalid remote length")
        return length

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new = offset
        elif whence == io.SEEK_CUR:
            new = self.pos + offset
        elif whence == io.SEEK_END:
            new = self.length + offset
        else:
            raise ValueError("unsupported whence")
        if new < 0:
            raise ValueError("negative seek position")
        self.pos = min(new, self.length)
        return self.pos

    def _chunk(self, index: int) -> bytes:
        if index in self.cache:
            data = self.cache.pop(index)
            self.cache[index] = data
            return data
        start = index * self.chunk_size
        if start >= self.length:
            return b""
        end = min(start + self.chunk_size - 1, self.length - 1)
        data, content_range = self._request_range(start, end)
        expected = f"bytes {start}-{start + len(data) - 1}/{self.length}"
        if content_range != expected:
            raise RuntimeError(f"range mismatch: expected {expected!r}, got {content_range!r}")
        self.cache[index] = data
        return data

    def read(self, size: int = -1) -> bytes:
        if self.pos >= self.length:
            return b""
        if size is None or size < 0:
            size = self.length - self.pos
        size = min(size, self.length - self.pos)
        if size == 0:
            return b""
        pieces: list[bytes] = []
        remaining = size
        while remaining > 0:
            index = self.pos // self.chunk_size
            within = self.pos % self.chunk_size
            chunk = self._chunk(index)
            if not chunk or within >= len(chunk):
                break
            take = min(remaining, len(chunk) - within)
            pieces.append(chunk[within:within + take])
            self.pos += take
            remaining -= take
        return b"".join(pieces)

    def readinto(self, b) -> int:
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bounded HTTP-range pilot for LTMD-U2 PDF page counts.")
    parser.add_argument("--viewer-key", default="P0CMA")
    parser.add_argument("--cycle", default="2026")
    parser.add_argument("--level", default="primaria")
    parser.add_argument("--chunk-size", type=int, default=262144)
    parser.add_argument("--max-bytes", type=int, default=16777216)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", type=Path, default=Path("u2-page-count-pilot.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"[A-Z0-9]+", args.viewer_key):
        raise RuntimeError("invalid viewer key")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.level):
        raise RuntimeError("invalid level")
    if not re.fullmatch(r"[0-9]{4}", args.cycle):
        raise RuntimeError("invalid cycle")

    url = (
        f"https://{SOURCE_HOST}/pdf-reader/assets/"
        f"{args.level}/{args.cycle}/{args.viewer_key}.pdf"
    )
    remote = HTTPRangeFile(
        url,
        chunk_size=args.chunk_size,
        max_bytes=args.max_bytes,
        timeout=args.timeout,
    )
    state = "observed"
    page_count = None
    error = None
    try:
        buffered = io.BufferedReader(remote, buffer_size=65536)
        reader = PdfReader(buffered, strict=False)
        page_count = len(reader.pages)
    except BudgetExceeded as exc:
        state = "budget_exceeded"
        error = str(exc)
    except Exception as exc:
        state = "parser_error"
        error = f"{type(exc).__name__}: {exc}"

    result = {
        "schema": "LTMD_U2_PAGE_COUNT_RANGE_PILOT_0.1",
        "source_object_id": f"CONALITEG:{args.cycle}:{args.level}:{args.viewer_key}",
        "asset_url": url,
        "observed_at": args.observed_at,
        "page_count_state": state,
        "page_count": page_count,
        "parser": "pypdf",
        "parser_version": pypdf_version,
        "method": "seekable_http_range_reader_no_source_file_persisted",
        "remote_total_bytes": remote.length,
        "chunk_size": args.chunk_size,
        "max_network_bytes": args.max_bytes,
        "range_requests": remote.requests,
        "network_bytes_fetched": remote.fetched_bytes,
        "cached_chunks": len(remote.cache),
        "error": error,
        "source_admission_state": "not_assessed",
        "text_verification_state": "not_assessed",
        "evidence_scope": "page-tree count only; no text or semantic validation",
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if state == "observed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
