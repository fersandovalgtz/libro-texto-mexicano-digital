#!/usr/bin/env python3
"""Validate the incremental FTRL downstream for the four resolved W2 DMA 2018 books.

This validator deliberately preserves the 57-book / 11,945-page archival baseline
as historical evidence and validates only the newly admitted 4-book / 892-page
delta against the current 61-book / 12,837-page W2 source partition.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

DMA_2018 = {
    "H2018P3DMA": 225,
    "H2018P4DMA": 257,
    "H2018P5DMA": 225,
    "H2018P6DMA": 185,
}
EXPECTED_DELTA_PAGES = 892
EXPECTED_HISTORICAL = 64
EXPECTED_ADMITTED = 64
EXPECTED_CANONICAL = 61
EXPECTED_ALIASES = 3
EXPECTED_WITHHELD = 0
EXPECTED_TOTAL = 12837
BASELINE_CANONICAL = 57
BASELINE_PAGES = 11945
SCHEMA = "LTMD_FTRL_W2_DMA_2018_DELTA_EVIDENCE_0.1"
BOOK_SCHEMA = "LTMD_FTRL_W2_BOOK_UNIT_0.2"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def page_key_hash(viewer_key: str, page_index: int) -> str:
    return hashlib.sha256(f"{viewer_key}:src{page_index:04d}".encode("utf-8")).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-root", type=Path, required=True)
    ap.add_argument("--asset-manifest", type=Path, required=True)
    ap.add_argument("--processing-inventory", type=Path, required=True)
    ap.add_argument("--baseline-closure", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    proc = read_csv(args.processing_inventory)
    assets = read_csv(args.asset_manifest)
    if len(proc) != EXPECTED_CANONICAL:
        raise SystemExit(f"expected {EXPECTED_CANONICAL} current W2 canonical rows, found {len(proc)}")
    if len(assets) != EXPECTED_TOTAL:
        raise SystemExit(f"expected {EXPECTED_TOTAL} current W2 source pages, found {len(assets)}")

    proc_by = {r["viewer_key"]: r for r in proc}
    if set(DMA_2018) - set(proc_by):
        raise SystemExit("one or more DMA 2018 identities are absent from current canonical inventory")
    if any(
        proc_by[v]["technical_identity_covered"] != "1"
        or proc_by[v]["is_canonical_processing_object"] != "1"
        or proc_by[v]["persistent_internal_source_gaps"] != "0"
        for v in DMA_2018
    ):
        raise SystemExit("DMA 2018 current processing inventory is not technically admissible")

    delta_assets = [r for r in assets if r["viewer_key"] in DMA_2018]
    counts = Counter(r["viewer_key"] for r in delta_assets)
    if dict(counts) != DMA_2018:
        raise SystemExit(f"DMA 2018 source-page count drift: {dict(counts)}")
    if len(delta_assets) != EXPECTED_DELTA_PAGES:
        raise SystemExit("DMA 2018 delta page denominator drift")

    expected_hashes = {
        page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in delta_assets
    }
    if len(expected_hashes) != EXPECTED_DELTA_PAGES:
        raise SystemExit("DMA 2018 page-key collision or duplicate")

    baseline = json.loads(args.baseline_closure.read_text(encoding="utf-8"))
    if not baseline.get("archival_complete"):
        raise SystemExit("historical W2 baseline is not archival_complete")
    bf = baseline.get("ftrl", {})
    if int(bf.get("canonical_processing_objects", -1)) != BASELINE_CANONICAL:
        raise SystemExit("historical W2 baseline canonical denominator drift")
    if int(bf.get("source_pages", -1)) != BASELINE_PAGES:
        raise SystemExit("historical W2 baseline page denominator drift")
    exceptions = baseline.get("source_exceptions", {}).get("viewer_keys", [])
    if set(exceptions) != set(DMA_2018):
        raise SystemExit("historical W2 baseline does not document the exact DMA 2018 retention set")

    evidence_files = sorted(args.evidence_root.rglob("w2_*_evidence.json"))
    if len(evidence_files) != len(DMA_2018):
        raise SystemExit(f"expected 4 DMA 2018 evidence files, found {len(evidence_files)}")

    seen_viewers: set[str] = set()
    union_hashes: set[str] = set()
    book_records: dict[str, int] = {}
    sqlite_records = 0
    fts_records = 0
    qc_records = 0
    product_hashes: list[dict[str, object]] = []

    partition_checks = {
        "historical_identities": EXPECTED_HISTORICAL,
        "admitted_historical_identities": EXPECTED_ADMITTED,
        "canonical_processing_objects": EXPECTED_CANONICAL,
        "exact_source_aliases": EXPECTED_ALIASES,
        "withheld_identities": EXPECTED_WITHHELD,
        "full_admitted_canonical_source_pages": EXPECTED_TOTAL,
    }

    for path in evidence_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") != BOOK_SCHEMA:
            raise SystemExit(f"unexpected DMA 2018 book evidence schema: {path}")
        if data.get("status") != "validated" or data.get("wave") != "W2":
            raise SystemExit(f"non-validated or foreign DMA 2018 evidence: {path}")
        viewer = data.get("viewer_key")
        if viewer not in DMA_2018 or viewer in seen_viewers:
            raise SystemExit(f"unexpected or duplicate DMA 2018 viewer evidence: {viewer}")
        seen_viewers.add(viewer)

        pages = int(data["page_records"])
        if pages != DMA_2018[viewer]:
            raise SystemExit(f"DMA 2018 evidence page drift for {viewer}: {pages}")
        hashes = list(data["page_key_hashes"])
        if len(hashes) != pages or len(set(hashes)) != pages:
            raise SystemExit(f"duplicate/missing DMA 2018 page hashes for {viewer}")
        if union_hashes & set(hashes):
            raise SystemExit(f"cross-book DMA 2018 page hash overlap for {viewer}")
        union_hashes.update(hashes)

        partition = data["source_partition"]
        if any(int(partition[k]) != v for k, v in partition_checks.items()):
            raise SystemExit(f"current W2 source partition drift for {viewer}")

        validation = data["validation"]
        if validation["sqlite_integrity"] != "ok":
            raise SystemExit(f"SQLite integrity failure for {viewer}")
        if (
            int(validation["sqlite_pages"]) != pages
            or int(validation["fts_rows"]) != pages
            or int(validation["qc_page_records"]) != pages
        ):
            raise SystemExit(f"DMA 2018 validation cardinality drift for {viewer}")
        sqlite_records += int(validation["sqlite_pages"])
        fts_records += int(validation["fts_rows"])
        qc_records += int(validation["qc_page_records"])
        book_records[viewer] = pages

        if data.get("text_verified") is not False or data.get("semantic_ready") is not False:
            raise SystemExit(f"forbidden semantic/text promotion in {viewer}")

        for group in ("restricted_products", "text_free_products"):
            if len(data[group]) != 3:
                raise SystemExit(f"unexpected product count for {viewer}: {group}")
            for item in data[group]:
                if len(item["sha256"]) != 64 or int(item["bytes"]) <= 0:
                    raise SystemExit(f"invalid product descriptor for {viewer}")
                product_hashes.append({
                    "viewer_key": viewer,
                    "class": group,
                    "name": item["name"],
                    "bytes": item["bytes"],
                    "sha256": item["sha256"],
                })

    if seen_viewers != set(DMA_2018):
        raise SystemExit("DMA 2018 evidence viewer union is not exhaustive")
    if union_hashes != expected_hashes or len(union_hashes) != EXPECTED_DELTA_PAGES:
        raise SystemExit("DMA 2018 page evidence union is not exact and exhaustive")
    if not (sqlite_records == fts_records == qc_records == EXPECTED_DELTA_PAGES):
        raise SystemExit("DMA 2018 SQLite/FTS/QC cardinality drift")

    out = {
        "schema": SCHEMA,
        "status": "validated",
        "wave": "W2",
        "domain": "Matemáticas",
        "mode": "incremental_downstream_after_routing_resolution",
        "baseline": {
            "archival_closure": str(args.baseline_closure),
            "canonical_processing_objects": BASELINE_CANONICAL,
            "source_pages": BASELINE_PAGES,
            "archival_complete": True,
        },
        "current_partition": {
            "historical_identities": EXPECTED_HISTORICAL,
            "admitted_historical_identities": EXPECTED_ADMITTED,
            "canonical_processing_objects": EXPECTED_CANONICAL,
            "exact_source_aliases": EXPECTED_ALIASES,
            "withheld_identities": EXPECTED_WITHHELD,
            "source_pages": EXPECTED_TOTAL,
        },
        "delta": {
            "viewer_keys": sorted(DMA_2018),
            "canonical_processing_objects": len(DMA_2018),
            "book_page_records": dict(sorted(book_records.items())),
            "source_pages": EXPECTED_DELTA_PAGES,
            "unique_page_key_hashes": len(union_hashes),
            "sqlite_page_rows": sqlite_records,
            "fts_rows": fts_records,
            "qc_page_records": qc_records,
        },
        "products": sorted(product_hashes, key=lambda x: (x["viewer_key"], x["class"], x["name"])),
        "computationally_validated": True,
        "archival_complete": False,
        "text_verified": False,
        "semantic_ready": False,
        "epistemic_guards": [
            "routing_resolved != downstream_processed",
            "downstream_processed != ftrl_validated",
            "ftrl_validated != text_verified",
            "text_verified != semantic_ready",
            "incremental_validation != archival_completion",
            "search_hit != historical_claim",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "books": 4, "pages": EXPECTED_DELTA_PAGES, "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
