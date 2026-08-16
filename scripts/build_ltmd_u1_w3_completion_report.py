#!/usr/bin/env python3
"""Build the LTMD-U1 W3 Español/Lengua technical completion report from finalized artifacts only."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

PROC = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
MAN = Path('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv')
OCR = Path('data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv')
OCR_SUM = Path('data/catalog/ltmd_u1_w3_spanish_ocr_summary.csv')
STRUCT = Path('data/catalog/ltmd_u1_w3_spanish_page_structure.csv')
FRAGS = Path('data/catalog/ltmd_u1_w3_spanish_fragment_manifest.csv')
FRAG_SUM = Path('data/catalog/ltmd_u1_w3_spanish_fragment_manifest_summary.csv')
FRAG_GAPS = Path('data/catalog/ltmd_u1_w3_spanish_fragment_sequence_gaps.csv')
UNITS = Path('data/catalog/ltmd_u1_w3_spanish_exact_content_units.csv')
IDENTITY_PROJ = Path('data/catalog/ltmd_u1_w3_spanish_identity_content_projection.csv')
OVERLAP = Path('data/catalog/ltmd_u1_w3_spanish_exact_viewer_overlap.csv')
OUT = Path('docs/LTMD_U1_W3_COMPLETION.md')
VERSION = 'LTMD_U1_W3_COMPLETION_0.1'
EXPECTED_IDENTITIES = 130
EXPECTED_CANONICAL = 114
EXPECTED_ALIASES = 16
EXPECTED_PAGES = 20765
EXPECTED_SOURCE_GAPS = 8


def read(path):
    if not path.exists():
        raise SystemExit(f'missing finalized W3 artifact: {path}')
    return list(csv.DictReader(path.open(encoding='utf-8', newline='')))


def main():
    proc = read(PROC)
    man = read(MAN)
    ocr = read(OCR)
    ocr_sum = read(OCR_SUM)
    struct = read(STRUCT)
    frags = read(FRAGS)
    frag_sum = read(FRAG_SUM)
    gap_rows = read(FRAG_GAPS)
    units = read(UNITS)
    identity_proj = read(IDENTITY_PROJ)
    overlap = read(OVERLAP)

    if len(proc) != EXPECTED_IDENTITIES or len({r['viewer_key'] for r in proc}) != EXPECTED_IDENTITIES:
        raise SystemExit('W3 completion: processing inventory cardinality failure')
    eligible = {r['viewer_key'] for r in proc if r['ocr_identity_eligible'] == '1'}
    canonical = {r['viewer_key'] for r in proc if r['is_canonical_processing_object'] == '1'}
    aliases = eligible - canonical
    exact_alias = {r['viewer_key'] for r in proc if r['processing_mode'] == 'exact_byte_alias'}
    route_alias = {r['viewer_key'] for r in proc if r['processing_mode'] == 'paired_route_alias_2018_to_2019'}
    source_gaps = sum(int(r['persistent_internal_source_gaps'] or 0) for r in proc if r['viewer_key'] in canonical)
    if len(eligible) != EXPECTED_IDENTITIES or len(canonical) != EXPECTED_CANONICAL or len(aliases) != EXPECTED_ALIASES:
        raise SystemExit('W3 completion: processing topology failure')
    if len(exact_alias) != 8 or len(route_alias) != 8 or exact_alias | route_alias != aliases:
        raise SystemExit('W3 completion: alias-vocabulary/topology failure')
    if source_gaps != EXPECTED_SOURCE_GAPS:
        raise SystemExit('W3 completion: persistent-source-gap count failure')

    if len(man) != EXPECTED_PAGES or {r['viewer_key'] for r in man} != canonical:
        raise SystemExit('W3 completion: canonical page manifest failure')
    if any(r['asset_status'] != 'source_jpeg' for r in man):
        raise SystemExit('W3 completion: non-source row in canonical page manifest')

    if len(ocr) != EXPECTED_PAGES or len(ocr_sum) != EXPECTED_CANONICAL:
        raise SystemExit('W3 completion: OCR cardinality failure')
    if {r['ocr_version'] for r in ocr} != {'LTMD_U1_W3_SPANISH_OCR_0.1'}:
        raise SystemExit('W3 completion: OCR version failure')
    if any(r['source_sha256_verified'] != '1' or r['ocr_status'] != 'ok' or r['ocr_class'] == 'unresolved' for r in ocr):
        raise SystemExit('W3 completion: OCR provenance/execution failure')
    text_detected = sum(r['ocr_class'] == 'text_detected' for r in ocr)
    no_text = sum(r['ocr_class'] == 'no_text_detected' for r in ocr)
    if text_detected + no_text != EXPECTED_PAGES:
        raise SystemExit('W3 completion: OCR class accounting failure')

    if len(struct) != EXPECTED_PAGES or {r['viewer_key'] for r in struct} != canonical:
        raise SystemExit('W3 completion: PAGESTRUCT cardinality failure')
    if {r['classifier_version'] for r in struct} != {'PAGESTRUCT_LTMD_U1_W3_SPANISH_0.1'}:
        raise SystemExit('W3 completion: PAGESTRUCT version failure')
    struct_counts = Counter(r['primary_structure'] for r in struct)
    frag_eligible = struct_counts['textual'] + struct_counts['mixed_text_image']
    if frag_eligible <= 0:
        raise SystemExit('W3 completion: no FRAGSEG-eligible pages')

    if not frags or {r['viewer_key'] for r in frags} != canonical:
        raise SystemExit('W3 completion: FRAGSEG viewer coverage failure')
    if {r['segmenter_version'] for r in frags} != {'FRAGSEG_LTMD_U1_W3_SPANISH_0.1'}:
        raise SystemExit('W3 completion: FRAGSEG version failure')
    frag_ids = [r['fragment_id'] for r in frags]
    if len(frag_ids) != len(set(frag_ids)):
        raise SystemExit('W3 completion: duplicate fragment IDs')
    all_summary = [r for r in frag_sum if r['viewer_key'] == 'ALL']
    if len(all_summary) != 1 or int(all_summary[0]['fragment_count']) != len(frags):
        raise SystemExit('W3 completion: FRAGSEG summary mismatch')
    segmented_pages = int(all_summary[0]['segmented_page_count'])
    if segmented_pages > frag_eligible:
        raise SystemExit('W3 completion: segmented pages exceed eligible pages')
    empty_eligible = frag_eligible - segmented_pages
    gap_slots = sum(int(r.get('missing_slot_count') or 0) for r in gap_rows)

    if not units:
        raise SystemExit('W3 completion: exact-content-unit view empty')
    if len(identity_proj) != EXPECTED_IDENTITIES or len({r['viewer_key'] for r in identity_proj}) != EXPECTED_IDENTITIES:
        raise SystemExit('W3 completion: identity-content projection failure')
    unique_hashes = {r['text_sha256'] for r in frags}
    if len(units) != len(unique_hashes) or {r['text_sha256'] for r in units} != unique_hashes:
        raise SystemExit('W3 completion: exact-content-unit/hash mismatch')
    repeated_units = sum(int(r['canonical_occurrence_count']) > 1 for r in units)
    cross_viewer_units = sum(int(r['canonical_viewer_count']) > 1 for r in units)
    cross_generation_units = sum(int(r['represented_catalog_generation_count']) > 1 for r in units)

    candidate_counts = Counter(r['candidate_type'] for r in frags)
    classes = ['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown']

    lines = [
        '# LTMD-U1 W3 — cierre técnico de Español/Lengua',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '## Resultado ejecutivo',
        '',
        f'- Identidades de catálogo cubiertas operacionalmente: **{len(eligible)}/{EXPECTED_IDENTITIES}**.',
        f'- Contenidos canónicos computados: **{len(canonical)}**.',
        f'- Aliases de provenance: **{len(aliases)}** — byte-exactos: **{len(exact_alias)}**; ruta pareada 2018→2019: **{len(route_alias)}**.',
        f'- Huecos internos persistentes de fuente: **{source_gaps}**, preservados sin renumeración.',
        f'- Páginas fuente canónicas: **{len(man):,}**.',
        '',
        '## OCR 0.1',
        '',
        f'- Páginas canónicas procesadas: **{len(ocr):,}**.',
        f'- SHA-256 verificados: **{len(ocr):,}/{len(ocr):,}**.',
        f'- Texto detectado: **{text_detected:,} ({100*text_detected/len(ocr):.2f}%)**.',
        f'- `no_text_detected`: **{no_text:,}**.',
        '- `unresolved`: **0**.',
        '',
        '## PAGESTRUCT 0.1',
        '',
        f'- Páginas clasificadas: **{len(struct):,}**.',
    ]
    for cls in classes:
        lines.append(f'- `{cls}`: **{struct_counts[cls]:,}**.')
    lines += [
        f'- Páginas elegibles para FRAGSEG: **{frag_eligible:,}**.',
        '',
        '## FRAGSEG 0.1',
        '',
        f'- Páginas con ≥1 fragmento: **{segmented_pages:,}**.',
        f'- Páginas elegibles sin fragmentos: **{empty_eligible:,}**.',
        f'- Fragmentos técnicos: **{len(frags):,}**.',
        f'- IDs de fragmento únicos: **{len(set(frag_ids)):,}**.',
        f'- Páginas con huecos legítimos de secuencia: **{len(gap_rows):,}**.',
        f'- Slots omitidos: **{gap_slots:,}**.',
        '',
        '### Tipos candidatos',
        '',
    ]
    for typ in sorted(candidate_counts):
        lines.append(f'- `{typ}`: **{candidate_counts[typ]:,}**.')
    lines += [
        '',
        '## Reutilización textual exacta y dependencia documental',
        '',
        f'- Unidades textuales exactas únicas: **{len(units):,}**.',
        f'- Unidades repetidas en ≥2 ocurrencias canónicas: **{repeated_units:,}**.',
        f'- Unidades presentes en ≥2 visores canónicos: **{cross_viewer_units:,}**.',
        f'- Unidades representadas en ≥2 generaciones de catálogo: **{cross_generation_units:,}**.',
        f'- Pares de visores canónicos con ≥1 unidad exacta compartida: **{len(overlap):,}**.',
        '',
        '## Límite epistemológico',
        '',
        'Este es un cierre **técnico**, no una validación semántica. El proyecto opera temporalmente sin referencia humana. La confianza interna de Tesseract no equivale a exactitud textual validada; los tipos de FRAGSEG son candidatos técnicos; y la igualdad de `text_sha256` prueba únicamente igualdad dentro de la representación OCR+segmentación fijada, no equivalencia bibliográfica, curricular, pedagógica ni semántica.',
        '',
        '`SEMB03` permanece en `WAITING_HUMAN_REFERENCE`. La ausencia de referencia humana no invalida ni detiene estas capas de procedencia, estructura, segmentación y dependencia documental.',
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
