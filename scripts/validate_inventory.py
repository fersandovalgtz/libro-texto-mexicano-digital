#!/usr/bin/env python3
"""Valida la estructura mínima del inventario de libros del piloto 0.1."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {
    "book_id",
    "title",
    "generation",
    "grade",
    "subject_or_field",
    "source_url",
    "source_repository",
    "access_date",
    "rights_note",
    "availability_status",
}


def validate_inventory(path: Path) -> list[str]:
    errors: list[str] = []

    if not path.exists():
        return [f"No existe el archivo: {path}"]

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            errors.append("Faltan columnas obligatorias: " + ", ".join(missing))
            return errors

        seen_ids: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            book_id = (row.get("book_id") or "").strip()
            if not book_id:
                errors.append(f"Línea {line_number}: book_id vacío")
            elif book_id in seen_ids:
                errors.append(f"Línea {line_number}: book_id duplicado: {book_id}")
            else:
                seen_ids.add(book_id)

            for field in REQUIRED_COLUMNS - {"book_id"}:
                if not (row.get(field) or "").strip():
                    errors.append(f"Línea {line_number}: campo obligatorio vacío: {field}")

    return errors


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/book_inventory.csv")
    errors = validate_inventory(target)

    if errors:
        print("Inventario inválido:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Inventario válido: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
