#!/usr/bin/env python3
"""Verify the preregistered positional QC page sample without downloading images.

Reads the metadata-only page manifest, selects rows marked as QC positional
candidates, and performs HTTP HEAD requests only. The output records status,
content type and advertised content length. No image body is downloaded.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 QC asset header audit"
FIELDS = (
    "page_id",
    "book_id",
    "catalog_generation",
    "viewer_page",
    "source_filename",
    "source_asset_url",
    "qc_slot",
    "http_status",
    "content_type",
    "content_length",
    "probe_status",
    "error",
)


def probe(url: str, timeout: int = 20) -> dict[str, str | int]:
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
    except Exception as exc:
        return {
            "http_status": "",
            "content_type": "",
            "content_length": "",
            "probe_status": "error",
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="data/derived/page_manifest.csv")
    ap.add_argument("--output", default="data/derived/qc_sample_probe.csv")
    args = ap.parse_args()

    with Path(args.manifest).open(encoding="utf-8", newline="") as fh:
        selected = [r for r in csv.DictReader(fh) if r["qc_positional_candidate"] == "yes"]

    output_rows = []
    for row in selected:
        result = probe(row["source_asset_url"])
        output_rows.append(
            {
                "page_id": row["page_id"],
                "book_id": row["book_id"],
                "catalog_generation": row["catalog_generation"],
                "viewer_page": row["viewer_page"],
                "source_filename": row["source_filename"],
                "source_asset_url": row["source_asset_url"],
                "qc_slot": row["qc_slot"],
                **result,
            }
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    ok = sum(r["probe_status"] == "ok" for r in output_rows)
    print(f"Probed {len(output_rows)} preregistered page URLs; {ok} returned headers successfully")
    for row in output_rows:
        print(row["page_id"], row["source_filename"], row["http_status"], row["content_type"], row["content_length"], row["probe_status"])


if __name__ == "__main__":
    main()
