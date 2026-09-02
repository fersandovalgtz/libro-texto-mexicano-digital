#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HOST = "libros.conaliteg.gob.mx"
USER_AGENT = "LTMD-U2-reader-infra-probe/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"
MAX_HTML_BYTES = 524_288
MAX_SCRIPT_BYTES = 1_048_576

SCRIPT_SRC_RE = re.compile(r"<script\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"'][^>]*>", re.I)
LINK_HREF_RE = re.compile(r"<link\b[^>]*\bhref\s*=\s*[\"']([^\"']+)[\"'][^>]*>", re.I)
INLINE_SCRIPT_RE = re.compile(r"<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>", re.I | re.S)

# Only record URL/path-like literals and endpoint-shape clues, never arbitrary source text.
CLUE_PATTERNS = [
    re.compile(r"[\"']([^\"']{0,180}(?:\.htm|\.html|\.pdf|\.json|\.jpg|\.jpeg|\.png|\.webp|\.js|\.css)[^\"']{0,80})[\"']", re.I),
    re.compile(r"[\"']([^\"']{0,180}(?:ciclo|clave|nivel|page|pagina|página|pages|assets|images|libros|reader)[^\"']{0,80})[\"']", re.I),
]


def bounded_get(url: str, max_bytes: int, timeout: float) -> dict[str, object]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/javascript,text/javascript,*/*;q=0.5"},
        method="GET",
    )
    status = None
    final_url = url
    content_type = "not_exposed"
    content_length = "not_exposed"
    body = b""
    truncated = False
    error = ""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = int(response.status)
            final_url = response.geturl()
            parsed = urllib.parse.urlparse(final_url)
            if parsed.scheme != "https" or parsed.hostname != HOST:
                raise RuntimeError(f"redirected outside institutional host: {final_url}")
            content_type = response.headers.get("Content-Type", "not_exposed").split(";", 1)[0].strip()
            content_length = response.headers.get("Content-Length", "not_exposed")
            raw = response.read(max_bytes + 1)
            body = raw[:max_bytes]
            truncated = len(raw) > max_bytes
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        final_url = exc.geturl() or url
        content_type = exc.headers.get("Content-Type", "not_exposed").split(";", 1)[0].strip()
        content_length = exc.headers.get("Content-Length", "not_exposed")
        try:
            raw = exc.read(max_bytes + 1)
            body = raw[:max_bytes]
            truncated = len(raw) > max_bytes
        except Exception:
            pass
        error = f"HTTPError {status}"
    except (urllib.error.URLError, TimeoutError, socket.timeout, RuntimeError) as exc:
        error = f"{type(exc).__name__}: {exc}"

    return {
        "url": url,
        "status": status if status is not None else "not_exposed",
        "final_url": final_url,
        "content_type": content_type,
        "content_length_header": content_length,
        "sample_bytes": len(body),
        "sample_truncated": truncated,
        "sample_sha256": hashlib.sha256(body).hexdigest() if body else "not_observed",
        "error": error,
        "_body": body,
    }


def same_host_urls(base_url: str, values: list[str]) -> list[str]:
    out = set()
    for value in values:
        url = urllib.parse.urljoin(base_url, value)
        p = urllib.parse.urlparse(url)
        if p.scheme == "https" and p.hostname == HOST:
            out.add(url)
    return sorted(out)


def extract_clues(text: str) -> list[str]:
    clues = set()
    for pattern in CLUE_PATTERNS:
        for match in pattern.findall(text):
            clue = " ".join(match.split())
            if 1 <= len(clue) <= 260:
                clues.add(clue)
    return sorted(clues)


def public_record(result: dict[str, object]) -> dict[str, object]:
    return {k: v for k, v in result.items() if k != "_body"}


def probe(reader_url: str, timeout: float) -> dict[str, object]:
    shell = bounded_get(reader_url, MAX_HTML_BYTES, timeout)
    html = bytes(shell["_body"]).decode("utf-8", errors="replace")
    script_urls = same_host_urls(str(shell["final_url"]), SCRIPT_SRC_RE.findall(html))
    link_urls = same_host_urls(str(shell["final_url"]), LINK_HREF_RE.findall(html))
    inline_scripts = INLINE_SCRIPT_RE.findall(html)

    inline_records = []
    inline_clues = set()
    for script in inline_scripts:
        encoded = script.encode("utf-8")
        clues = extract_clues(script)
        inline_clues.update(clues)
        inline_records.append({
            "bytes": len(encoded),
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "clues": clues,
        })

    script_records = []
    all_script_clues = set()
    for script_url in script_urls:
        result = bounded_get(script_url, MAX_SCRIPT_BYTES, timeout)
        text = bytes(result["_body"]).decode("utf-8", errors="replace")
        clues = extract_clues(text)
        all_script_clues.update(clues)
        record = public_record(result)
        record["clues"] = clues
        script_records.append(record)

    out = {
        "schema": "LTMD_U2_READER_INFRASTRUCTURE_PROBE_0.1",
        "reader_url": reader_url,
        "reader_shell": public_record(shell),
        "same_host_script_urls": script_urls,
        "same_host_link_urls": link_urls,
        "inline_scripts": inline_records,
        "inline_clues": sorted(inline_clues),
        "script_resources": script_records,
        "script_clues": sorted(all_script_clues),
        "evidence_scope": "reader_shell_and_same_host_static_script_metadata_clues_only",
        "rights_note": "Response bodies were used transiently for parsing and hashing and are not emitted by this probe.",
    }
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Inspect current CONALITEG reader infrastructure without persisting source bodies.")
    p.add_argument("--reader-url", default="https://libros.conaliteg.gob.mx/pdf-reader/reader.html?ciclo=2026&clave=P1MLA&nivel=primaria")
    p.add_argument("--output", type=Path, default=Path("u2-reader-infrastructure.json"))
    p.add_argument("--timeout", type=float, default=20.0)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    result = probe(args.reader_url, args.timeout)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("reader_status=", result["reader_shell"]["status"])
    print("same_host_scripts=", len(result["same_host_script_urls"]))
    print("same_host_links=", len(result["same_host_link_urls"]))
    print("inline_clues=", result["inline_clues"])
    print("script_clues=", result["script_clues"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
