#!/usr/bin/env python3
"""Text-free preflight for exhaustive LTMD-U1 W3 Español/Lengua."""
from __future__ import annotations

import argparse, csv, hashlib, json, re
from collections import Counter
from pathlib import Path

SCHEMA = "LTMD_FTRL_W3_PREFLIGHT_0.1"
EXPECTED_HISTORICAL = 130
EXPECTED_CANONICAL = 114
EXPECTED_ALIASES = 16
EXPECTED_EXACT = 8
EXPECTED_ROUTE = 8
EXPECTED_PAGES = 20765
EXPECTED_GAPS = 8
EXPECTED_PARTIAL = 7
EXPECTED_TERMINAL = 109
SHA = re.compile(r"^[0-9a-f]{64}$")

P = {
    "coverage": Path("data/catalog/ltmd_u1_coverage.csv"),
    "processing": Path("data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv"),
    "asset_summary": Path("data/catalog/ltmd_u1_w3_spanish_asset_summary.csv"),
    "manifest": Path("data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv"),
    "gaps": Path("data/catalog/ltmd_u1_w3_spanish_canonical_gap_manifest.csv"),
    "exact": Path("data/catalog/ltmd_u1_w3_spanish_exact_aliases.csv"),
    "routes": Path("data/catalog/ltmd_u1_w3_spanish_2018_2019_route_relationships.csv"),
    "ocr_summary": Path("data/catalog/ltmd_u1_w3_spanish_ocr_summary.csv"),
    "ocr_metrics": Path("data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv"),
    "retained": Path("data/catalog/ltmd_u1_retained_source_register.csv"),
}

def rows(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))

def n(row, key):
    v = row.get(key, "")
    if v in {"", None}: raise AssertionError(f"missing {key}: {row}")
    return int(float(v))

def fp(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="local/ftrl/ltmd_u1_w3_preflight.json")
    a = ap.parse_args()

    coverage = [r for r in rows(P["coverage"]) if r.get("operational_domain") == "espanol_lengua"]
    processing = rows(P["processing"]); summary = rows(P["asset_summary"])
    manifest = rows(P["manifest"]); gaps = rows(P["gaps"])
    exact = rows(P["exact"]); routes = rows(P["routes"])
    ocrs = rows(P["ocr_summary"]); ocrm = rows(P["ocr_metrics"])
    retained = rows(P["retained"])

    keys = {r["viewer_key"] for r in coverage}
    assert len(coverage) == len(keys) == EXPECTED_HISTORICAL
    by = {r["viewer_key"]: r for r in processing}
    assert len(processing) == len(by) == EXPECTED_HISTORICAL and set(by) == keys
    assert sum(n(r,"ocr_identity_eligible") for r in processing) == EXPECTED_HISTORICAL
    assert all(not (r.get("block_reason") or "").strip() for r in processing)

    modes = Counter(r["processing_mode"] for r in processing)
    assert modes == {"direct_canonical":107,"partial_canonical_explicit_gap":7,"exact_byte_alias":8,"paired_route_alias_2018_to_2019":8}, modes
    canonical = {r["viewer_key"] for r in processing if n(r,"is_canonical_processing_object") == 1}
    aliases = set(by) - canonical
    assert len(canonical) == EXPECTED_CANONICAL and len(aliases) == EXPECTED_ALIASES
    assert len({by[k]["canonical_processing_viewer_key"] for k in by}) == EXPECTED_CANONICAL
    for k,r in by.items():
        target = r["canonical_processing_viewer_key"]
        assert target in canonical
        assert (target == k) == (k in canonical)

    assert not [r for r in retained if r.get("viewer_key") in keys]
    sb = {r["viewer_key"]:r for r in summary}; assert set(sb) == keys
    cs = [sb[k] for k in canonical]
    assert sum(n(r,"source_jpegs") for r in cs) == EXPECTED_PAGES
    assert sum(n(r,"terminal_synthetic_candidates") for r in cs) == EXPECTED_TERMINAL
    assert sum(n(r,"internal_unserved") for r in cs) == EXPECTED_GAPS
    assert sum(n(r,"probe_errors") for r in cs) == 0

    assert len(manifest) == EXPECTED_PAGES and {r["viewer_key"] for r in manifest} == canonical
    seen=set(); counts=Counter()
    for r in manifest:
        k=(r["viewer_key"],n(r,"viewer_page")); assert k not in seen; seen.add(k)
        counts[r["viewer_key"]]+=1
        assert r["asset_status"] == "source_jpeg" and n(r,"byte_size") > 0 and SHA.fullmatch(r["sha256"])
    for k in canonical: assert counts[k] == n(by[k],"direct_source_jpegs")

    assert len(gaps) == EXPECTED_GAPS
    gc=Counter(); gs=set()
    for r in gaps:
        k=(r["viewer_key"],n(r,"viewer_page")); assert k not in gs; gs.add(k)
        assert r["viewer_key"] in canonical and by[r["viewer_key"]]["processing_mode"] == "partial_canonical_explicit_gap"
        assert r["gap_state"] == "internal_unserved_position_observed" and n(r,"available_neighbours_sha_verified") == 1
        gc[r["viewer_key"]]+=1
    assert len(gc) == EXPECTED_PARTIAL
    for k in canonical: assert gc[k] == n(by[k],"persistent_internal_source_gaps")

    assert len(exact) == EXPECTED_EXACT
    for r in exact:
        alias,target=r["viewer_key"],r["canonical_viewer_key"]
        assert alias in aliases and target in canonical and by[alias]["canonical_processing_viewer_key"] == target
        assert by[alias]["processing_mode"] == "exact_byte_alias" and n(r,"all_pages_byte_identical_aligned") == 1
        assert n(r,"source_jpeg_count") == n(by[target],"direct_source_jpegs")

    assert len(routes) == EXPECTED_ROUTE
    for r in routes:
        alias,target=r["viewer_key_2018"],r["viewer_key_2019"]
        compared=n(r,"compared_source_assets")
        assert alias in aliases and target in canonical and by[alias]["canonical_processing_viewer_key"] == target
        assert by[alias]["processing_mode"] == "paired_route_alias_2018_to_2019"
        assert n(r,"complete_route_resolution") == 1 and n(r,"sha256_matches") == compared and n(r,"byte_size_matches") == compared
        assert compared == n(by[target],"direct_source_jpegs")

    assert len(ocrs) == EXPECTED_CANONICAL and {r["viewer_key"] for r in ocrs} == canonical
    assert sum(n(r,"pages") for r in ocrs) == EXPECTED_PAGES
    assert sum(n(r,"sha_verified") for r in ocrs) == EXPECTED_PAGES and sum(n(r,"unresolved") for r in ocrs) == 0
    assert len(ocrm) == EXPECTED_PAGES and sum(n(r,"source_sha256_verified") for r in ocrm) == EXPECTED_PAGES

    out = {
        "schema":SCHEMA,"status":"ready_for_ftrl_runtime_after_w1_gate","wave":"W3","operational_domain":"espanol_lengua",
        "historical_identities":130,"canonical_processing_objects":114,"alias_identities":16,"exact_byte_aliases":8,
        "paired_route_aliases_2018_to_2019":8,"canonical_source_pages":20765,"partial_canonical_objects":7,
        "documented_internal_source_gaps":8,"terminal_synthetic_candidates":109,"identity_level_active_retentions":0,
        "prior_ocr_anchor":{"canonical_objects":114,"pages":20765,"sha_verified_pages":20765,"unresolved_pages":0,"interpretation":"technical_anchor_only_not_ftrl_completion"},
        "ftrl_runtime_activated":False,"corpus_ready":False,"ocr_available_ftrl":False,"text_verified":False,"semantic_ready":False,
        "source_fingerprints":{"processing_inventory_canonical_sha256":fp(processing),"canonical_page_manifest_canonical_sha256":fp(manifest),"gap_manifest_canonical_sha256":fp(gaps),"exact_aliases_canonical_sha256":fp(exact),"route_relationships_canonical_sha256":fp(routes)},
        "epistemic_guards":["preflight_ready != corpus_ready","prior_ocr_anchor != ftrl_validated","ocr_available != text_verified","corpus_ready != semantic_ready","search_hit != historical_claim"]
    }
    p=Path(a.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))

if __name__ == "__main__": main()
