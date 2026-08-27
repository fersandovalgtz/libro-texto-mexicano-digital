#!/usr/bin/env python3
"""Validate exact union of the four W9 FTRL book-unit evidences."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED = {
    "H2008P1ED252": 114,
    "H2008P2ED260": 106,
    "H2008P5ED280": 114,
    "H2008P6ED287": 114,
}
EXPECTED_TOTAL = sum(EXPECTED.values())
SCHEMA = "LTMD_FTRL_W9_GLOBAL_EVIDENCE_0.1"


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
    assert len(proc) == 4
    assert {r["viewer_key"] for r in proc} == set(EXPECTED)
    assert all(r["technical_identity_covered"] == "1" and r["is_canonical_processing_object"] == "1" for r in proc)
    assert len(assets) == EXPECTED_TOTAL
    counts = Counter(r["viewer_key"] for r in assets)
    assert dict(counts) == EXPECTED

    expected_hashes = {
        page_key_hash(r["viewer_key"], int(r["source_image_index"]))
        for r in assets
    }
    assert len(expected_hashes) == EXPECTED_TOTAL

    evidence_files = sorted(args.evidence_root.rglob("w9_*_evidence.json"))
    if len(evidence_files) != 4:
        raise SystemExit(f"expected 4 W9 evidence files, found {len(evidence_files)}")

    seen_viewers: set[str] = set()
    union_hashes: set[str] = set()
    book_records: dict[str, int] = {}
    qc_records = 0
    sqlite_records = 0
    fts_records = 0
    product_hashes: list[dict[str, object]] = []

    for path in evidence_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema"] == "LTMD_FTRL_W9_BOOK_UNIT_0.1"
        assert data["status"] == "validated"
        assert data["wave"] == "W9"
        viewer = data["viewer_key"]
        assert viewer in EXPECTED and viewer not in seen_viewers
        seen_viewers.add(viewer)
        pages = int(data["page_records"])
        assert pages == EXPECTED[viewer]
        hashes = list(data["page_key_hashes"])
        assert len(hashes) == pages == len(set(hashes))
        assert not (union_hashes & set(hashes))
        union_hashes.update(hashes)
        validation = data["validation"]
        assert validation["sqlite_integrity"] == "ok"
        assert int(validation["sqlite_pages"]) == pages
        assert int(validation["fts_rows"]) == pages
        assert int(validation["qc_page_records"]) == pages
        sqlite_records += int(validation["sqlite_pages"])
        fts_records += int(validation["fts_rows"])
        qc_records += int(validation["qc_page_records"])
        book_records[viewer] = pages
        for group in ("restricted_products", "text_free_products"):
            for item in data[group]:
                assert len(item["sha256"]) == 64 and int(item["bytes"]) > 0
                product_hashes.append({"viewer_key": viewer, "class": group, "name": item["name"], "bytes": item["bytes"], "sha256": item["sha256"]})

    assert seen_viewers == set(EXPECTED)
    assert union_hashes == expected_hashes
    assert len(union_hashes) == EXPECTED_TOTAL
    assert sqlite_records == fts_records == qc_records == EXPECTED_TOTAL

    out = {
        "schema": SCHEMA,
        "status": "validated",
        "wave": "W9",
        "domain": "Educación Física",
        "historical_identities": 4,
        "canonical_processing_objects": 4,
        "source_pages": EXPECTED_TOTAL,
        "book_page_records": dict(sorted(book_records.items())),
        "unique_page_key_hashes": len(union_hashes),
        "sqlite_page_rows": sqlite_records,
        "fts_rows": fts_records,
        "qc_page_records": qc_records,
        "source_gaps": 0,
        "aliases": 0,
        "products": sorted(product_hashes, key=lambda x: (x["viewer_key"], x["class"], x["name"])),
        "archival_complete": False,
        "text_verified": False,
        "semantic_ready": False,
        "epistemic_guards": ["computationally_validated != archival_complete", "ocr_available != text_verified", "corpus_ready != semantic_ready", "search_hit != historical_claim", "zero_hits != demonstrated_absence"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "books": 4, "pages": EXPECTED_TOTAL, "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
