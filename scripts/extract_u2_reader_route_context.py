#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

BUNDLE_URL = "https://libros.conaliteg.gob.mx/pdf-reader/reader.bundle.js"
USER_AGENT = "LTMD-U2-reader-route-context/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"
MAX_BYTES = 1_048_576
WINDOW = 900

TARGETS = {
    "pdf_template": r"\$\{t\}\?`/\$\{t\}/\$\{i\}\.pdf`",
    "legacy_htm_template": r"Js=Ds\?`\.\./\$\{Ds\}/\$\{Qs\}\.htm`",
    "url_search_params": r"URLSearchParams",
    "ciclo_literal": r"ciclo",
    "clave_literal": r"clave",
    "nivel_literal": r"nivel",
    "document_pdf_literal": r"document\.pdf",
}


def fetch_text(timeout: float) -> tuple[str, dict[str, str]]:
    req = urllib.request.Request(
        BUNDLE_URL,
        headers={"User-Agent": USER_AGENT, "Accept": "application/javascript,text/javascript,*/*;q=0.2"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise RuntimeError("reader bundle exceeds bounded probe limit")
        final_url = response.geturl()
        if final_url != BUNDLE_URL:
            raise RuntimeError(f"unexpected redirect: {final_url}")
        return raw.decode("utf-8", errors="replace"), {
            "status": str(response.status),
            "content_type": response.headers.get("Content-Type", "not_exposed").split(";", 1)[0],
            "content_length_header": response.headers.get("Content-Length", "not_exposed"),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": str(len(raw)),
        }


def compact(s: str) -> str:
    return " ".join(s.split())


def windows(text: str, pattern: str, limit: int = 12) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for match in re.finditer(pattern, text, re.I):
        start = max(0, match.start() - WINDOW)
        end = min(len(text), match.end() + WINDOW)
        out.append({
            "match_start": match.start(),
            "match_text": compact(match.group(0)),
            "context": compact(text[start:end]),
        })
        if len(out) >= limit:
            break
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("u2-reader-route-context.json"))
    p.add_argument("--timeout", type=float, default=20.0)
    args = p.parse_args()

    text, meta = fetch_text(args.timeout)
    findings = {name: windows(text, pattern) for name, pattern in TARGETS.items()}
    result = {
        "schema": "LTMD_U2_READER_ROUTE_CONTEXT_0.1",
        "bundle_url": BUNDLE_URL,
        "bundle": meta,
        "window_chars_each_side": WINDOW,
        "findings": findings,
        "evidence_scope": "bounded static JavaScript route-construction context only",
        "rights_note": "Only narrow code contexts required to determine transport routing are emitted; source-book content is not accessed by this probe.",
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("bundle_sha256=", meta["sha256"])
    for name, items in findings.items():
        print(name, "matches=", len(items))
        for item in items[:3]:
            print(name, "context=", item["context"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
