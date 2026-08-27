#!/usr/bin/env python3
"""Promote LTMD-U1 completion ledger 0.4 to 0.5 after verified W4 closure.

Metadata-only promotion. It consumes the canonical 0.4 ledger, the versioned
W4 processing inventory, and public text-free archival-closure evidence. It
never reads or emits OCR text, private Drive identifiers, or key material.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

W4_PROCESSING = Path("data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv")
W4_CLOSURE = Path("data/research/ltmd_u1_w4_archival_closure.json")
DEFAULT_LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
DEFAULT_SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
OLD_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.4"
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.5"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.5"
W4_RUN = "33033136922"
W4_COMMIT = "455e0f21434162c4b77a0b5d52269b65512c486d"
W4_ARCHIVE = "LTMD-U1 — corpus FTRL privado/W4 — Ciencias Sociales/run_33033136922__455e0f2__2026-08-26/02_CONSOLIDATED_PRIVATE"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def no_private_locator(value) -> None:
    if isinstance(value, dict):
        forbidden = {"drive_id", "file_id", "folder_id", "drive_url", "private_url"}
        if forbidden & set(value):
            raise AssertionError(f"public W4 closure exposes private locator: {forbidden & set(value)}")
        for child in value.values(): no_private_locator(child)
    elif isinstance(value, list):
        for child in value: no_private_locator(child)
    elif isinstance(value, str):
        if "drive.google.com" in value or "docs.google.com" in value or "BEGIN PRIVATE KEY" in value:
            raise AssertionError("public W4 closure exposes forbidden private material")


def validate_closure(p: dict) -> None:
    assert p["schema"] == "LTMD_FTRL_ARCHIVAL_CLOSURE_0.5"
    assert p["wave"] == "W4" and p["archival_complete"] is True
    assert p["ftrl"] == {
        "canonical_processing_objects": 14,
        "commit": W4_COMMIT,
        "distributed_shards": 8,
        "fts_rows": 2414,
        "global_exact_union": True,
        "historical_identities": 14,
        "page_partition_complete": True,
        "page_partition_unique": True,
        "page_records": 2414,
        "run_id": W4_RUN,
        "sqlite_integrity": "ok",
        "status": "validated",
    }
    a = p["persistent_archive"]
    assert a["destination_shared"] is False
    assert a["encrypted_handoffs_preserved"] is True and a["encrypted_handoffs_unique"] == 8
    assert a["private_consolidation_validated"] is True
    assert a["archive_closure_record_preserved"] is True
    assert a["redownload_checksum_verification_complete"] is True
    assert a["restricted_plaintext_publicly_exposed"] is False
    assert a["text_free_evidence_preserved"] is True
    assert a["consolidated_archive_bytes"] == 4945342
    assert a["consolidated_archive_sha256"] == "1a6546354f94259ffbc3bb8233c405138f01316cfc188a80786af9d7238761d8"
    assert p["qc"]["page_records"] == 2414
    assert p["qc"]["pages_flagged_for_technical_review"] + p["qc"]["pages_unflagged"] == 2414
    assert p["security"]["plaintext_restricted_outputs_published"] is False
    assert p["text_verified"] is False and p["semantic_ready"] is False
    no_private_locator(p)


def validate_processing(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    assert len(rows) == 14 and len({r["viewer_key"] for r in rows}) == 14
    assert all(r["processing_mode"] == "direct_canonical" for r in rows)
    assert sum(r["is_canonical_processing_object"] == "1" for r in rows) == 14
    assert sum(int(r["persistent_internal_source_gaps"]) for r in rows) == 0
    assert sum(int(r["direct_source_jpegs"]) for r in rows) == 2414
    assert all(r["canonical_processing_viewer_key"] == r["viewer_key"] for r in rows)
    return {r["viewer_key"]: r for r in rows}


def validate_base(rows: list[dict[str, str]]) -> set[str]:
    assert len(rows) == 542 and len({r["viewer_key"] for r in rows}) == 542
    versions = {r["ledger_version"] for r in rows}
    assert versions in ({OLD_VERSION}, {VERSION})
    for wave, count in (("W1",40),("W3",130),("W5",18),("W6",42)):
        wr=[r for r in rows if r["wave"]==wave]
        assert len(wr)==count
        assert Counter(r["ftrl_status"] for r in wr)==Counter({"validated":count})
        assert Counter(r["archival_status"] for r in wr)==Counter({"archival_complete":count})
    w4=[r for r in rows if r["wave"]=="W4"]
    assert len(w4)==14
    if versions == {OLD_VERSION}:
        assert Counter(r["ftrl_status"] for r in w4)==Counter({"pending":14})
        assert Counter(r["archival_status"] for r in w4)==Counter({"not_started":14})
    return versions


def promote(rows: list[dict[str,str]], by: dict[str,dict[str,str]]) -> list[dict[str,str]]:
    out=[]
    for original in rows:
        row=dict(original); row["ledger_version"]=VERSION
        if row["wave"]=="W4":
            p=by[row["viewer_key"]]
            assert row["documentary_disposition"]=="required_ftrl_processing"
            row["source_ready"]="full"
            row["relation_type"]="direct_canonical"
            row["canonical_processing_viewer_key"]=p["canonical_processing_viewer_key"]
            row["is_canonical_processing_object"]="1"
            row["declared_positions"]=p["declared_positions"]
            row["canonical_source_pages"]=p["direct_source_jpegs"]
            row["persistent_unresolved_source_gaps"]="0"
            row["ftrl_status"]="validated"
            row["ftrl_run_id"]=W4_RUN; row["ftrl_commit"]=W4_COMMIT
            row["corpus_ready"]="1"; row["ocr_available"]="1"
            row["text_verified"]="0"; row["semantic_ready"]="0"
            row["archival_status"]="archival_complete"
            row["preservation_run_id"]="private_consolidation_2026-08-27"
            row["archive_destination_logical"]=W4_ARCHIVE
            row["interpretive_limit"]="Computational/archival closure only; OCR is not human text verification or semantic evidence."
        out.append(row)
    assert {r["viewer_key"] for r in out if r["wave"]=="W4"}==set(by)
    return out


def build_summary(rows: list[dict[str,str]]) -> dict:
    dispositions=Counter(r["documentary_disposition"] for r in rows)
    assert dispositions==Counter({"required_ftrl_processing":524,"active_retention":13,"final_exception":5})
    waves=Counter(r["wave"] for r in rows)
    assert waves==Counter({"W1":40,"W2":64,"W3":130,"W4":14,"W5":18,"W6":42,"W7":30,"W8":20,"W9":4,"W10":69,"W11":111})
    w4=[r for r in rows if r["wave"]=="W4"]
    assert Counter(r["ftrl_status"] for r in w4)==Counter({"validated":14})
    assert Counter(r["archival_status"] for r in w4)==Counter({"archival_complete":14})
    assert Counter(r["source_ready"] for r in w4)==Counter({"full":14})
    assert Counter(r["relation_type"] for r in w4)==Counter({"direct_canonical":14})
    assert sum(r["is_canonical_processing_object"]=="1" for r in w4)==14
    assert sum(int(r["canonical_source_pages"] or 0) for r in w4)==2414
    assert sum(int(r["persistent_unresolved_source_gaps"] or 0) for r in w4)==0
    canonical=Counter(); pages=Counter()
    for r in rows:
        if r["is_canonical_processing_object"]=="1":
            canonical[r["ftrl_status"]]+=1
            if r["canonical_source_pages"]: pages[r["ftrl_status"]]+=int(r["canonical_source_pages"])
    ftrl=Counter(r["ftrl_status"] for r in rows); archival=Counter(r["archival_status"] for r in rows)
    validated=ftrl["validated"]; terminal=validated+dispositions["final_exception"]
    remaining=len(rows)-terminal; pending=ftrl["pending"]
    assert validated==244 and terminal==249 and remaining==293 and pending==280
    assert canonical==Counter({"validated":216})
    assert pages==Counter({"validated":37606})
    assert archival==Counter({"not_started":293,"archival_complete":244,"not_applicable_final_exception":5})
    return {
      "schema":SUMMARY_SCHEMA,"ledger_version":VERSION,"status":"valid","documentary_identities":len(rows),
      "wave_denominators":dict(sorted(waves.items())),"documentary_dispositions":dict(sorted(dispositions.items())),
      "source_readiness":dict(sorted(Counter(r["source_ready"] for r in rows).items())),
      "known_processing_topology_identities":sum(bool(r["canonical_processing_viewer_key"]) for r in rows),
      "ftrl_identity_status":dict(sorted(ftrl.items())),
      "canonical_processing_objects_by_ftrl_status":dict(sorted(canonical.items())),
      "canonical_source_pages_by_ftrl_status":dict(sorted(pages.items())),
      "corpus_ready_identities":sum(int(r["corpus_ready"]) for r in rows),
      "ocr_available_identities":sum(int(r["ocr_available"]) for r in rows),
      "text_verified_identities":sum(int(r["text_verified"]) for r in rows),
      "semantic_ready_identities":sum(int(r["semantic_ready"]) for r in rows),
      "archival_status":dict(sorted(archival.items())),
      "strict_identity_progress":{"terminal_identities":terminal,"terminal_fraction":round(terminal/len(rows),6),"remaining_identities":remaining,"remaining_fraction":round(remaining/len(rows),6),"processable_pending":pending,"active_retentions":13,"definition":"validated FTRL identities plus documented final exceptions over the fixed 542-identity denominator"},
      "global_closure":{"eligible":False,"reason":"active retentions and unfinished FTRL waves remain; archival completion is incomplete outside validated waves","active_retentions":13,"final_exceptions":5},
      "epistemic_guards":["topology_ready != corpus_ready","preflight_ready != ftrl_validated","corpus_ready != semantic_ready","ocr_available != text_verified","search_hit != historical_claim","zero_hits != demonstrated_absence","computationally_validated != archival_complete"]
    }


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,default=DEFAULT_LEDGER); ap.add_argument("--output",type=Path,default=DEFAULT_LEDGER); ap.add_argument("--summary-output",type=Path,default=DEFAULT_SUMMARY); args=ap.parse_args()
    validate_closure(json.loads(W4_CLOSURE.read_text(encoding="utf-8")))
    by=validate_processing(read_csv(W4_PROCESSING)); rows=read_csv(args.input); validate_base(rows)
    rows=promote(rows,by); summary=build_summary(rows); write_csv(args.output,rows)
    args.summary_output.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))

if __name__ == "__main__": main()
