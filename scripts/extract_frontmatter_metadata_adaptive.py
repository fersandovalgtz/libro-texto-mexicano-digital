#!/usr/bin/env python3
"""Extract bibliographic candidates from early pages without persisting OCR text.

Temporary JPEGs and OCR text exist only during execution. Output contains only
short derived metadata: candidate page type, years, edition phrases, ISBN,
word count, selected PSM and status.
"""
from __future__ import annotations
import argparse,csv,re,subprocess,tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request,urlopen

UA="LibroTextoMexicanoDigital/0.1 adaptive frontmatter audit"
YEAR_RE=re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
ISBN_RE=re.compile(r"\b(?:ISBN(?:-1[03])?\s*[: ]\s*)?((?:97[89][- ]?)?[0-9][-0-9 ]{8,16}[0-9Xx])\b")
EDITION_RE=re.compile(r"(?i)\b((?:primera|segunda|tercera|cuarta|quinta|sexta|séptima|octava|novena|décima|\d+\.?)\s+(?:edición|reimpresión)|edición\s+(?:revisada|actualizada))\b")
FIELDS=("book_id","catalog_generation","viewer_page","source_filename","candidate_page_type","candidate_years","candidate_edition_phrases","candidate_isbn","ocr_word_count","selected_psm","ocr_status","verification_status","error")

def fetch(url,target,timeout=30):
    req=Request(url,headers={"User-Agent":UA})
    with urlopen(req,timeout=timeout) as r,target.open("wb") as fh:
        raw=r.headers.get("Content-Length"); expected=int(raw) if raw and raw.isdigit() else None; total=0
        while expected is None or total<expected:
            need=65536 if expected is None else min(65536,expected-total)
            chunk=r.read(need)
            if not chunk: break
            fh.write(chunk); total+=len(chunk)

def ocr(path,lang,modes=(6,11),timeout=20):
    errors=[]
    for psm in modes:
        try:
            proc=subprocess.run(["tesseract",str(path),"stdout","-l",lang,"--psm",str(psm)],capture_output=True,text=True,timeout=timeout)
            if proc.returncode!=0:
                errors.append(f"psm{psm} exit {proc.returncode}"); continue
            text=proc.stdout or ""
            if text.strip(): return text,psm," | ".join(errors)
            errors.append(f"psm{psm} no_text")
        except subprocess.TimeoutExpired:
            errors.append(f"psm{psm} timeout>{timeout}s")
    return "",None," | ".join(errors)

def classify(text):
    low=text.lower()
    legal=sum(t in low for t in ("derechos reservados","isbn","edición","reimpresión","secretaría de educación pública","comisión nacional de libros"))
    toc=sum(t in low for t in ("índice","contenido","bloque i","bloque 1","unidad i","unidad 1","lección"))
    if legal>=2:return "legal_candidate"
    if toc>=2:return "toc_candidate"
    return "frontmatter_other"

def process(row,root,lang,modes,timeout):
    img=root/f"{row['page_id']}.jpg"
    try:
        fetch(row["source_asset_url"],img)
        text,psm,notes=ocr(img,lang,modes,timeout)
        if not text.strip():
            return {"book_id":row["book_id"],"catalog_generation":row["catalog_generation"],"viewer_page":row["viewer_page"],"source_filename":row["source_filename"],"candidate_page_type":"frontmatter_other","candidate_years":"","candidate_edition_phrases":"","candidate_isbn":"","ocr_word_count":0,"selected_psm":psm or "","ocr_status":"no_text_or_timeout","verification_status":"unverified","error":notes}
        years=sorted(set(YEAR_RE.findall(text)))
        editions=[]
        for m in EDITION_RE.finditer(text):
            v=re.sub(r"\s+"," ",m.group(1)).strip()
            if v.lower() not in {x.lower() for x in editions}:editions.append(v)
        isbns=[]
        for m in ISBN_RE.finditer(text):
            v=re.sub(r"[^0-9Xx]","",m.group(1)).upper()
            if len(v) in (10,13) and v not in isbns:isbns.append(v)
        return {"book_id":row["book_id"],"catalog_generation":row["catalog_generation"],"viewer_page":row["viewer_page"],"source_filename":row["source_filename"],"candidate_page_type":classify(text),"candidate_years":"|".join(years),"candidate_edition_phrases":"|".join(editions[:5]),"candidate_isbn":"|".join(isbns[:5]),"ocr_word_count":len(text.split()),"selected_psm":psm,"ocr_status":"ok","verification_status":"ocr_candidate_not_verified","error":notes}
    except Exception as exc:
        return {"book_id":row["book_id"],"catalog_generation":row["catalog_generation"],"viewer_page":row["viewer_page"],"source_filename":row["source_filename"],"candidate_page_type":"","candidate_years":"","candidate_edition_phrases":"","candidate_isbn":"","ocr_word_count":"","selected_psm":"","ocr_status":"error","verification_status":"unverified","error":f"{type(exc).__name__}: {exc}"}
    finally: img.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--manifest",default="data/derived/page_manifest.csv"); ap.add_argument("--output",default="data/derived/frontmatter_metadata_candidates.csv"); ap.add_argument("--pages",type=int,default=8); ap.add_argument("--lang",default="spa"); ap.add_argument("--modes",default="6,11"); ap.add_argument("--timeout",type=int,default=20); ap.add_argument("--workers",type=int,default=8); args=ap.parse_args()
    modes=[int(x) for x in args.modes.split(',') if x.strip()]
    with Path(args.manifest).open(encoding="utf-8",newline="") as fh: selected=[r for r in csv.DictReader(fh) if int(r["viewer_page"])<=args.pages]
    with tempfile.TemporaryDirectory(prefix="ltmd-front-") as tmp:
        root=Path(tmp)
        with ThreadPoolExecutor(max_workers=args.workers) as pool: results=list(pool.map(lambda r:process(r,root,args.lang,modes,args.timeout),selected))
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as fh: w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(results)
    print(f"Front matter candidates: {len(results)} rows")
    for r in results:
        if r["candidate_page_type"]!="frontmatter_other" or r["candidate_years"] or r["candidate_isbn"] or r["candidate_edition_phrases"]: print(r)
if __name__=="__main__":main()
