#!/usr/bin/env python3
"""Trace how CONALITEG's historical viewer resolves book metadata and page assets.

This audit is intentionally non-destructive: it fetches only the public viewer
HTML and its small JavaScript controller files, then records compact snippets
around identifiers that control the manifest and page URL construction. It does
not request book page images.
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

USER_AGENT = "LibroTextoMexicanoDigital/0.1 manifest trace"
TARGETS = (
    "ag_clave", "ag_pages", "data[", "data =", "data=", "const data", "let data", "var data",
    "addPage", "loadSmallPage", "loadLargePage", "pageElement", "backgroundImage",
    "background-image", "src", ".jpg", ".jpeg", ".png", "images/", "pages/",
    "ag_dir", "ag_path", "ag_url", "ag_libro", "urlActual", "pathname",
    "getJSON", "ajax", "fetch(", "$.get", "$.ajax",
)


class ScriptCollector(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.scripts: list[str] = []
        self.inline: list[str] = []
        self._inline = False
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return
        attrs = dict(attrs)
        src = attrs.get("src")
        if src:
            self.scripts.append(urljoin(self.base_url, src))
        else:
            self._inline = True
            self._buf = []

    def handle_data(self, data):
        if self._inline:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "script" and self._inline:
            self.inline.append("".join(self._buf))
            self._inline = False
            self._buf = []


def fetch_text(url: str, timeout: int = 30) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def compact_snippets(text: str, radius: int = 360) -> list[dict]:
    snippets: list[dict] = []
    seen: set[tuple[int, str]] = set()
    low = text.lower()
    for target in TARGETS:
        t = target.lower()
        start = 0
        while True:
            idx = low.find(t, start)
            if idx < 0:
                break
            key = (idx, t)
            if key not in seen:
                seen.add(key)
                left = max(0, idx - radius)
                right = min(len(text), idx + len(t) + radius)
                excerpt = text[left:right].replace("\r", " ").replace("\n", " ")
                excerpt = re.sub(r"\s+", " ", excerpt).strip()
                snippets.append({"target": target, "offset": idx, "excerpt": excerpt})
            start = idx + len(t)
    snippets.sort(key=lambda item: item["offset"])
    return snippets[:200]


def trace(url: str) -> dict:
    html = fetch_text(url)
    parser = ScriptCollector(url)
    parser.feed(html)
    origin = urlparse(url).netloc

    sources: list[dict] = [
        {
            "name": "viewer_html",
            "url": url,
            "bytes": len(html.encode("utf-8")),
            "snippets": compact_snippets(html),
        }
    ]

    for idx, inline in enumerate(parser.inline, start=1):
        snippets = compact_snippets(inline)
        if snippets:
            sources.append({
                "name": f"inline_script_{idx}",
                "url": url,
                "bytes": len(inline.encode("utf-8")),
                "snippets": snippets,
            })

    for src in parser.scripts:
        if urlparse(src).netloc != origin:
            continue
        try:
            text = fetch_text(src)
            snippets = compact_snippets(text)
            # js.js is intentionally tiny; preserve its full text as a derived
            # diagnostic because it may contain the manifest bootstrap.
            full_text = text if src.endswith("/js.js") and len(text) <= 2000 else None
            if snippets or full_text is not None or src.endswith("/x.js"):
                sources.append({
                    "name": Path(urlparse(src).path).name,
                    "url": src,
                    "bytes": len(text.encode("utf-8")),
                    "full_text_if_small": full_text,
                    "snippets": snippets,
                })
        except Exception as exc:
            sources.append({
                "name": Path(urlparse(src).path).name,
                "url": src,
                "error": f"{type(exc).__name__}: {exc}",
            })

    return {"viewer_url": url, "sources": sources}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="data/book_inventory.csv")
    ap.add_argument("--output", default="data/derived/viewer_manifest_trace.json")
    args = ap.parse_args()

    results: list[dict] = []
    with Path(args.inventory).open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            result = {
                "book_id": row["book_id"],
                "catalog_generation": row["catalog_generation"],
                "source_url": row["source_url"],
            }
            try:
                result.update(trace(row["source_url"]))
                result["status"] = "ok"
            except Exception as exc:
                result["status"] = "error"
                result["error"] = f"{type(exc).__name__}: {exc}"
            results.append(result)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} records to {out}")


if __name__ == "__main__":
    main()
