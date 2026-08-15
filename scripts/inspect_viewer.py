#!/usr/bin/env python3
"""Inspect CONALITEG viewer pages without downloading book assets.

Reads data/book_inventory.csv, fetches each viewer HTML page, and records
candidate linked resources (scripts, styles, iframes, embeds, images and URLs
that look like PDF/page/image endpoints). The goal is to discover the actual
resource architecture before designing ingestion.

This script does NOT download book PDFs or page images.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 research metadata audit"
RESOURCE_RE = re.compile(
    r"(?:https?://[^\s\"'<>]+|[^\s\"'<>]+\.(?:pdf|jpg|jpeg|png|webp|js|css)(?:\?[^\s\"'<>]*)?)",
    re.IGNORECASE,
)


class ResourceParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.resources: set[str] = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("src", "href", "data", "poster"):
            value = attrs.get(key)
            if value:
                self.resources.add(urljoin(self.base_url, value))

    def handle_data(self, data):
        for match in RESOURCE_RE.findall(data):
            self.resources.add(urljoin(self.base_url, match))


def fetch_html(url: str, timeout: int = 30) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def inspect(url: str) -> dict:
    html = fetch_html(url)
    parser = ResourceParser(url)
    parser.feed(html)

    inline_candidates = {
        urljoin(url, match)
        for match in RESOURCE_RE.findall(html)
    }
    resources = sorted(parser.resources | inline_candidates)

    interesting = [
        item
        for item in resources
        if any(token in item.lower() for token in ("pdf", "page", "jpg", "jpeg", "png", "viewer", "book", "libro"))
    ]

    return {
        "viewer_url": url,
        "html_bytes": len(html.encode("utf-8")),
        "resource_count": len(resources),
        "resources": resources,
        "interesting_candidates": interesting,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/book_inventory.csv")
    parser.add_argument("--output", default="data/derived/viewer_inspection.json")
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    with inventory_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            record = {
                "book_id": row["book_id"],
                "generation": row["generation"],
                "source_url": row["source_url"],
            }
            try:
                record.update(inspect(row["source_url"]))
                record["status"] = "ok"
            except Exception as exc:  # audit script: preserve failures as data
                record["status"] = "error"
                record["error"] = f"{type(exc).__name__}: {exc}"
            results.append(record)

    output_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(results)} records to {output_path}")


if __name__ == "__main__":
    main()
