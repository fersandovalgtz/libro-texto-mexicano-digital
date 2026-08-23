#!/usr/bin/env python3
"""Build a deterministic SHA-256 ledger for LTMD-U1 public derived evidence.

The ledger is intentionally restricted to repository-resident, public artefacts:
derived catalogues, scientific reports, pipeline code, CI definitions, landing
pages and scholarly metadata. It never downloads or hashes CONALITEG/SEP source
assets, temporary OCR text, page images, PDFs, or other reconstructive source
material.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/catalog/ltmd_u1_evidence_integrity.csv"
OUT_MD = ROOT / "docs/LTMD_U1_EVIDENCE_INTEGRITY.md"
VERSION = "LTMD_U1_EVIDENCE_INTEGRITY_0.1"

EXCLUDED = {
    OUT_CSV.relative_to(ROOT).as_posix(),
    OUT_MD.relative_to(ROOT).as_posix(),
}
FORBIDDEN_SUFFIXES = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".bmp",
    ".pdf", ".zip", ".7z", ".tar", ".gz",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_class(rel: str) -> str:
    if rel.startswith("data/catalog/"):
        return "derived_data"
    if rel.startswith("docs/"):
        return "evidence_report"
    if rel.startswith("scripts/"):
        return "scientific_code"
    if rel.startswith(".github/workflows/"):
        return "automation"
    if rel in {"README.md", "README.en.md"}:
        return "landing_page"
    return "scholarly_metadata"


def add_glob(targets: set[Path], pattern: str) -> None:
    for path in ROOT.glob(pattern):
        if path.is_file():
            targets.add(path)


def collect_targets() -> list[Path]:
    targets: set[Path] = set()

    # Public U1 evidence and derived catalogues.
    add_glob(targets, "data/catalog/ltmd_u1_*")
    add_glob(targets, "docs/LTMD_U1_*.md")

    # Scientific implementation and orchestration that produce/validate U1.
    add_glob(targets, "scripts/*ltmd_u1*.py")
    add_glob(targets, ".github/workflows/*ltmd-u1*.yml")
    add_glob(targets, ".github/workflows/*ltmd-u1*.yaml")

    # Public-facing state and scholarly metadata, when present.
    for rel in ("README.md", "README.en.md", "CITATION.cff", "codemeta.json"):
        path = ROOT / rel
        if path.is_file():
            targets.add(path)

    clean: list[Path] = []
    for path in targets:
        rel = path.relative_to(ROOT).as_posix()
        if rel in EXCLUDED:
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise SystemExit(f"Forbidden source-like/binary artefact entered integrity scope: {rel}")
        clean.append(path)

    return sorted(clean, key=lambda p: p.relative_to(ROOT).as_posix())


def main() -> None:
    targets = collect_targets()
    if not targets:
        raise SystemExit("Integrity scope is unexpectedly empty")

    rows: list[dict[str, str | int]] = []
    for path in targets:
        rel = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "path": rel,
                "artifact_class": artifact_class(rel),
                "sha256": sha256_file(path),
                "byte_size": path.stat().st_size,
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["path", "artifact_class", "sha256", "byte_size"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    classes = Counter(str(r["artifact_class"]) for r in rows)
    total_bytes = sum(int(r["byte_size"]) for r in rows)

    lines = [
        "# LTMD-U1 — integridad de la evidencia pública derivada",
        "",
        f"Versión: `{VERSION}`.",
        "",
        "Este control produce un inventario determinista y direccionado por contenido de la capa pública de evidencia LTMD-U1. Cada archivo incluido queda identificado por ruta, clase de artefacto, tamaño en bytes y SHA-256.",
        "",
        "## Alcance",
        "",
        f"- Artefactos públicos verificados: **{len(rows)}**.",
        f"- Bytes públicos cubiertos: **{total_bytes}**.",
        "- Algoritmo: **SHA-256**.",
        "- Activos fuente originales descargados o persistidos por este control: **0**.",
        "- OCR completo persistido por este control: **0**.",
        "- El propio ledger y este informe se excluyen para evitar autorreferencia criptográfica.",
        "",
        "## Cobertura por clase",
        "",
        "| clase | archivos |",
        "|---|---:|",
    ]
    for cls in sorted(classes):
        lines.append(f"| `{cls}` | {classes[cls]} |")

    lines.extend(
        [
            "",
            "## Regla de interpretación",
            "",
            "Un SHA-256 distinto significa que el artefacto público cambió y el ledger debe regenerarse. Este control acredita integridad de los archivos derivados publicados en el repositorio; no autentica ni redistribuye los libros, páginas, imágenes u OCR fuente de CONALITEG/SEP, y no sustituye las verificaciones de procedencia y admisibilidad de cada ola.",
            "",
            "Archivo canónico del ledger: `data/catalog/ltmd_u1_evidence_integrity.csv`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    # Immediate self-check of the emitted ledger.
    with OUT_CSV.open("r", encoding="utf-8", newline="") as fh:
        check = list(csv.DictReader(fh))
    if len(check) != len(rows):
        raise SystemExit("Integrity ledger row count mismatch")
    if len({r["path"] for r in check}) != len(check):
        raise SystemExit("Integrity ledger contains duplicate paths")
    if any(len(r["sha256"]) != 64 for r in check):
        raise SystemExit("Integrity ledger contains malformed SHA-256 values")


if __name__ == "__main__":
    main()
