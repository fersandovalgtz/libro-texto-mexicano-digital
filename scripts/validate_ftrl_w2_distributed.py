#!/usr/bin/env python3
"""Validate the exact union of all W2 Mathematics FTRL book evidences."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_HISTORICAL = 64
EXPECTED_ADMITTED = 60
EXPECTED_CANONICAL = 57
EXPECTED_ALIASES = 3
EXPECTED_WITHHELD = 4
EXPECTED_TOTAL = 11945
WITHHELD = ["H2018P3DMA", "H2018P4DMA", "H2018P5DMA", "H2018P6DMA"]
ALIASES = {
    "H1982P4MA388": "H1972P4MA083",
    "H1982P5MA394": "H1972P5MA089",
    "H1982P6MA399": "H1972P6MA094",
}
SCHEMA = "LTMD_FTRL_W2_GLOBAL_EVIDENCE_0.1"


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
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    proc = read_csv(args.processing_inventory)
    assets = read_csv(args.asset_manifest)
    if len(proc) != EXPECTED_CANONICAL:
        raise SystemExit(f"expected {EXPECTED_CANONICAL} W2 processing rows, found {len(proc)}")
    viewers = {r["viewer_key"] for r in proc}
    if len(viewers) != EXPECTED_CANONICAL:
        raise SystemExit("duplicate W2 canonical processing identity")
    if not all(
        r["technical_identity_covered"] == "1"
        and r["is_canonical_processing_object"] == "1"
        and r["persistent_internal_source_gaps"] == "0"
        for r in proc
    ):
        raise SystemExit("invalid W2 admitted processing inventory")
    if len(assets) != EXPECTED_TOTAL:
        raise SystemExit(f"expected {EXPECTED_TOTAL} W2 source pages, found {len(assets)}")
    counts = Counter(r["viewer_key"] for r in assets)
    expected_counts = Counter({
        r["viewer_key"]: int(r["direct_source_jpegs"]) for r in proc
    })
    if counts != expected_counts:
        raise SystemExit(f"W2 per-viewer page counts drift: {counts} != {expected_counts}")

    expected_hashes = {
        page_key_hash(r["viewer_key"], int(r["source_image_index"])) for r in assets
    }
    if len(expected_hashes) != EXPECTED_TOTAL:
        raise SystemExit("W2 expected page-key hash collision or duplicate")

    evidence_files = sorted(args.evidence_root.rglob("w2_*_evidence.json"))
    if len(evidence_files) != EXPECTED_CANONICAL:
        raise SystemExit(
            f"expected {EXPECTED_CANONICAL} W2 evidence files, found {len(evidence_files)}"
        )

    seen_viewers: set[str] = set()
    union_hashes: set[str] = set()
    book_records: dict[str, int] = {}
    qc_records = sqlite_records = fts_records = 0
    product_hashes: list[dict[str, object]] = []

    for path in evidence_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["schema"] != "LTMD_FTRL_W2_BOOK_UNIT_0.1":
            raise SystemExit(f"unexpected W2 book evidence schema: {path}")
        if data["status"] != "validated" or data["wave"] != "W2":
            raise SystemExit(f"non-validated or foreign W2 evidence: {path}")
        viewer = data["viewer_key"]
        if viewer not in viewers or viewer in seen_viewers:
            raise SystemExit(f"unexpected or duplicate W2 viewer evidence: {viewer}")
        seen_viewers.add(viewer)

        pages = int(data["page_records"])
        if pages != expected_counts[viewer]:
            raise SystemExit(f"W2 evidence page drift for {viewer}: {pages}")
        hashes = list(data["page_key_hashes"])
        if len(hashes) != pages or len(set(hashes)) != pages:
            raise SystemExit(f"duplicate/missing W2 page hashes for {viewer}")
        if union_hashes & set(hashes):
            raise SystemExit(f"cross-book W2 page hash overlap for {viewer}")
        union_hashes.update(hashes)

        partition = data["source_partition"]
        checks = {
            "historical_identities": EXPECTED_HISTORICAL,
            "admitted_historical_identities": EXPECTED_ADMITTED,
            "canonical_processing_objects": EXPECTED_CANONICAL,
            "exact_source_aliases": EXPECTED_ALIASES,
            "withheld_identities": EXPECTED_WITHHELD,
            "full_admitted_canonical_source_pages": EXPECTED_TOTAL,
        }
        if any(int(partition[k]) != v for k, v in checks.items()):
            raise SystemExit(f"W2 source partition drift for {viewer}")

        validation = data["validation"]
        if validation["sqlite_integrity"] != "ok":
            raise SystemExit(f"SQLite integrity failure for {viewer}")
        if (
            int(validation["sqlite_pages"]) != pages
            or int(validation["fts_rows"]) != pages
            or int(validation["qc_page_records"]) != pages
        ):
            raise SystemExit(f"W2 validation cardinality drift for {viewer}")
        sqlite_records += int(validation["sqlite_pages"])
        fts_records += int(validation["fts_rows"])
        qc_records += int(validation["qc_page_records"])
        book_records[viewer] = pages

        for group in ("restricted_products", "text_free_products"):
            if len(data[group]) != 3:
                raise SystemExit(f"unexpected W2 product count for {viewer}: {group}")
            for item in data[group]:
                if len(item["sha256"]) != 64 or int(item["bytes"]) <= 0:
                    raise SystemExit(f"invalid W2 product descriptor for {viewer}")
                product_hashes.append({
                    "viewer_key": viewer,
                    "class": group,
                    "name": item["name"],
                    "bytes": item["bytes"],
                    "sha256": item["sha256"],
                })

    if seen_viewers != viewers:
        raise SystemExit("W2 evidence viewer union is not exhaustive")
    if union_hashes != expected_hashes or len(union_hashes) != EXPECTED_TOTAL:
        raise SystemExit("W2 page evidence union is not exact and exhaustive")
    if (
        sqlite_records != EXPECTED_TOTAL
        or fts_records != EXPECTED_TOTAL
        or qc_records != EXPECTED_TOTAL
    ):
        raise SystemExit("W2 global SQLite/FTS/QC cardinality drift")
    if len(product_hashes) != EXPECTED_CANONICAL * 6:
        raise SystemExit("W2 global product descriptor cardinality drift")

    out = {
        "schema": SCHEMA,
        "status": "validated",
        "wave": "W2",
        "domain": "Matemáticas",
        "historical_identities": EXPECTED_HISTORICAL,
        "admitted_historical_identities": EXPECTED_ADMITTED,
        "canonical_processing_objects": EXPECTED_CANONICAL,
        "exact_source_aliases": EXPECTED_ALIASES,
        "alias_map": ALIASES,
        "withheld_source_identities": EXPECTED_WITHHELD,
        "withheld_viewer_keys": WITHHELD,
        "source_pages": EXPECTED_TOTAL,
        "book_page_records": dict(sorted(book_records.items())),
        "unique_page_key_hashes": len(union_hashes),
        "sqlite_page_rows": sqlite_records,
        "fts_rows": fts_records,
        "qc_page_records": qc_records,
        "source_gaps_in_admitted_canonical_objects": 0,
        "aliases_for_withheld_identities": 0,
        "products": sorted(
            product_hashes,
            key=lambda x: (x["viewer_key"], x["class"], x["name"]),
        ),
        "archival_complete": False,
        "text_verified": False,
        "semantic_ready": False,
        "epistemic_guards": [
            "computationally_validated != archival_complete",
            "ocr_available != text_verified",
            "corpus_ready != semantic_ready",
            "source_alias_requires_full_sequence_byte_identity",
            "retained_source_identity != alias_candidate",
            "dma_2018 != dma_2019_without_documentary_or_cryptographic_proof",
            "search_hit != historical_claim",
            "zero_hits != demonstrated_absence",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(
        {
            "status": "ok",
            "books": EXPECTED_CANONICAL,
            "aliases": EXPECTED_ALIASES,
            "withheld": EXPECTED_WITHHELD,
            "pages": EXPECTED_TOTAL,
            "output": str(args.output),
        },
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
