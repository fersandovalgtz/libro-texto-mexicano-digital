#!/usr/bin/env python3
"""Run a non-publishing OCR viability benchmark on the positional QC sample.

Source JPEGs are downloaded to a temporary directory only and deleted when the
process exits. Tesseract TSV output is parsed in memory. The script writes only
aggregate page metrics; it does not persist OCR text or source images.

Tesseract confidence is a diagnostic proxy, NOT a substitute for CER/WER
against a human reference.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 OCR viability benchmark"
FIELDS = (
    "page_id","book_id","catalog_generation","viewer_page","qc_slot",
    "source_bytes","ocr_engine","ocr_language","psm","recognized_words",
    "ocr_chars","mean_word_confidence","median_word_confidence",
    "low_confidence_word_rate","ocr_status","error",
)


def download(url: str, target: Path, timeout: int = 20) -> int:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Connection": "close"})
    with urlopen(req, timeout=timeout) as response, target.open("wb") as fh:
        expected_header = response.headers.get("Content-Length")
        expected = int(expected_header) if expected_header and expected_header.isdigit() else None
        total = 0
        while expected is None or total < expected:
            remaining = 65536 if expected is None else min(65536, expected - total)
            if remaining <= 0:
                break
            chunk = response.read(remaining)
            if not chunk:
                break
            fh.write(chunk)
            total += len(chunk)
        if expected is not None and total != expected:
            raise IOError(f"incomplete JPEG: read {total} of {expected} bytes")
    return total


def tesseract_metrics(image: Path, lang: str, psm: int) -> dict:
    cmd = ["tesseract", str(image), "stdout", "-l", lang, "--psm", str(psm), "tsv"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"tesseract exit {proc.returncode}")

    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter="\t"))
    words = []
    confs = []
    for row in rows:
        text = (row.get("text") or "").strip()
        try:
            conf = float(row.get("conf") or -1)
        except ValueError:
            conf = -1
        if text and conf >= 0:
            words.append(text)
            confs.append(conf)

    chars = sum(len(w) for w in words)
    low_rate = (sum(c < 60 for c in confs) / len(confs)) if confs else 1.0
    return {
        "recognized_words": len(words),
        "ocr_chars": chars,
        "mean_word_confidence": f"{statistics.mean(confs):.2f}" if confs else "",
        "median_word_confidence": f"{statistics.median(confs):.2f}" if confs else "",
        "low_confidence_word_rate": f"{low_rate:.4f}",
    }


def process(row: dict[str,str], tempdir: Path, lang: str, psm: int) -> dict:
    image = tempdir / f"{row['page_id']}.jpg"
    try:
        size = download(row["source_asset_url"], image)
        metrics = tesseract_metrics(image, lang, psm)
        return {
            "page_id":row["page_id"],"book_id":row["book_id"],
            "catalog_generation":row["catalog_generation"],"viewer_page":row["viewer_page"],
            "qc_slot":row["qc_slot"],"source_bytes":size,"ocr_engine":"tesseract",
            "ocr_language":lang,"psm":psm,**metrics,"ocr_status":"ok","error":"",
        }
    except Exception as exc:
        return {
            "page_id":row["page_id"],"book_id":row["book_id"],
            "catalog_generation":row["catalog_generation"],"viewer_page":row["viewer_page"],
            "qc_slot":row["qc_slot"],"source_bytes":"","ocr_engine":"tesseract",
            "ocr_language":lang,"psm":psm,"recognized_words":"","ocr_chars":"",
            "mean_word_confidence":"","median_word_confidence":"",
            "low_confidence_word_rate":"","ocr_status":"error",
            "error":f"{type(exc).__name__}: {exc}",
        }
    finally:
        image.unlink(missing_ok=True)


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",default="data/derived/page_manifest.csv")
    ap.add_argument("--output",default="data/derived/ocr_sample_metrics.csv")
    ap.add_argument("--lang",default="spa")
    ap.add_argument("--psm",type=int,default=3)
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--slots",default="",help="Optional comma-separated qc_slot filter, e.g. q1_1,q4_2")
    args=ap.parse_args()

    allowed={s.strip() for s in args.slots.split(",") if s.strip()}
    with Path(args.manifest).open(encoding="utf-8",newline="") as fh:
        selected=[r for r in csv.DictReader(fh) if r["qc_positional_candidate"]=="yes" and (not allowed or r["qc_slot"] in allowed)]

    with tempfile.TemporaryDirectory(prefix="ltmd-ocr-") as tmp:
        tempdir=Path(tmp)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            results=list(pool.map(lambda r: process(r,tempdir,args.lang,args.psm),selected))

    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=FIELDS); writer.writeheader(); writer.writerows(results)

    ok=sum(r["ocr_status"]=="ok" for r in results)
    print(f"OCR benchmark completed: {ok}/{len(results)} pages")
    for r in results:
        print(r["page_id"],r["recognized_words"],r["mean_word_confidence"],r["low_confidence_word_rate"],r["ocr_status"])


if __name__ == "__main__":
    main()
