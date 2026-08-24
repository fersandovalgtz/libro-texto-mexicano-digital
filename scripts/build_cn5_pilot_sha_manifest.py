#!/usr/bin/env python3
"""Rebuild a page-level SHA-256 source manifest for the four CN5 pilot books.

This utility downloads source JPEG bytes only long enough to calculate byte size
and SHA-256. It does not OCR, retain, or publish source images. The resulting CSV
contains metadata/hashes only and is suitable as a public provenance layer.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

VERSION = "CN5_PILOT_SHA_MANIFEST_0.1"
PILOT_BOOKS = {
    "LTMD-CN5-G1972",
    "LTMD-CN5-G1988",
    "LTMD-CN5-G1993",
    "LTMD-CN5-G2014",
}
COMPACT_FIELDS = ("viewer_page", "source_image_index", "byte_size", "sha256")
FIELDS = (
    "manifest_version",
    "page_id",
    "book_id",
    "catalog_generation",
    "grade",
    "viewer_key",
    "viewer_page",
    "source_image_index",
    "source_filename",
    "source_asset_url",
    "asset_status",
    "http_status",
    "content_type",
    "byte_size",
    "sha256",
    "fetch_attempts",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def viewer_key(url: str) -> str:
    return Path(urlparse(url).path).name.rsplit(".", 1)[0]


def jobs_from_inventory(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    selected = [r for r in rows if r["book_id"] in PILOT_BOOKS]
    assert {r["book_id"] for r in selected} == PILOT_BOOKS
    jobs: list[dict[str, object]] = []
    for book in selected:
        assets = int(book["source_asset_count"])
        key = viewer_key(book["source_url"])
        base = urljoin(book["source_url"], f"c/{key}/")
        for viewer_page in range(1, assets + 1):
            source_index = 0 if viewer_page == 1 else viewer_page
            filename = f"{source_index:03d}.jpg"
            jobs.append(
                {
                    "manifest_version": VERSION,
                    "page_id": f"{book['book_id']}-VP{viewer_page:03d}",
                    "book_id": book["book_id"],
                    "catalog_generation": book["catalog_generation"],
                    "grade": book["grade"],
                    "viewer_key": key,
                    "viewer_page": viewer_page,
                    "source_image_index": source_index,
                    "source_filename": filename,
                    "source_asset_url": urljoin(base, filename),
                }
            )
    return jobs


def fetch_one(job: dict[str, object], timeout: int, retries: int) -> dict[str, object]:
    url = str(job["source_asset_url"])
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LTMD-FTRL/0.1 provenance audit"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                status = getattr(resp, "status", 200)
                ctype = resp.headers.get_content_type()
            if status != 200:
                raise RuntimeError(f"HTTP {status}: {url}")
            if ctype != "image/jpeg":
                raise RuntimeError(f"unexpected content type {ctype}: {url}")
            out = dict(job)
            out.update(
                {
                    "asset_status": "source_jpeg",
                    "http_status": status,
                    "content_type": ctype,
                    "byte_size": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "fetch_attempts": attempt,
                }
            )
            return out
        except Exception as exc:  # network provenance run: bounded retry only
            last = exc
            if attempt < retries:
                time.sleep(min(2 ** (attempt - 1), 8))
    raise RuntimeError(f"failed after {retries} attempts: {url}: {last}")


def write_manifest(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_compact_anchor(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COMPACT_FIELDS)
        writer.writeheader()
        writer.writerows({key: row[key] for key in COMPACT_FIELDS} for row in rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", default="data/book_inventory.csv")
    ap.add_argument("--ocr-metrics", default="data/derived/ocr_page_metrics.csv")
    ap.add_argument("--output", default="local/ftrl/cn5_pilot_sha_manifest.csv")
    ap.add_argument("--summary", default="local/ftrl/cn5_pilot_sha_manifest_summary.json")
    ap.add_argument("--compact-output-dir", default=None)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--retries", type=int, default=4)
    args = ap.parse_args()

    inventory = read_csv(Path(args.inventory))
    metrics = read_csv(Path(args.ocr_metrics))
    metric_bytes = {
        r["page_id"]: int(r["source_bytes"])
        for r in metrics
        if r["book_id"] in PILOT_BOOKS and r["asset_status"] == "source_jpeg"
    }

    jobs = jobs_from_inventory(inventory)
    assert len(jobs) == 759, len(jobs)
    assert len(metric_bytes) == 759, len(metric_bytes)

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_one, j, args.timeout, args.retries): j for j in jobs}
        for i, future in enumerate(as_completed(futures), 1):
            row = future.result()
            expected_bytes = metric_bytes.get(str(row["page_id"]))
            if expected_bytes is None:
                raise AssertionError(f"page absent from prior OCR metrics: {row['page_id']}")
            if int(row["byte_size"]) != expected_bytes:
                raise AssertionError(
                    f"source byte drift: {row['page_id']}: current={row['byte_size']} prior={expected_bytes}"
                )
            results.append(row)
            if i % 50 == 0 or i == len(jobs):
                print(f"verified {i}/{len(jobs)} source JPEGs")

    results.sort(key=lambda r: (str(r["book_id"]), int(r["viewer_page"])))
    assert len({str(r["page_id"]) for r in results}) == 759
    assert all(len(str(r["sha256"])) == 64 for r in results)

    write_manifest(Path(args.output), results)

    if args.compact_output_dir:
        compact_dir = Path(args.compact_output_dir)
        compact_dir.mkdir(parents=True, exist_ok=True)
        for bid in sorted(PILOT_BOOKS):
            rows = [r for r in results if r["book_id"] == bid]
            write_compact_anchor(compact_dir / f"{bid}.csv", rows)

    by_book: dict[str, dict[str, int]] = {}
    for bid in sorted(PILOT_BOOKS):
        rows = [r for r in results if r["book_id"] == bid]
        by_book[bid] = {
            "source_jpegs": len(rows),
            "unique_source_hashes": len({str(r["sha256"]) for r in rows}),
            "total_source_bytes": sum(int(r["byte_size"]) for r in rows),
        }

    summary = {
        "schema": "LTMD_CN5_PILOT_SHA_ANCHOR_0.1",
        "manifest_version": VERSION,
        "status": "validated",
        "books": len(PILOT_BOOKS),
        "source_jpegs": len(results),
        "prior_ocr_metric_byte_matches": len(results),
        "source_byte_drift": 0,
        "by_book": by_book,
        "publication_scope": "metadata_and_hashes_only_no_source_bytes_no_ocr_text",
    }
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
