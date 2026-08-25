#!/usr/bin/env python3
"""Validate public, text-free W3 archival-closure evidence."""
from __future__ import annotations

import json
import re
from pathlib import Path

PATH = Path("data/research/ltmd_u1_w3_archive_closure_2026_08_25.json")
SHA = re.compile(r"^[0-9a-f]{64}$")


def no_private_locator(value) -> None:
    if isinstance(value, dict):
        forbidden = {"drive_id", "file_id", "folder_id", "drive_url", "private_url"}
        assert not (forbidden & set(value))
        for child in value.values():
            no_private_locator(child)
    elif isinstance(value, list):
        for child in value:
            no_private_locator(child)
    elif isinstance(value, str):
        assert "drive.google.com" not in value
        assert "docs.google.com" not in value
        assert "BEGIN PRIVATE KEY" not in value
        assert "BEGIN RSA PRIVATE KEY" not in value


def main() -> None:
    p = json.loads(PATH.read_text(encoding="utf-8"))
    assert p["schema"] == "LTMD_FTRL_W3_ARCHIVE_CLOSURE_0.1"
    assert p["source"] == {
        "workflow_run_id": "32853375619",
        "source_commit": "2a55ec09124054729e9c45a2285686cf4abf8776",
        "workflow_conclusion": "success",
    }
    c = p["computational_validation"]
    assert (c["shard_count"], c["historical_identities"], c["canonical_processing_objects"], c["page_records"]) == (52, 130, 114, 20765)
    assert c["page_partition_complete"] and c["page_partition_unique"] and c["global_union_exact"]
    assert c["sqlite_integrity"] == "ok" and c["fts_rows"] == 20765

    a = p["persistent_archive"]
    assert a["destination"] == "private_google_drive" and a["destination_shared"] is False
    assert a["all_required_products_present"] and a["all_required_products_redownload_verified"]
    assert [b["bytes"] for b in a["encrypted_handoff_bundles"]] == [10215122, 26337085]
    assert all(b["redownload_verified"] for b in a["encrypted_handoff_bundles"])
    assert len(a["consolidated_products"]) == 7
    assert all(x["redownload_verified"] for x in a["consolidated_products"])
    assert a["public_text_free_evidence"]["contains_restricted_ocr_text"] is False
    assert a["public_text_free_evidence"]["redownload_verified"] is True
    for x in a["encrypted_handoff_bundles"] + a["consolidated_products"] + [a["public_text_free_evidence"]]:
        assert SHA.fullmatch(x["sha256"])

    assert p["quality_control"]["pages_flagged_for_review"] == 4025
    assert p["states"] == {
        "ocr_available": True,
        "computationally_validated": True,
        "archival_complete": True,
        "corpus_ready": True,
        "text_verified": False,
        "semantic_ready": False,
    }
    no_private_locator(p)
    print("LTMD W3 archive closure evidence: OK")


if __name__ == "__main__":
    main()
