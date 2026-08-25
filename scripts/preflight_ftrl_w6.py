#!/usr/bin/env python3
"""Text-free preflight for exhaustive LTMD-U1 W6 Geografía/Atlas."""
from __future__ import annotations

import argparse, csv, hashlib, json, re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "LTMD_FTRL_W6_PREFLIGHT_0.1"
EXPECTED_HISTORICAL = 42
EXPECTED_CANONICAL = 37
EXPECTED_ALIASES = 5
EXPECTED_PAGES = 5258
EXPECTED_RECOVERED = 2
EXPECTED_TERMINAL = 36
SHA = re.compile(r"^[0-9a-f]{64}$")

P = {
    "scope": Path("data/catalog/ltmd_u1_w6_scope.csv"),
    "processing": Path("data/catalog/ltmd_u1_w6_geography_atlas_processing_inventory.csv"),
    "manifest": Path("data/catalog/ltmd_u1_w6_geography_atlas_canonical_page_manifest.csv"),
    "routes": Path("data/catalog/ltmd_u1_w6_geography_atlas_2018_2019_route_relationships.csv"),
    "recovery": Path("data/catalog/ltmd_u1_w6_h2008p4ge273_gap_recovery.csv"),
    "ocr_summary": Path("data/catalog/ltmd_u1_w6_geography_atlas_ocr_summary.csv"),
    "ocr_metrics": Path("data/catalog/ltmd_u1_w6_geography_atlas_ocr_metrics.csv"),
    "retained": Path("data/catalog/ltmd_u1_retained_source_register.csv"),
}

def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))

def n(row: dict[str, str], key: str) -> int:
    v = row.get(key, "")
    if v in {"", None}:
        raise AssertionError(f"missing {key}: {row}")
    return int(float(v))

def fp(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def source_index(url: str) -> int:
    stem = Path(urlparse(url).path).stem
    if not stem.isdigit():
        raise AssertionError(f"non-numeric W6 source image index: {url}")
    return int(stem)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="local/ftrl/ltmd_u1_w6_preflight.json")
    a = ap.parse_args()

    scope = rows(P["scope"]); processing = rows(P["processing"]); manifest = rows(P["manifest"])
    routes = rows(P["routes"]); recovery = rows(P["recovery"])
    ocrs = rows(P["ocr_summary"]); ocrm = rows(P["ocr_metrics"]); retained = rows(P["retained"])

    keys = {r["viewer_key"] for r in scope}
    assert len(scope) == len(keys) == EXPECTED_HISTORICAL
    assert {r.get("operational_domain") for r in scope} == {"geografia_atlas"}

    by = {r["viewer_key"]: r for r in processing}
    assert len(processing) == len(by) == EXPECTED_HISTORICAL and set(by) == keys
    assert all(n(r, "technical_identity_covered") == 1 for r in processing)
    assert all(n(r, "persistent_source_gaps") == 0 for r in processing)
    modes = Counter(r["processing_mode"] for r in processing)
    assert modes == {"direct_canonical": 36, "route_alias_to_2019": 5, "direct_canonical_reconciled_gap": 1}, modes

    canonical = {r["viewer_key"] for r in processing if n(r, "is_canonical_processing_object") == 1}
    aliases = set(by) - canonical
    assert len(canonical) == EXPECTED_CANONICAL and len(aliases) == EXPECTED_ALIASES
    for key, r in by.items():
        target = r["canonical_processing_viewer_key"]
        assert target in canonical
        assert (target == key) == (key in canonical)

    assert len(routes) == EXPECTED_ALIASES
    for r in routes:
        alias, target = r["viewer_key_2018"], r["canonical_processing_viewer_key"]
        assert alias in aliases and target in canonical
        assert by[alias]["processing_mode"] == "route_alias_to_2019"
        assert n(r, "complete_route_resolution") == 1
        compared = n(r, "compared_source_assets")
        assert n(r, "sha256_matches") == compared and n(r, "byte_size_matches") == compared

    assert len(recovery) == EXPECTED_RECOVERED
    assert {n(r, "viewer_page") for r in recovery} == {70, 117}
    for r in recovery:
        assert r["viewer_key"] == "H2008P4GE273"
        assert n(r, "candidate_live_verified") == 1
        assert r["recovery_status"] == "cryptographically_recovered_same_position_reference"
        assert SHA.fullmatch(r["effective_sha256"])
        assert n(r, "effective_byte_size") > 0

    assert len(manifest) == EXPECTED_PAGES and {r["viewer_key"] for r in manifest} == canonical
    seen = set(); recovered = 0
    for r in manifest:
        idx = source_index(r["source_asset_url"])
        key = (r["viewer_key"], idx)
        assert key not in seen; seen.add(key)
        assert n(r, "byte_size") > 0 and SHA.fullmatch(r["sha256"])
        assert r["source_kind"] in {"direct_source_jpeg", "cryptographically_recovered_same_position_reference"}
        if r["source_kind"] == "cryptographically_recovered_same_position_reference":
            recovered += 1
            assert r["viewer_key"] == "H2008P4GE273" and r["recovery_reference_viewer_key"] == "H1993P4GE196"
    assert recovered == EXPECTED_RECOVERED and len(seen) == EXPECTED_PAGES

    assert sum(n(r, "terminal_synthetic_candidates") for r in processing if n(r, "is_canonical_processing_object") == 1) == EXPECTED_TERMINAL
    assert not [r for r in retained if r.get("viewer_key") in keys]

    assert len(ocrs) == EXPECTED_CANONICAL and {r["viewer_key"] for r in ocrs} == canonical
    assert sum(n(r, "pages") for r in ocrs) == EXPECTED_PAGES
    assert sum(n(r, "sha_verified") for r in ocrs) == EXPECTED_PAGES
    assert sum(n(r, "unresolved") for r in ocrs) == 0
    assert len(ocrm) == EXPECTED_PAGES
    assert sum(n(r, "source_sha256_verified") for r in ocrm) == EXPECTED_PAGES

    out = {
        "schema": SCHEMA,
        "status": "ready_for_ftrl_runtime",
        "wave": "W6",
        "operational_domain": "geografia_atlas",
        "historical_identities": EXPECTED_HISTORICAL,
        "canonical_processing_objects": EXPECTED_CANONICAL,
        "alias_identities": EXPECTED_ALIASES,
        "route_aliases_2018_to_2019": EXPECTED_ALIASES,
        "canonical_source_pages": EXPECTED_PAGES,
        "cryptographically_recovered_pages": EXPECTED_RECOVERED,
        "persistent_source_gaps": 0,
        "terminal_synthetic_candidates": EXPECTED_TERMINAL,
        "identity_level_active_retentions": 0,
        "prior_ocr_anchor": {
            "canonical_objects": EXPECTED_CANONICAL,
            "pages": EXPECTED_PAGES,
            "sha_verified_pages": EXPECTED_PAGES,
            "unresolved_pages": 0,
            "interpretation": "technical_anchor_only_not_ftrl_completion; metrics do not retain page OCR text",
        },
        "ftrl_runtime_activated": False,
        "corpus_ready": False,
        "ocr_available_ftrl": False,
        "text_verified": False,
        "semantic_ready": False,
        "source_fingerprints": {
            "processing_inventory_canonical_sha256": fp(processing),
            "canonical_page_manifest_canonical_sha256": fp(manifest),
            "route_relationships_canonical_sha256": fp(routes),
            "gap_recovery_canonical_sha256": fp(recovery),
        },
        "epistemic_guards": [
            "preflight_ready != ftrl_validated",
            "prior_ocr_anchor != ftrl_validated",
            "ocr_available != text_verified",
            "corpus_ready != semantic_ready",
            "search_hit != historical_claim",
            "zero_hits != demonstrated_absence",
        ],
    }
    p = Path(a.output); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
