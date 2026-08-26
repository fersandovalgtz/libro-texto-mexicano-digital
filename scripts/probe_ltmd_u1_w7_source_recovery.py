#!/usr/bin/env python3
"""Fail-closed source-recovery probe for LTMD-U1 W7.

The probe is intentionally non-mutating: it reads candidate URLs, records
retrieval/technical evidence, validates declared sequence completeness, and
writes JSON/CSV evidence. It never edits the canonical LTMD ledger.

A candidate becomes ``admissible`` only when:
1. every declared asset was fetched and technically verified;
2. the declared sequence is complete and contiguous; and
3. provenance_status == "verified" and rights_status == "verified" on every row.

"rights_status=verified" is an operator-supplied gate for the intended corpus
processing. It is evidence metadata, not a grant or inference of copyright,
redistribution, or publication rights.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import socket
import ssl
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

VERSION = "LTMD_U1_W7_SOURCE_RECOVERY_PROBE_0.1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_BYTES = 64 * 1024 * 1024
VERIFIED = "verified"


@dataclass(frozen=True)
class Candidate:
    identity: str
    candidate_url: str
    sequence_index: int
    expected_sequence_length: int
    expected_sha256: str = ""
    provenance_status: str = "unknown"
    rights_status: str = "unknown"
    notes: str = ""


@dataclass
class AssetResult:
    probe_version: str
    identity: str
    candidate_url: str
    final_url: str
    sequence_index: int
    expected_sequence_length: int
    discovered: bool
    verified: bool
    http_status: int | None
    content_type: str
    byte_size: int
    sha256: str
    expected_sha256: str
    hash_match: bool | None
    media_signature: str
    provenance_status: str
    rights_status: str
    failure_reason: str
    notes: str


def _norm_status(value: str) -> str:
    return (value or "unknown").strip().lower()


def _parse_positive_int(value: str, field: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc
    if parsed < 1:
        raise ValueError(f"{field} must be >= 1")
    return parsed


def load_candidates(path: Path) -> list[Candidate]:
    required = {"identity", "candidate_url", "sequence_index", "expected_sequence_length"}
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = set(reader.fieldnames or [])
        missing = required - fields
        if missing:
            raise ValueError(f"candidate CSV missing columns: {', '.join(sorted(missing))}")
        candidates: list[Candidate] = []
        for line_no, row in enumerate(reader, start=2):
            identity = (row.get("identity") or "").strip()
            url = (row.get("candidate_url") or "").strip()
            if not identity:
                raise ValueError(f"line {line_no}: identity is required")
            if not url:
                raise ValueError(f"line {line_no}: candidate_url is required")
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(f"line {line_no}: candidate_url must be http(s)")
            if parsed.username or parsed.password:
                raise ValueError(f"line {line_no}: URL credentials are not allowed")
            expected_sha = (row.get("expected_sha256") or "").strip().lower()
            if expected_sha and (len(expected_sha) != 64 or any(c not in "0123456789abcdef" for c in expected_sha)):
                raise ValueError(f"line {line_no}: expected_sha256 must be 64 lowercase/uppercase hex characters")
            candidates.append(
                Candidate(
                    identity=identity,
                    candidate_url=url,
                    sequence_index=_parse_positive_int(row.get("sequence_index", ""), "sequence_index"),
                    expected_sequence_length=_parse_positive_int(
                        row.get("expected_sequence_length", ""), "expected_sequence_length"
                    ),
                    expected_sha256=expected_sha,
                    provenance_status=_norm_status(row.get("provenance_status", "unknown")),
                    rights_status=_norm_status(row.get("rights_status", "unknown")),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    if not candidates:
        raise ValueError("candidate CSV contains no rows")
    return candidates


def inspect_payload(data: bytes, content_type: str, expected_sha256: str = "") -> tuple[bool, str, str, bool | None, str]:
    """Return verified, media_signature, sha256, hash_match, failure_reason."""
    digest = hashlib.sha256(data).hexdigest()
    expected = (expected_sha256 or "").lower()
    hash_match = digest == expected if expected else None

    if not data:
        return False, "empty", digest, hash_match, "empty response body"
    if expected and not hash_match:
        return False, "hash-mismatch", digest, False, "sha256 does not match expected_sha256"

    lower_type = (content_type or "").lower()
    stripped = data.lstrip()
    if stripped.startswith(b"%PDF-"):
        if b"%%EOF" not in data[-8192:]:
            return False, "pdf", digest, hash_match, "PDF EOF marker not found near end of payload"
        return True, "pdf", digest, hash_match, ""

    if data.startswith(b"\xff\xd8\xff"):
        if not data.rstrip().endswith(b"\xff\xd9"):
            return False, "jpeg", digest, hash_match, "JPEG end marker not found"
        return True, "jpeg", digest, hash_match, ""

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        if b"IEND" not in data[-64:]:
            return False, "png", digest, hash_match, "PNG IEND marker not found near end of payload"
        return True, "png", digest, hash_match, ""

    if "text/html" in lower_type or stripped[:64].lower().startswith((b"<!doctype html", b"<html")):
        return False, "html", digest, hash_match, "HTML is not an admissible source asset"

    return False, "unknown", digest, hash_match, "unrecognized source-asset signature"


def _read_limited(response, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(1024 * 1024, max_bytes + 1 - total))
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValueError(f"response exceeds max_bytes={max_bytes}")
        chunks.append(chunk)
    return b"".join(chunks)


def probe_candidate(
    candidate: Candidate,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    max_bytes: int = DEFAULT_MAX_BYTES,
    allowed_hosts: set[str] | None = None,
) -> AssetResult:
    parsed = urlparse(candidate.candidate_url)
    host = (parsed.hostname or "").lower()
    if allowed_hosts and host not in allowed_hosts:
        return AssetResult(
            VERSION, candidate.identity, candidate.candidate_url, "", candidate.sequence_index,
            candidate.expected_sequence_length, False, False, None, "", 0, "",
            candidate.expected_sha256, None, "not-fetched", candidate.provenance_status,
            candidate.rights_status, f"host not allowed: {host}", candidate.notes,
        )

    req = Request(
        candidate.candidate_url,
        headers={
            "User-Agent": "LTMD-U1-W7-source-recovery-probe/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)",
            "Accept": "application/pdf,image/jpeg,image/png,application/octet-stream;q=0.8,*/*;q=0.1",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=timeout, context=ssl.create_default_context()) as response:
            status = int(getattr(response, "status", response.getcode()))
            final_url = response.geturl()
            content_type = response.headers.get_content_type() if response.headers else ""
            if not 200 <= status < 300:
                return AssetResult(
                    VERSION, candidate.identity, candidate.candidate_url, final_url,
                    candidate.sequence_index, candidate.expected_sequence_length, False, False,
                    status, content_type, 0, "", candidate.expected_sha256, None, "not-fetched",
                    candidate.provenance_status, candidate.rights_status,
                    f"unexpected HTTP status {status}", candidate.notes,
                )
            data = _read_limited(response, max_bytes)
            verified, signature, digest, hash_match, reason = inspect_payload(
                data, content_type, candidate.expected_sha256
            )
            return AssetResult(
                VERSION, candidate.identity, candidate.candidate_url, final_url,
                candidate.sequence_index, candidate.expected_sequence_length, True, verified,
                status, content_type, len(data), digest, candidate.expected_sha256, hash_match,
                signature, candidate.provenance_status, candidate.rights_status, reason,
                candidate.notes,
            )
    except HTTPError as exc:
        return AssetResult(
            VERSION, candidate.identity, candidate.candidate_url, candidate.candidate_url,
            candidate.sequence_index, candidate.expected_sequence_length, False, False,
            int(exc.code), exc.headers.get_content_type() if exc.headers else "", 0, "",
            candidate.expected_sha256, None, "not-fetched", candidate.provenance_status,
            candidate.rights_status, f"HTTP error {exc.code}", candidate.notes,
        )
    except (URLError, TimeoutError, socket.timeout, ssl.SSLError, ValueError, OSError) as exc:
        return AssetResult(
            VERSION, candidate.identity, candidate.candidate_url, "",
            candidate.sequence_index, candidate.expected_sequence_length, False, False,
            None, "", 0, "", candidate.expected_sha256, None, "not-fetched",
            candidate.provenance_status, candidate.rights_status,
            f"{type(exc).__name__}: {exc}", candidate.notes,
        )


def summarize(results: Iterable[AssetResult]) -> list[dict[str, object]]:
    grouped: dict[str, list[AssetResult]] = {}
    for result in results:
        grouped.setdefault(result.identity, []).append(result)

    summaries: list[dict[str, object]] = []
    for identity in sorted(grouped):
        rows = sorted(grouped[identity], key=lambda r: r.sequence_index)
        declared_lengths = {r.expected_sequence_length for r in rows}
        indexes = [r.sequence_index for r in rows]
        expected_length = next(iter(declared_lengths)) if len(declared_lengths) == 1 else 0
        unique_indexes = len(indexes) == len(set(indexes))
        expected_indexes = list(range(1, expected_length + 1)) if expected_length else []
        sequence_verified = (
            len(declared_lengths) == 1
            and unique_indexes
            and indexes == expected_indexes
            and all(r.verified for r in rows)
        )
        provenance_verified = all(r.provenance_status == VERIFIED for r in rows)
        rights_verified = all(r.rights_status == VERIFIED for r in rows)
        admissible = sequence_verified and provenance_verified and rights_verified
        failures: list[str] = []
        if len(declared_lengths) != 1:
            failures.append("inconsistent expected_sequence_length")
        elif indexes != expected_indexes:
            failures.append("sequence is not complete and contiguous")
        if not all(r.verified for r in rows):
            failures.append("one or more assets are not technically verified")
        if not provenance_verified:
            failures.append("provenance_status is not verified for every asset")
        if not rights_verified:
            failures.append("rights_status is not verified for every asset")

        summaries.append({
            "probe_version": VERSION,
            "identity": identity,
            "declared_asset_count": len(rows),
            "expected_sequence_length": expected_length,
            "discovered_assets": sum(1 for r in rows if r.discovered),
            "verified_assets": sum(1 for r in rows if r.verified),
            "sequence_verified": sequence_verified,
            "provenance_verified": provenance_verified,
            "rights_verified": rights_verified,
            "admissible": admissible,
            "failure_reasons": failures,
        })
    return summaries


def write_reports(results: list[AssetResult], summaries: list[dict[str, object]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "probe_version": VERSION,
        "non_mutating": True,
        "assets": [asdict(r) for r in results],
        "identities": summaries,
    }
    (out_dir / "ltmd_u1_w7_source_recovery_probe.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    asset_fields = list(asdict(results[0]).keys())
    with (out_dir / "ltmd_u1_w7_source_recovery_assets.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=asset_fields)
        writer.writeheader()
        writer.writerows(asdict(r) for r in results)

    summary_fields = [
        "probe_version", "identity", "declared_asset_count", "expected_sequence_length",
        "discovered_assets", "verified_assets", "sequence_verified", "provenance_verified",
        "rights_verified", "admissible", "failure_reasons",
    ]
    with (out_dir / "ltmd_u1_w7_source_recovery_summary.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=summary_fields)
        writer.writeheader()
        for summary in summaries:
            row = dict(summary)
            row["failure_reasons"] = " | ".join(summary["failure_reasons"])
            writer.writerow(row)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True, help="CSV of candidate source assets")
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/ltmd_u1_w7_source_recovery"))
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument(
        "--allow-host", action="append", default=[],
        help="Optional exact hostname allowlist; repeat for multiple hosts. Host filtering never implies admissibility.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.timeout <= 0 or args.max_bytes < 1:
        raise SystemExit("--timeout and --max-bytes must be positive")
    try:
        candidates = load_candidates(args.candidates)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    hosts = {h.strip().lower() for h in args.allow_host if h.strip()} or None
    results = [
        probe_candidate(c, timeout=args.timeout, max_bytes=args.max_bytes, allowed_hosts=hosts)
        for c in candidates
    ]
    summaries = summarize(results)
    write_reports(results, summaries, args.out_dir)

    for summary in summaries:
        print(
            summary["identity"],
            f"discovered={summary['discovered_assets']}/{summary['declared_asset_count']}",
            f"verified={summary['verified_assets']}/{summary['declared_asset_count']}",
            f"sequence_verified={str(summary['sequence_verified']).lower()}",
            f"admissible={str(summary['admissible']).lower()}",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
