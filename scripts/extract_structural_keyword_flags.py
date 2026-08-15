#!/usr/bin/env python3
"""Extract non-substitutive structural keyword signals from candidate pages.

The script downloads only front/end-zone source JPEGs, runs the exact selected
Tesseract PSM from ocr_page_metrics.csv, searches OCR text in-memory for a small
predeclared structural vocabulary, writes category scores/flags only, and deletes
all temporary image/OCR material. It never writes OCR transcription to the repo.
"""
from __future__ import annotations

import csv
import re
import subprocess
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

METRICS = Path("data/derived/ocr_page_metrics.csv")
OUT = Path("data/derived/structural_keyword_flags.csv")

SOURCE_CODES = {
    "1972": "H1972P5CI084",
    "1988": "H1988P5CI123",
    "1993": "H1993P5CI200",
    "2014": "H2014P5CNA",
}

VOCAB = {
    "front_matter": [
        r"\bpresentacion\b", r"\bprologo\b", r"\bintroduccion\b",
        r"\bconoce tu libro\b", r"\bal alumno\b", r"\bal maestro\b",
        r"\bmensaje\b",
    ],
    "toc_navigation": [
        r"\bindice\b", r"\bcontenido(?:s)?\b", r"\bpagina(?:s)?\b",
        r"\bbloque(?:s)?\b", r"\btema(?:s)?\b", r"\bleccion(?:es)?\b",
    ],
    "bibliography_credits": [
        r"\bbibliografia\b", r"\breferencias\b", r"\bfuentes consultadas\b",
        r"\bpara saber mas\b", r"\bisbn\b", r"\bderechos reservados\b",
        r"\bprimera edicion\b", r"\bsegunda edicion\b", r"\btercera edicion\b",
        r"\bcoordinacion\b", r"\bsecretaria de educacion publica\b",
        r"\bimpreso en mexico\b",
    ],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.casefold()
    s = re.sub(r"\s+", " ", s)
    return s


def load_rows():
    rows = list(csv.DictReader(METRICS.open(encoding="utf-8")))
    by_gen = {}
    for r in rows:
        by_gen.setdefault(r["catalog_generation"], []).append(r)
    candidates = []
    for gen, group in by_gen.items():
        max_page = max(int(r["viewer_page"]) for r in group if r["asset_status"] == "source_jpeg")
        for r in group:
            if r["asset_status"] != "source_jpeg":
                continue
            p = int(r["viewer_page"])
            if p <= 16 or p > max_page - 16:
                candidates.append((r, max_page))
    return candidates


def run_ocr(img: Path, psm: str) -> str:
    cp = subprocess.run(
        ["tesseract", str(img), "stdout", "-l", "spa", "--psm", psm],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        timeout=90, check=False,
    )
    return cp.stdout if cp.returncode == 0 else ""


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "page_id", "catalog_generation", "viewer_page", "selected_psm",
        "front_zone", "end_zone", "front_matter_score", "toc_navigation_score",
        "bibliography_credits_score", "matched_category_count", "scanner_version",
    ]
    out = []
    with tempfile.TemporaryDirectory(prefix="ltmd-structure-") as td:
        td = Path(td)
        for r, max_page in load_rows():
            gen = r["catalog_generation"]
            p = int(r["viewer_page"])
            img = td / f"{gen}_{p:03d}.jpg"
            url = f"https://historico.conaliteg.gob.mx/c/{SOURCE_CODES[gen]}/{p:03d}.jpg"
            try:
                urllib.request.urlretrieve(url, img)
                text = norm(run_ocr(img, r["selected_psm"] or "3"))
            except Exception:
                text = ""
            scores = {}
            for cat, pats in VOCAB.items():
                scores[cat] = sum(1 for pat in pats if re.search(pat, text))
            out.append({
                "page_id": r["page_id"],
                "catalog_generation": gen,
                "viewer_page": p,
                "selected_psm": r["selected_psm"],
                "front_zone": 1 if p <= 16 else 0,
                "end_zone": 1 if p > max_page - 16 else 0,
                "front_matter_score": scores["front_matter"],
                "toc_navigation_score": scores["toc_navigation"],
                "bibliography_credits_score": scores["bibliography_credits"],
                "matched_category_count": sum(1 for v in scores.values() if v > 0),
                "scanner_version": "STRUCTKW_0.1",
            })
            try:
                img.unlink(missing_ok=True)
            except Exception:
                pass
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(out)
    print(f"wrote {len(out)} candidate rows to {OUT}")


if __name__ == "__main__":
    main()
