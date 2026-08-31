#!/usr/bin/env python3
"""Deterministic, text-private Indigenous-language retrieval for LTMD FTRL SQLite corpora.

Version: LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2

The script reads the private `pages` tables but emits no OCR text or snippets.
It deduplicates by page_id and fails on metadata/hash conflicts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "LTMD_U1_INDIGENOUS_LANGUAGES_RERUN_0.2"
NAMED_CONTEXT_WINDOW = 30
CONCEPT_INDIGENOUS_WINDOW = 60

DIRECT_EXPLICIT_PHRASES = (
    "lengua indigena", "lenguas indigenas", "idioma indigena", "idiomas indigenas",
    "lengua originaria", "lenguas originarias", "idioma originario", "idiomas originarios",
)
CONCEPT_PHRASES = (
    "diversidad linguistica", "pluralidad linguistica", "derechos linguisticos",
    "derecho linguistico", "discriminacion linguistica", "lengua nacional", "lenguas nacionales",
)
INDIGENOUS_SIGNAL_TOKENS = {
    "indigena", "indigenas", "originaria", "originarias", "originario", "originarios",
}
LINGUISTIC_CONTEXT_TOKENS = {
    "lengua", "lenguas", "idioma", "idiomas", "habla", "hablas", "hablan", "hablar",
    "hablaba", "hablaban", "hablante", "hablantes", "bilingue", "bilingues", "bilinguismo",
    "monolingue", "monolingues", "monolinguismo", "vocabulario", "palabra", "palabras",
    "traduccion", "traducciones", "traducir", "traduce", "traducido", "dialecto", "dialectos",
    "linguistica", "linguisticas", "linguistico", "linguisticos", "alfabeto", "alfabetos",
    "escritura", "escrito", "escrita", "oral", "orales", "oralidad", "pronuncia", "pronunciacion",
}
LANGUAGE_FORMS = {
    "Náhuatl": {"nahuatl", "nahua", "nahuas"},
    "Maya": {"maya", "mayas"},
    "Zapoteco": {"zapoteco", "zapoteca", "zapotecos", "zapotecas"},
    "Mixteco": {"mixteco", "mixteca", "mixtecos", "mixtecas"},
    "Purépecha / tarasco": {"purepecha", "purepechas", "purhepecha", "purhepechas", "tarasco", "tarasca", "tarascos", "tarascas"},
    "Otomí": {"otomi", "otomis"},
    "Huasteco / teenek": {"huasteco", "huasteca", "huastecos", "huastecas", "teenek", "tenek"},
    "Tarahumara / rarámuri": {"tarahumara", "tarahumaras", "raramuri", "raramuris"},
    "Cora / náayeri": {"cora", "coras", "naayeri", "nayeri"},
    "Mayo / yoreme": {"mayo", "mayos", "yoreme", "yoremes"},
    "Yaqui": {"yaqui", "yaquis"},
    "Tseltal / tzeltal": {"tseltal", "tseltales", "tzeltal", "tzeltales"},
}
TOKEN_RE = re.compile(r"[a-z0-9]+", re.ASCII)


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").casefold()
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(fold(text))


def find_phrase_starts(tokens: list[str], phrase: str) -> list[int]:
    parts = phrase.split()
    if not parts or len(parts) > len(tokens):
        return []
    size = len(parts)
    return [i for i in range(len(tokens) - size + 1) if tokens[i:i + size] == parts]


def nearest_distance(indices_a: list[int], indices_b: list[int]) -> int | None:
    if not indices_a or not indices_b:
        return None
    a, b = sorted(indices_a), sorted(indices_b)
    i = j = 0
    best = None
    while i < len(a) and j < len(b):
        distance = abs(a[i] - b[j])
        best = distance if best is None or distance < best else best
        if a[i] < b[j]:
            i += 1
        else:
            j += 1
    return best


def analyze_text(text: str) -> dict:
    tokens = tokenize(text)
    positions = defaultdict(list)
    for index, token in enumerate(tokens):
        positions[token].append(index)

    direct_hits = []
    for phrase in DIRECT_EXPLICIT_PHRASES:
        if find_phrase_starts(tokens, phrase):
            direct_hits.append(phrase)

    context_positions = [p for token in LINGUISTIC_CONTEXT_TOKENS for p in positions.get(token, [])]
    language_hits = {}
    all_language_positions = []
    for group, forms in LANGUAGE_FORMS.items():
        form_positions = []
        matched_forms = []
        for form in sorted(forms):
            hits = positions.get(form, [])
            if hits:
                form_positions.extend(hits)
                matched_forms.append(form)
        if not form_positions:
            continue
        distance = nearest_distance(form_positions, context_positions)
        if distance is not None and distance <= NAMED_CONTEXT_WINDOW:
            language_hits[group] = {"forms": matched_forms, "min_context_distance": distance}
            all_language_positions.extend(form_positions)

    concept_hits = []
    concept_positions = []
    for phrase in CONCEPT_PHRASES:
        starts = find_phrase_starts(tokens, phrase)
        if starts:
            concept_hits.append(phrase)
            concept_positions.extend(starts)

    indigenous_positions = [p for token in INDIGENOUS_SIGNAL_TOKENS for p in positions.get(token, [])]
    anchor_positions = indigenous_positions + all_language_positions
    qualified_concepts = []
    concept_min_distance = None
    if concept_positions and anchor_positions:
        concept_min_distance = nearest_distance(concept_positions, anchor_positions)
        if concept_min_distance is not None and concept_min_distance <= CONCEPT_INDIGENOUS_WINDOW:
            qualified_concepts = concept_hits

    explicit_hits = sorted(set(direct_hits + qualified_concepts))
    return {
        "broad_candidate": bool(explicit_hits or language_hits),
        "explicit_general": bool(explicit_hits),
        "explicit_terms": explicit_hits,
        "named_language_contextual": bool(language_hits),
        "language_hits": language_hits,
        "concept_min_anchor_distance": concept_min_distance,
    }


def page_fingerprint(row: sqlite3.Row) -> tuple:
    return (row["canonical_viewer_key"], row["source_sha256"], row["ocr_sha256"],
            str(row["catalog_generation"]), str(row["page_index"]), str(row["viewer_page"]))


def iter_pages(db_paths: list[Path]):
    seen = {}
    for db in db_paths:
        connection = sqlite3.connect(str(db))
        connection.row_factory = sqlite3.Row
        try:
            rows = connection.execute("""
                SELECT page_id, viewer_key, canonical_viewer_key, wave, catalog_generation,
                       grade_code, title_core, page_index, viewer_page, source_asset_url,
                       source_sha256, ocr_sha256, ocr_confidence_mean, search_text
                FROM pages
            """)
            for row in rows:
                fingerprint = page_fingerprint(row)
                prior = seen.get(row["page_id"])
                if prior is not None:
                    if prior != fingerprint:
                        raise RuntimeError(f"conflicting duplicate page_id: {row['page_id']} in {db}")
                    continue
                seen[row["page_id"]] = fingerprint
                yield dict(row)
        finally:
            connection.close()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(db_paths: list[Path], out_dir: Path, expected_pages: int | None, expected_objects: int | None) -> dict:
    pages = list(iter_pages(db_paths))
    total_pages = len(pages)
    objects = {p["canonical_viewer_key"] for p in pages}
    if expected_pages is not None and total_pages != expected_pages:
        raise RuntimeError(f"page cardinality mismatch: got {total_pages}, expected {expected_pages}")
    if expected_objects is not None and len(objects) != expected_objects:
        raise RuntimeError(f"object cardinality mismatch: got {len(objects)}, expected {expected_objects}")

    totals_by_gen = Counter(str(p["catalog_generation"]) for p in pages)
    candidates = []
    broad_by_gen = Counter()
    explicit_by_gen = Counter()
    named_by_gen = Counter()
    language_pages = Counter()
    language_books = defaultdict(set)
    language_generation_pages = Counter()
    language_generation_books = defaultdict(set)

    for page in pages:
        result = analyze_text(page.get("search_text") or "")
        if not result["broad_candidate"]:
            continue
        generation = str(page["catalog_generation"])
        broad_by_gen[generation] += 1
        if result["explicit_general"]:
            explicit_by_gen[generation] += 1
        if result["named_language_contextual"]:
            named_by_gen[generation] += 1
        languages = sorted(result["language_hits"])
        for language in languages:
            language_pages[language] += 1
            language_books[language].add(page["canonical_viewer_key"])
            language_generation_pages[(language, generation)] += 1
            language_generation_books[(language, generation)].add(page["canonical_viewer_key"])
        minimum_named_distance = min(
            (value["min_context_distance"] for value in result["language_hits"].values()), default=""
        )
        matched_forms = []
        for language in languages:
            matched_forms.extend(
                f"{language}:{form}" for form in result["language_hits"][language]["forms"]
            )
        candidates.append({
            "page_id": page["page_id"],
            "canonical_viewer_key": page["canonical_viewer_key"],
            "wave": page["wave"],
            "generation": generation,
            "grade_code": page["grade_code"],
            "title_core": page["title_core"],
            "page_index": page["page_index"],
            "viewer_page": page["viewer_page"],
            "source_asset_url": page["source_asset_url"],
            "source_sha256": page["source_sha256"],
            "ocr_sha256": page["ocr_sha256"],
            "ocr_confidence_mean": page["ocr_confidence_mean"],
            "explicit_general": int(result["explicit_general"]),
            "named_language_contextual": int(result["named_language_contextual"]),
            "matched_explicit_terms": ";".join(result["explicit_terms"]),
            "matched_language_groups": ";".join(languages),
            "matched_language_forms": ";".join(sorted(matched_forms)),
            "min_named_context_distance_tokens": minimum_named_distance,
            "concept_min_anchor_distance_tokens": (
                result["concept_min_anchor_distance"] if result["concept_min_anchor_distance"] is not None else ""
            ),
            "validation_status": "not_visually_validated",
        })

    candidates.sort(key=lambda row: (
        int(row["generation"]) if str(row["generation"]).isdigit() else str(row["generation"]),
        row["canonical_viewer_key"], int(row["page_index"] or 0), row["page_id"],
    ))
    generation_rows = []
    for generation in sorted(totals_by_gen, key=lambda value: int(value) if value.isdigit() else value):
        total = totals_by_gen[generation]
        broad = broad_by_gen[generation]
        explicit = explicit_by_gen[generation]
        named = named_by_gen[generation]
        generation_rows.append({
            "generation": generation,
            "total_pages": total,
            "broad_candidate_pages": broad,
            "explicit_general_pages": explicit,
            "named_language_contextual_pages": named,
            "broad_pages_per_1000": f"{broad / total * 1000:.4f}",
            "explicit_pages_per_1000": f"{explicit / total * 1000:.4f}",
            "named_context_pages_per_1000": f"{named / total * 1000:.4f}",
        })

    language_rows = [{
        "language_group": language,
        "candidate_pages": language_pages[language],
        "books_with_presence": len(language_books[language]),
    } for language in LANGUAGE_FORMS]
    language_rows.sort(key=lambda row: (-row["candidate_pages"], row["language_group"]))

    language_generation_rows = []
    for language in LANGUAGE_FORMS:
        for generation in sorted(totals_by_gen, key=lambda value: int(value) if value.isdigit() else value):
            count = language_generation_pages[(language, generation)]
            if count:
                language_generation_rows.append({
                    "language_group": language,
                    "generation": generation,
                    "candidate_pages": count,
                    "books_with_presence": len(language_generation_books[(language, generation)]),
                    "total_generation_pages": totals_by_gen[generation],
                    "pages_per_1000_generation_pages": f"{count / totals_by_gen[generation] * 1000:.4f}",
                })

    out_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = out_dir / "ltmd_u1_indigenous_languages_candidate_ledger_0_2.csv"
    generation_path = out_dir / "ltmd_u1_indigenous_languages_generation_summary_0_2.csv"
    language_path = out_dir / "ltmd_u1_indigenous_languages_named_language_counts_0_2.csv"
    language_generation_path = out_dir / "ltmd_u1_indigenous_languages_named_language_by_generation_0_2.csv"
    write_csv(candidate_path, list(candidates[0].keys()) if candidates else ["page_id"], candidates)
    write_csv(generation_path, list(generation_rows[0].keys()), generation_rows)
    write_csv(language_path, list(language_rows[0].keys()), language_rows)
    write_csv(language_generation_path,
              list(language_generation_rows[0].keys()) if language_generation_rows else ["language_group"],
              language_generation_rows)

    manifest = {
        "analysis_version": VERSION,
        "input_database_count": len(db_paths),
        "input_database_file_hashes": [
            {"basename": path.name, "sha256": sha256_file(path)} for path in sorted(db_paths)
        ],
        "corpus": {"unique_pages": total_pages, "unique_canonical_objects": len(objects)},
        "parameters": {
            "named_context_window_tokens": NAMED_CONTEXT_WINDOW,
            "concept_indigenous_window_tokens": CONCEPT_INDIGENOUS_WINDOW,
            "normalization": "Unicode NFKD + casefold + combining-mark removal + ASCII alphanumeric tokenization",
            "direct_explicit_phrases": list(DIRECT_EXPLICIT_PHRASES),
            "concept_phrases": list(CONCEPT_PHRASES),
            "linguistic_context_tokens": sorted(LINGUISTIC_CONTEXT_TOKENS),
            "indigenous_signal_tokens": sorted(INDIGENOUS_SIGNAL_TOKENS),
            "language_forms": {key: sorted(value) for key, value in LANGUAGE_FORMS.items()},
        },
        "results": {
            "broad_candidate_pages": len(candidates),
            "explicit_general_pages": sum(explicit_by_gen.values()),
            "named_language_contextual_pages": sum(named_by_gen.values()),
            "candidate_books": len({row["canonical_viewer_key"] for row in candidates}),
        },
        "scientific_state": {
            "source_visual_validation_complete": False,
            "text_verified_promotions": 0,
            "semantic_ready_promotions": 0,
            "note": "Independent deterministic rerun; do not tune to reproduce study 0.1 exploratory aggregates.",
        },
        "outputs": {
            candidate_path.name: sha256_file(candidate_path),
            generation_path.name: sha256_file(generation_path),
            language_path.name: sha256_file(language_path),
            language_generation_path.name: sha256_file(language_generation_path),
        },
    }
    manifest_path = out_dir / "ltmd_u1_indigenous_languages_rerun_manifest_0_2.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", action="append", required=True, help="SQLite database path; repeat for each DB")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-pages", type=int)
    parser.add_argument("--expected-objects", type=int)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    databases = [Path(path) for path in args.database]
    missing = [str(path) for path in databases if not path.is_file()]
    if missing:
        raise SystemExit("missing databases: " + ", ".join(missing))
    manifest = run(databases, Path(args.output_dir), args.expected_pages, args.expected_objects)
    print(json.dumps(manifest["results"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
