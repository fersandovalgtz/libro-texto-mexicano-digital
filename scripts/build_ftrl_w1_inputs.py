#!/usr/bin/env python3
"""Build normalized, text-free FTRL inputs for exhaustive LTMD-U1 W1.

W1 Ciencias Naturales has 40 historical identities in the master LTMD-U1
coverage denominator. The original family-readiness register documents 37 of
those identities. This normalizer preserves that register as historical evidence
and explicitly supplements it with three already-materialized, versioned source
layers:

* H1966P6CI374 and H1966P6CI375 from the W1-1966 SHA-256 page manifest;
* H1993P6CI209 / LTMD-CN6-G1993-DH from the audited CN46 manifest.

The resulting FTRL cohort is exhaustive for the current W1 denominator. The
script performs no network access and emits no OCR text.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

READINESS = Path("data/catalog/ciencias_naturales_family_asset_readiness.csv")
COVERAGE = Path("data/catalog/ltmd_u1_coverage.csv")
DIRECT_MANIFEST = Path("data/catalog/ciencias_naturales_pending_page_manifest.csv")
W1966_MANIFEST = Path("data/catalog/ltmd_u1_w1_1966_page_manifest.csv")
W1966_SUMMARY = Path("data/catalog/ltmd_u1_w1_1966_page_manifest_summary.csv")
CN46_MANIFEST = Path("data/expansion/cn46_page_manifest.csv")
CN46_SUMMARY = Path("data/expansion/cn46_page_manifest_summary.csv")
CN5_SHA_DIR = Path("data/catalog/cn5_pilot_sha")
VERSION = "LTMD_U1_W1_FTRL_INPUTS_0.2"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_HISTORICAL = 40
EXPECTED_ALIASES = 4
EXPECTED_CANONICAL = 36
EXPECTED_SOURCE_PAGES = 6516
EXPECTED_INTERNAL_GAPS = 3
SUPPLEMENTAL_VIEWERS = {"H1966P6CI374", "H1966P6CI375", "H1993P6CI209"}
PILOT_BOOKS = {
    "LTMD-CN5-G1972",
    "LTMD-CN5-G1988",
    "LTMD-CN5-G1993",
    "LTMD-CN5-G2014",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def as_int(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value == "":
        raise AssertionError(f"missing integer field {key}: {row}")
    return int(value)


def source_url(viewer_key: str, source_image_index: int) -> str:
    return (
        "https://historico.conaliteg.gob.mx/c/"
        f"{viewer_key}/{source_image_index:03d}.jpg"
    )


def exhaustive_readiness() -> list[dict[str, str]]:
    """Return the 40-identity W1 processing cohort without rewriting legacy data."""
    legacy = read_csv(READINESS)
    coverage = [
        row for row in read_csv(COVERAGE)
        if row.get("operational_domain") == "ciencias_naturales"
    ]
    if len(coverage) != EXPECTED_HISTORICAL:
        raise AssertionError(
            f"W1 master denominator drift: {len(coverage)} != {EXPECTED_HISTORICAL}"
        )

    by_viewer = {row["viewer_key"]: row for row in legacy}
    if len(by_viewer) != len(legacy):
        raise AssertionError("duplicate viewer_key in legacy W1 readiness")
    coverage_by_viewer = {row["viewer_key"]: row for row in coverage}
    if len(coverage_by_viewer) != len(coverage):
        raise AssertionError("duplicate viewer_key in W1 master denominator")
    if not set(by_viewer) <= set(coverage_by_viewer):
        raise AssertionError(
            f"legacy readiness contains non-W1 identities: "
            f"{sorted(set(by_viewer) - set(coverage_by_viewer))}"
        )

    missing = set(coverage_by_viewer) - set(by_viewer)
    if missing != SUPPLEMENTAL_VIEWERS:
        raise AssertionError(
            f"unexpected W1 supplemental identity set: {sorted(missing)}"
        )

    w1966 = {row["viewer_key"]: row for row in read_csv(W1966_SUMMARY)}
    cn46 = {row["viewer_key"]: row for row in read_csv(CN46_SUMMARY)}

    for viewer_key in sorted(missing):
        cov = coverage_by_viewer[viewer_key]
        if cov.get("asset_resolved_full") != "1" or cov.get("page_manifest_ready") != "1":
            raise AssertionError(f"supplemental W1 source is not materialized: {viewer_key}")
        if cov.get("ocr_ready") != "1":
            raise AssertionError(f"supplemental W1 source is not OCR-ready: {viewer_key}")

        if viewer_key in w1966:
            src = w1966[viewer_key]
            strategy = "w1_1966_sha256_manifest"
            internal_unserved = as_int(src, "internal_unserved")
            grade = src["grade_code"]
        elif viewer_key == "H1993P6CI209" and viewer_key in cn46:
            src = cn46[viewer_key]
            strategy = "existing_pilot_or_cn46_manifest"
            internal_unserved = 0
            grade = src["grade"]
        else:
            raise AssertionError(f"no versioned supplemental source for {viewer_key}")

        if src["book_id"] != cov["book_id"]:
            raise AssertionError(
                f"book_id mismatch for {viewer_key}: {src['book_id']} != {cov['book_id']}"
            )
        if src["catalog_generation"] != cov["catalog_generation"]:
            raise AssertionError(f"generation mismatch for {viewer_key}")
        if grade != cov["grade_code"]:
            raise AssertionError(f"grade mismatch for {viewer_key}")
        if as_int(src, "unique_source_hashes") != as_int(src, "source_jpegs"):
            raise AssertionError(f"non-unique supplemental SHA-256 set: {viewer_key}")

        row = {
            "book_id": cov["book_id"],
            "viewer_key": viewer_key,
            "catalog_generation": cov["catalog_generation"],
            "grade": cov["grade_code"],
            "viewer_positions_declared": src["viewer_positions"],
            "resolved_source_assets": src["source_jpegs"],
            "terminal_synthetic": src["terminal_synthetic"],
            "internal_unserved_positions": str(internal_unserved),
            "asset_strategy": strategy,
            "asset_readiness": "full_versioned_sha256_source",
            "alias_to_book_id": "",
            "exhaustive_source_basis": (
                "ltmd_u1_w1_1966_page_manifest"
                if viewer_key in w1966
                else "cn46_page_manifest"
            ),
        }
        legacy.append(row)

    exhaustive_viewers = {row["viewer_key"] for row in legacy}
    if exhaustive_viewers != set(coverage_by_viewer):
        raise AssertionError("exhaustive W1 identity reconciliation failed")
    return legacy


def normalized_asset_row(
    *,
    readiness: dict[str, str],
    viewer_page: int,
    source_image_index: int,
    source_asset_url: str,
    byte_size: int,
    sha256: str,
    source_layer: str,
    http_status: str = "200",
    content_type: str = "image/jpeg",
) -> dict[str, str | int]:
    if not SHA256_RE.fullmatch(sha256):
        raise AssertionError(
            f"invalid SHA-256 for {readiness['book_id']}:{source_image_index}"
        )
    if byte_size <= 0:
        raise AssertionError(
            f"non-positive byte size for {readiness['book_id']}:{source_image_index}"
        )
    return {
        "audit_version": VERSION,
        "book_id": readiness["book_id"],
        "viewer_key": readiness["viewer_key"],
        "catalog_generation": as_int(readiness, "catalog_generation"),
        "grade_code": as_int(readiness, "grade"),
        "title_core": "Ciencias Naturales",
        "viewer_ui": "normalized_w1_exhaustive",
        "ag_clave": readiness["viewer_key"],
        "viewer_page": viewer_page,
        "declared_positions": as_int(readiness, "viewer_positions_declared"),
        "source_image_index": source_image_index,
        "source_asset_url": source_asset_url,
        "is_final_declared_position": int(
            viewer_page == as_int(readiness, "viewer_positions_declared")
        ),
        "asset_status": "source_jpeg",
        "probe_state": "versioned_sha256_provenance",
        "http_status": http_status,
        "content_type": content_type,
        "byte_size": byte_size,
        "sha256": sha256,
        "attempts": "",
        "error": "",
        "source_layer": source_layer,
    }


def load_direct_rows(
    readiness_by_id: dict[str, dict[str, str]], canonical: set[str]
) -> dict[str, list[dict[str, str | int]]]:
    selected = {
        bid
        for bid in canonical
        if readiness_by_id[bid]["asset_strategy"]
        in {"direct_sha256_manifest", "direct_manifest_plus_focused_gap_audit"}
    }
    out = {bid: [] for bid in selected}
    for row in read_csv(DIRECT_MANIFEST):
        bid = row["book_id"]
        if bid not in selected or row["asset_status"] != "source_jpeg":
            continue
        r = readiness_by_id[bid]
        out[bid].append(
            normalized_asset_row(
                readiness=r,
                viewer_page=as_int(row, "viewer_page"),
                source_image_index=as_int(row, "source_image_index"),
                source_asset_url=row["source_asset_url"],
                byte_size=as_int(row, "byte_size"),
                sha256=row["sha256"],
                source_layer="ciencias_naturales_pending_page_manifest",
                http_status=row.get("http_status", "200"),
                content_type=row.get("content_type", "image/jpeg"),
            )
        )
    return out


def load_1966_rows(
    readiness_by_id: dict[str, dict[str, str]], canonical: set[str]
) -> dict[str, list[dict[str, str | int]]]:
    selected = {
        bid
        for bid in canonical
        if readiness_by_id[bid]["asset_strategy"] == "w1_1966_sha256_manifest"
    }
    out = {bid: [] for bid in selected}
    for row in read_csv(W1966_MANIFEST):
        bid = row["book_id"]
        if bid not in selected or row["asset_status"] != "source_jpeg":
            continue
        r = readiness_by_id[bid]
        out[bid].append(
            normalized_asset_row(
                readiness=r,
                viewer_page=as_int(row, "viewer_page"),
                source_image_index=as_int(row, "source_image_index"),
                source_asset_url=row["source_asset_url"],
                byte_size=as_int(row, "byte_size"),
                sha256=row["sha256"],
                source_layer="ltmd_u1_w1_1966_page_manifest",
                http_status=row.get("http_status", "200"),
                content_type=row.get("content_type", "image/jpeg"),
            )
        )
    return out


def load_cn46_rows(
    readiness_by_id: dict[str, dict[str, str]], canonical: set[str]
) -> dict[str, list[dict[str, str | int]]]:
    selected = {
        bid
        for bid in canonical
        if readiness_by_id[bid]["asset_strategy"] == "existing_pilot_or_cn46_manifest"
        and bid not in PILOT_BOOKS
    }
    out = {bid: [] for bid in selected}
    for row in read_csv(CN46_MANIFEST):
        bid = row["book_id"]
        if bid not in selected or row["asset_status"] != "source_jpeg":
            continue
        r = readiness_by_id[bid]
        out[bid].append(
            normalized_asset_row(
                readiness=r,
                viewer_page=as_int(row, "viewer_page"),
                source_image_index=as_int(row, "source_image_index"),
                source_asset_url=row["source_asset_url"],
                byte_size=as_int(row, "byte_size"),
                sha256=row["sha256"],
                source_layer="cn46_page_manifest",
                http_status=row.get("http_status", "200"),
                content_type=row.get("content_type", "image/jpeg"),
            )
        )
    return out


def load_cn5_anchor_rows(
    readiness_by_id: dict[str, dict[str, str]], canonical: set[str]
) -> dict[str, list[dict[str, str | int]]]:
    selected = PILOT_BOOKS & canonical
    if selected != PILOT_BOOKS:
        raise AssertionError(f"pilot canonical set drifted: {sorted(selected)}")
    out = {bid: [] for bid in selected}
    files = sorted(CN5_SHA_DIR.glob("*.csv"))
    if len(files) != 9:
        raise AssertionError(f"expected 9 compact CN5 anchor files, found {len(files)}")
    for path in files:
        match = re.match(r"^(LTMD-CN5-G\d{4})-part\d+\.csv$", path.name)
        if not match:
            raise AssertionError(f"unexpected CN5 anchor filename: {path.name}")
        bid = match.group(1)
        if bid not in selected:
            raise AssertionError(f"unexpected CN5 anchor book: {bid}")
        r = readiness_by_id[bid]
        for row in read_csv(path):
            index = as_int(row, "source_image_index")
            out[bid].append(
                normalized_asset_row(
                    readiness=r,
                    viewer_page=as_int(row, "viewer_page"),
                    source_image_index=index,
                    source_asset_url=source_url(r["viewer_key"], index),
                    byte_size=as_int(row, "byte_size"),
                    sha256=row["sha256"],
                    source_layer="cn5_pilot_sha_anchor",
                )
            )
    return out


def build_processing_rows(
    readiness: list[dict[str, str]],
) -> list[dict[str, str | int]]:
    by_id = {row["book_id"]: row for row in readiness}
    rows: list[dict[str, str | int]] = []
    for row in readiness:
        alias_target = row["alias_to_book_id"]
        canonical = by_id[alias_target] if alias_target else row
        is_canonical = int(not alias_target)
        if alias_target:
            mode = "byte_identical_alias"
            state = "alias_to_versioned_canonical_assets"
        elif row["asset_readiness"] == "partial_internal_unserved":
            mode = "source_admitted_canonical_with_documented_gaps"
            state = "partial_declared_positions_source_admitted"
        elif row["book_id"] in PILOT_BOOKS:
            mode = "versioned_sha256_anchor_canonical"
            state = "full_source_anchor"
        elif row["asset_strategy"] == "w1_1966_sha256_manifest":
            mode = "versioned_sha256_manifest_canonical"
            state = "full_materialized_w1_1966_source"
        else:
            mode = "direct_canonical"
            state = "full_direct_or_audited_source"
        rows.append(
            {
                "processing_version": VERSION,
                "book_id": row["book_id"],
                "viewer_key": row["viewer_key"],
                "catalog_generation": as_int(row, "catalog_generation"),
                "grade_code": as_int(row, "grade"),
                "title_core": "Ciencias Naturales",
                "original_source_state": state,
                "processing_mode": mode,
                "canonical_processing_viewer_key": canonical["viewer_key"],
                "technical_identity_covered": 1,
                "is_canonical_processing_object": is_canonical,
                "declared_positions": as_int(row, "viewer_positions_declared"),
                "direct_source_jpegs": as_int(row, "resolved_source_assets") if is_canonical else 0,
                "terminal_synthetic_candidates_original_route": as_int(row, "terminal_synthetic"),
                "persistent_unresolved_source_gaps": as_int(row, "internal_unserved_positions"),
                "evidence_basis": row["asset_strategy"],
                "interpretive_limit": (
                    "Operational processing topology only; source-admitted coverage, aliases, "
                    "and unserved positions do not establish bibliographic identity, semantic "
                    "equivalence, or verified OCR text."
                ),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    if not rows:
        raise AssertionError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--asset-output",
        type=Path,
        default=Path("local/ftrl/ltmd_u1_w1_asset_manifest.csv"),
    )
    parser.add_argument(
        "--processing-output",
        type=Path,
        default=Path("local/ftrl/ltmd_u1_w1_processing_inventory.csv"),
    )
    args = parser.parse_args()

    readiness = exhaustive_readiness()
    by_id = {row["book_id"]: row for row in readiness}
    if len(by_id) != len(readiness):
        raise AssertionError("duplicate W1 book_id in exhaustive readiness")
    aliases = {
        bid: row["alias_to_book_id"]
        for bid, row in by_id.items()
        if row["alias_to_book_id"]
    }
    canonical = set(by_id) - set(aliases)

    assert len(readiness) == EXPECTED_HISTORICAL, len(readiness)
    assert len(aliases) == EXPECTED_ALIASES, len(aliases)
    assert len(canonical) == EXPECTED_CANONICAL, len(canonical)
    for alias, target in aliases.items():
        assert target in canonical, f"invalid alias target {alias} -> {target}"

    layers: dict[str, list[dict[str, str | int]]] = {}
    for source in (
        load_direct_rows(by_id, canonical),
        load_1966_rows(by_id, canonical),
        load_cn46_rows(by_id, canonical),
        load_cn5_anchor_rows(by_id, canonical),
    ):
        overlap = set(layers) & set(source)
        if overlap:
            raise AssertionError(
                f"canonical objects assigned to multiple layers: {sorted(overlap)}"
            )
        layers.update(source)

    if set(layers) != canonical:
        missing = sorted(canonical - set(layers))
        extra = sorted(set(layers) - canonical)
        raise AssertionError(
            f"W1 layer reconciliation mismatch missing={missing} extra={extra}"
        )

    assets: list[dict[str, str | int]] = []
    for bid in sorted(canonical):
        rows = layers[bid]
        expected = as_int(by_id[bid], "resolved_source_assets")
        if len(rows) != expected:
            raise AssertionError(
                f"source page mismatch for {bid}: {len(rows)} != {expected}"
            )
        keys = {
            (str(r["viewer_key"]), int(r["source_image_index"]))
            for r in rows
        }
        if len(keys) != len(rows):
            raise AssertionError(f"duplicate source page identity within {bid}")
        assets.extend(rows)

    assets.sort(
        key=lambda r: (
            int(r["catalog_generation"]),
            int(r["grade_code"]),
            str(r["viewer_key"]),
            int(r["source_image_index"]),
        )
    )
    page_keys = {
        (str(r["viewer_key"]), int(r["source_image_index"]))
        for r in assets
    }
    assert len(page_keys) == len(assets), "duplicate normalized W1 page identity"
    assert len(assets) == EXPECTED_SOURCE_PAGES, len(assets)
    assert all(int(r["byte_size"]) > 0 for r in assets)
    assert all(SHA256_RE.fullmatch(str(r["sha256"])) for r in assets)

    processing = build_processing_rows(readiness)
    assert len(processing) == EXPECTED_HISTORICAL
    assert sum(
        int(r["is_canonical_processing_object"]) for r in processing
    ) == EXPECTED_CANONICAL
    assert sum(
        int(r["persistent_unresolved_source_gaps"])
        for r in processing
        if int(r["is_canonical_processing_object"])
    ) == EXPECTED_INTERNAL_GAPS
    assert sum(int(r["direct_source_jpegs"]) for r in processing) == EXPECTED_SOURCE_PAGES

    write_csv(args.asset_output, assets)
    write_csv(args.processing_output, processing)

    layer_counts: dict[str, int] = {}
    for row in assets:
        layer = str(row["source_layer"])
        layer_counts[layer] = layer_counts.get(layer, 0) + 1
    print(
        {
            "schema": VERSION,
            "historical_identities": len(processing),
            "canonical_processing_objects": EXPECTED_CANONICAL,
            "byte_identical_aliases": EXPECTED_ALIASES,
            "source_admitted_pages": len(assets),
            "documented_internal_unserved_positions": EXPECTED_INTERNAL_GAPS,
            "source_layers": dict(sorted(layer_counts.items())),
            "asset_output": str(args.asset_output),
            "processing_output": str(args.processing_output),
        }
    )


if __name__ == "__main__":
    main()
