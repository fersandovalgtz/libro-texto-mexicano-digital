#!/usr/bin/env python3
"""Normalize heterogeneous LTMD U1 source manifests into one universal FTRL contract.

This command never probes or downloads source assets. It only reconciles already-audited
manifests against the global LTMD coverage/identity topology and emits text-free metadata.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

VERSION = "LTMD_FTRL_SOURCE_0.1"
IDENTITY_VERSION = "LTMD_FTRL_IDENTITY_0.1"
SUMMARY_VERSION = "LTMD_FTRL_SOURCE_NORMALIZATION_0.1"
SHA256_LEN = 64

SOURCE_FIELDS = [
    "schema_version",
    "source_ids",
    "wave",
    "operational_domain",
    "viewer_key",
    "canonical_viewer_key",
    "catalog_generation",
    "grade_code",
    "title_core",
    "viewer_page",
    "source_image_index",
    "source_asset_url",
    "asset_status",
    "byte_size",
    "sha256",
    "source_manifest_paths",
]

IDENTITY_FIELDS = [
    "identity_version",
    "viewer_key",
    "canonical_viewer_key",
    "catalog_generation",
    "grade_code",
    "title_core",
    "operational_domain",
    "coverage_mode",
    "source_url",
]

REGISTRY_REQUIRED = {
    "registry_version",
    "source_id",
    "wave",
    "operational_domain",
    "asset_manifest_path",
    "viewer_key_column",
    "catalog_generation_column",
    "grade_column",
    "title_column",
    "viewer_page_column",
    "source_index_column",
    "url_column",
    "status_column",
    "admitted_status",
    "byte_size_column",
    "sha256_column",
    "default_enabled",
    "notes",
}

COVERAGE_REQUIRED = {
    "viewer_key",
    "catalog_generation",
    "grade_code",
    "title_core",
    "operational_domain",
    "source_url",
}

QUEUE_REQUIRED = {
    "viewer_key",
    "catalog_generation",
    "grade_code",
    "title_core",
    "operational_domain",
    "effective_fragseg_coverage",
    "coverage_inherited_from_viewer",
    "source_url",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path, required: set[str] | None = None) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise SystemExit(f"missing required CSV: {path}")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit(f"CSV has no header: {path}")
        fields = list(reader.fieldnames)
        if required and not required <= set(fields):
            missing = sorted(required - set(fields))
            raise SystemExit(f"{path} lacks required columns: {missing}")
        rows = [dict(row) for row in reader]
    return rows, fields


def parse_int(value: str, label: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"invalid integer for {label}: {value!r}") from exc


def validate_sha(value: str, label: str) -> str:
    value = str(value).strip().lower()
    if len(value) != SHA256_LEN or any(ch not in "0123456789abcdef" for ch in value):
        raise SystemExit(f"invalid SHA-256 for {label}: {value!r}")
    return value


def write_csv_atomic(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def load_coverage(path: Path) -> dict[str, dict[str, str]]:
    rows, _ = read_csv(path, COVERAGE_REQUIRED)
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row["viewer_key"].strip()
        if not key:
            raise SystemExit(f"coverage row without viewer_key in {path}")
        if key in result:
            raise SystemExit(f"duplicate viewer_key in coverage registry: {key}")
        result[key] = row
    return result


def load_identity_topology(path: Path) -> tuple[set[str], dict[str, str], list[dict[str, str]]]:
    rows, _ = read_csv(path, QUEUE_REQUIRED)
    direct: set[str] = set()
    identity_to_canonical: dict[str, str] = {}
    covered_rows: list[dict[str, str]] = []

    for row in rows:
        viewer = row["viewer_key"].strip()
        if row["effective_fragseg_coverage"].strip() != "1":
            continue
        inherited = row["coverage_inherited_from_viewer"].strip()
        canonical = inherited or viewer
        identity_to_canonical[viewer] = canonical
        covered_rows.append(row)
        if not inherited:
            direct.add(viewer)

    dangling = sorted({canonical for canonical in identity_to_canonical.values() if canonical not in direct})
    if dangling:
        raise SystemExit(
            "identity topology points to canonical viewers without direct effective coverage: "
            + ", ".join(dangling[:20])
        )
    return direct, identity_to_canonical, covered_rows


def resolve_source_value(row: dict[str, str], column: str, label: str) -> str:
    if not column:
        return ""
    if column not in row:
        raise SystemExit(f"configured column {column!r} missing while reading {label}")
    return str(row.get(column) or "").strip()


def normalize_registry_row(
    cfg: dict[str, str],
    manifest_row: dict[str, str],
    coverage: dict[str, dict[str, str]],
    direct_viewers: set[str],
) -> dict | None:
    viewer = resolve_source_value(manifest_row, cfg["viewer_key_column"], cfg["source_id"])
    if not viewer or viewer not in direct_viewers:
        return None

    status = resolve_source_value(manifest_row, cfg["status_column"], cfg["source_id"])
    if status != cfg["admitted_status"].strip():
        return None

    metadata = coverage.get(viewer)
    if metadata is None:
        raise SystemExit(f"source viewer {viewer} is absent from global coverage registry")

    generation = parse_int(
        resolve_source_value(manifest_row, cfg["catalog_generation_column"], cfg["source_id"]),
        f"{cfg['source_id']}:{viewer}:catalog_generation",
    )
    grade = parse_int(
        resolve_source_value(manifest_row, cfg["grade_column"], cfg["source_id"]),
        f"{cfg['source_id']}:{viewer}:grade",
    )
    source_index = parse_int(
        resolve_source_value(manifest_row, cfg["source_index_column"], cfg["source_id"]),
        f"{cfg['source_id']}:{viewer}:source_image_index",
    )

    viewer_page_raw = resolve_source_value(
        manifest_row, cfg["viewer_page_column"], cfg["source_id"]
    )
    viewer_page = ""
    if viewer_page_raw:
        viewer_page = parse_int(
            viewer_page_raw, f"{cfg['source_id']}:{viewer}:viewer_page"
        )

    title = resolve_source_value(manifest_row, cfg["title_column"], cfg["source_id"])
    if not title:
        title = metadata["title_core"].strip()
    if not title:
        raise SystemExit(f"cannot resolve title_core for {viewer}")

    expected_generation = parse_int(metadata["catalog_generation"], f"coverage:{viewer}:generation")
    expected_grade = parse_int(metadata["grade_code"], f"coverage:{viewer}:grade")
    if generation != expected_generation or grade != expected_grade:
        raise SystemExit(
            f"metadata mismatch for {viewer}: source=({generation},{grade}) "
            f"coverage=({expected_generation},{expected_grade})"
        )

    domain = cfg["operational_domain"].strip()
    coverage_domain = metadata["operational_domain"].strip()
    if domain != coverage_domain:
        raise SystemExit(
            f"operational_domain mismatch for {viewer}: registry={domain} coverage={coverage_domain}"
        )

    url = resolve_source_value(manifest_row, cfg["url_column"], cfg["source_id"])
    if not url:
        raise SystemExit(f"empty source URL for {cfg['source_id']}:{viewer}:src{source_index:04d}")

    sha = validate_sha(
        resolve_source_value(manifest_row, cfg["sha256_column"], cfg["source_id"]),
        f"{cfg['source_id']}:{viewer}:src{source_index:04d}",
    )
    byte_size_raw = resolve_source_value(
        manifest_row, cfg["byte_size_column"], cfg["source_id"]
    )
    byte_size = ""
    if byte_size_raw:
        byte_size = parse_int(
            byte_size_raw, f"{cfg['source_id']}:{viewer}:src{source_index:04d}:byte_size"
        )
        if byte_size < 0:
            raise SystemExit(f"negative byte_size for {viewer}:src{source_index:04d}")

    return {
        "schema_version": VERSION,
        "source_ids": cfg["source_id"].strip(),
        "wave": cfg["wave"].strip(),
        "operational_domain": domain,
        "viewer_key": viewer,
        "canonical_viewer_key": viewer,
        "catalog_generation": generation,
        "grade_code": grade,
        "title_core": title,
        "viewer_page": viewer_page,
        "source_image_index": source_index,
        "source_asset_url": url,
        "asset_status": "source_jpeg",
        "byte_size": byte_size,
        "sha256": sha,
        "source_manifest_paths": cfg["asset_manifest_path"].strip(),
    }


def build_identity_rows(
    covered_rows: list[dict[str, str]],
    represented_canonicals: set[str],
    coverage: dict[str, dict[str, str]],
) -> list[dict]:
    output: list[dict] = []
    for row in covered_rows:
        viewer = row["viewer_key"].strip()
        inherited = row["coverage_inherited_from_viewer"].strip()
        canonical = inherited or viewer
        if canonical not in represented_canonicals:
            continue
        metadata = coverage.get(viewer)
        if metadata is None:
            raise SystemExit(f"identity viewer absent from coverage registry: {viewer}")
        output.append(
            {
                "identity_version": IDENTITY_VERSION,
                "viewer_key": viewer,
                "canonical_viewer_key": canonical,
                "catalog_generation": parse_int(metadata["catalog_generation"], f"identity:{viewer}:generation"),
                "grade_code": parse_int(metadata["grade_code"], f"identity:{viewer}:grade"),
                "title_core": metadata["title_core"].strip(),
                "operational_domain": metadata["operational_domain"].strip(),
                "coverage_mode": "inherited_alias" if inherited else "direct",
                "source_url": metadata["source_url"].strip(),
            }
        )
    output.sort(
        key=lambda row: (
            row["operational_domain"],
            int(row["catalog_generation"]),
            int(row["grade_code"]),
            row["viewer_key"],
        )
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/catalog/ltmd_u1_ftrl_source_registry.csv"),
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=Path("data/catalog/ltmd_u1_coverage.csv"),
    )
    parser.add_argument(
        "--identity-topology",
        type=Path,
        default=Path("data/catalog/ltmd_u1_wave_queue.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/catalog/ltmd_u1_ftrl_source_manifest.csv"),
    )
    parser.add_argument(
        "--identity-output",
        type=Path,
        default=Path("data/catalog/ltmd_u1_ftrl_identity_map.csv"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("data/catalog/ltmd_u1_ftrl_source_summary.json"),
    )
    parser.add_argument(
        "--source-id",
        action="append",
        dest="source_ids",
        help="Normalize only selected registry source_id values; repeat as needed",
    )
    args = parser.parse_args()

    registry_rows, registry_fields = read_csv(args.registry, REGISTRY_REQUIRED)
    if not registry_rows:
        raise SystemExit("FTRL source registry is empty")
    versions = {row["registry_version"].strip() for row in registry_rows}
    if versions != {"LTMD_U1_FTRL_SOURCE_REGISTRY_0.1"}:
        raise SystemExit(f"unexpected source registry versions: {sorted(versions)}")

    requested = set(args.source_ids or [])
    available = {row["source_id"].strip() for row in registry_rows}
    unknown = sorted(requested - available)
    if unknown:
        raise SystemExit("unknown source_id values: " + ", ".join(unknown))

    selected_registry = [
        row
        for row in registry_rows
        if (row["source_id"].strip() in requested if requested else row["default_enabled"].strip() == "1")
    ]
    if not selected_registry:
        raise SystemExit("no FTRL source datasets selected")

    coverage = load_coverage(args.coverage)
    direct_viewers, identity_to_canonical, covered_rows = load_identity_topology(
        args.identity_topology
    )

    normalized: dict[tuple[str, int], dict] = {}
    duplicate_identical = 0
    source_stats: list[dict] = []
    admitted_by_wave: Counter[str] = Counter()
    admitted_by_domain: Counter[str] = Counter()

    for cfg in selected_registry:
        source_id = cfg["source_id"].strip()
        manifest_path = Path(cfg["asset_manifest_path"].strip())
        rows, fields = read_csv(manifest_path)

        configured_columns = [
            cfg["viewer_key_column"],
            cfg["catalog_generation_column"],
            cfg["grade_column"],
            cfg["viewer_page_column"],
            cfg["source_index_column"],
            cfg["url_column"],
            cfg["status_column"],
            cfg["byte_size_column"],
            cfg["sha256_column"],
        ]
        if cfg["title_column"].strip():
            configured_columns.append(cfg["title_column"])
        missing_columns = sorted({column for column in configured_columns if column and column not in fields})
        if missing_columns:
            raise SystemExit(
                f"{source_id} registry mapping references absent columns in {manifest_path}: "
                + ", ".join(missing_columns)
            )

        selected_count = 0
        direct_viewers_seen: set[str] = set()
        for raw in rows:
            record = normalize_registry_row(cfg, raw, coverage, direct_viewers)
            if record is None:
                continue
            selected_count += 1
            direct_viewers_seen.add(record["viewer_key"])
            key = (record["viewer_key"], int(record["source_image_index"]))
            previous = normalized.get(key)
            if previous is None:
                normalized[key] = record
            else:
                if previous["sha256"] != record["sha256"]:
                    raise SystemExit(
                        f"conflicting admitted bytes for {key}: "
                        f"{previous['source_ids']}={previous['sha256']} vs "
                        f"{record['source_ids']}={record['sha256']}"
                    )
                duplicate_identical += 1
                source_ids = sorted(set(previous["source_ids"].split("|")) | {record["source_ids"]})
                source_paths = sorted(
                    set(previous["source_manifest_paths"].split("|"))
                    | {record["source_manifest_paths"]}
                )
                previous["source_ids"] = "|".join(source_ids)
                previous["source_manifest_paths"] = "|".join(source_paths)

        source_stats.append(
            {
                "source_id": source_id,
                "wave": cfg["wave"].strip(),
                "operational_domain": cfg["operational_domain"].strip(),
                "manifest_path": str(manifest_path),
                "manifest_rows": len(rows),
                "admitted_direct_rows": selected_count,
                "direct_viewers": len(direct_viewers_seen),
                "manifest_sha256": sha256_file(manifest_path),
            }
        )

    output_rows = list(normalized.values())
    output_rows.sort(
        key=lambda row: (
            row["wave"],
            row["operational_domain"],
            int(row["catalog_generation"]),
            int(row["grade_code"]),
            row["viewer_key"],
            int(row["source_image_index"]),
        )
    )
    if not output_rows:
        raise SystemExit("normalization produced no admitted source rows")

    for row in output_rows:
        admitted_by_wave[row["wave"]] += 1
        admitted_by_domain[row["operational_domain"]] += 1

    represented_canonicals = {row["viewer_key"] for row in output_rows}
    identity_rows = build_identity_rows(covered_rows, represented_canonicals, coverage)
    represented_identities = {row["viewer_key"] for row in identity_rows}

    direct_without_source = sorted(direct_viewers - represented_canonicals)
    inherited_without_source = sorted(
        viewer
        for viewer, canonical in identity_to_canonical.items()
        if canonical not in represented_canonicals
    )

    write_csv_atomic(args.output, SOURCE_FIELDS, output_rows)
    write_csv_atomic(args.identity_output, IDENTITY_FIELDS, identity_rows)

    summary = {
        "schema_version": SUMMARY_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "registry_version": next(iter(versions)),
        "registry_sha256": sha256_file(args.registry),
        "coverage_sha256": sha256_file(args.coverage),
        "identity_topology_sha256": sha256_file(args.identity_topology),
        "selected_source_datasets": len(selected_registry),
        "normalized_source_rows": len(output_rows),
        "represented_canonical_viewers": len(represented_canonicals),
        "represented_historical_identities": len(represented_identities),
        "identical_duplicate_rows_collapsed": duplicate_identical,
        "source_rows_by_wave": dict(sorted(admitted_by_wave.items())),
        "source_rows_by_domain": dict(sorted(admitted_by_domain.items())),
        "global_direct_effective_viewers": len(direct_viewers),
        "global_effective_identities": len(identity_to_canonical),
        "direct_effective_viewers_without_registered_source_rows": direct_without_source,
        "effective_identities_without_registered_source_rows": inherited_without_source,
        "source_datasets": source_stats,
        "outputs": {
            "source_manifest": str(args.output),
            "identity_map": str(args.identity_output),
        },
        "interpretive_limit": (
            "Normalization records technical source admissibility and identity topology only. "
            "It does not assert semantic equivalence, OCR accuracy, or completeness beyond the "
            "registered audited source manifests."
        ),
    }
    write_json_atomic(args.summary_output, summary)

    print(
        json.dumps(
            {
                "status": "ok",
                "source_datasets": len(selected_registry),
                "source_rows": len(output_rows),
                "canonical_viewers": len(represented_canonicals),
                "historical_identities": len(represented_identities),
                "global_direct_without_source_rows": len(direct_without_source),
                "global_identities_without_source_rows": len(inherited_without_source),
                "duplicates_collapsed": duplicate_identical,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
