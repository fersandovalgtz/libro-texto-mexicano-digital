#!/usr/bin/env python3
"""Promote LTMD-U1 completion ledger 0.6 to 0.7 after verified W7 closure.

Metadata-only promotion. It consumes the canonical 0.6 ledger, the W7 source-
admissibility gate, public text-free global evidence, and public archival closure
evidence. It promotes only the 25 source-admitted identities. The five active
source retentions remain blocked and are never aliased or imputed. This script
never reads or emits OCR text, private Drive identifiers, or key material.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

W7_GATE = Path("data/catalog/ltmd_u1_w7_source_admissibility.csv")
W7_GLOBAL = Path("data/research/ltmd_u1_w7_global_evidence.json")
W7_CLOSURE = Path("data/research/ltmd_u1_w7_archival_closure.json")
DEFAULT_LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
DEFAULT_SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
OLD_VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.6"
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.7"
SUMMARY_SCHEMA = "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.7"
W7_RUN = "33207787127"
W7_COMMIT = "02024976ec3d87827460b8b610abe499d870db13"
W7_ARCHIVE = "LTMD-U1 — corpus FTRL privado/W7 — Formación Cívica y Ética/run_33207787127__0202497__2026-08-28/02_CONSOLIDATED_PRIVATE"
WITHHELD = {"H2014P5FCA","H2018P3FCA","H2018P4FCA","H2018P5FCA","H2018P6FCA"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def no_private_locator(value) -> None:
    if isinstance(value, dict):
        forbidden = {"drive_id","file_id","folder_id","drive_url","private_url","private_key"}
        assert not (forbidden & set(value)), f"public W7 evidence exposes private material: {forbidden & set(value)}"
        for child in value.values(): no_private_locator(child)
    elif isinstance(value, list):
        for child in value: no_private_locator(child)
    elif isinstance(value, str):
        lowered=value.lower()
        assert "drive.google.com" not in lowered and "docs.google.com" not in lowered and "begin private key" not in lowered


def validate_gate(rows: list[dict[str,str]]) -> tuple[dict[str,dict[str,str]], set[str]]:
    assert len(rows)==30 and len({r["viewer_key"] for r in rows})==30
    admitted=[r for r in rows if r["decision"]=="ocr_source_admitted"]
    withheld=[r for r in rows if r["decision"]!="ocr_source_admitted"]
    assert len(admitted)==25 and len(withheld)==5
    assert {r["viewer_key"] for r in withheld}==WITHHELD
    assert all(r["ocr_source_admitted"]=="1" and r["direct_asset_ready"]=="1" and int(r["internal_unserved"])==0 for r in admitted)
    assert all(r["ocr_source_admitted"]=="0" and r["direct_asset_ready"]=="0" for r in withheld)
    assert sum(int(r["source_jpegs"]) for r in admitted)==3261
    return {r["viewer_key"]:r for r in admitted}, WITHHELD


def validate_global(p: dict, admitted: dict[str,dict[str,str]]) -> dict[str,int]:
    assert p["schema"]=="LTMD_FTRL_W7_GLOBAL_EVIDENCE_0.1"
    assert p["wave"]=="W7" and p["status"]=="validated"
    assert p["historical_identities"]==30 and p["canonical_processing_objects"]==25
    assert p["withheld_source_identities"]==5 and p["source_pages"]==3261
    assert p["unique_page_key_hashes"]==3261
    assert p["sqlite_page_rows"]==3261 and p["fts_rows"]==3261 and p["qc_page_records"]==3261
    assert p["source_gaps_in_admitted_canonical_objects"]==0
    assert p["aliases_for_withheld_identities"]==0
    assert p["archival_complete"] is False
    assert p["text_verified"] is False and p["semantic_ready"] is False
    pages={k:int(v) for k,v in p["book_page_records"].items()}
    assert set(pages)==set(admitted) and sum(pages.values())==3261
    for viewer,row in admitted.items():
        assert pages[viewer]==int(row["source_jpegs"])
        assert int(row["declared_positions"])==pages[viewer]+1
    products=p["products"]
    assert len(products)==150
    assert Counter(x["viewer_key"] for x in products)==Counter({k:6 for k in admitted})
    assert Counter(x["class"] for x in products)==Counter({"restricted_products":75,"text_free_products":75})
    assert all(int(x["bytes"])>0 and len(x["sha256"])==64 for x in products)
    no_private_locator(p)
    return pages


def validate_closure(p: dict) -> None:
    assert p["schema"]=="LTMD_FTRL_ARCHIVAL_CLOSURE_0.7"
    assert p["wave"]=="W7" and p["archival_complete"] is True
    f=p["ftrl"]
    assert f["canonical_processing_objects"]==25 and f["historical_identities"]==30 and f["withheld_source_identities"]==5
    assert f["distributed_books"]==25 and f["page_records"]==3261 and f["fts_rows"]==3261
    assert f["run_id"]==W7_RUN and f["commit"]==W7_COMMIT and f["status"]=="validated"
    assert f["global_exact_union"] is True and f["page_partition_complete"] is True and f["page_partition_unique"] is True
    assert f["sqlite_integrity"]=="ok"
    a=p["persistent_archive"]
    assert a["destination_shared"] is False
    assert a["encrypted_handoffs_preserved"] is True and a["encrypted_handoffs_unique"]==25
    assert a["private_consolidation_validated"] is True and a["archive_closure_record_preserved"] is True
    assert a["redownload_checksum_verification_complete"] is True
    assert a["restricted_plaintext_publicly_exposed"] is False
    assert a["text_free_evidence_preserved"] is True and a["text_free_evidence_unique"]==26
    assert a["consolidated_archive_bytes"]==6666433
    assert a["consolidated_archive_sha256"]=="f81272e4a86e432dd27cf0d4c769f06f7561a31e22236af74554bb2d024bcbd9"
    assert a["logical_destination"]==W7_ARCHIVE
    q=p["qc"]
    assert q=={"page_records":3261,"pages_flagged_for_technical_review":428,"pages_unflagged":2833,"zero_search_text_pages":150}
    assert q["pages_flagged_for_technical_review"]+q["pages_unflagged"]==3261
    sr=p["source_retention"]
    assert sr["count"]==5 and set(sr["viewer_keys"])==WITHHELD and sr["aliases_introduced"]==0
    assert p["security"]["plaintext_restricted_outputs_published"] is False
    assert p["security"]["private_key_stored_outside_public_repository"] is True
    assert p["text_verified"] is False and p["semantic_ready"] is False
    no_private_locator(p)


def validate_base(rows: list[dict[str,str]], admitted:set[str]) -> set[str]:
    assert len(rows)==542 and len({r["viewer_key"] for r in rows})==542
    versions={r["ledger_version"] for r in rows}
    assert versions in ({OLD_VERSION},{VERSION})
    for wave,count in (("W1",40),("W3",130),("W4",14),("W5",18),("W6",42),("W9",4)):
        wr=[r for r in rows if r["wave"]==wave]
        assert len(wr)==count
        assert Counter(r["ftrl_status"] for r in wr)==Counter({"validated":count})
        assert Counter(r["archival_status"] for r in wr)==Counter({"archival_complete":count})
    w7=[r for r in rows if r["wave"]=="W7"]
    assert len(w7)==30 and {r["viewer_key"] for r in w7}==admitted|WITHHELD
    retained=[r for r in w7 if r["viewer_key"] in WITHHELD]
    assert all(r["documentary_disposition"]=="active_retention" for r in retained)
    assert all(r["ftrl_status"]=="blocked_active_retention" and r["archival_status"]=="not_started" for r in retained)
    assert all(r["is_canonical_processing_object"]=="0" and r["corpus_ready"]=="0" and r["ocr_available"]=="0" for r in retained)
    if versions=={OLD_VERSION}:
        proc=[r for r in w7 if r["viewer_key"] in admitted]
        assert all(r["ftrl_status"]=="pending" and r["archival_status"]=="not_started" for r in proc)
    else:
        proc=[r for r in w7 if r["viewer_key"] in admitted]
        assert all(r["ftrl_status"]=="validated" and r["archival_status"]=="archival_complete" for r in proc)
    return versions


def promote(rows:list[dict[str,str]], gate:dict[str,dict[str,str]], pages:dict[str,int]) -> list[dict[str,str]]:
    out=[]
    for original in rows:
        row=dict(original); row["ledger_version"]=VERSION
        viewer=row["viewer_key"]
        if viewer in gate:
            g=gate[viewer]
            assert row["wave"]=="W7" and row["documentary_disposition"]=="required_ftrl_processing"
            row["source_ready"]="full"
            row["relation_type"]="direct_canonical"
            row["canonical_processing_viewer_key"]=viewer
            row["is_canonical_processing_object"]="1"
            row["declared_positions"]=g["declared_positions"]
            row["canonical_source_pages"]=str(pages[viewer])
            row["persistent_unresolved_source_gaps"]="0"
            row["ftrl_status"]="validated"
            row["ftrl_run_id"]=W7_RUN
            row["ftrl_commit"]=W7_COMMIT
            row["corpus_ready"]="1"; row["ocr_available"]="1"
            row["text_verified"]="0"; row["semantic_ready"]="0"
            row["archival_status"]="archival_complete"
            row["preservation_run_id"]="private_consolidation_2026-08-28"
            row["archive_destination_logical"]=W7_ARCHIVE
            row["interpretive_limit"]="Computational/archival closure of source-admitted W7 only; retained identities remain excluded; OCR is not human text verification or semantic evidence."
        out.append(row)
    return out


def build_summary(rows:list[dict[str,str]]) -> dict:
    dispositions=Counter(r["documentary_disposition"] for r in rows)
    assert dispositions==Counter({"required_ftrl_processing":524,"active_retention":13,"final_exception":5})
    waves=Counter(r["wave"] for r in rows)
    assert waves==Counter({"W1":40,"W2":64,"W3":130,"W4":14,"W5":18,"W6":42,"W7":30,"W8":20,"W9":4,"W10":69,"W11":111})
    w7=[r for r in rows if r["wave"]=="W7"]
    assert Counter(r["ftrl_status"] for r in w7)==Counter({"validated":25,"blocked_active_retention":5})
    assert Counter(r["archival_status"] for r in w7)==Counter({"archival_complete":25,"not_started":5})
    assert sum(r["is_canonical_processing_object"]=="1" for r in w7)==25
    assert sum(int(r["canonical_source_pages"] or 0) for r in w7 if r["is_canonical_processing_object"]=="1")==3261
    assert sum(int(r["corpus_ready"]) for r in w7)==25 and sum(int(r["ocr_available"]) for r in w7)==25
    assert sum(int(r["text_verified"]) for r in w7)==0 and sum(int(r["semantic_ready"]) for r in w7)==0
    canonical=Counter(); pages=Counter()
    for r in rows:
        if r["is_canonical_processing_object"]=="1":
            canonical[r["ftrl_status"]]+=1
            if r["canonical_source_pages"]: pages[r["ftrl_status"]]+=int(r["canonical_source_pages"])
    ftrl=Counter(r["ftrl_status"] for r in rows); archival=Counter(r["archival_status"] for r in rows)
    validated=ftrl["validated"]; terminal=validated+dispositions["final_exception"]
    remaining=len(rows)-terminal; pending=ftrl["pending"]
    assert validated==273 and terminal==278 and remaining==264 and pending==251
    assert canonical==Counter({"validated":245}) and pages==Counter({"validated":41315})
    assert archival==Counter({"archival_complete":273,"not_applicable_final_exception":5,"not_started":264})
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


def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,default=DEFAULT_LEDGER); ap.add_argument("--output",type=Path,default=DEFAULT_LEDGER); ap.add_argument("--summary-output",type=Path,default=DEFAULT_SUMMARY); args=ap.parse_args()
    gate,_=validate_gate(read_csv(W7_GATE))
    global_evidence=json.loads(W7_GLOBAL.read_text(encoding="utf-8")); pages=validate_global(global_evidence,gate)
    validate_closure(json.loads(W7_CLOSURE.read_text(encoding="utf-8")))
    rows=read_csv(args.input); validate_base(rows,set(gate)); rows=promote(rows,gate,pages); summary=build_summary(rows)
    write_csv(args.output,rows); args.summary_output.write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,sort_keys=True))

if __name__=="__main__": main()
