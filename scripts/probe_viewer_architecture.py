#!/usr/bin/env python3
"""Probe the dynamic architecture of CONALITEG historical viewers.

Fetches each viewer HTML and same-origin JavaScript assets, then extracts
high-signal snippets and path-like string literals. It does not download book
pages or PDFs. Intended for reproducible reverse-engineering of the public
viewer so the ingestion pipeline can be designed against observed behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 architecture audit"
KEYWORDS = (
    "page", "pag", "pagina", "libro", "book", "jpg", "jpeg", "png", "pdf",
    "src", "href", "hash", "ajax", "load", "imagen", "image", "folio",
    "window.location", "document.location", "document.write", "background",
)
STRING_RE = re.compile(r"(['\"])(.{1,240}?)\1", re.DOTALL)


class ScriptParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.script_srcs: list[str] = []
        self.inline_scripts: list[str] = []
        self._in_script = False
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return
        attrs = dict(attrs)
        src = attrs.get("src")
        if src:
            self.script_srcs.append(urljoin(self.base_url, src))
            self._in_script = False
        else:
            self._in_script = True
            self._buf = []

    def handle_data(self, data):
        if self._in_script:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._in_script:
            self.inline_scripts.append("".join(self._buf))
            self._in_script = False
            self._buf = []


def fetch_text(url: str, timeout: int = 30) -> tuple[str, dict]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        text = raw.decode(charset, errors="replace")
        return text, {
            "http_status": getattr(response, "status", None),
            "content_type": response.headers.get("Content-Type", ""),
            "bytes": len(raw),
            "final_url": response.geturl(),
        }


def signal_lines(text: str, max_lines: int = 120) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        compact = line.strip()
        low = compact.lower()
        if compact and any(k in low for k in KEYWORDS):
            out.append(compact[:1000])
        if len(out) >= max_lines:
            break
    return out


def path_like_strings(text: str, max_items: int = 200) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for _, value in STRING_RE.findall(text):
        value = value.strip()
        low = value.lower()
        interesting = (
            "/" in value
            or ".jpg" in low
            or ".jpeg" in low
            or ".png" in low
            or ".pdf" in low
            or "page" in low
            or "pag" in low
            or "libro" in low
            or "book" in low
        )
        if interesting and value not in seen:
            seen.add(value)
            found.append(value[:500])
        if len(found) >= max_items:
            break
    return found


def probe(url: str) -> dict:
    html, html_meta = fetch_text(url)
    parser = ScriptParser(url)
    parser.feed(html)

    origin = urlparse(url).netloc
    assets = []
    for src in parser.script_srcs:
        parsed = urlparse(src)
        if parsed.netloc != origin:
            continue
        try:
            text, meta = fetch_text(src)
            assets.append({
                "url": src,
                **meta,
                "signal_lines": signal_lines(text),
                "path_like_strings": path_like_strings(text),
            })
        except Exception as exc:
            assets.append({"url": src, "error": f"{type(exc).__name__}: {exc}"})

    inline = []
    for idx, text in enumerate(parser.inline_scripts, start=1):
        sig = signal_lines(text)
        paths = path_like_strings(text)
        if sig or paths:
            inline.append({
                "index": idx,
                "bytes": len(text.encode("utf-8")),
                "signal_lines": sig,
                "path_like_strings": paths,
            })

    return {
        "viewer_url": url,
        "html": html_meta,
        "inline_scripts": inline,
        "same_origin_script_assets": assets,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="data/book_inventory.csv")
    ap.add_argument("--output", default="data/derived/viewer_architecture_probe.json")
    args = ap.parse_args()

    results = []
    with Path(args.inventory).open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            record = {
                "book_id": row["book_id"],
                "catalog_generation": row["catalog_generation"],
                "source_url": row["source_url"],
            }
            try:
                record.update(probe(row["source_url"]))
                record["status"] = "ok"
            except Exception as exc:
                record["status"] = "error"
                record["error"] = f"{type(exc).__name__}: {exc}"
            results.append(record)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} records to {out}")


if __name__ == "__main__":
    main()
