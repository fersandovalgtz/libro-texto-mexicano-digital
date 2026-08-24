#!/usr/bin/env python3
"""Normalize versioned W3 Español/Lengua source topology for generic FTRL."""
from __future__ import annotations

import argparse, csv, re
from pathlib import Path

VERSION="LTMD_U1_W3_FTRL_INPUTS_0.1"
EXPECTED_HISTORICAL=130
EXPECTED_CANONICAL=114
EXPECTED_ALIASES=16
EXPECTED_PAGES=20765
SHA=re.compile(r"^[0-9a-f]{64}$")
PROCESSING=Path("data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv")
MANIFEST=Path("data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv")

def read(path):
    with path.open(encoding="utf-8",newline="") as fh: return list(csv.DictReader(fh))

def n(row,key):
    v=row.get(key,"")
    if v in {"",None}: raise AssertionError(f"missing {key}: {row}")
    return int(float(v))

def write(path, rows, fields):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--asset-output",default="local/ftrl/ltmd_u1_w3_asset_manifest.csv")
    ap.add_argument("--processing-output",default="local/ftrl/ltmd_u1_w3_processing_inventory.csv")
    a=ap.parse_args()
    processing=read(PROCESSING); manifest=read(MANIFEST)
    assert len(processing)==EXPECTED_HISTORICAL
    by={r["viewer_key"]:r for r in processing}; assert len(by)==EXPECTED_HISTORICAL
    canonical={r["viewer_key"] for r in processing if n(r,"is_canonical_processing_object")==1}
    assert len(canonical)==EXPECTED_CANONICAL and len(processing)-len(canonical)==EXPECTED_ALIASES
    assert all(n(r,"ocr_identity_eligible")==1 for r in processing)

    pfields=["processing_version","viewer_key","catalog_generation","grade_code","title_core","processing_mode","canonical_processing_viewer_key","technical_identity_covered","is_canonical_processing_object","declared_positions","direct_source_jpegs","persistent_internal_source_gaps","source_processing_basis","interpretive_limit"]
    pout=[]
    for r in processing:
        target=r["canonical_processing_viewer_key"]; assert target in canonical
        pout.append({"processing_version":VERSION,"viewer_key":r["viewer_key"],"catalog_generation":n(r,"catalog_generation"),"grade_code":n(r,"grade_code"),"title_core":r["title_core"],"processing_mode":r["processing_mode"],"canonical_processing_viewer_key":target,"technical_identity_covered":1,"is_canonical_processing_object":n(r,"is_canonical_processing_object"),"declared_positions":n(r,"declared_positions"),"direct_source_jpegs":n(r,"direct_source_jpegs"),"persistent_internal_source_gaps":n(r,"persistent_internal_source_gaps"),"source_processing_basis":r["evidence_basis"],"interpretive_limit":r["interpretive_limit"]})

    assert len(manifest)==EXPECTED_PAGES and {r["viewer_key"] for r in manifest}==canonical
    afields=["audit_version","viewer_key","catalog_generation","grade_code","title_core","viewer_page","source_image_index","source_asset_url","asset_status","byte_size","sha256","processing_mode","source_provenance"]
    aout=[]; seen=set()
    for r in manifest:
        key=(r["viewer_key"],n(r,"source_image_index")); assert key not in seen; seen.add(key)
        assert r["asset_status"]=="source_jpeg" and n(r,"byte_size")>0 and SHA.fullmatch(r["sha256"])
        aout.append({"audit_version":VERSION,"viewer_key":r["viewer_key"],"catalog_generation":n(r,"catalog_generation"),"grade_code":n(r,"grade_code"),"title_core":r["title_core"],"viewer_page":n(r,"viewer_page"),"source_image_index":n(r,"source_image_index"),"source_asset_url":r["source_asset_url"],"asset_status":"source_jpeg","byte_size":n(r,"byte_size"),"sha256":r["sha256"],"processing_mode":by[r["viewer_key"]]["processing_mode"],"source_provenance":r["source_provenance"]})

    write(Path(a.processing_output),pout,pfields); write(Path(a.asset_output),aout,afields)
    print(f"Built W3 FTRL inputs: historical={len(pout)}, canonical={len(canonical)}, aliases={EXPECTED_ALIASES}, pages={len(aout)}")

if __name__=="__main__": main()
