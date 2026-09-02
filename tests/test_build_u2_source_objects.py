import csv
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "build_u2_source_objects.py"
SPEC = importlib.util.spec_from_file_location("build_u2_source_objects", SCRIPT)
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

INVENTORY = ROOT / "data" / "catalog" / "conaliteg_primaria_2026_2027_inventory.csv"
MATERIALIZED = ROOT / "data" / "catalog" / "ltmd_u2_source_objects_2026_2027.csv"
SCHEMA = ROOT / "schemas" / "ltmd_u2_source_object.schema.json"


def write_inventory(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "catalog_entry_id",
        "cycle",
        "level",
        "grade",
        "viewer_key",
        "title",
        "publisher",
        "viewer_url",
        "public_repo_status",
        "source_checked",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def row(entry_id: str, cycle: str, grade: int, key: str, *, url_cycle: str | None = None):
    url_cycle = url_cycle or cycle
    return {
        "catalog_entry_id": entry_id,
        "cycle": f"{cycle}-{int(cycle) + 1}",
        "level": "primaria",
        "grade": str(grade),
        "viewer_key": key,
        "title": f"Libro {key}",
        "publisher": "SEP",
        "viewer_url": (
            "https://libros.conaliteg.gob.mx/pdf-reader/reader.html"
            f"?ciclo={url_cycle}&clave={key}&nivel=primaria"
        ),
        "public_repo_status": "catalog_metadata_only",
        "source_checked": "2026-08-31",
    }


def test_repository_inventory_materializes_exact_42_to_39(tmp_path):
    objects = mod.build_source_objects(INVENTORY)
    assert len(objects) == 39
    assert sum(int(item["catalog_entry_count"]) for item in objects) == 42

    by_key = {item["viewer_key"]: item for item in objects}
    assert by_key["P1LPM"]["catalog_grades"] == "1|2"
    assert by_key["P3LPM"]["catalog_grades"] == "3|4"
    assert by_key["P5LPM"]["catalog_grades"] == "5|6"

    output = tmp_path / "objects.csv"
    mod.write_source_objects(objects, output)
    assert output.read_bytes() == MATERIALIZED.read_bytes()


def test_repository_rows_conform_to_u2_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    for item in mod.build_source_objects(INVENTORY):
        validator.validate(item)


def test_same_viewer_key_in_different_source_cycles_does_not_collide(tmp_path):
    inventory = tmp_path / "inventory.csv"
    write_inventory(
        inventory,
        [
            row("e1", "2026", 1, "P1AAA"),
            row("e2", "2027", 1, "P1AAA"),
        ],
    )

    objects = mod.build_source_objects(
        inventory,
        expected_catalog_entries=2,
        expected_source_objects=2,
        enforce_current_shared_keys=False,
    )
    assert [item["source_object_id"] for item in objects] == [
        "CONALITEG:2026:primaria:P1AAA",
        "CONALITEG:2027:primaria:P1AAA",
    ]


def test_viewer_url_key_mismatch_is_rejected(tmp_path):
    inventory = tmp_path / "inventory.csv"
    bad = row("e1", "2026", 1, "P1AAA")
    bad["viewer_url"] = (
        "https://libros.conaliteg.gob.mx/pdf-reader/reader.html"
        "?ciclo=2026&clave=P1BBB&nivel=primaria"
    )
    write_inventory(inventory, [bad])

    try:
        mod.build_source_objects(
            inventory,
            expected_catalog_entries=1,
            expected_source_objects=1,
            enforce_current_shared_keys=False,
        )
    except RuntimeError as exc:
        assert "viewer_key mismatch" in str(exc)
    else:
        raise AssertionError("expected viewer-key identity gate")


def test_conflicting_metadata_for_one_source_object_is_rejected(tmp_path):
    inventory = tmp_path / "inventory.csv"
    first = row("e1", "2026", 1, "P1AAA")
    second = row("e2", "2026", 2, "P1AAA")
    second["title"] = "Título incompatible"
    write_inventory(inventory, [first, second])

    try:
        mod.build_source_objects(
            inventory,
            expected_catalog_entries=2,
            expected_source_objects=1,
            enforce_current_shared_keys=False,
        )
    except RuntimeError as exc:
        assert "conflicting title" in str(exc)
    else:
        raise AssertionError("expected source-object metadata conflict gate")
