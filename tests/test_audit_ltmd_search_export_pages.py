"""Regression tests for a private LTMD search-export anomaly detector.

All book excerpts and page texts are SYNTHETIC; no textbook material or user
screenshots are committed to this repository.
"""
import json

import pytest

from scripts import audit_ltmd_search_export_pages as audit


def entry(number: int, page: int, body: str, key: str = "P3PAA") -> str:
    return (
        f"{number}. Libro completamente ficticio\n"
        f"Ciclo escolar 2026–2027 · Grado 3 · Página del visor {page}\n\n"
        f"{body}\n\n"
        "SEP/CONALITEG. Libro completamente ficticio. "
        f"Ciclo escolar 2026–2027, grado 3. Posición del visor: {page}.\n"
        f"https://libros.conaliteg.gob.mx/pdf-reader/reader.html?"
        f"nivel=primaria&ciclo=2026&clave={key}\n\n"
        "─────────────────────\n\n"
    )


def export(*items: str, advertised_total: int | None = None) -> str:
    total = advertised_total or len(items)
    return (
        "LTMD Research\nBúsqueda: palabra_de_prueba\n"
        "Generación: todas\nGrado: todos\nLibro: todos\n"
        "Búsqueda: frase exacta\n"
        f"Resultados 1–{len(items)} de {total}\n\n"
        + "".join(items)
    )


def test_detects_cross_page_reused_span_and_reports_no_source_text():
    sequence = " ".join(f"palabra{i:03d}" for i in range(50))
    text = export(
        entry(1, 7, "Introducción ficticia. " + sequence + " Fin de introducción."),
        entry(2, 86, sequence),
        entry(3, 110, "Un texto enteramente distinto sin coincidencias largas."),
        advertised_total=513,
    )
    report = audit.audit_export(text)
    assert report["exported_results"] == 3
    assert report["reported_total_results"] == 513
    assert report["report_is_partial_if_export_is_paginated"] is True
    assert report["flag_count"] == 1
    flag = report["review_flags"][0]
    assert flag["result_ordinals"] == [1, 2]
    assert flag["viewer_pages"] == [7, 86]
    assert flag["longest_contiguous_overlap_words"] == 50
    assert flag["fraction_of_shorter_snippet"] == 1.0
    assert flag["possible_front_matter_contamination"] is True
    assert flag["state"] == "cross_page_overlap_requires_source_review"
    serialized = json.dumps(report)
    for secret in ("palabra001", "Introducción ficticia", "palabra_de_prueba",
                   "libros.conaliteg.gob.mx", "source_asset_url"):
        assert secret not in serialized
    assert report["state"] == "private_export_screening_not_source_validation"


def test_other_books_do_not_mix_even_with_identical_text():
    passage = " ".join(f"ficticia{i}" for i in range(60))
    text = export(entry(1, 7, passage, "P3PAA"),
                  entry(2, 86, passage, "P1PAA"))
    report = audit.audit_export(text)
    assert report["flag_count"] == 0


def test_same_book_and_page_do_not_trigger_cross_page_alert():
    passage = " ".join(f"ficticia{i}" for i in range(50))
    text = export(entry(1, 7, passage), entry(2, 7, passage))
    assert audit.audit_export(text)["flag_count"] == 0


def test_short_boilerplate_is_not_flagged():
    passage = " ".join(f"ficticia{i}" for i in range(20))
    text = export(
        entry(1, 7, passage + " otras palabras irrepetibles alpha beta"),
        entry(2, 86, passage + " diferentes vocablos omega gamma"),
    )
    assert audit.audit_export(text)["flag_count"] == 0


def test_repeated_prose_is_only_a_flag_not_a_diagnosis():
    passage = " ".join(f"palabra{i}" for i in range(40))
    text = export(entry(1, 20, passage), entry(2, 40, passage))
    report = audit.audit_export(text)
    assert report["flag_count"] == 1
    assert report["review_flags"][0]["possible_front_matter_contamination"] is False
    assert "inspect" in report["warnings"][0].lower()


def test_min_words_parameter_is_bounded():
    text = export(entry(1, 1, "un texto"), entry(2, 2, "otro texto"))
    with pytest.raises(ValueError, match="min_shared_words"):
        audit.audit_export(text, min_shared_words=12)


def test_does_not_infer_missing_export_rows():
    text = export(entry(1, 1, "texto sintético"), advertised_total=513)
    report = audit.audit_export(text)
    assert report["exported_results"] == 1
    assert report["reported_total_results"] == 513
    assert report["report_is_partial_if_export_is_paginated"] is True


def test_incomplete_or_noncontiguous_export_is_rejected():
    text = export(entry(1, 7, "texto sintético"), entry(2, 86, "segundo texto"))
    with pytest.raises(ValueError, match="incomplete"):
        audit.audit_export(text.replace("2. Libro completamente ficticio", "OTRO. Libro completamente ficticio"))
    with pytest.raises(ValueError, match="ordinals"):
        audit.audit_export(text.replace("2. Libro completamente ficticio", "3. Libro completamente ficticio"))


def test_link_must_use_a_single_official_viewer_identity():
    text = export(entry(1, 7, "texto sintético"))
    with pytest.raises(ValueError, match="noncanonical"):
        audit.audit_export(text.replace("libros.conaliteg.gob.mx", "not-official.example.org"))
    with pytest.raises(ValueError, match="identifier"):
        audit.audit_export(text.replace("&clave=P3PAA", "&clave="))


def test_empty_or_wrong_format_rejected():
    with pytest.raises(ValueError, match="result-range"):
        audit.audit_export("texto cualquiera")
