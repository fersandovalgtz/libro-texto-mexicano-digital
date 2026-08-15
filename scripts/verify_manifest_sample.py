#!/usr/bin/env python3
"""Verify preregistered QC page URLs with concurrent HTTP HEAD requests only.

No image body is downloaded. HEAD failures are recorded as inconclusive rather
than treated automatically as missing assets, because some servers restrict
HEAD independently of GET.
"""

from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 QC asset header audit"
FIELDS = (
    "page_id", "book_id", "catalog_generation", "viewer_page",
    "source_filename", "source_asset_url", "qc_slot", "http_status",
    "content_type", "content_length", "probe_status", "error",
)


def probe(url: str, timeout: int = 8) -> dict[str, str | int]:
    req = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    try:
        with urlopen(req, timeout=timeout) as response:
            return {
                "http_status": getattr(response, "status", ""),
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": response.headers.get("Content-Length", ""),
                "probe_status": "ok",
                "error": "",
            }
    except HTTPError as exc:
        return {
            "http_status": exc.code,
            "content_type": exc.headers.get("Content-Type", "") if exc.headers else "",
            "content_length": exc.headers.get("Content-Length", "") if exc.headers else "",
            "probe_status": "head_http_error",
            "error": f"HTTPError: {exc}",
        }
    except Exception as exc:
        return {
            "http_status": "",
            "content_type": "",
            "content_length": "",
            "probe_status": "head_inconclusive",
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/derived/page_manifest.csv")
    ap.add_argument("--output", default="data/derived/qc_sample_probe.csv")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    with Path(args.manifest).open(encoding="utf-8", newline="") as fh:
        selected = [r for r in csv.DictReader(fh) if r["qc_positional_candidate"] == "yes"]

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda r: probe(r["source_asset_url"]), selected))

    output_rows = []
    for row, result in zip(selected, results):
        output_rows.append({
            "page_id": row["page_id"],
            "book_id": row["book_id"],
            "catalog_generation": row["catalog_generation"],
            "viewer_page": row["viewer_page"],
            "source_filename": row["source_filename"],
            "source_asset_url": row["source_asset_url"],
            "qc_slot": row["qc_slot"],
            **result,
        })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    ok = sum(r["probe_status"] == "ok" for r in output_rows)
    print(f"Probed {len(output_rows)} preregistered page URLs; {ok} returned HEAD successfully")
    for row in output_rows:
        print(row["page_id"], row["source_filename"], row["http_status"], row["content_type"], row["content_length"], row["probe_status"])


if __name__ == "__main__":
    main()
