#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

DEFAULT_ASSETS = Path("data/catalog/ltmd_u2_asset_resolution_2026_09_02.csv")
DEFAULT_CSV = Path("u2-page-count-resolution-probe.csv")
DEFAULT_JSON = Path("u2-page-count-resolution-probe.json")
EXPECTED_OBJECTS = 39

FIELDS = [
    "source_object_id",
    "viewer_key",
    "asset_url",
    "observed_at",
    "page_count_state",
    "page_count",
    "remote_total_bytes",
    "network_bytes_fetched",
    "range_requests",
    "max_network_bytes",
    "startxref_offset",
    "xref_kind",
    "xref_sections_traversed",
    "root_ref",
    "pages_ref",
    "method",
    "source_admission_state",
    "text_verification_state",
    "evidence_scope",
    "error",
]


def read_assets(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_OBJECTS:
        raise RuntimeError(f"expected {EXPECTED_OBJECTS} U2 assets, got {len(rows)}")
    ids = [row["source_object_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("source_object_id values are not unique")
    if any(row.get("asset_resolution_state") != "resolved_pdf" for row in rows):
        raise RuntimeError("batch page-count probe requires resolved_pdf for all input objects")
    return rows


def ref_text(value: object) -> str:
    if isinstance(value, list) and len(value) == 2:
        return f"{value[0]} {value[1]} R"
    return "not_observed"


def run_one(
    row: dict[str, str],
    *,
    observed_at: str,
    max_bytes: int,
    xref_window: int,
    tail_bytes: int,
    object_window: int,
    timeout: float,
    workdir: Path,
) -> dict[str, object]:
    key = row["viewer_key"]
    output = workdir / f"{key}.json"
    cmd = [
        sys.executable,
        "scripts/probe_u2_classic_xref_page_count.py",
        "--viewer-key", key,
        "--cycle", "2026",
        "--level", "primaria",
        "--tail-bytes", str(tail_bytes),
        "--xref-window", str(xref_window),
        "--object-window", str(object_window),
        "--max-bytes", str(max_bytes),
        "--timeout", str(timeout),
        "--observed-at", observed_at,
        "--output", str(output),
    ]
    completed = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
    if not output.exists():
        return {
            "schema": "LTMD_U2_CLASSIC_XREF_PAGE_COUNT_PILOT_0.1",
            "source_object_id": row["source_object_id"],
            "asset_url": row["asset_url"],
            "observed_at": observed_at,
            "page_count_state": "runner_error",
            "page_count": None,
            "method": "targeted_tail_startxref_classic_xref_catalog_pages_count",
            "remote_total_bytes": int(row["total_bytes"]),
            "network_bytes_fetched": 0,
            "range_requests": 0,
            "max_network_bytes": max_bytes,
            "startxref_offset": None,
            "xref_kind": None,
            "xref_sections_traversed": 0,
            "root_ref": None,
            "pages_ref": None,
            "error": f"child probe produced no JSON; returncode={completed.returncode}; output={completed.stdout[-1000:]}",
            "source_admission_state": "not_assessed",
            "text_verification_state": "not_assessed",
            "evidence_scope": "structural trailer/xref/catalog/root-/Pages-/Count only; no page enumeration, text extraction, OCR, or semantic validation",
        }
    result = json.loads(output.read_text(encoding="utf-8"))
    if result["source_object_id"] != row["source_object_id"]:
        raise RuntimeError(f"{key}: child source identity mismatch")
    if result["asset_url"] != row["asset_url"]:
        raise RuntimeError(f"{key}: child asset URL mismatch")
    if int(result["remote_total_bytes"]) != int(row["total_bytes"]):
        raise RuntimeError(f"{key}: remote byte length changed from asset-resolution observation")
    return result


def to_csv_row(row: dict[str, str], result: dict[str, object]) -> dict[str, str]:
    return {
        "source_object_id": row["source_object_id"],
        "viewer_key": row["viewer_key"],
        "asset_url": row["asset_url"],
        "observed_at": str(result.get("observed_at") or "not_observed"),
        "page_count_state": str(result.get("page_count_state") or "not_observed"),
        "page_count": str(result["page_count"]) if result.get("page_count") is not None else "not_observed",
        "remote_total_bytes": str(result["remote_total_bytes"]) if result.get("remote_total_bytes") is not None else "not_observed",
        "network_bytes_fetched": str(result.get("network_bytes_fetched", 0)),
        "range_requests": str(result.get("range_requests", 0)),
        "max_network_bytes": str(result.get("max_network_bytes", "not_observed")),
        "startxref_offset": str(result["startxref_offset"]) if result.get("startxref_offset") is not None else "not_observed",
        "xref_kind": str(result.get("xref_kind") or "not_observed"),
        "xref_sections_traversed": str(result.get("xref_sections_traversed", 0)),
        "root_ref": ref_text(result.get("root_ref")),
        "pages_ref": ref_text(result.get("pages_ref")),
        "method": str(result.get("method") or "not_observed"),
        "source_admission_state": str(result.get("source_admission_state") or "not_assessed"),
        "text_verification_state": str(result.get("text_verification_state") or "not_assessed"),
        "evidence_scope": str(result.get("evidence_scope") or "not_observed"),
        "error": str(result["error"]) if result.get("error") else "none",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch bounded structural page-count probe for all 39 LTMD-U2 PDF assets.")
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--max-bytes", type=int, default=4194304)
    parser.add_argument("--xref-window", type=int, default=3145728)
    parser.add_argument("--tail-bytes", type=int, default=65536)
    parser.add_argument("--object-window", type=int, default=65536)
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    assets = read_assets(args.assets)
    results: list[dict[str, object]] = []
    csv_rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="ltmd-u2-page-count-") as tmp:
        workdir = Path(tmp)
        for index, row in enumerate(assets, start=1):
            result = run_one(
                row,
                observed_at=args.observed_at,
                max_bytes=args.max_bytes,
                xref_window=args.xref_window,
                tail_bytes=args.tail_bytes,
                object_window=args.object_window,
                timeout=args.timeout,
                workdir=workdir,
            )
            results.append(result)
            csv_rows.append(to_csv_row(row, result))
            print(
                f"[{index:02d}/{len(assets)}] {row['viewer_key']} "
                f"state={result.get('page_count_state')} pages={result.get('page_count')} "
                f"net={result.get('network_bytes_fetched')}"
            )

    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)

    states = Counter(str(result.get("page_count_state")) for result in results)
    summary = {
        "schema": "LTMD_U2_PAGE_COUNT_BATCH_PROBE_0.1",
        "observed_at": args.observed_at,
        "input_asset_registry": str(args.assets),
        "total_objects": len(results),
        "states": dict(sorted(states.items())),
        "observed_page_counts": sum(result.get("page_count") is not None for result in results),
        "total_network_bytes_fetched": sum(int(result.get("network_bytes_fetched") or 0) for result in results),
        "max_network_bytes_per_object": args.max_bytes,
        "method": "targeted_tail_startxref_classic_xref_catalog_pages_count",
        "source_pdf_bytes_persisted": False,
        "source_admission_state": "not_assessed",
        "text_verification_state": "not_assessed",
        "evidence_scope": "structural page-count evidence only; no page enumeration, text extraction, OCR, licensing inference, or semantic validation",
        "results": results,
    }
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, ensure_ascii=False))
    return 0 if states == {"observed": EXPECTED_OBJECTS} else 2


if __name__ == "__main__":
    raise SystemExit(main())
