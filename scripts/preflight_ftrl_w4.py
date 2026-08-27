#!/usr/bin/env python3
"""Text-free preflight for exhaustive LTMD-U1 W4 Ciencias Sociales."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "LTMD_FTRL_W4_PREFLIGHT_0.1"
EXPECTED_HISTORICAL = 14
EXPECTED_CANONICAL = 14
EXPECTED_PAGES = 2414
EXPECTED_TERMINAL = 14
SHA = re.compile(r"^[0-9a-f]{64}$")

SCOPE = Path("data/catalog/ltmd_u1_w4_scope.csv")
PROCESSING = Path("data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv")
MANIFEST = Path("data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv")
RETAINED = Path("data/catalog/ltmd_u1_retained_source_register.csv")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def n(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value in {"", None}:
        raise AssertionError(f"missing {key}: {row}")
    return int(float(value))


def fingerprint(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="local/ftrl/ltmd_u1_w4_preflight.json")
    args = ap.parse_args()

    scope = rows(SCOPE)
    processing = rows(PROCESSING)
    manifest = rows(MANIFEST)
    retained = rows(RETAINED)

    keys = {r["viewer_key"] for r in scope}
    assert len(scope) == len(keys) == EXPECTED_HISTORICAL
    assert {r["operational_domain"] for r in scope} == {"ciencias_sociales"}

    by = {r["viewer_key"]: r for r in processing}
    assert len(processing) == len(by) == EXPECTED_HISTORICAL
    assert set(by) == keys
    assert all(n(r, "ocr_identity_eligible") == 1 for r in processing)
    assert all(n(r, "is_canonical_processing_object") == 1 for r in processing)
    assert all(r["processing_mode"] == "direct_canonical" for r in processing)
    assert all(r["canonical_processing_viewer_key"] == r["viewer_key"] for r in processing)
    assert all(n(r, "persistent_internal_source_gaps") == 0 for r in processing)
    assert sum(n(r, "terminal_synthetic_candidates") for r in processing) == EXPECTED_TERMINAL
    assert sum(n(r, "direct_source_jpegs") for r in processing) == EXPECTED_PAGES

    assert len(manifest) == EXPECTED_PAGES
    assert {r["viewer_key"] for r in manifest} == keys
    seen = set()
    for r in manifest:
        key = (r["viewer_key"], int(r["source_image_index"]))
        assert key not in seen
        seen.add(key)
        assert r["asset_status"] == "source_jpeg"
        assert int(r["byte_size"]) > 0
        assert SHA.fullmatch(r["sha256"])
    assert len(seen) == EXPECTED_PAGES
    assert not [r for r in retained if r.get("viewer_key") in keys]

    payload = {
        "schema": SCHEMA,
        "status": "ready_for_ftrl_runtime",
        "wave": "W4",
        "operational_domain": "ciencias_sociales",
        "historical_identities": EXPECTED_HISTORICAL,
        "canonical_processing_objects": EXPECTED_CANONICAL,
        "alias_identities": 0,
        "canonical_source_pages": EXPECTED_PAGES,
        "persistent_source_gaps": 0,
        "terminal_synthetic_candidates": EXPECTED_TERMINAL,
        "identity_level_active_retentions": 0,
        "ftrl_runtime_activated": False,
        "corpus_ready": False,
        "ocr_available_ftrl": False,
        "text_verified": False,
        "semantic_ready": False,
        "source_fingerprints": {
            "processing_inventory_canonical_sha256": fingerprint(processing),
            "canonical_page_manifest_canonical_sha256": fingerprint(manifest),
        },
        "epistemic_guards": [
            "preflight_ready != ftrl_validated",
            "ocr_available != text_verified",
            "corpus_ready != semantic_ready",
            "search_hit != historical_claim",
            "zero_hits != demonstrated_absence",
        ],
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
