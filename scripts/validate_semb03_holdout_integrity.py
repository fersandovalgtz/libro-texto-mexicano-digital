#!/usr/bin/env python3
"""Validate SEMB 0.3 holdout-integrity invariants.

This validator makes the 2026-08-27 remediation machine-readable. It does not
create labels, open a private holdout, or alter scientific coverage.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data/validation/semb03_holdout_integrity_status.json"
SAMPLE = ROOT / "data/validation/semb03_human_reference_sample.csv"
ANNOT = ROOT / "data/validation/semb03_human_reference_annotation_template.csv"
COMMITMENT = ROOT / "data/validation/semb03_private_holdout_commitment.json"
LOCK = ROOT / "data/validation/semb03_model_lock.json"
LOCKED_RESULT = ROOT / "data/validation/semb03_locked_validation_result.json"


def fail(msg: str) -> None:
    raise SystemExit(f"SEMB03 holdout integrity: FAIL — {msg}")


def main() -> None:
    if not STATUS.exists():
        fail("missing integrity status")
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    if status.get("integrity_version") != "SEMB03_HOLDOUT_INTEGRITY_0.1":
        fail("unexpected integrity status version")

    legacy = status["legacy_public_sample"]
    replacement = status["replacement_private_holdout"]
    if legacy.get("final_validation_admissibility") != "invalidated_by_prelock_public_exposure":
        fail("legacy public holdout must remain invalid for final validation")
    if legacy.get("nominal_locked_validation_rows") != 160:
        fail("legacy status must document 160 exposed nominal validation rows")
    if replacement.get("n") != 160 or replacement.get("per_generation") != 40:
        fail("replacement holdout must be fixed at 160 = 40 per generation")
    if replacement.get("source_pool_must_exclude_all_legacy_480") is not True:
        fail("replacement must exclude all 480 legacy public sample identities")
    if replacement.get("fragment_ids_must_not_be_committed_before_evaluation") is not True:
        fail("replacement IDs must remain outside Git before evaluation")

    rows = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    if len(rows) != 480 or len({r["fragment_id"] for r in rows}) != 480:
        fail("legacy public sample must remain an auditable 480-row unique historical artifact")
    counts = Counter(r["analysis_role"] for r in rows)
    if counts != Counter({"development": 320, "locked_validation": 160}):
        fail(f"unexpected legacy role counts: {dict(counts)}")

    ann = list(csv.DictReader(ANNOT.open(encoding="utf-8")))
    if len(ann) != 480:
        fail("legacy annotation template must retain 480 rows for historical auditability")
    human_fields = [
        "annotator_id", "annotation_round", "actionable", "action_labels",
        "position_labels", "annotation_confidence", "ambiguity_note",
    ]
    leaked = [
        (i + 2, field)
        for i, row in enumerate(ann)
        for field in human_fields
        if (row.get(field) or "").strip()
    ]
    if leaked:
        fail(f"public human annotation values detected, first={leaked[0]}")

    if LOCKED_RESULT.exists() and not LOCK.exists():
        fail("locked validation result exists without a prior model lock")

    if COMMITMENT.exists():
        commitment = json.loads(COMMITMENT.read_text(encoding="utf-8"))
        allowed_keys = {
            "commitment_version", "created_utc", "selection_algorithm_version",
            "holdout_n", "per_generation", "legacy_sample_excluded",
            "ids_public", "private_manifest_sha256", "private_manifest_bytes",
            "source_manifest_git_blob_sha", "notes",
        }
        extra = set(commitment) - allowed_keys
        if extra:
            fail(f"public commitment contains unsupported fields: {sorted(extra)}")
        if commitment.get("holdout_n") != 160:
            fail("private holdout commitment must document holdout_n=160")
        pg = commitment.get("per_generation")
        if pg != {"1972": 40, "1988": 40, "1993": 40, "2014": 40}:
            fail("private holdout commitment must document 40 cases per generation")
        if commitment.get("legacy_sample_excluded") is not True:
            fail("commitment must assert exclusion of all 480 legacy identities")
        if commitment.get("ids_public") is not False:
            fail("commitment must assert ids_public=false")
        digest = commitment.get("private_manifest_sha256", "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            fail("invalid private manifest SHA-256 commitment")

    if LOCK.exists():
        if not COMMITMENT.exists():
            fail("model lock exists without private holdout commitment")
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        if "private_holdout_commitment_sha256" not in lock:
            fail("model lock does not bind the private holdout commitment")
        if lock.get("legacy_public_holdout_admissible") is not False:
            fail("model lock must explicitly reject the legacy public holdout")

    print("SEMB03 holdout integrity: OK")
    print("legacy nominal holdout: exposed / inadmissible for final validation")
    print("public human labels detected: 0")
    print("replacement private holdout commitment:", "present" if COMMITMENT.exists() else "pending")
    print("model lock:", "present" if LOCK.exists() else "pending")


if __name__ == "__main__":
    main()
