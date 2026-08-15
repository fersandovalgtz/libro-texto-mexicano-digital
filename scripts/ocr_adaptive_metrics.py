#!/usr/bin/env python3
"""Metadata-only OCR metrics for the LTMD pilot.

Downloads source JPEGs only to a temporary directory, runs Tesseract, and writes
page-level metrics only. No source image or OCR transcription is persisted.

Operational strategy:
- baseline `psm 3` is accepted when it detects at least one word;
- if baseline detects zero words or fails, all configured fallback modes are run;
- a fallback is accepted only when it detects at least `--fallback-min-words`
  (default 5), which avoids treating a couple of low-confidence tokens as a
  successful page extraction;
- among valid fallback candidates, the mode with the largest word count is
  selected (confidence breaks ties);
- rows marked `terminal_synthetic` are never sent to OCR.
"""
from __future__ import annotations

import argparse, csv, statistics, subprocess, tempfile
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

UA = "LibroTextoMexicanoDigital/0.1 OCR metrics"
FIELDS = [
    "page_id","book_id","catalog_generation","viewer_page","qc_slot","asset_status",
    "source_bytes","attempts","selected_psm","recognized_words","ocr_chars",
    "mean_word_confidence","median_word_confidence","low_confidence_word_rate",
    "ocr_class","ocr_status","error"
]

def download(url: str, target: Path, timeout: int = 30) -> int:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as r, target.open("wb") as fh:
        expected = r.headers.get("Content-Length")
        expected_n = int(expected) if expected and expected.isdigit() else None
        total = 0
        while expected_n is None or total < expected_n:
            need = 65536 if expected_n is None else min(65536, expected_n-total)
            chunk = r.read(need)
            if not chunk: break
            fh.write(chunk); total += len(chunk)
        return total

def run_tesseract(image: Path, lang: str, psm: int, timeout: int) -> dict:
    cmd=["tesseract",str(image),"stdout","-l",lang,"--psm",str(psm),"tsv"]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"tesseract exit {proc.returncode}")
    rows=list(csv.DictReader(proc.stdout.splitlines(),delimiter="\t"))
    words=[]; confs=[]
    for row in rows:
        txt=(row.get("text") or "").strip()
        try: conf=float(row.get("conf") or -1)
        except ValueError: conf=-1
        if txt and conf >= 0:
            words.append(txt); confs.append(conf)
    low=(sum(c<60 for c in confs)/len(confs)) if confs else 1.0
    return {
        "recognized_words":len(words),
        "ocr_chars":sum(len(w) for w in words),
        "mean_word_confidence":f"{statistics.mean(confs):.2f}" if confs else "",
        "median_word_confidence":f"{statistics.median(confs):.2f}" if confs else "",
        "low_confidence_word_rate":f"{low:.4f}",
    }

def _score(metrics: dict) -> tuple[int, float]:
    words=int(metrics.get("recognized_words") or 0)
    try: conf=float(metrics.get("mean_word_confidence") or 0)
    except ValueError: conf=0.0
    return words, conf

def process(row: dict[str,str], tempdir: Path, lang: str, modes: list[int], timeout: int, fallback_min_words: int) -> dict:
    image=tempdir/f"{row['page_id']}.jpg"
    attempts=[]; errors=[]
    base={
        "page_id":row["page_id"],"book_id":row["book_id"],
        "catalog_generation":row["catalog_generation"],"viewer_page":row["viewer_page"],
        "qc_slot":row.get("qc_slot", ""),"asset_status":row.get("asset_status","source_jpeg"),
    }
    empty_metrics={"recognized_words":"","ocr_chars":"","mean_word_confidence":"","median_word_confidence":"","low_confidence_word_rate":""}
    try:
        size=download(row["source_asset_url"],image)
        if not modes:
            raise ValueError("At least one PSM mode is required")

        baseline_psm=modes[0]
        baseline_metrics=None
        try:
            baseline_metrics=run_tesseract(image,lang,baseline_psm,timeout)
            attempts.append(f"psm{baseline_psm}:ok:{baseline_metrics['recognized_words']}")
        except subprocess.TimeoutExpired:
            attempts.append(f"psm{baseline_psm}:timeout")
            errors.append(f"psm{baseline_psm} timeout>{timeout}s")
        except Exception as exc:
            attempts.append(f"psm{baseline_psm}:error")
            errors.append(f"psm{baseline_psm} {type(exc).__name__}: {exc}")

        if baseline_metrics and int(baseline_metrics["recognized_words"]) > 0:
            return {**base,"source_bytes":size,"attempts":";".join(attempts),
                "selected_psm":baseline_psm,**baseline_metrics,"ocr_class":"text_detected",
                "ocr_status":"ok","error":" | ".join(errors)}

        fallback_results=[]
        for psm in modes[1:]:
            try:
                metrics=run_tesseract(image,lang,psm,timeout)
                attempts.append(f"psm{psm}:ok:{metrics['recognized_words']}")
                fallback_results.append((psm,metrics))
            except subprocess.TimeoutExpired:
                attempts.append(f"psm{psm}:timeout")
                errors.append(f"psm{psm} timeout>{timeout}s")
            except Exception as exc:
                attempts.append(f"psm{psm}:error")
                errors.append(f"psm{psm} {type(exc).__name__}: {exc}")

        valid=[(psm,m) for psm,m in fallback_results if int(m["recognized_words"]) >= fallback_min_words]
        if valid:
            selected_psm, selected_metrics=max(valid,key=lambda item:_score(item[1]))
            return {**base,"source_bytes":size,"attempts":";".join(attempts),
                "selected_psm":selected_psm,**selected_metrics,"ocr_class":"text_detected",
                "ocr_status":"ok","error":" | ".join(errors)}

        observed=[]
        if baseline_metrics is not None:
            observed.append((baseline_psm,baseline_metrics))
        observed.extend(fallback_results)
        if observed:
            _, best_metrics=max(observed,key=lambda item:_score(item[1]))
            return {**base,"source_bytes":size,"attempts":";".join(attempts),
                "selected_psm":"",**best_metrics,"ocr_class":"no_text_detected",
                "ocr_status":"ok","error":" | ".join(errors)}

        return {**base,"source_bytes":size,"attempts":";".join(attempts),"selected_psm":"",
            **empty_metrics,"ocr_class":"unresolved","ocr_status":"error","error":" | ".join(errors)}
    except Exception as exc:
        return {**base,"source_bytes":"","attempts":";".join(attempts),"selected_psm":"",
            **empty_metrics,"ocr_class":"unresolved","ocr_status":"error",
            "error":f"{type(exc).__name__}: {exc}"}
    finally:
        image.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",default="data/derived/page_manifest.csv")
    ap.add_argument("--output",default="data/derived/ocr_adaptive_metrics.csv")
    ap.add_argument("--lang",default="spa")
    ap.add_argument("--modes",default="3,11,6")
    ap.add_argument("--fallback-min-words",type=int,default=5)
    ap.add_argument("--timeout",type=int,default=60)
    ap.add_argument("--workers",type=int,default=2)
    ap.add_argument("--slots",default="q1_1,q4_2")
    ap.add_argument("--all-pages",action="store_true",help="Process every source-JPEG row in the page manifest instead of only QC candidates")
    args=ap.parse_args()
    modes=[int(x) for x in args.modes.split(",") if x.strip()]
    slots={x.strip() for x in args.slots.split(",") if x.strip()}
    with Path(args.manifest).open(encoding="utf-8",newline="") as fh:
        source=list(csv.DictReader(fh))
    source_assets=[
        r for r in source
        if r.get("asset_status","source_jpeg")!="terminal_synthetic"
        and (r.get("source_asset_url") or "").strip()
    ]
    if args.all_pages:
        selected=source_assets
    else:
        selected=[r for r in source_assets if r["qc_positional_candidate"]=="yes" and (not slots or r["qc_slot"] in slots)]
    with tempfile.TemporaryDirectory(prefix="ltmd-ocr-") as tmp:
        td=Path(tmp)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            rows=list(pool.map(lambda r: process(r,td,args.lang,modes,args.timeout,args.fallback_min_words),selected))
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f"OCR metrics: {len(rows)} source assets")
    print("text_detected=",sum(r["ocr_class"]=="text_detected" for r in rows),
          "no_text_detected=",sum(r["ocr_class"]=="no_text_detected" for r in rows),
          "unresolved=",sum(r["ocr_class"]=="unresolved" for r in rows))
    print("selected_psm=",{psm:sum(str(r["selected_psm"])==str(psm) for r in rows) for psm in modes})

if __name__=="__main__": main()
