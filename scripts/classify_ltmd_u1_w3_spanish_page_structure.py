#!/usr/bin/env python3
"""Classify canonical W3 Español/Lengua pages with the frozen conservative PAGESTRUCT logic."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

METRICS = Path('data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv')
FLAGS = Path('data/catalog/ltmd_u1_w3_spanish_structural_keyword_flags.csv')
PROC = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_page_structure.csv')
SUMMARY = Path('data/catalog/ltmd_u1_w3_spanish_page_structure_summary.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_page_structure.md')
VERSION = 'PAGESTRUCT_LTMD_U1_W3_SPANISH_0.1'
EXPECTED_CANONICAL = 114
EXPECTED_IDENTITIES = 130
EXPECTED_ALIASES = 16
EXPECTED_GAPS = 8
EXPECTED_PAGES = 20765


def fnum(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def inum(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def classify(row, kw):
    words = inum(row.get('recognized_words'))
    conf = fnum(row.get('mean_word_confidence'), 0) or 0
    low = fnum(row.get('low_confidence_word_rate'), 1)
    psm = inum(row.get('selected_psm'))
    ocr_class = row.get('ocr_class', '')
    front = inum(kw.get('front_zone'))
    end = inum(kw.get('end_zone'))
    front_score = inum(kw.get('front_matter_score'))
    nav_score = inum(kw.get('toc_navigation_score'))
    biblio_score = inum(kw.get('bibliography_credits_score'))
    fallback = psm in (6, 11)
    visual = ocr_class == 'no_text_detected' or (fallback and conf < 50 and low >= .65) or (words <= 3 and conf < 50)
    strong = words >= 120 and conf >= 75 and low <= .25
    moderate = words >= 20 and conf >= 60 and low <= .40
    dense_end = end and words >= 800 and conf < 85
    evidence = []
    if front: evidence.append('front_zone')
    if end: evidence.append('end_zone')
    if fallback: evidence.append('fallback_psm')
    if visual: evidence.append('visual_noise')
    if strong: evidence.append('text_rich')
    elif moderate: evidence.append('text_present')
    if dense_end: evidence.append('dense_end_uncertain')
    if front_score: evidence.append('front_kw')
    if nav_score: evidence.append('nav_kw')
    if biblio_score: evidence.append('biblio_credit_kw')

    if biblio_score >= 2 or (biblio_score >= 1 and (front or end) and conf >= 55):
        primary, certainty, rule = 'bibliography_or_credits', ('high' if biblio_score >= 2 else 'medium'), 'KW_BIBLIO_CREDITS'
    elif nav_score >= 2 or (nav_score >= 1 and front and conf >= 65):
        primary, certainty, rule = 'toc_or_navigation', ('high' if nav_score >= 2 else 'medium'), 'KW_NAVIGATION'
    elif front_score >= 1 and front and conf >= 55:
        primary, certainty, rule = 'front_matter', ('medium' if front_score == 1 else 'high'), 'KW_FRONT_MATTER'
    elif visual:
        primary, certainty, rule = 'visual_only', ('high' if (fallback and low >= .80) or ocr_class == 'no_text_detected' else 'medium'), 'OCR_VISUAL_NOISE'
    elif dense_end:
        primary, certainty, rule = 'unknown', 'medium', 'END_ZONE_DENSE_UNCERTAIN'
    elif strong:
        primary, certainty, rule = 'textual', 'high', 'OCR_TEXT_RICH'
    elif moderate:
        primary, certainty, rule = 'mixed_text_image', 'medium', 'OCR_MODERATE_TEXT'
    elif words >= 4 and conf >= 75 and low <= .30:
        primary, certainty, rule = 'mixed_text_image', 'low', 'OCR_SPARSE_HIGH_CONF'
    else:
        primary, certainty, rule = 'unknown', 'low', 'CONSERVATIVE_UNKNOWN'
    return primary, certainty, rule, ';'.join(evidence)


def main():
    metrics = list(csv.DictReader(METRICS.open(encoding='utf-8', newline='')))
    flags = {r['page_id']: r for r in csv.DictReader(FLAGS.open(encoding='utf-8', newline=''))}
    proc_rows = list(csv.DictReader(PROC.open(encoding='utf-8', newline='')))
    if len(metrics) != EXPECTED_PAGES:
        raise SystemExit(f'W3 PAGESTRUCT requires {EXPECTED_PAGES} OCR pages, got {len(metrics)}')
    if len({r['viewer_key'] for r in metrics}) != EXPECTED_CANONICAL:
        raise SystemExit(f'W3 PAGESTRUCT requires {EXPECTED_CANONICAL} canonical viewers')
    if len(proc_rows) != EXPECTED_IDENTITIES:
        raise SystemExit('W3 processing inventory cardinality mismatch')
    canonical = {r['viewer_key'] for r in proc_rows if r['is_canonical_processing_object'] == '1'}
    aliases = {r['viewer_key'] for r in proc_rows if r['ocr_identity_eligible'] == '1'} - canonical
    gaps = sum(int(r['persistent_internal_source_gaps'] or 0) for r in proc_rows if r['viewer_key'] in canonical)
    if len(canonical) != EXPECTED_CANONICAL or len(aliases) != EXPECTED_ALIASES or gaps != EXPECTED_GAPS:
        raise SystemExit('W3 processing topology mismatch')

    out = []
    for row in metrics:
        kw = flags.get(row['page_id'], {})
        primary, certainty, rule, evidence = classify(row, kw)
        out.append({
            'page_id': row['page_id'],
            'viewer_key': row['viewer_key'],
            'catalog_generation': row['catalog_generation'],
            'grade': row['grade'],
            'title_core': row['title_core'],
            'viewer_page': row['viewer_page'],
            'selected_psm': row['selected_psm'],
            'recognized_words': row['recognized_words'],
            'mean_word_confidence': row['mean_word_confidence'],
            'low_confidence_word_rate': row['low_confidence_word_rate'],
            'ocr_class': row['ocr_class'],
            'front_matter_score': kw.get('front_matter_score', ''),
            'toc_navigation_score': kw.get('toc_navigation_score', ''),
            'bibliography_credits_score': kw.get('bibliography_credits_score', ''),
            'primary_structure': primary,
            'classification_certainty': certainty,
            'classification_rule': rule,
            'evidence_flags': evidence,
            'classifier_version': VERSION,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)

    counts = defaultdict(Counter)
    for row in out:
        counts[row['viewer_key']][row['primary_structure']] += 1
        counts['ALL'][row['primary_structure']] += 1
    classes = ['textual','mixed_text_image','visual_only','front_matter','toc_or_navigation','bibliography_or_credits','unknown']
    summary = []
    for key in sorted([x for x in counts if x != 'ALL']) + ['ALL']:
        c = counts[key]
        rec = {'viewer_key': key, 'n_pages': sum(c.values())}
        rec.update({cl: c[cl] for cl in classes})
        summary.append(rec)
    with SUMMARY.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    allc = counts['ALL']
    eligible = allc['textual'] + allc['mixed_text_image']
    lines = [
        '# PAGESTRUCT — LTMD-U1 W3 Español/Lengua',
        '',
        f'Versión: `{VERSION}`. Páginas clasificadas: **{len(out):,}**.',
        '',
        f'Objetos canónicos: **{EXPECTED_CANONICAL}**; representan **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}** identidades mediante **{EXPECTED_ALIASES}** aliases de provenance.',
        f'Huecos internos persistentes preservados sin renumeración: **{EXPECTED_GAPS}**.',
        '',
        '## Total',
    ]
    for cl in classes:
        lines.append(f'- `{cl}`: {allc[cl]:,}.')
    lines += [
        '',
        f'Páginas elegibles para FRAGSEG (`textual` + `mixed_text_image`): **{eligible:,}**.',
        '',
        '## Regla',
        'Se conserva la lógica PAGESTRUCT conservadora usada en Ciencias Naturales, W1 y W2. Esta capa es estructural, no pedagógica ni semántica. La ausencia temporal de referencia humana no impide PAGESTRUCT/FRAGSEG, pero sí impide tratar cualquier clasificador semántico no validado como evidencia histórica primaria.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
