#!/usr/bin/env python3
"""Incremental W2 Mathematics OCR metrics for the four route-resolved DMA 2018 books.

Reuses the frozen OCR 0.2 page processor without recomputing the 57 historical
canonical books. Full OCR text is never persisted; output is technical metrics.
"""
from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

import ocr_ltmd_u1_w2_math_book as base

DMA_EXPECTED = {
    "H2018P3DMA": 225,
    "H2018P4DMA": 257,
    "H2018P5DMA": 225,
    "H2018P6DMA": 185,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viewer-key", required=True, choices=sorted(DMA_EXPECTED))
    ap.add_argument("--output-dir", default="data/work/ltmd_u1_w2_math_ocr_dma2018")
    args = ap.parse_args()

    viewer = args.viewer_key
    allrows = list(csv.DictReader(base.MAN.open(encoding="utf-8", newline="")))
    source = [
        r for r in allrows
        if r["viewer_key"] == viewer
        and r["effective_asset_status"] in ("source_jpeg", "source_jpeg_recovered")
    ]
    source.sort(key=lambda r: int(r["viewer_page"]))
    expected = DMA_EXPECTED[viewer]
    if len(source) != expected:
        raise SystemExit(f"{viewer}: expected {expected} effective source pages, got {len(source)}")
    if any(not r.get("effective_sha256") or not r.get("effective_asset_url") for r in source):
        raise SystemExit(f"{viewer}: missing effective source evidence")

    with tempfile.TemporaryDirectory(prefix="ltmd-u1-w2-math-dma2018-ocr-") as td:
        outrows = [base.process(r, Path(td)) for r in source]
    outrows.sort(key=lambda r: int(r["viewer_page"]))

    if len({r["page_id"] for r in outrows}) != expected:
        raise SystemExit(f"{viewer}: duplicate/missing page IDs")
    if any(str(r["source_sha256_verified"]) != "1" for r in outrows):
        raise SystemExit(f"{viewer}: one or more SHA checks failed")
    unresolved = [r for r in outrows if r["ocr_class"] == "unresolved" or r["ocr_status"] != "ok"]
    if unresolved:
        raise SystemExit(f"{viewer}: unresolved OCR pages={len(unresolved)}")

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"ocr_{viewer.lower()}.csv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=base.FIELDS)
        writer.writeheader()
        writer.writerows(outrows)

    print(
        f"{viewer}: incremental OCR metrics pages={expected}; "
        f"sha_verified={expected}; text_persisted=0; out={out}"
    )


if __name__ == "__main__":
    main()
