#!/usr/bin/env python3
"""Rebuild and validate the LTMD-U1 W4 Social Sciences technical completion report.

The report is derived only from finalized W4 artifacts. Any cardinality,
provenance, version, topology, PAGESTRUCT, FRAGSEG or exact-reuse drift aborts
rather than silently rewriting the technical closure.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

PROC = Path('data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv')
MAN = Path('data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv')
OCR = Path('data/catalog/ltmd_u1_w4_social_sciences_ocr_metrics.csv')
OCR_SUM = Path('data/catalog/ltmd_u1_w4_social_sciences_ocr_summary.csv')
STRUCT = Path('data/catalog/ltmd_u1_w4_social_sciences_page_structure.csv')
STRUCT_SUM = Path('data/catalog/ltmd_u1_w4_social_sciences_page_structure_summary.csv')
FRAGS = Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest.csv')
FRAG_SUM = Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_manifest_summary.csv')
FRAG_GAPS = Path('data/catalog/ltmd_u1_w4_social_sciences_fragment_sequence_gaps.csv')
UNITS = Path('data/catalog/ltmd_u1_w4_social_sciences_exact_content_units.csv')
OVERLAP = Path('data/catalog/ltmd_u1_w4_social_sciences_exact_viewer_overlap.csv')
OUT = Path('docs/LTMD_U1_W4_COMPLETION.md')

VERSION = 'LTMD_U1_W4_COMPLETION_0.1'
PROC_VERSION = 'LTMD_U1_W4_SOCIAL_SCIENCES_PROCESSING_0.1'
MAN_VERSION = 'LTMD_U1_W4_SOCIAL_SCIENCES_CANONICAL_PAGE_MANIFEST_0.1'
OCR_VERSION = 'LTMD_U1_W4_SOCIAL_SCIENCES_OCR_0.1'
STRUCT_VERSION = 'PAGESTRUCT_LTMD_U1_W4_SOCIAL_SCIENCES_0.1'
FRAG_VERSION = 'FRAGSEG_LTMD_U1_W4_SOCIAL_SCIENCES_0.1'
REUSE_VERSION = 'LTMD_U1_W4_SOCIAL_SCIENCES_EXACT_REUSE_0.1'

EXPECTED_IDENTITIES = 14
EXPECTED_PAGES = 2414
EXPECTED_FRAG_PAGES = 2018
EXPECTED_FRAGMENTS = 21380
EXPECTED_GAP_PAGES = 42
EXPECTED_GAP_SLOTS = 46
EXPECTED_UNITS = 17735
EXPECTED_REPEATED_UNITS = 2503
EXPECTED_CROSS_VIEWER_UNITS = 2454
EXPECTED_CROSS_GENERATION_UNITS = 2431
EXPECTED_OVERLAP_PAIRS = 85

STRUCT_CLASSES = [
    'textual', 'mixed_text_image', 'visual_only', 'front_matter',
    'toc_or_navigation', 'bibliography_or_credits', 'unknown',
]


def read(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f'missing finalized W4 artifact: {path}')
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f'W4 completion: {message}')


def main() -> None:
    proc = read(PROC)
    man = read(MAN)
    ocr = read(OCR)
    ocr_sum = read(OCR_SUM)
    struct = read(STRUCT)
    struct_sum = read(STRUCT_SUM)
    frags = read(FRAGS)
    frag_sum = read(FRAG_SUM)
    gap_rows = read(FRAG_GAPS)
    units = read(UNITS)
    overlap = read(OVERLAP)

    # Processing topology.
    viewers = {row['viewer_key'] for row in proc}
    require(len(proc) == EXPECTED_IDENTITIES and len(viewers) == EXPECTED_IDENTITIES,
            'processing inventory cardinality failure')
    require({row['processing_version'] for row in proc} == {PROC_VERSION},
            'processing version drift')
    require(all(row['ocr_identity_eligible'] == '1' for row in proc),
            'non-eligible identity present')
    require(all(row['is_canonical_processing_object'] == '1' for row in proc),
            'non-canonical processing object present')
    require(all(row['processing_mode'] == 'direct_canonical' for row in proc),
            'unexpected processing alias/mode')
    require(all(row['canonical_processing_viewer_key'] == row['viewer_key'] for row in proc),
            'canonical viewer mapping drift')
    source_gaps = sum(int(row['persistent_internal_source_gaps'] or 0) for row in proc)
    require(source_gaps == 0, 'persistent source gaps are no longer zero')

    # Canonical source pages.
    require(len(man) == EXPECTED_PAGES, 'canonical page cardinality failure')
    require({row['viewer_key'] for row in man} == viewers, 'canonical viewer coverage mismatch')
    require({row['manifest_version'] for row in man} == {MAN_VERSION}, 'manifest version drift')
    require(all(row['asset_status'] == 'source_jpeg' for row in man), 'non-source page in canonical manifest')
    require(all(row['processing_mode'] == 'direct_canonical' for row in man), 'canonical manifest processing-mode drift')
    require(all(row['page_numbering_policy'] == 'preserve_original_viewer_page_no_renumbering' for row in man),
            'page-numbering policy drift')
    page_ids = {(row['viewer_key'], row['viewer_page']) for row in man}
    require(len(page_ids) == EXPECTED_PAGES, 'duplicate canonical viewer/page key')

    # OCR.
    require(len(ocr) == EXPECTED_PAGES and len(ocr_sum) == EXPECTED_IDENTITIES,
            'OCR cardinality failure')
    require({row['ocr_version'] for row in ocr} == {OCR_VERSION}, 'OCR version drift')
    require({row['viewer_key'] for row in ocr} == viewers, 'OCR viewer coverage mismatch')
    require(all(row['source_sha256_verified'] == '1' for row in ocr), 'OCR source hash verification failure')
    require(all(row['ocr_status'] == 'ok' for row in ocr), 'OCR execution failure')
    require(all(row['ocr_class'] != 'unresolved' for row in ocr), 'unresolved OCR page persisted')
    text_detected = sum(row['ocr_class'] == 'text_detected' for row in ocr)
    no_text = sum(row['ocr_class'] == 'no_text_detected' for row in ocr)
    require(text_detected + no_text == EXPECTED_PAGES, 'OCR class accounting failure')
    require(sum(int(row['pages']) for row in ocr_sum) == EXPECTED_PAGES, 'OCR summary page total mismatch')
    require(sum(int(row['sha_verified']) for row in ocr_sum) == EXPECTED_PAGES, 'OCR summary SHA total mismatch')
    require(sum(int(row['unresolved']) for row in ocr_sum) == 0, 'OCR summary unresolved count nonzero')

    # PAGESTRUCT.
    require(len(struct) == EXPECTED_PAGES, 'PAGESTRUCT cardinality failure')
    require({row['viewer_key'] for row in struct} == viewers, 'PAGESTRUCT viewer coverage mismatch')
    require({row['classifier_version'] for row in struct} == {STRUCT_VERSION}, 'PAGESTRUCT version drift')
    struct_counts = Counter(row['primary_structure'] for row in struct)
    require(set(struct_counts) <= set(STRUCT_CLASSES), 'unexpected PAGESTRUCT class')
    all_struct = [row for row in struct_sum if row['viewer_key'] == 'ALL']
    require(len(all_struct) == 1, 'PAGESTRUCT ALL summary missing/duplicated')
    summary_struct = all_struct[0]
    require(int(summary_struct['n_pages']) == EXPECTED_PAGES, 'PAGESTRUCT summary total mismatch')
    for cls in STRUCT_CLASSES:
        require(int(summary_struct[cls]) == struct_counts[cls], f'PAGESTRUCT summary mismatch for {cls}')
    frag_eligible = struct_counts['textual'] + struct_counts['mixed_text_image']
    require(frag_eligible == EXPECTED_FRAG_PAGES, 'FRAGSEG-eligible page count drift')

    # FRAGSEG.
    require(len(frags) == EXPECTED_FRAGMENTS, 'FRAGSEG fragment cardinality failure')
    require({row['viewer_key'] for row in frags} == viewers, 'FRAGSEG viewer coverage mismatch')
    require({row['segmenter_version'] for row in frags} == {FRAG_VERSION}, 'FRAGSEG version drift')
    fragment_ids = [row['fragment_id'] for row in frags]
    require(len(fragment_ids) == len(set(fragment_ids)), 'duplicate fragment IDs')
    require(all(row.get('text_sha256') for row in frags), 'fragment without text_sha256')
    all_frag = [row for row in frag_sum if row['viewer_key'] == 'ALL']
    require(len(all_frag) == 1, 'FRAGSEG ALL summary missing/duplicated')
    summary_frag = all_frag[0]
    require(summary_frag['segmenter_version'] == FRAG_VERSION, 'FRAGSEG summary version drift')
    require(int(summary_frag['fragment_count']) == EXPECTED_FRAGMENTS, 'FRAGSEG summary fragment count mismatch')
    require(int(summary_frag['segmented_page_count']) == EXPECTED_FRAG_PAGES, 'FRAGSEG segmented page count mismatch')
    candidate_fields = [field for field in summary_frag if field.endswith('_candidate')]
    candidate_counts = Counter(row['candidate_type'] for row in frags)
    require(sum(candidate_counts.values()) == EXPECTED_FRAGMENTS, 'candidate-type accounting failure')
    for field in candidate_fields:
        require(int(summary_frag[field]) == candidate_counts[field], f'candidate summary mismatch for {field}')
    gap_slots = sum(int(row.get('missing_slot_count') or 0) for row in gap_rows)
    require(len(gap_rows) == EXPECTED_GAP_PAGES, 'FRAGSEG sequence-gap page count drift')
    require(gap_slots == EXPECTED_GAP_SLOTS, 'FRAGSEG sequence-gap slot count drift')

    # Exact reuse/dependence.
    require(len(units) == EXPECTED_UNITS, 'exact-content unit cardinality failure')
    require(len({row['text_sha256'] for row in units}) == EXPECTED_UNITS, 'duplicate exact-content hashes')
    require({row['analysis_version'] for row in units} == {REUSE_VERSION}, 'exact-reuse unit version drift')
    require({row['analysis_version'] for row in overlap} == {REUSE_VERSION}, 'exact-reuse overlap version drift')
    require({row['text_sha256'] for row in units} == {row['text_sha256'] for row in frags},
            'exact-content unit/hash coverage mismatch')
    repeated_units = sum(int(row['occurrence_count']) > 1 for row in units)
    cross_viewer_units = sum(int(row['viewer_count']) > 1 for row in units)
    cross_generation_units = sum(int(row['catalog_generation_count']) > 1 for row in units)
    require(repeated_units == EXPECTED_REPEATED_UNITS, 'repeated-unit count drift')
    require(cross_viewer_units == EXPECTED_CROSS_VIEWER_UNITS, 'cross-viewer unit count drift')
    require(cross_generation_units == EXPECTED_CROSS_GENERATION_UNITS, 'cross-generation unit count drift')
    require(len(overlap) == EXPECTED_OVERLAP_PAIRS, 'exact-viewer-overlap pair count drift')

    lines = [
        '# LTMD-U1 W4 — cierre técnico Ciencias Sociales',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '## Resultado ejecutivo',
        f'- Identidades/canónicos técnicos: **{len(viewers)}/{EXPECTED_IDENTITIES}**.',
        '- Aliases de libro completo byte-exacto: **0**.',
        f'- Huecos internos de fuente: **{source_gaps}**.',
        f'- Páginas canónicas: **{len(man):,}**.',
        '',
        '## OCR 0.1',
        f'- SHA-256 verificados: **{len(ocr):,}/{len(ocr):,}**.',
        f'- Texto detectado: **{text_detected:,} ({100 * text_detected / len(ocr):.2f}%)**.',
        f'- `no_text_detected`: **{no_text:,}**.',
        '- `unresolved`: **0**.',
        '',
        '## PAGESTRUCT 0.1',
    ]
    for cls in STRUCT_CLASSES:
        lines.append(f'- `{cls}`: **{struct_counts[cls]:,}**.')
    lines += [
        '',
        f'- Páginas elegibles para FRAGSEG: **{frag_eligible:,}**.',
        '',
        '## FRAGSEG 0.1',
        f'- Páginas con ≥1 fragmento: **{int(summary_frag["segmented_page_count"]):,}**.',
        f'- Páginas elegibles sin fragmentos: **{frag_eligible - int(summary_frag["segmented_page_count"]):,}**.',
        f'- Fragmentos técnicos: **{len(frags):,}**.',
        f'- IDs únicos: **{len(set(fragment_ids)):,}**.',
        f'- Páginas con huecos legítimos de secuencia: **{len(gap_rows):,}**.',
        f'- Slots omitidos: **{gap_slots:,}**.',
        '',
        '### Tipos candidatos',
    ]
    for typ in sorted(candidate_counts):
        lines.append(f'- `{typ}`: **{candidate_counts[typ]:,}**.')
    lines += [
        '',
        '## Reutilización textual exacta',
        f'- Unidades exactas únicas: **{len(units):,}**.',
        f'- Unidades repetidas: **{repeated_units:,}**.',
        f'- Unidades presentes en ≥2 visores: **{cross_viewer_units:,}**.',
        f'- Unidades presentes en ≥2 generaciones: **{cross_generation_units:,}**.',
        f'- Pares de visores con ≥1 unidad exacta compartida: **{len(overlap):,}**.',
        '',
        '## Límite epistemológico',
        'Este cierre es técnico. El proyecto opera temporalmente sin referencia humana: no se afirma CER/WER validado, desempeño semántico contra gold standard ni equivalencia curricular/pedagógica a partir de las categorías automáticas. PAGESTRUCT, FRAGSEG y `text_sha256` se usan como infraestructura y evidencia de estructura/dependencia documental, no como sustituto de validación humana.',
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
