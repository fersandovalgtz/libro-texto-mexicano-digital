#!/usr/bin/env python3
"""Prepare a replacement SEMB 0.3 holdout without publishing its identities.

The 160 nominal validation identities in SEMB03_SAMPLE_0.2 were exposed in the
public Git history before model lock. This utility creates a fresh private
holdout from manifest metadata only, excluding all 480 legacy sample identities.

Private outputs live under private/ (gitignored). The only public-safe output is
a cryptographic commitment JSON containing no sample or fragment identifiers.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import secrets
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/derived/fragment_manifest.csv"
LEGACY = ROOT / "data/validation/semb03_human_reference_sample.csv"
DEFAULT_SEED = ROOT / "private/semb03/holdout_seed.bin"
DEFAULT_PRIVATE = ROOT / "private/semb03/holdout_manifest.csv"
DEFAULT_COMMITMENT = ROOT / "data/validation/semb03_private_holdout_commitment.json"
VERSION = "SEMB03_PRIVATE_HOLDOUT_0.1"
GENERATIONS = ("1972", "1988", "1993", "2014")
RARE = {"activity_candidate", "experiment_candidate", "project_candidate", "assessment_candidate"}


def eligible(row: dict[str, str]) -> bool:
    return row["candidate_type"] != "heading_candidate" and int(row["token_count"]) >= 4


def score(seed: bytes, label: str, fragment_id: str) -> bytes:
    return hmac.new(seed, f"{VERSION}|{label}|{fragment_id}".encode(), hashlib.sha256).digest()


def pick(pool: list[dict[str, str]], n: int, seed: bytes, label: str, used: set[str]) -> list[dict[str, str]]:
    candidates = [r for r in pool if r["fragment_id"] not in used]
    candidates.sort(key=lambda r: score(seed, label, r["fragment_id"]))
    if len(candidates) < n:
        raise SystemExit(f"insufficient eligible pool for {label}: requested {n}, have {len(candidates)}")
    selected = candidates[:n]
    used.update(r["fragment_id"] for r in selected)
    return selected


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(path: Path) -> str:
    """Return Git's content-addressed blob SHA for the exact source manifest bytes."""
    try:
        value = subprocess.check_output(
            ["git", "hash-object", str(path)], cwd=ROOT, text=True
        ).strip().lower()
    except Exception as exc:
        raise SystemExit(f"cannot derive Git blob SHA for source manifest: {exc}") from exc
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise SystemExit("unexpected Git blob SHA returned for source manifest")
    return value


def init_seed(path: Path) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing private seed: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(secrets.token_bytes(32))
    print(f"created private seed at {path}; do not commit or print its contents")


def build(seed_path: Path, private_path: Path, commitment_path: Path) -> None:
    seed = seed_path.read_bytes()
    if len(seed) < 32:
        raise SystemExit("private seed must contain at least 32 bytes")

    manifest_bytes = MANIFEST.read_bytes()
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    legacy = list(csv.DictReader(LEGACY.open(encoding="utf-8")))
    if len(legacy) != 480:
        raise SystemExit("expected the auditable 480-row legacy public sample")
    legacy_ids = {r["fragment_id"] for r in legacy}
    if len(legacy_ids) != 480:
        raise SystemExit("legacy public sample contains duplicate fragment IDs")

    selected: list[dict[str, str]] = []
    for generation in GENERATIONS:
        pool = [
            r for r in rows
            if r["catalog_generation"] == generation
            and r["fragment_id"] not in legacy_ids
            and eligible(r)
        ]
        used: set[str] = set()
        candidate = []
        # Preserve broad candidate-type coverage without consulting semantic outputs.
        candidate += pick([r for r in pool if r["candidate_type"] == "expository_candidate"], 25, seed, f"{generation}:expository", used)
        candidate += pick([r for r in pool if r["candidate_type"] == "instruction_candidate"], 25, seed, f"{generation}:instruction", used)
        candidate += pick([r for r in pool if r["candidate_type"] == "question_candidate"], 25, seed, f"{generation}:question", used)
        candidate += pick([r for r in pool if r["candidate_type"] in RARE], 20, seed, f"{generation}:rare", used)
        candidate += pick(pool, 25, seed, f"{generation}:remainder", used)
        # Select 40 privately from the 120 metadata-balanced candidates.
        candidate.sort(key=lambda r: score(seed, f"{generation}:final40", r["fragment_id"]))
        chosen = candidate[:40]
        if len(chosen) != 40 or len({r["fragment_id"] for r in chosen}) != 40:
            raise SystemExit(f"failed to select 40 unique rows for generation {generation}")
        selected.extend(chosen)

    ids = {r["fragment_id"] for r in selected}
    if len(selected) != 160 or len(ids) != 160:
        raise SystemExit("replacement holdout must contain 160 unique identities")
    if ids & legacy_ids:
        raise SystemExit("replacement holdout overlaps legacy public sample")

    private_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "holdout_version", "private_sample_id", "fragment_id", "page_id",
        "catalog_generation", "candidate_type", "token_count", "char_count", "text_sha256",
    ]
    with private_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(selected, key=lambda r: score(seed, "private-order", r["fragment_id"])):
            opaque = hmac.new(seed, f"opaque|{row['fragment_id']}".encode(), hashlib.sha256).hexdigest()[:20].upper()
            writer.writerow({
                "holdout_version": VERSION,
                "private_sample_id": f"S03H-{opaque}",
                "fragment_id": row["fragment_id"],
                "page_id": row["page_id"],
                "catalog_generation": row["catalog_generation"],
                "candidate_type": row["candidate_type"],
                "token_count": row["token_count"],
                "char_count": row["char_count"],
                "text_sha256": row["text_sha256"],
            })

    private_bytes = private_path.read_bytes()
    counts = {g: sum(1 for r in selected if r["catalog_generation"] == g) for g in GENERATIONS}
    commitment = {
        "commitment_version": "SEMB03_PRIVATE_HOLDOUT_COMMITMENT_0.1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "selection_algorithm_version": VERSION,
        "holdout_n": 160,
        "per_generation": counts,
        "legacy_sample_excluded": True,
        "ids_public": False,
        "private_manifest_sha256": sha256_bytes(private_bytes),
        "private_manifest_bytes": len(private_bytes),
        "source_manifest_sha256": sha256_bytes(manifest_bytes),
        "source_manifest_git_blob_sha": git_blob_sha(MANIFEST),
        "notes": "Commit this JSON only. Keep seed and private manifest outside Git until final evaluation is closed.",
    }
    commitment_path.parent.mkdir(parents=True, exist_ok=True)
    commitment_path.write_text(json.dumps(commitment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"private holdout: {private_path} (160 IDs, not for Git)")
    print(f"public-safe commitment: {commitment_path}")
    print("legacy overlap: 0")
    print(f"source manifest blob: {commitment['source_manifest_git_blob_sha']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-file", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--private-output", type=Path, default=DEFAULT_PRIVATE)
    parser.add_argument("--commitment-output", type=Path, default=DEFAULT_COMMITMENT)
    parser.add_argument("--init-seed", action="store_true", help="create a new 32-byte private seed and exit")
    args = parser.parse_args()
    if args.init_seed:
        init_seed(args.seed_file)
        return
    if not args.seed_file.exists():
        raise SystemExit(f"missing private seed {args.seed_file}; run once with --init-seed")
    build(args.seed_file, args.private_output, args.commitment_output)


if __name__ == "__main__":
    main()
