#!/usr/bin/env python3
"""Build the metadata-only page manifest for pilot 0.1.

No source images are downloaded.

Viewer architecture observed on 2026-08-15:
- `claves.json` reports a viewer-page count N;
- viewer page 1 maps to `000.jpg`;
- viewer pages 2..N-1 map to their zero-padded viewer number;
- viewer page N is a terminal synthetic page with no JPEG asset in all four
  books of pilot 0.1.

The manifest intentionally preserves the terminal viewer row so the distinction
between viewer structure and source assets remains explicit.

QC positions remain calculated against the original viewer-page count used in
the preregistration. They are not recalculated after the terminal-page audit.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from urllib.parse import urljoin, urlparse

QC_SLOTS = (
    (0.10, "q1_1"),
    (0.20, "q1_2"),
    (0.33, "q2_1"),
    (0.42, "q2_2"),
    (0.48, "q2_3"),
    (0.58, "q3_1"),
    (0.67, "q3_2"),
    (0.73, "q3_3"),
    (0.83, "q4_1"),
    (0.95, "q4_2"),
)

FIELDS = (
    "page_id",
    "book_id",
    "catalog_generation",
    "viewer_key",
    "viewer_page",
    "source_image_index",
    "source_filename",
    "source_asset_url",
    "asset_status",
    "position_ratio",
    "position_quartile",
    "qc_positional_candidate",
    "qc_slot",
    "page_type_status",
)

def viewer_key(url: str) -> str:
    return Path(urlparse(url).path).name.rsplit(".", 1)[0]

def qc_targets(viewer_page_count: int) -> dict[int, str]:
    """Map preregistered positional targets to QC slot labels."""
    targets: dict[int, str] = {}
    for fraction, slot in QC_SLOTS:
        page = round(viewer_page_count * fraction)
        page = min(viewer_page_count, max(2, page))
        while page in targets and page < viewer_page_count:
            page += 1
        while page in targets and page > 2:
            page -= 1
        targets[page] = slot
    return targets

def quartile(page: int, viewer_page_count: int) -> str:
    ratio = page / viewer_page_count
    if ratio <= 0.25:
        return "Q1"
    if ratio <= 0.50:
        return "Q2"
    if ratio <= 0.75:
        return "Q3"
    return "Q4"

def build_rows(inventory_path: Path) -> list[dict[str, str | int]]:
    with inventory_path.open(encoding="utf-8", newline="") as fh:
        books = list(csv.DictReader(fh))

    rows: list[dict[str, str | int]] = []
    for book in books:
        viewer_pages = int(book["page_count"])
        source_assets = int(book.get("source_asset_count") or viewer_pages)
        if source_assets > viewer_pages:
            raise ValueError(
                f"{book['book_id']}: source_asset_count cannot exceed page_count"
            )

        key = viewer_key(book["source_url"])
        base = urljoin(book["source_url"], f"c/{key}/")
        qc = qc_targets(viewer_pages)

        for viewer_page in range(1, viewer_pages + 1):
            has_asset = viewer_page <= source_assets
            image_index = (0 if viewer_page == 1 else viewer_page) if has_asset else ""
            filename = f"{int(image_index):03d}.jpg" if has_asset else ""
            asset_url = urljoin(base, filename) if has_asset else ""
            terminal = not has_asset

            rows.append(
                {
                    "page_id": f"{book['book_id']}-VP{viewer_page:03d}",
                    "book_id": book["book_id"],
                    "catalog_generation": book["catalog_generation"],
                    "viewer_key": key,
                    "viewer_page": viewer_page,
                    "source_image_index": image_index,
                    "source_filename": filename,
                    "source_asset_url": asset_url,
                    "asset_status": "source_jpeg" if has_asset else "terminal_synthetic",
                    "position_ratio": f"{viewer_page / viewer_pages:.6f}",
                    "position_quartile": quartile(viewer_page, viewer_pages),
                    "qc_positional_candidate": "yes" if viewer_page in qc else "no",
                    "qc_slot": qc.get(viewer_page, ""),
                    "page_type_status": "terminal_synthetic" if terminal else "unclassified",
                }
            )
    return rows

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="data/book_inventory.csv")
    ap.add_argument("--output", default="data/derived/page_manifest.csv")
    args = ap.parse_args()

    rows = build_rows(Path(args.inventory))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} viewer rows to {output}")
    print("source_jpeg=", sum(r["asset_status"] == "source_jpeg" for r in rows))
    print("terminal_synthetic=", sum(r["asset_status"] == "terminal_synthetic" for r in rows))
    print("QC positional candidates=", sum(r["qc_positional_candidate"] == "yes" for r in rows))

if __name__ == "__main__":
    main()
