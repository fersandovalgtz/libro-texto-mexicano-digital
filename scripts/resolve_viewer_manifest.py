#!/usr/bin/env python3
"""Resolve the public CONALITEG viewer manifest for the pilot corpus.

The script fetches only small controller resources (`x.js` and `claves.json`).
It does NOT download book page images. For each book in the inventory it:

1. derives the viewer key from the HTML filename;
2. reads the corresponding `ag_pages` entry from `claves.json`;
3. extracts compact function bodies from `x.js` for page creation/loading;
4. records string templates that appear to construct page-image URLs.

This produces metadata needed to build a page manifest before any OCR work.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 viewer manifest resolver"
FUNCTIONS = ("addPage", "loadPage", "loadSmallPage", "loadLargePage")


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 30) -> str:
    raw = fetch_bytes(url, timeout=timeout)
    return raw.decode("utf-8", errors="replace")


def extract_function(text: str, name: str) -> str | None:
    """Extract a JS function body using brace balancing."""
    match = re.search(rf"function\s+{re.escape(name)}\s*\([^)]*\)\s*\{{", text)
    if not match:
        return None
    start = match.start()
    brace = text.find("{", match.start())
    depth = 0
    quote: str | None = None
    escape = False
    for i in range(brace, len(text)):
        ch = text[i]
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def urlish_literals(text: str) -> list[str]:
    vals: list[str] = []
    seen: set[str] = set()
    for _, val in re.findall(r"(['\"])(.*?)\1", text, flags=re.DOTALL):
        low = val.lower()
        if any(tok in low for tok in (".jpg", ".jpeg", ".png", ".webp", "page", "pag", "large", "small")):
            compact = re.sub(r"\s+", " ", val).strip()
            if compact and compact not in seen:
                seen.add(compact)
                vals.append(compact)
    return vals


def viewer_key(url: str) -> str:
    name = Path(urlparse(url).path).name
    return name.rsplit(".", 1)[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="data/book_inventory.csv")
    ap.add_argument("--output", default="data/derived/resolved_viewer_manifest.json")
    args = ap.parse_args()

    inventory = list(csv.DictReader(Path(args.inventory).open(encoding="utf-8", newline="")))
    if not inventory:
        raise SystemExit("Inventory is empty")

    base = inventory[0]["source_url"]
    x_url = urljoin(base, "x.js")
    claves_url = urljoin(base, "claves.json")

    x_js = fetch_text(x_url)
    claves = json.loads(fetch_bytes(claves_url).decode("utf-8-sig"))

    functions = {name: extract_function(x_js, name) for name in FUNCTIONS}
    function_literals = {
        name: urlish_literals(body or "") for name, body in functions.items()
    }

    books = []
    for row in inventory:
        key = viewer_key(row["source_url"])
        entry = claves.get(key)
        books.append(
            {
                "book_id": row["book_id"],
                "catalog_generation": row["catalog_generation"],
                "viewer_key": key,
                "source_url": row["source_url"],
                "manifest_entry": entry,
                "page_count": entry.get("ag_pages") if isinstance(entry, dict) else None,
                "manifest_status": "ok" if isinstance(entry, dict) else "missing",
            }
        )

    result = {
        "controller_url": x_url,
        "manifest_url": claves_url,
        "controller_functions": functions,
        "urlish_literals": function_literals,
        "books": books,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("=== Manifest entries ===")
    for book in books:
        print(book["book_id"], book["viewer_key"], "pages=", book["page_count"], "entry=", book["manifest_entry"])
    print("=== Page-loading functions ===")
    for name in FUNCTIONS:
        print(f"--- {name} ---")
        print(functions[name])
        print("urlish_literals=", function_literals[name])
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
