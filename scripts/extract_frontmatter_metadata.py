#!/usr/bin/env python3
"""Extract limited bibliographic metadata from early viewer pages.

This utility is designed for a temporary research runner. It downloads only a
small front-matter window, OCRs each image in memory/on temporary storage, and
writes *derived metadata only*: candidate page type, candidate years, ISBN-like
identifiers and very short matched labels. It never writes full OCR text or
source images to the repository.

All OCR-derived bibliographic values remain candidates until visually checked
against the source page.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

USER_AGENT = "LibroTextoMexicanoDigital/0.1 frontmatter metadata audit"
YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
ISBN_RE = re.compile(r"\b(?:ISBN(?:-1[03])?\s*[: ]\s*)?((?:97[89][- ]?)?[0-9][-0-9 ]{8,16}[0-9Xx])\b")
EDITION_RE = re.compile(r"(?i)\b((?:primera|segunda|tercera|cuarta|quinta|sexta|séptima|octava|novena|décima|\d+\.?)\s+(?:edición|reimpresión)|edición\s+(?:revisada|actualizada))\b")

FIELDS = (
    "book_id","catalog_generation","viewer_page","source_filename",
    "candidate_page_type","candidate_years","candidate_edition_phrases",
    "candidate_isbn","ocr_word_count","ocr_status","verification_status","error",
)


def fetch(url: str, target: Path, timeout: int = 30) -> None:
    req=Request(url,headers={"User-Agent":USER_AGENT})
    with urlopen(req,timeout=timeout) as response, target.open("wb") as fh:
        while True:
            chunk=response.read(65536)
            if not chunk: break
            fh.write(chunk)


def ocr(path: Path, lang: str) -> str:
    proc=subprocess.run(["tesseract",str(path),"stdout","-l",lang,"--psm","3"],capture_output=True,text=True,timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"tesseract exit {proc.returncode}")
    return proc.stdout


def classify(text: str) -> str:
    low=text.lower()
    legal=sum(tok in low for tok in ("derechos reservados","isbn","edición","reimpresión","secretaría de educación pública","comisión nacional de libros"))
    toc=sum(tok in low for tok in ("índice","contenido","bloque i","bloque 1","unidad i","unidad 1"))
    if legal >= 2: return "legal_candidate"
    if toc >= 2: return "toc_candidate"
    return "frontmatter_other"


def clean_isbn(value: str) -> str:
    return re.sub(r"[^0-9Xx]","",value).upper()


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",default="data/derived/page_manifest.csv")
    ap.add_argument("--output",default="data/derived/frontmatter_metadata_candidates.csv")
    ap.add_argument("--pages",type=int,default=12,help="Inspect viewer pages 1..N only")
    ap.add_argument("--lang",default="spa")
    args=ap.parse_args()

    with Path(args.manifest).open(encoding="utf-8",newline="") as fh:
        all_rows=list(csv.DictReader(fh))
    selected=[r for r in all_rows if int(r["viewer_page"]) <= args.pages]

    results=[]
    with tempfile.TemporaryDirectory(prefix="ltmd-frontmatter-") as tmp:
        root=Path(tmp)
        for row in selected:
            image=root/f"{row['page_id']}.jpg"
            try:
                fetch(row["source_asset_url"],image)
                text=ocr(image,args.lang)
                years=sorted(set(YEAR_RE.findall(text)))
                editions=[]
                for match in EDITION_RE.finditer(text):
                    val=re.sub(r"\s+"," ",match.group(1)).strip()
                    if val.lower() not in {x.lower() for x in editions}: editions.append(val)
                isbns=[]
                for match in ISBN_RE.finditer(text):
                    val=clean_isbn(match.group(1))
                    if len(val) in (10,13) and val not in isbns: isbns.append(val)
                results.append({
                    "book_id":row["book_id"],"catalog_generation":row["catalog_generation"],
                    "viewer_page":row["viewer_page"],"source_filename":row["source_filename"],
                    "candidate_page_type":classify(text),"candidate_years":"|".join(years),
                    "candidate_edition_phrases":"|".join(editions[:5]),"candidate_isbn":"|".join(isbns[:5]),
                    "ocr_word_count":len(text.split()),"ocr_status":"ok",
                    "verification_status":"ocr_candidate_not_verified","error":"",
                })
            except Exception as exc:
                results.append({
                    "book_id":row["book_id"],"catalog_generation":row["catalog_generation"],
                    "viewer_page":row["viewer_page"],"source_filename":row["source_filename"],
                    "candidate_page_type":"","candidate_years":"","candidate_edition_phrases":"",
                    "candidate_isbn":"","ocr_word_count":"","ocr_status":"error",
                    "verification_status":"unverified","error":f"{type(exc).__name__}: {exc}",
                })
            finally:
                image.unlink(missing_ok=True)

    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=FIELDS); writer.writeheader(); writer.writerows(results)
    print(f"Wrote {len(results)} derived front-matter candidate rows to {out}")
    for r in results:
        if r["candidate_page_type"] != "frontmatter_other" or r["candidate_years"] or r["candidate_isbn"]:
            print(r)


if __name__ == "__main__":
    main()
