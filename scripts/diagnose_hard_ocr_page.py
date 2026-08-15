#!/usr/bin/env python3
"""Deep OCR diagnostic for a single hard page, metrics only.

Creates temporary preprocessed variants and runs multiple Tesseract segmentation
modes. OCR text is never written to disk or to the output CSV; only word counts
and confidence metrics are retained.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

UA = "LibroTextoMexicanoDigital/0.1 hard-page diagnostic"
FIELDS = ["page_id","variant","psm","words","mean_confidence","median_confidence","low_confidence_rate","status","error"]


def fetch(url: str, target: Path) -> None:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=35) as r, target.open("wb") as fh:
        expected = r.headers.get("Content-Length")
        expected_n = int(expected) if expected and expected.isdigit() else None
        total = 0
        while expected_n is None or total < expected_n:
            need = 65536 if expected_n is None else min(65536, expected_n-total)
            chunk = r.read(need)
            if not chunk:
                break
            fh.write(chunk); total += len(chunk)


def otsu_threshold(gray: Image.Image) -> int:
    hist = gray.histogram()
    total = sum(hist)
    sum_total = sum(i * n for i, n in enumerate(hist))
    sum_b = 0.0
    w_b = 0
    max_var = -1.0
    threshold = 127
    for i, n in enumerate(hist):
        w_b += n
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += i * n
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = i
    return threshold


def build_variants(source: Path, root: Path) -> dict[str, Path]:
    with Image.open(source) as im:
        gray = im.convert("L")
        variants: dict[str, Image.Image] = {}
        variants["original_gray"] = gray.copy()
        variants["autocontrast"] = ImageOps.autocontrast(gray)
        enlarged = ImageOps.autocontrast(gray).resize((gray.width * 2, gray.height * 2), Image.Resampling.LANCZOS)
        variants["autocontrast_2x"] = enlarged
        sharp = enlarged.filter(ImageFilter.SHARPEN)
        variants["autocontrast_2x_sharpen"] = ImageEnhance.Contrast(sharp).enhance(1.4)
        t = otsu_threshold(gray)
        variants["otsu"] = gray.point(lambda p: 255 if p > t else 0)
        out = {}
        for name, image in variants.items():
            p = root / f"{name}.png"
            image.save(p)
            out[name] = p
        return out


def ocr_metrics(path: Path, psm: int, timeout: int) -> dict[str, str | int]:
    proc = subprocess.run(
        ["tesseract", str(path), "stdout", "-l", "spa", "--psm", str(psm), "tsv"],
        capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or f"tesseract exit {proc.returncode}")
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    confs = []
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
    low = sum(c < 60 for c in confs) / len(confs) if confs else 1.0
    return {
        "words": words,
        "mean_confidence": f"{statistics.mean(confs):.2f}" if confs else "",
        "median_confidence": f"{statistics.median(confs):.2f}" if confs else "",
        "low_confidence_rate": f"{low:.4f}" if confs else "",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page-id", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--output", default="data/derived/hard_page_ocr_diagnostic.csv")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    results = []
    with tempfile.TemporaryDirectory(prefix="ltmd-hard-page-") as d:
        root = Path(d)
        source = root / "source.jpg"
        fetch(args.url, source)
        variants = build_variants(source, root)
        for variant, path in variants.items():
            for psm in (3, 6, 11):
                try:
                    metrics = ocr_metrics(path, psm, args.timeout)
                    results.append({"page_id":args.page_id,"variant":variant,"psm":psm,**metrics,"status":"ok","error":""})
                except Exception as exc:
                    results.append({"page_id":args.page_id,"variant":variant,"psm":psm,"words":"","mean_confidence":"","median_confidence":"","low_confidence_rate":"","status":"error","error":f"{type(exc).__name__}: {exc}"})

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(results)

    for r in sorted(results, key=lambda x:int(x["words"] or 0), reverse=True):
        print(r)

if __name__ == "__main__":
    main()
