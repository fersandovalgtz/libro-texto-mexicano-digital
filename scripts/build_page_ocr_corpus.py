#!/usr/bin/env python3
"""Build a local, page-level OCR corpus from an LTMD source-asset manifest.

The output contains complete OCR text and is intentionally designed for local,
reconstructible research use. Do not commit the generated JSONL by default.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

VERSION = "LTMD_FTRL_OCR_0.1"
DEFAULT_USER_AGENT = "LTMD-FTRL/0.1 (+https://github.com/fersandovalgtz/libro-texto-mexicano-digital)"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_for_search(text: str) -> str:
    """Create a conservative search representation without altering raw OCR."""
    text = unicodedata.normalize("NFKC", text.replace("\u00ad", ""))
    text = re.sub(r"(?<=[^\W\d_])-\s*\n\s*(?=[^\W\d_])", "", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def mean_word_confidence(tsv_path: Path) -> float | None:
    values: list[float] = []
    with tsv_path.open(encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            if row.get("level") != "5" or not (row.get("text") or "").strip():
                continue
            try:
                conf = float(row.get("conf", "-1"))
            except ValueError:
                continue
            if conf >= 0:
                values.append(conf)
    return round(sum(values) / len(values), 6) if values else None


def tesseract_version(executable: str) -> str:
    proc = subprocess.run(
        [executable, "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    return (proc.stdout or proc.stderr).splitlines()[0].strip()


def run_tesseract(
    image_path: Path,
    executable: str,
    language: str,
    psm: int,
) -> tuple[str, float | None]:
    with tempfile.TemporaryDirectory(prefix="ltmd-ftrl-") as tmp:
        output_base = Path(tmp) / "ocr"
        subprocess.run(
            [
                executable,
                str(image_path),
                str(output_base),
                "-l",
                language,
                "--psm",
                str(psm),
                "txt",
                "tsv",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        text = output_base.with_suffix(".txt").read_text(
            encoding="utf-8", errors="replace"
        )
        confidence = mean_word_confidence(output_base.with_suffix(".tsv"))
    return text, confidence


def download_verified(
    url: str,
    destination: Path,
    expected_sha256: str,
    timeout: int,
    user_agent: str,
    force: bool,
) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        if sha256_file(destination) == expected_sha256:
            return destination
        destination.unlink()

    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()

    observed = sha256_bytes(data)
    if observed != expected_sha256:
        raise RuntimeError(
            f"SHA-256 mismatch for {url}: expected {expected_sha256}, observed {observed}"
        )
    destination.write_bytes(data)
    return destination


def load_canonical_keys(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    required = {
        "viewer_key",
        "canonical_processing_viewer_key",
        "is_canonical_processing_object",
        "technical_identity_covered",
    }
    if not rows or not required <= set(rows[0]):
        raise SystemExit(f"processing inventory lacks required columns: {sorted(required)}")
    return {
        row["viewer_key"]
        for row in rows
        if row["is_canonical_processing_object"] == "1"
        and row["technical_identity_covered"] == "1"
    }


def iter_source_rows(
    manifest: Path,
    canonical_keys: set[str] | None,
    wave: str,
    viewer_keys: set[str] | None = None,
) -> Iterable[dict[str, str]]:
    rows = csv.DictReader(manifest.open(encoding="utf-8", newline=""))
    required = {
        "viewer_key",
        "catalog_generation",
        "grade_code",
        "title_core",
        "source_image_index",
        "source_asset_url",
        "asset_status",
        "sha256",
    }
    if rows.fieldnames is None or not required <= set(rows.fieldnames):
        raise SystemExit(f"asset manifest lacks required columns: {sorted(required)}")
    for row in rows:
        if row["asset_status"] != "source_jpeg":
            continue
        if canonical_keys is not None and row["viewer_key"] not in canonical_keys:
            continue
        if viewer_keys is not None and row["viewer_key"] not in viewer_keys:
            continue
        if not SHA256_RE.fullmatch(row["sha256"]):
            raise SystemExit(
                f"invalid source SHA-256 for {row['viewer_key']}:{row['source_image_index']}"
            )
        row["_wave"] = wave
        yield row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-manifest", type=Path, required=True)
    parser.add_argument("--processing-inventory", type=Path)
    parser.add_argument("--wave", required=True, help="LTMD wave identifier, e.g. W5")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--tesseract", default="tesseract")
    parser.add_argument("--language", default="spa")
    parser.add_argument("--psm", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--max-pages", type=int)
    parser.add_argument(
        "--viewer-key",
        action="append",
        dest="viewer_keys",
        help="Restrict processing to one canonical viewer_key; repeat to select several",
    )
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse matching records from an existing output JSONL",
    )
    args = parser.parse_args()

    if shutil.which(args.tesseract) is None:
        raise SystemExit(f"Tesseract executable not found: {args.tesseract}")
    if args.max_pages is not None and args.max_pages < 1:
        raise SystemExit("--max-pages must be >= 1")

    canonical_keys = load_canonical_keys(args.processing_inventory)
    selected_viewers = set(args.viewer_keys) if args.viewer_keys else None
    if selected_viewers is not None and canonical_keys is not None:
        unknown = selected_viewers - canonical_keys
        if unknown:
            raise SystemExit(
                "requested viewer_key values are not canonical source-admitted objects: "
                + ", ".join(sorted(unknown))
            )

    rows = list(
        iter_source_rows(
            args.asset_manifest,
            canonical_keys,
            args.wave,
            selected_viewers,
        )
    )
    rows.sort(
        key=lambda r: (
            int(r["catalog_generation"]),
            int(r["grade_code"]),
            r["viewer_key"],
            int(r["source_image_index"]),
        )
    )
    if args.max_pages is not None:
        rows = rows[: args.max_pages]
    if not rows:
        raise SystemExit("no source-admitted canonical JPEG rows selected")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    engine_version = tesseract_version(args.tesseract)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    reusable: dict[tuple[str, int], dict] = {}
    if args.resume and args.output.exists():
        with args.output.open(encoding="utf-8") as previous:
            for line_number, line in enumerate(previous, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SystemExit(
                        f"cannot resume from invalid JSON at line {line_number}: {exc}"
                    ) from exc
                reusable[(record["viewer_key"], int(record["page_index"]))] = record

    temp_output = args.output.with_name(args.output.name + ".tmp")
    seen: set[tuple[str, int]] = set()
    with temp_output.open("w", encoding="utf-8", newline="\n") as out:
        for number, row in enumerate(rows, 1):
            viewer_key = row["viewer_key"]
            page_index = int(row["source_image_index"])
            page_key = (viewer_key, page_index)
            if page_key in seen:
                raise SystemExit(f"duplicate page identity in manifest: {page_key}")
            seen.add(page_key)

            source_sha = row["sha256"]
            previous = reusable.get(page_key)
            if (
                previous
                and previous.get("source_sha256") == source_sha
                and previous.get("pipeline_version") == VERSION
                and previous.get("ocr_engine_version") == engine_version
                and previous.get("ocr_language") == args.language
                and int(previous.get("ocr_psm", -1)) == args.psm
            ):
                out.write(json.dumps(previous, ensure_ascii=False, sort_keys=True) + "\n")
                print(f"[{number}/{len(rows)}] {previous['page_id']} reused")
                continue

            suffix = Path(row["source_asset_url"]).suffix or ".jpg"
            image_path = (
                args.cache_dir
                / viewer_key
                / f"{page_index:04d}-{source_sha[:12]}{suffix}"
            )
            download_verified(
                row["source_asset_url"],
                image_path,
                source_sha,
                args.timeout,
                args.user_agent,
                args.force_download,
            )

            raw_text, confidence = run_tesseract(
                image_path, args.tesseract, args.language, args.psm
            )
            search_text = normalize_for_search(raw_text)
            record = {
                "schema_version": "LTMD_PAGE_OCR_0.1",
                "pipeline_version": VERSION,
                "page_id": f"{viewer_key}:src{page_index:04d}",
                "viewer_key": viewer_key,
                "canonical_viewer_key": viewer_key,
                "wave": args.wave,
                "catalog_generation": int(row["catalog_generation"]),
                "grade_code": int(row["grade_code"]),
                "title_core": row["title_core"],
                "page_index": page_index,
                "viewer_page": (
                    int(row["viewer_page"])
                    if (row.get("viewer_page") or "").isdigit()
                    else None
                ),
                "source_asset_url": row["source_asset_url"],
                "source_sha256": source_sha,
                "source_byte_size": (
                    int(row["byte_size"])
                    if (row.get("byte_size") or "").isdigit()
                    else None
                ),
                "ocr_engine": "tesseract",
                "ocr_engine_version": engine_version,
                "ocr_language": args.language,
                "ocr_psm": args.psm,
                "ocr_text_raw": raw_text,
                "ocr_sha256": sha256_bytes(raw_text.encode("utf-8")),
                "search_text": search_text,
                "search_text_sha256": sha256_bytes(search_text.encode("utf-8")),
                "ocr_confidence_mean": confidence,
                "ocr_char_count": len(raw_text),
                "ocr_word_count": len(re.findall(r"\S+", raw_text)),
                "generated_at": generated_at,
            }
            out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            print(
                f"[{number}/{len(rows)}] {record['page_id']} "
                f"chars={record['ocr_char_count']} conf={confidence}"
            )

    temp_output.replace(args.output)
    print(f"Wrote {len(rows)} OCR page records to {args.output}")


if __name__ == "__main__":
    main()
