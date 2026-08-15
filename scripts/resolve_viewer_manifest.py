#!/usr/bin/env python3
"""Resolve public CONALITEG viewer metadata for the pilot corpus.

The script fetches only small controller/metadata resources. It does NOT fetch
book page images. It resolves:

- viewer key and exact page count from `claves.json`;
- same-origin JavaScript modules referenced by the viewer controller;
- the functions that create/load book pages;
- string literals used by those functions to construct image paths.

The result is sufficient to design a page manifest before OCR begins.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 viewer metadata resolver"
FUNCTIONS = ("addPage", "loadPage", "loadSmallPage", "loadLargePage")
JS_LITERAL_RE = re.compile(r"(['\"])([^'\"]+?\.js(?:\?[^'\"]*)?)\1", re.IGNORECASE)


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 30) -> str:
    return fetch_bytes(url, timeout=timeout).decode("utf-8", errors="replace")


def extract_function(text: str, name: str) -> str | None:
    """Extract a classic JavaScript function body using brace balancing."""
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
        if any(tok in low for tok in (".jpg", ".jpeg", ".png", ".webp", "page", "pag", "large", "small", "files/")):
            compact = re.sub(r"\s+", " ", val).strip()
            if compact and compact not in seen:
                seen.add(compact)
                vals.append(compact)
    return vals


def viewer_key(url: str) -> str:
    return Path(urlparse(url).path).name.rsplit(".", 1)[0]


def discover_same_origin_modules(controller_url: str, controller_text: str) -> list[str]:
    origin = urlparse(controller_url).netloc
    modules: list[str] = []
    seen: set[str] = set()
    for _, literal in JS_LITERAL_RE.findall(controller_text):
        candidate = urljoin(controller_url, literal)
        if urlparse(candidate).netloc == origin and candidate not in seen:
            seen.add(candidate)
            modules.append(candidate)
    return modules


def resolve_functions(sources: dict[str, str]) -> dict[str, dict | None]:
    resolved: dict[str, dict | None] = {}
    for name in FUNCTIONS:
        found = None
        for url, text in sources.items():
            body = extract_function(text, name)
            if body:
                found = {
                    "source_url": url,
                    "body": body,
                    "urlish_literals": urlish_literals(body),
                }
                break
        resolved[name] = found
    return resolved


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="data/book_inventory.csv")
    ap.add_argument("--output", default="data/derived/resolved_viewer_manifest.json")
    args = ap.parse_args()

    with Path(args.inventory).open(encoding="utf-8", newline="") as fh:
        inventory = list(csv.DictReader(fh))
    if not inventory:
        raise SystemExit("Inventory is empty")

    base = inventory[0]["source_url"]
    controller_url = urljoin(base, "x.js")
    manifest_url = urljoin(base, "claves.json")

    controller = fetch_text(controller_url)
    claves = json.loads(fetch_bytes(manifest_url).decode("utf-8-sig"))

    module_urls = discover_same_origin_modules(controller_url, controller)
    source_texts: dict[str, str] = {controller_url: controller}
    module_errors: list[dict] = []
    for url in module_urls:
        try:
            source_texts[url] = fetch_text(url)
        except Exception as exc:
            module_errors.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})

    functions = resolve_functions(source_texts)

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
        "controller_url": controller_url,
        "manifest_url": manifest_url,
        "discovered_module_urls": module_urls,
        "module_errors": module_errors,
        "page_loading_functions": functions,
        "books": books,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("=== Manifest entries ===")
    for book in books:
        print(book["book_id"], book["viewer_key"], "pages=", book["page_count"])
    print("=== Discovered modules ===")
    for url in module_urls:
        print(url)
    print("=== Page-loading functions ===")
    for name, value in functions.items():
        print(f"--- {name} ---")
        if value:
            print("source=", value["source_url"])
            print(value["body"])
            print("urlish_literals=", value["urlish_literals"])
        else:
            print("NOT FOUND")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
