#!/usr/bin/env python3
"""Audit baseline `no_text_detected` pages without persisting OCR text.

For each registered page this script:
1. downloads the JPEG to a temporary directory;
2. computes non-textual image-complexity metrics;
3. retries OCR with sparse/layout alternatives (`psm 11`, then `psm 6`);
4. keeps only word counts/confidence metrics, never OCR transcription;
5. assigns a conservative technical class for later human review.

The classes are diagnostic, not semantic page-type labels:
- `recovered_by_fallback`: alternative segmentation detects >=5 words;
- `still_no_text_low_ink`: no fallback text and very little dark/edge content;
- `still_no_text_complex_image`: no fallback text but substantial visual content;
- `still_no_text_indeterminate`: neither rule is decisive;
- `error`: acquisition/processing failed.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageFilter, ImageStat

UA = "LibroTextoMexicanoDigital/0.1 no-text audit"
OUT_FIELDS = [
    "page_id","book_id","catalog_generation","viewer_page","source_bytes",
    "width","height","mean_gray","std_gray","entropy","dark_pixel_ratio",
    "very_dark_pixel_ratio","edge_mean","psm11_words","psm11_mean_confidence",
    "psm6_words","psm6_mean_confidence","max_fallback_words","audit_class",
    "audit_status","error"
]


def fetch(url: str, target: Path, timeout: int = 35) -> int:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as r, target.open("wb") as fh:
        expected = r.headers.get("Content-Length")
        expected_n = int(expected) if expected and expected.isdigit() else None
        total = 0
        while expected_n is None or total < expected_n:
            need = 65536 if expected_n is None else min(65536, expected_n-total)
            chunk = r.read(need)
            if not chunk:
                break
            fh.write(chunk)
            total += len(chunk)
        return total


def image_metrics(path: Path) -> dict[str, float | int]:
    with Image.open(path) as im:
        gray = im.convert("L")
        width, height = gray.size
        stat = ImageStat.Stat(gray)
        mean_gray = float(stat.mean[0])
        std_gray = float(stat.stddev[0])
        histogram = gray.histogram()
        total = max(1, width * height)
        dark = sum(histogram[:200]) / total
        very_dark = sum(histogram[:100]) / total
        entropy = float(gray.entropy())
        edge = gray.filter(ImageFilter.FIND_EDGES)
        edge_mean = float(ImageStat.Stat(edge).mean[0])
        return {
            "width": width,
            "height": height,
            "mean_gray": round(mean_gray, 3),
            "std_gray": round(std_gray, 3),
            "entropy": round(entropy, 4),
            "dark_pixel_ratio": round(dark, 6),
            "very_dark_pixel_ratio": round(very_dark, 6),
            "edge_mean": round(edge_mean, 3),
        }


def ocr_metrics(path: Path, psm: int, timeout: int) -> tuple[int, str]:
    proc = subprocess.run(
        ["tesseract", str(path), "stdout", "-l", "spa", "--psm", str(psm), "tsv"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or f"tesseract exit {proc.returncode}")
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    confs: list[float] = []
    words = 0
    for row in rows:
        text = (row.get("text") or "").strip()
        try:
            conf = float(row.get("conf") or -1)
        except ValueError:
            conf = -1
        if text and conf >= 0:
            words += 1
            confs.append(conf)
    mean_conf = f"{statistics.mean(confs):.2f}" if confs else ""
    return words, mean_conf


def classify(metrics: dict[str, float | int], max_words: int) -> str:
    if max_words >= 5:
        return "recovered_by_fallback"
    dark = float(metrics["dark_pixel_ratio"])
    std = float(metrics["std_gray"])
    entropy = float(metrics["entropy"])
    edge = float(metrics["edge_mean"])
    if dark < 0.015 and std < 25 and edge < 8:
        return "still_no_text_low_ink"
    if dark >= 0.03 or entropy >= 5.0 or edge >= 12:
        return "still_no_text_complex_image"
    return "still_no_text_indeterminate"


def process(row: dict[str, str], tmp: Path, timeout: int) -> dict[str, str | int | float]:
    image = tmp / f"{row['page_id']}.jpg"
    base = {
        "page_id": row["page_id"],
        "book_id": row["book_id"],
        "catalog_generation": row["catalog_generation"],
        "viewer_page": row["viewer_page"],
    }
    try:
        size = fetch(row["source_asset_url"], image)
        im = image_metrics(image)
        p11_words = p6_words = 0
        p11_conf = p6_conf = ""
        errors = []
        try:
            p11_words, p11_conf = ocr_metrics(image, 11, timeout)
        except Exception as exc:
            errors.append(f"psm11 {type(exc).__name__}: {exc}")
        try:
            p6_words, p6_conf = ocr_metrics(image, 6, timeout)
        except Exception as exc:
            errors.append(f"psm6 {type(exc).__name__}: {exc}")
        max_words = max(p11_words, p6_words)
        return {
            **base,
            "source_bytes": size,
            **im,
            "psm11_words": p11_words,
            "psm11_mean_confidence": p11_conf,
            "psm6_words": p6_words,
            "psm6_mean_confidence": p6_conf,
            "max_fallback_words": max_words,
            "audit_class": classify(im, max_words),
            "audit_status": "ok",
            "error": " | ".join(errors),
        }
    except Exception as exc:
        return {
            **base,
            "source_bytes": row.get("source_bytes", ""),
            "width":"","height":"","mean_gray":"","std_gray":"","entropy":"",
            "dark_pixel_ratio":"","very_dark_pixel_ratio":"","edge_mean":"",
            "psm11_words":"","psm11_mean_confidence":"","psm6_words":"",
            "psm6_mean_confidence":"","max_fallback_words":"","audit_class":"error",
            "audit_status":"error","error":f"{type(exc).__name__}: {exc}",
        }
    finally:
        image.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/derived/no_text_page_register.csv")
    ap.add_argument("--output", default="data/derived/no_text_page_audit.csv")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=45)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.input, encoding="utf-8", newline="")))
    with tempfile.TemporaryDirectory(prefix="ltmd-no-text-") as d:
        tmp = Path(d)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            audited = list(pool.map(lambda r: process(r, tmp, args.timeout), rows))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(audited)

    print("Audited", len(audited), "baseline no-text pages")
    classes = sorted({r["audit_class"] for r in audited})
    for cls in classes:
        print(cls, sum(r["audit_class"] == cls for r in audited))
    for gen in sorted({r["catalog_generation"] for r in audited}):
        rs = [r for r in audited if r["catalog_generation"] == gen]
        print(gen, {cls:sum(r["audit_class"] == cls for r in rs) for cls in classes})

if __name__ == "__main__":
    main()
