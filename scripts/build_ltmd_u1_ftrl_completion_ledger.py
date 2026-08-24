#!/usr/bin/env python3
"""Build the exhaustive LTMD-U1 FTRL completion ledger (542 documentary identities).

The ledger is metadata-only. It never reads, emits, or infers OCR text.
It joins the frozen U1 documentary denominator with versioned FTRL processing
inventories, the retained-source register, and a small wave-state registry.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any

COVERAGE = Path("data/catalog/ltmd_u1_coverage.csv")
RETAINED = Path("data/catalog/ltmd_u1_retained_source_register.csv")
W5_PROCESSING = Path("data/catalog/ltmd_u1_w5_history_processing_inventory.csv")
W1_BUILDER = Path("scripts/build_ftrl_w1_inputs.py")
WAVE_STATE = Path("data/research/ltmd_u1_ftrl_wave_state.json")
DEFAULT_LEDGER = Path("data/research/ltmd_u1_ftrl_completion_ledger.csv")
DEFAULT_SUMMARY = Path("data/research/ltmd_u1_ftrl_completion_summary.json")
VERSION = "LTMD_U1_FTRL_COMPLETION_LEDGER_0.1"
EXPECTED_IDENTITIES = 542
EXPECTED_WAVES = {
    "W1": 40, "W2": 64, "W3": 130, "W4": 14, "W5": 18,
    "W6": 42, "W7": 30, "W8": 20, "W9": 4, "W10": 69, "W11": 111,
}
DOMAIN_TO_WAVE = {
    "ciencias_naturales": "W1", "matematicas": "W2",
    "espanol_lengua": "W3", "ciencias_sociales": "W4", "historia": "W5",
    "geografia_atlas": "W6", "civica_etica": "W7", "artes": "W8",
    "educacion_fisica": "W9", "integrados_multiarea": "W10",
    "otros_no_clasificados": "W11",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_w1_processing() -> list[dict[str, Any]]:
    spec = importlib.util.spec_from_file_location("ltmd_w1_builder", W1_BUILDER)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load W1 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.build_processing_rows(module.exhaustive_readiness())
    if len(rows) != 40:
        raise AssertionError(f"W1 processing denominator drift: {len(rows)} != 40")
    return rows


def source_state(row: dict[str, str]) -> str:
    if row.get("asset_resolved_full") == "1":
        return "full"
    if row.get("asset_resolved_partial") == "1":
        return "partial"
    return "unresolved"


def as_bool01(value: Any) -> int:
    return 1 if str(value) == "1" or value is True else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    coverage = read_csv(COVERAGE)
    if len(coverage) != EXPECTED_IDENTITIES:
        raise AssertionError(f"U1 denominator drift: {len(coverage)} != {EXPECTED_IDENTITIES}")
    by_viewer = {r["viewer_key"]: r for r in coverage}
    if len(by_viewer) != EXPECTED_IDENTITIES:
        raise AssertionError("duplicate viewer_key in U1 coverage")

    retained_rows = read_csv(RETAINED)
    retained = {r["viewer_key"]: r for r in retained_rows}
    if len(retained) != len(retained_rows):
        raise AssertionError("duplicate viewer_key in retained-source register")
    if not set(retained) <= set(by_viewer):
        raise AssertionError("retained-source register contains identities outside U1")
    retained_status = Counter(r["status"] for r in retained_rows)
    if retained_status != Counter({"active_retention": 13, "final_exception": 5}):
        raise AssertionError(f"retained-source disposition drift: {retained_status}")

    w1_rows = load_w1_processing()
    w5_rows = read_csv(W5_PROCESSING)
    if len(w5_rows) != 18:
        raise AssertionError(f"W5 processing denominator drift: {len(w5_rows)} != 18")
    processing: dict[str, dict[str, Any]] = {}
    for row in [*w1_rows, *w5_rows]:
        key = str(row["viewer_key"])
        if key in processing:
            raise AssertionError(f"duplicate FTRL processing identity: {key}")
        processing[key] = row
    if not set(processing) <= set(by_viewer):
        raise AssertionError("FTRL processing inventory contains identities outside U1")

    state = json.loads(WAVE_STATE.read_text(encoding="utf-8"))
    if state["schema"] != "LTMD_U1_FTRL_WAVE_STATE_0.1":
        raise AssertionError("unexpected FTRL wave-state schema")
    wave_state = state["waves"]
    if set(wave_state) != set(EXPECTED_WAVES):
        raise AssertionError("wave-state registry must cover W1-W11 exactly")

    rows: list[dict[str, Any]] = []
    for cov in coverage:
        viewer = cov["viewer_key"]
        domain = cov["operational_domain"]
        if domain not in DOMAIN_TO_WAVE:
            raise AssertionError(f"unknown operational_domain for {viewer}: {domain}")
        wave = DOMAIN_TO_WAVE[domain]
        ws = wave_state[wave]
        ret = retained.get(viewer)
        proc = processing.get(viewer)

        disposition = ret["status"] if ret else "required_ftrl_processing"
        if disposition == "active_retention":
            identity_ftrl_status = "blocked_active_retention"
        elif disposition == "final_exception":
            identity_ftrl_status = "final_exception"
        else:
            identity_ftrl_status = ws["ftrl_status"]

        if proc:
            canonical_key = str(proc.get("canonical_processing_viewer_key", ""))
            relation_type = str(proc.get("processing_mode", ""))
            canonical_object = as_bool01(proc.get("is_canonical_processing_object", 0))
            declared_positions = str(proc.get("declared_positions", ""))
            canonical_source_pages = str(proc.get("direct_source_jpegs", ""))
            unresolved_gaps = str(proc.get("persistent_unresolved_source_gaps", ""))
        else:
            canonical_key = ""
            relation_type = disposition if disposition != "required_ftrl_processing" else "pending_topology"
            canonical_object = 0
            declared_positions = ""
            canonical_source_pages = ""
            unresolved_gaps = ""

        corpus_ready = int(identity_ftrl_status == "validated" and disposition == "required_ftrl_processing")
        ocr_available = corpus_ready
        archival_status = "not_applicable_final_exception" if disposition == "final_exception" else ws["archival_status"]

        rows.append({
            "ledger_version": VERSION,
            "viewer_key": viewer,
            "wave": wave,
            "operational_domain": domain,
            "catalog_generation": cov["catalog_generation"],
            "grade_code": cov["grade_code"],
            "title_core": cov["title_core"],
            "documentary_disposition": disposition,
            "retention_class": ret["retention_class"] if ret else "",
            "tracking_issue": ret["tracking_issue"] if ret else "",
            "source_ready": source_state(cov),
            "relation_type": relation_type,
            "canonical_processing_viewer_key": canonical_key,
            "is_canonical_processing_object": canonical_object,
            "declared_positions": declared_positions,
            "canonical_source_pages": canonical_source_pages,
            "persistent_unresolved_source_gaps": unresolved_gaps,
            "ftrl_status": identity_ftrl_status,
            "ftrl_run_id": ws.get("ftrl_run_id", "") if disposition == "required_ftrl_processing" else "",
            "ftrl_commit": ws.get("ftrl_commit", "") if disposition == "required_ftrl_processing" else "",
            "corpus_ready": corpus_ready,
            "ocr_available": ocr_available,
            "text_verified": 0,
            "semantic_ready": as_bool01(cov.get("semantic_ready", 0)),
            "archival_status": archival_status,
            "preservation_run_id": ws.get("preservation_run_id", "") if disposition != "final_exception" else "",
            "archive_destination_logical": ws.get("archive_destination_logical", "") if disposition != "final_exception" else "",
            "interpretive_limit": "Technical/archival state only; no semantic or historical claim is implied.",
        })

    wave_counts = Counter(r["wave"] for r in rows)
    if dict(sorted(wave_counts.items())) != EXPECTED_WAVES:
        raise AssertionError(f"wave denominator drift: {dict(sorted(wave_counts.items()))}")
    dispositions = Counter(r["documentary_disposition"] for r in rows)
    expected_dispositions = Counter({"required_ftrl_processing": 524, "active_retention": 13, "final_exception": 5})
    if dispositions != expected_dispositions:
        raise AssertionError(f"disposition drift: {dispositions}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    canonical_by_status = Counter()
    pages_by_status = Counter()
    for r in rows:
        if r["is_canonical_processing_object"]:
            canonical_by_status[r["ftrl_status"]] += 1
            if str(r["canonical_source_pages"]):
                pages_by_status[r["ftrl_status"]] += int(r["canonical_source_pages"])

    summary = {
        "schema": "LTMD_U1_FTRL_COMPLETION_SUMMARY_0.1",
        "ledger_version": VERSION,
        "status": "valid",
        "documentary_identities": len(rows),
        "wave_denominators": dict(sorted(wave_counts.items())),
        "documentary_dispositions": dict(sorted(dispositions.items())),
        "ftrl_identity_status": dict(sorted(Counter(r["ftrl_status"] for r in rows).items())),
        "canonical_processing_objects_by_ftrl_status": dict(sorted(canonical_by_status.items())),
        "canonical_source_pages_by_ftrl_status": dict(sorted(pages_by_status.items())),
        "corpus_ready_identities": sum(int(r["corpus_ready"]) for r in rows),
        "ocr_available_identities": sum(int(r["ocr_available"]) for r in rows),
        "text_verified_identities": sum(int(r["text_verified"]) for r in rows),
        "semantic_ready_identities": sum(int(r["semantic_ready"]) for r in rows),
        "archival_status": dict(sorted(Counter(r["archival_status"] for r in rows).items())),
        "global_closure": {
            "eligible": False,
            "reason": "active retentions and unfinished FTRL waves remain; archival completion is also incomplete",
            "active_retentions": dispositions["active_retention"],
            "final_exceptions": dispositions["final_exception"],
        },
        "epistemic_guards": [
            "corpus_ready != semantic_ready",
            "ocr_available != text_verified",
            "search_hit != historical_claim",
            "zero_hits != demonstrated_absence",
            "computationally_validated != archival_complete",
        ],
    }
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
