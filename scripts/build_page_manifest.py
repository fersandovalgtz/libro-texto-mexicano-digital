#!/usr/bin/env python3
"""Build the metadata-only page manifest for pilot 0.1.

No source images are downloaded. The mapping is derived from the public viewer
controller observed on 2026-08-15:

- viewer page 1 -> image index 0 -> 000.jpg
- viewer pages 2..N -> image index equal to viewer page, zero-padded to 3 digits
- asset path -> /c/{viewer_key}/{image_index:03d}.jpg

The script also preregisters ten positional OCR-QC candidates per book, matching
the 2/3/3/2 quarter allocation in docs/EXTRACTION_SPEC.md. The legal and table
of contents pages are intentionally left to be identified from front matter.
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
    "position_ratio",
    "position_quartile",
    "qc_positional_candidate",
    "qc_slot",
    "page_type_status",
)


def viewer_key(url: str) -> str:
    return Path(urlparse(url).path).name.rsplit(".", 1)[0]


def qc_targets(page_count: int) -> dict[int, str]:
    """Map reproducible positional targets to QC slot labels."""
    targets: dict[int, str] = {}
    for fraction, slot in QC_SLOTS:
        page = round(page_count * fraction)
        page = min(page_count, max(2, page))
        while page in targets and page < page_count:
            page += 1
        while page in targets and page > 2:
            page -= 1
        targets[page] = slot
    return targets


def quartile(page: int, page_count: int) -> str:
    ratio = page / page_count
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
        n = int(book["page_count"])
        key = viewer_key(book["source_url"])
        base = urljoin(book["source_url"], f"c/{key}/")
        qc = qc_targets(n)

        for viewer_page in range(1, n + 1):
            image_index = 0 if viewer_page == 1 else viewer_page
            filename = f"{image_index:03d}.jpg"
            rows.append(
                {
                    "page_id": f"{book['book_id']}-VP{viewer_page:03d}",
                    "book_id": book["book_id"],
                    "catalog_generation": book["catalog_generation"],
                    "viewer_key": key,
                    "viewer_page": viewer_page,
                    "source_image_index": image_index,
                    "source_filename": filename,
                    "source_asset_url": urljoin(base, filename),
                    "position_ratio": f"{viewer_page / n:.6f}",
                    "position_quartile": quartile(viewer_page, n),
                    "qc_positional_candidate": "yes" if viewer_page in qc else "no",
                    "qc_slot": qc.get(viewer_page, ""),
                    "page_type_status": "unclassified",
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

    print(f"Wrote {len(rows)} page metadata rows to {output}")
    print(f"QC positional candidates: {sum(r['qc_positional_candidate'] == 'yes' for r in rows)}")


if __name__ == "__main__":
    main()
