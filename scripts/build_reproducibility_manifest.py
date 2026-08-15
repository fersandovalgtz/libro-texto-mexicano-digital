#!/usr/bin/env python3
"""Build a cryptographic reproducibility manifest for key pilot inputs.

The manifest records SHA-256, byte size, line count, and CSV data-row count
where applicable. It contains no source images or OCR text.

Use --source-commit to bind the snapshot to the exact Git commit whose files
were hashed. The manifest itself may then be committed in a subsequent commit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

DEFAULT_PATHS = [
    "data/book_inventory.csv",
    "data/derived/ocr_page_metrics.csv",
    "data/derived/ocr_full_pilot_baseline_summary.csv",
    "data/derived/ocr_full_pilot_summary.csv",
    "data/derived/no_text_page_register.csv",
    "data/derived/no_text_page_audit_summary.csv",
    "data/derived/cer_sample_technical_summary.csv",
    "data/derived/ocr_structure_by_quartile.csv",
    "data/samples/ocr_cer_wer_page_sample.csv",
    "data/samples/ocr_cer_wer_stress_sample.csv",
    "data/samples/human_validation_page_pool.csv",
    "data/derived/fragments_schema.csv",
    "docs/CODEBOOK_0_1.md",
    "docs/ANNOTATION_MANUAL_0_1.md",
    "docs/CODER_AGREEMENT_PROTOCOL_0_1.md",
    "docs/OCR_REFERENCE_ALIGNMENT_PROTOCOL.md",
    "docs/OCR_REGION_HYPOTHESIS_METHOD.md",
    "docs/CER_WER_EXECUTION_WORKFLOW.md",
    "docs/DATA_MODEL.md",
    "docs/DATA_GOVERNANCE.md",
    "docs/RIGHTS_PUBLICATION_MATRIX.md",
    "docs/METHOD_INDEX.md",
]

FIELDS = [
    "snapshot_source_commit",
    "path",
    "sha256",
    "bytes",
    "line_count",
    "csv_data_rows",
    "kind",
]


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def csv_rows(path: Path) -> str:
    if path.suffix.lower() != ".csv":
        return ""
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows=list(csv.reader(fh))
    return str(max(0,len(rows)-1))


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-commit",required=True)
    ap.add_argument("--output",default="data/derived/reproducibility_manifest.csv")
    args=ap.parse_args()

    records=[]
    missing=[]
    for raw in DEFAULT_PATHS:
        p=Path(raw)
        if not p.exists():
            missing.append(raw)
            continue
        data=p.read_bytes()
        line_count=data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
        records.append({
            "snapshot_source_commit":args.source_commit,
            "path":raw,
            "sha256":sha256(p),
            "bytes":len(data),
            "line_count":line_count,
            "csv_data_rows":csv_rows(p),
            "kind":"csv_data" if p.suffix.lower()==".csv" else "method_document",
        })

    if missing:
        raise RuntimeError("Missing snapshot paths: "+", ".join(missing))

    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=FIELDS); w.writeheader(); w.writerows(records)

    print(f"Snapshot source commit: {args.source_commit}")
    print(f"Manifest rows: {len(records)}")
    for r in records:
        print(r['path'],r['sha256'],r['bytes'],r['csv_data_rows'])

if __name__=="__main__":
    main()
