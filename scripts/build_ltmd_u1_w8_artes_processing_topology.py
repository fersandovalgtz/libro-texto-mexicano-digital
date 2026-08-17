#!/usr/bin/env python3
"""Build the closed LTMD-U1 W8 Artes processing topology from source-admissible evidence."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

VERSION = "LTMD_U1_W8_ARTES_PROCESSING_TOPOLOGY_0.1"
EXPECTED_IDENTITIES = 20
EXPECTED_ADMITTED = 16
EXPECTED_RETAINED = 4
EXPECTED_SOURCE_PAGES = 1490

ADMISSIBILITY = Path("data/catalog/ltmd_u1_w8_artes_source_admissibility.csv")
ASSETS = Path("data/catalog/ltmd_u1_w8_artes_asset_manifest.csv")
PROCESSING = Path("data/catalog/ltmd_u1_w8_processing_inventory.csv")
PAGES = Path("data/catalog/ltmd_u1_w8_canonical_page_manifest.csv")
REPORT = Path("docs/LTMD_U1_W8_ARTES_PROCESSING_TOPOLOGY.md")

PROCESSING_FIELDS = [
    "topology_version", "book_id", "viewer_key", "catalog_generation", "grade_code",
    "title_core", "source_status", "processing_mode", "is_canonical_processing_object",
    "ocr_identity_eligible", "source_page_count", "declared_positions",
    "persistent_internal_source_gaps", "probe_errors", "semantic_state", "alias_state",
    "source_url",
]

PAGE_FIELDS = [
    "manifest_version", "page_id", "book_id", "viewer_key", "catalog_generation",
    "grade_code", "title_core", "viewer_page", "source_image_index", "processing_mode",
    "source_provenance", "source_asset_url", "byte_size", "sha256", "asset_status",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_int(value: str) -> int:
    return int(value or "0")


def page_id(viewer_key: str, viewer_page: str) -> str:
    return f"U1-{viewer_key}-P{int(viewer_page):03d}"


def main() -> None:
    admissibility = read_rows(ADMISSIBILITY)
    assets = read_rows(ASSETS)

    if len(admissibility) != EXPECTED_IDENTITIES:
        raise SystemExit(
            f"W8 topology failed: expected {EXPECTED_IDENTITIES} admissibility rows, got {len(admissibility)}"
        )
    if len({row["viewer_key"] for row in admissibility}) != EXPECTED_IDENTITIES:
        raise SystemExit("W8 topology failed: duplicate viewer_key in admissibility matrix")

    by_viewer = {row["viewer_key"]: row for row in admissibility}
    admitted = {key for key, row in by_viewer.items() if row["source_status"] == "SOURCE_ADMISSIBLE"}
    retained = {key for key, row in by_viewer.items() if row["source_status"] == "SOURCE_RETAINED"}
    if len(admitted) != EXPECTED_ADMITTED or len(retained) != EXPECTED_RETAINED:
        raise SystemExit(
            f"W8 topology failed: expected {EXPECTED_ADMITTED} admitted / {EXPECTED_RETAINED} retained, "
            f"got {len(admitted)} / {len(retained)}"
        )
    if admitted & retained or admitted | retained != set(by_viewer):
        raise SystemExit("W8 topology failed: admissibility partition is not exact")

    asset_viewers = {row["viewer_key"] for row in assets}
    if asset_viewers != set(by_viewer):
        raise SystemExit(
            "W8 topology failed: asset/admissibility identity drift; "
            f"missing={sorted(set(by_viewer) - asset_viewers)} unexpected={sorted(asset_viewers - set(by_viewer))}"
        )

    source_assets = [row for row in assets if row["asset_status"] == "source_jpeg"]
    if len(source_assets) != EXPECTED_SOURCE_PAGES:
        raise SystemExit(
            f"W8 topology failed: expected {EXPECTED_SOURCE_PAGES} source JPEG rows, got {len(source_assets)}"
        )
    if any(row["viewer_key"] not in admitted for row in source_assets):
        raise SystemExit("W8 topology failed: retained viewer contributed a source JPEG")
    if any(not row["sha256"] or len(row["sha256"]) != 64 for row in source_assets):
        raise SystemExit("W8 topology failed: source JPEG without a SHA-256 fingerprint")
    if any(as_int(row["byte_size"]) <= 0 for row in source_assets):
        raise SystemExit("W8 topology failed: source JPEG without positive byte_size")
    if any(row["probe_state"] != "served_image" or row["content_type"] != "image/jpeg" for row in source_assets):
        raise SystemExit("W8 topology failed: non-served/non-JPEG row marked source_jpeg")

    source_counts = Counter(row["viewer_key"] for row in source_assets)
    processing_rows: list[dict[str, str | int]] = []
    for row in sorted(
        admissibility,
        key=lambda r: (int(r["catalog_generation"]), int(r["grade_code"]), r["viewer_key"]),
    ):
        key = row["viewer_key"]
        is_admitted = key in admitted
        expected_count = as_int(row["source_jpegs"])
        observed_count = source_counts.get(key, 0)
        if observed_count != expected_count:
            raise SystemExit(
                f"W8 topology failed: source page drift for {key}: admissibility={expected_count} assets={observed_count}"
            )
        if is_admitted:
            if row["source_admissible"] != "1" or row["direct_asset_ready"] != "1":
                raise SystemExit(f"W8 topology failed: admitted viewer lacks executable source flags: {key}")
            if as_int(row["internal_unserved"]) != 0 or as_int(row["probe_errors"]) != 0:
                raise SystemExit(f"W8 topology failed: admitted viewer has source defects: {key}")
            mode = "direct_canonical"
        else:
            if row["source_admissible"] != "0" or observed_count != 0:
                raise SystemExit(f"W8 topology failed: retained viewer is not fully withheld: {key}")
            mode = "withheld_source"

        processing_rows.append({
            "topology_version": VERSION,
            "book_id": row["book_id"],
            "viewer_key": key,
            "catalog_generation": row["catalog_generation"],
            "grade_code": row["grade_code"],
            "title_core": row["title_core"],
            "source_status": row["source_status"],
            "processing_mode": mode,
            "is_canonical_processing_object": int(is_admitted),
            "ocr_identity_eligible": int(is_admitted),
            "source_page_count": observed_count,
            "declared_positions": row["declared_positions"],
            "persistent_internal_source_gaps": row["internal_unserved"],
            "probe_errors": row["probe_errors"],
            "semantic_state": row["semantic_state"],
            "alias_state": row["alias_state"],
            "source_url": row["source_url"],
        })

    page_rows: list[dict[str, str]] = []
    seen_page_ids: set[str] = set()
    for row in sorted(source_assets, key=lambda r: (r["viewer_key"], int(r["viewer_page"]))):
        key = row["viewer_key"]
        adm = by_viewer[key]
        pid = page_id(key, row["viewer_page"])
        if pid in seen_page_ids:
            raise SystemExit(f"W8 topology failed: duplicate page_id {pid}")
        seen_page_ids.add(pid)
        page_rows.append({
            "manifest_version": VERSION,
            "page_id": pid,
            "book_id": adm["book_id"],
            "viewer_key": key,
            "catalog_generation": adm["catalog_generation"],
            "grade_code": adm["grade_code"],
            "title_core": adm["title_core"],
            "viewer_page": row["viewer_page"],
            "source_image_index": row["source_image_index"],
            "processing_mode": "direct_canonical",
            "source_provenance": "official_conaliteg_source_jpeg_sha256_verified",
            "source_asset_url": row["source_asset_url"],
            "byte_size": row["byte_size"],
            "sha256": row["sha256"],
            "asset_status": row["asset_status"],
        })

    if len(page_rows) != EXPECTED_SOURCE_PAGES or len(seen_page_ids) != EXPECTED_SOURCE_PAGES:
        raise SystemExit("W8 topology failed: canonical page manifest cardinality mismatch")
    if {row["viewer_key"] for row in page_rows} != admitted:
        raise SystemExit("W8 topology failed: canonical page manifest does not cover exactly the admitted cohort")

    PROCESSING.parent.mkdir(parents=True, exist_ok=True)
    with PROCESSING.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PROCESSING_FIELDS)
        writer.writeheader()
        writer.writerows(processing_rows)

    with PAGES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAGE_FIELDS)
        writer.writeheader()
        writer.writerows(page_rows)

    retained_ids = ", ".join(f"`{key}`" for key in sorted(retained))
    generation_counts = Counter(by_viewer[key]["catalog_generation"] for key in admitted)
    generation_pages = Counter(row["catalog_generation"] for row in page_rows)
    lines = [
        "# LTMD-U1 W8 Artes — topología cerrada de procesamiento",
        "",
        f"Versión: `{VERSION}`.",
        "",
        "## Contrato ejecutable",
        "",
        f"- Identidades W8: **{EXPECTED_IDENTITIES}**.",
        f"- Objetos canónicos admitidos a OCR: **{EXPECTED_ADMITTED}**.",
        f"- Identidades retenidas por fuente: **{EXPECTED_RETAINED}**.",
        f"- JPEG fuente canónicos, con SHA-256 y tamaño: **{EXPECTED_SOURCE_PAGES}**.",
        "- Alias creados: **0**.",
        "- Modo de los admitidos: `direct_canonical`.",
        "- Modo de los retenidos: `withheld_source`.",
        "",
        "## Cohorte retenida",
        "",
        retained_ids + ".",
        "",
        "Las cuatro identidades retenidas no aportan páginas al manifiesto canónico y no son elegibles para OCR. El constructor aborta si una de ellas aparece como `source_jpeg`, si cambia la partición 16/4 o si deriva la cardinalidad de 1,490 páginas.",
        "",
        "## Cobertura admitida por generación",
        "",
        "| generación | visores admitidos | páginas fuente |",
        "|---:|---:|---:|",
    ]
    for generation in sorted(generation_counts, key=int):
        lines.append(f"| {generation} | {generation_counts[generation]} | {generation_pages[generation]} |")
    lines += [
        "",
        "## Regla de procedencia",
        "",
        "Cada fila del manifiesto canónico conserva URL oficial, índice de imagen, tamaño y SHA-256 del activo observado por la auditoría W8. La topología no descarga ni relicencia JPEG y no crea equivalencias históricas o semánticas.",
        "",
        "Este producto abre exclusivamente la fase técnica OCR/PAGESTRUCT/FRAGSEG para los 16 objetos admitidos. No autoriza todavía inferencias curriculares, pedagógicas, históricas o de continuidad entre generaciones.",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        f"{VERSION}: identities={len(processing_rows)} admitted={len(admitted)} retained={len(retained)} "
        f"source_pages={len(page_rows)}"
    )


if __name__ == "__main__":
    main()
