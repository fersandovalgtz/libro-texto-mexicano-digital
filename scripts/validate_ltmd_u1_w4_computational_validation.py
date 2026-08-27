#!/usr/bin/env python3
"""Validate public text-free W4 computational-validation evidence."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

GLOBAL = Path("data/research/ltmd_u1_w4_distributed_global_evidence.json")
CLOSURE = Path("data/research/ltmd_u1_w4_computational_validation.json")
SHA = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_GLOBAL_SHA = "357abe7dabb958ec9261953625a417bc0454d93c75d098f867a8c459b8d1a10e"
EXPECTED_SHARDS = {
    0: (340493, "87caa0985d84702820dbf5e9c4e7ee2e824308b0418fd99f3e8bba5083254bb9"),
    1: (567283, "1be071f469a52f9937297d30728cef374081dd55c53d46c92cae19d988061210"),
    2: (624340, "077e11378e75942bb5ed539eca3e8d0f15550f7ee5570eec3d6bc3c243ac0c69"),
    3: (780679, "41961cdedc95f05df35fb19e0ce8d8ed0fef5ecdaae8ff5370e21b476ad78031"),
    4: (722432, "bb42ed6c32e79ef022cb6cb6183a0a5c073e231996a0d6b7c97702df39198d87"),
    5: (672688, "f2bb26f553192988ceed3d58794d81584854b46afaabc23fec890603f4be6afd"),
    6: (710674, "c2ca23908a1b655ca3e64f53e2324b6b68b17596e2b59cb04706feab1d49ac9f"),
    7: (578634, "1ddd98e61da8fba91be06bd1f70940924dd784a6f239731587ae548cbe841645"),
}
FORBIDDEN_KEYS = {"ocr_text_raw", "search_text", "snippet", "text"}
FORBIDDEN_STRINGS = ("drive.google.com", "docs.google.com", "BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY")


def walk(value) -> None:
    if isinstance(value, dict):
        hits = FORBIDDEN_KEYS & set(value)
        if hits:
            raise AssertionError(f"restricted-text keys in public evidence: {sorted(hits)}")
        for child in value.values():
            walk(child)
    elif isinstance(value, list):
        for child in value:
            walk(child)
    elif isinstance(value, str):
        if any(token in value for token in FORBIDDEN_STRINGS):
            raise AssertionError("private locator/key material in public W4 evidence")


def main() -> None:
    raw = GLOBAL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_GLOBAL_SHA
    g = json.loads(raw)
    c = json.loads(CLOSURE.read_text(encoding="utf-8"))
    walk(g); walk(c)

    assert g["schema"] == "LTMD_FTRL_W4_DISTRIBUTED_GLOBAL_0.1"
    assert g["status"] == "distributed_computationally_validated"
    assert g["wave"] == "W4" and g["domain"] == "Ciencias Sociales"
    assert g["historical_identities"] == 14
    assert g["canonical_processing_objects"] == 14
    assert g["page_records"] == g["unique_page_records"] == g["expected_page_records"] == 2414
    assert g["shard_count"] == 8 and g["shard_size_distribution"] == {"301": 2, "302": 6}
    assert g["page_partition_complete"] is True and g["page_partition_unique"] is True
    assert g["same_source_commit_and_workflow_run"] is True
    assert g["source_commits_observed"] == ["455e0f21434162c4b77a0b5d52269b65512c486d"]
    assert g["workflow_run_ids_observed"] == ["33033136922"]
    assert g["archival_complete"] is False and g["text_verified"] is False and g["semantic_ready"] is False

    assert c["schema"] == "LTMD_U1_W4_COMPUTATIONAL_VALIDATION_0.1"
    assert c["computational_status"] == "distributed_computationally_validated"
    assert c["source_commit"] == g["source_commits_observed"][0]
    assert c["workflow_run_id"] == g["workflow_run_ids_observed"][0]
    assert c["global_text_free_evidence_sha256"] == EXPECTED_GLOBAL_SHA
    p = c["encrypted_handoff_persistence"]
    assert p["status"] == "persisted_and_redownload_verified"
    assert p["files_expected"] == p["files_persisted"] == 8
    assert p["drive_visibility_verified"] == "not_shared"
    assert p["redownload_sha256_matches_actions_artifact"] is True
    assert p["plaintext_restricted_outputs_persisted_publicly"] is False
    observed = {int(x["shard"]): (int(x["bytes"]), x["sha256"]) for x in p["shards"]}
    assert observed == EXPECTED_SHARDS
    assert all(SHA.fullmatch(v[1]) for v in observed.values())
    assert c["archival_complete"] is False
    assert c["text_verified"] is False and c["semantic_ready"] is False
    assert "private decryption" in c["archival_blocker"].lower()
    print("W4 public computational validation evidence: OK")


if __name__ == "__main__":
    main()
