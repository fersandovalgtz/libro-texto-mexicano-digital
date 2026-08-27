#!/usr/bin/env python3
"""Freeze a SEMB 0.3 candidate before private locked validation is opened.

The lock records cryptographic hashes of the development result, configuration,
executable code, preregistered acceptance criteria and the public cryptographic
commitment to the replacement private holdout. It refuses retroactive locks and
explicitly rejects the legacy public 160-case subset as final validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("data/validation/semb03_model_lock.json")
CRIT = Path("data/validation/semb03_acceptance_criteria.json")
COMMITMENT = Path("data/validation/semb03_private_holdout_commitment.json")
INTEGRITY = Path("data/validation/semb03_holdout_integrity_status.json")
LOCKED_RESULT = Path("data/validation/semb03_locked_validation_result.json")
VERSION = "SEMB03_MODEL_LOCK_0.2"


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def valid_hex(value: object, n: int) -> bool:
    return isinstance(value, str) and len(value) == n and all(c in "0123456789abcdef" for c in value.lower())


def git_head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-result", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--code", nargs="+", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--model-revision", required=True)
    args = parser.parse_args()

    if OUT.exists():
        raise SystemExit("Model lock already exists; refusing overwrite")
    if LOCKED_RESULT.exists():
        raise SystemExit("Locked validation result already exists; cannot create a retroactive lock")
    if not COMMITMENT.exists():
        raise SystemExit(
            "Missing replacement private holdout commitment; prepare the private 160-case holdout "
            "and commit only data/validation/semb03_private_holdout_commitment.json before model lock"
        )
    if not INTEGRITY.exists():
        raise SystemExit("Missing holdout-integrity status; refusing un-audited model lock")

    development = Path(args.development_result)
    config = Path(args.config)
    code_files = list(map(Path, args.code))
    for path in [development, config, CRIT, COMMITMENT, INTEGRITY, *code_files]:
        if not path.exists():
            raise SystemExit(f"missing lock input: {path}")

    dev = json.loads(development.read_text(encoding="utf-8"))
    if int(dev.get("development_n", -1)) != 320:
        raise SystemExit("development_result must document development_n=320")
    if dev.get("locked_validation_accessed") is not False:
        raise SystemExit("development_result must assert locked_validation_accessed=false")

    criteria = json.loads(CRIT.read_text(encoding="utf-8"))
    if criteria.get("criteria_version") != "SEMB03_ACCEPTANCE_0.1":
        raise SystemExit("unexpected acceptance criteria version")

    integrity = json.loads(INTEGRITY.read_text(encoding="utf-8"))
    legacy = integrity.get("legacy_public_sample", {})
    if legacy.get("final_validation_admissibility") != "invalidated_by_prelock_public_exposure":
        raise SystemExit("integrity status does not invalidate the legacy public holdout")

    commitment = json.loads(COMMITMENT.read_text(encoding="utf-8"))
    if commitment.get("commitment_version") != "SEMB03_PRIVATE_HOLDOUT_COMMITMENT_0.1":
        raise SystemExit("unexpected private holdout commitment version")
    if commitment.get("holdout_n") != 160:
        raise SystemExit("private holdout commitment must document holdout_n=160")
    if commitment.get("per_generation") != {"1972": 40, "1988": 40, "1993": 40, "2014": 40}:
        raise SystemExit("private holdout commitment must document 40 cases per generation")
    if commitment.get("legacy_sample_excluded") is not True:
        raise SystemExit("private holdout must exclude all 480 legacy public identities")
    if commitment.get("ids_public") is not False:
        raise SystemExit("private holdout commitment must assert ids_public=false")
    manifest_digest = commitment.get("private_manifest_sha256")
    source_manifest_digest = commitment.get("source_manifest_sha256")
    source_manifest_blob = commitment.get("source_manifest_git_blob_sha")
    if not valid_hex(manifest_digest, 64):
        raise SystemExit("private holdout commitment lacks a valid manifest SHA-256")
    if not valid_hex(source_manifest_digest, 64):
        raise SystemExit("private holdout commitment lacks a valid source-manifest SHA-256")
    if not valid_hex(source_manifest_blob, 40):
        raise SystemExit("private holdout commitment lacks a valid source-manifest Git blob SHA")

    lock = {
        "lock_version": VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": git_head(),
        "model_name": args.model_name,
        "model_revision": args.model_revision,
        "development_result": str(development),
        "development_result_sha256": sha(development),
        "config": str(config),
        "config_sha256": sha(config),
        "code_files": [{"path": str(path), "sha256": sha(path)} for path in code_files],
        "acceptance_criteria": str(CRIT),
        "acceptance_criteria_sha256": sha(CRIT),
        "acceptance_criteria_version": criteria["criteria_version"],
        "holdout_integrity_status": str(INTEGRITY),
        "holdout_integrity_status_sha256": sha(INTEGRITY),
        "private_holdout_commitment": str(COMMITMENT),
        "private_holdout_commitment_sha256": sha(COMMITMENT),
        "private_holdout_manifest_sha256": manifest_digest,
        "source_fragment_manifest_sha256": source_manifest_digest,
        "source_fragment_manifest_git_blob_sha": source_manifest_blob,
        "legacy_public_holdout_admissible": False,
        "locked_validation_accessed_before_lock": False,
        "historical_outputs_used_for_selection": False
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(lock, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
