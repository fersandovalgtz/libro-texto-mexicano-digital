#!/usr/bin/env python3
"""Build the canonical page manifest for LTMD-U1 W3 Spanish/Language.

This is the sole source topology authorized for downstream OCR. It retains only
source JPEG rows for the 114 canonical processing objects, preserves original
viewer-page numbers, and excludes aliases, terminal synthetic candidates, and
persistently unserved internal positions without renumbering anything.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

PROCESSING = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
ASSETS = Path('data/catalog/ltmd_u1_w3_spanish_asset_manifest.csv')
GAPS = Path('data/catalog/ltmd_u1_w3_spanish_internal_unserved_audit.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv')
GAP_OUT = Path('data/catalog/ltmd_u1_w3_spanish_canonical_gap_manifest.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.md')
VERSION = 'LTMD_U1_W3_SPANISH_CANONICAL_PAGE_MANIFEST_0.1'
EXPECTED_IDENTITIES = 130
EXPECTED_CANONICAL = 114
EXPECTED_PERSISTENT_GAPS = 8


def main():
    processing = list(csv.DictReader(PROCESSING.open(encoding='utf-8')))
    assets = list(csv.DictReader(ASSETS.open(encoding='utf-8')))
    gaps = list(csv.DictReader(GAPS.open(encoding='utf-8')))

    if len(processing) != EXPECTED_IDENTITIES or len({r['viewer_key'] for r in processing}) != EXPECTED_IDENTITIES:
        raise SystemExit('W3 processing inventory cardinality drift')
    if any(r['ocr_identity_eligible'] != '1' for r in processing):
        raise SystemExit('W3 contains OCR-ineligible identities')

    canonical_rows = [r for r in processing if r['is_canonical_processing_object'] == '1']
    canonical_keys = {r['viewer_key'] for r in canonical_rows}
    if len(canonical_rows) != EXPECTED_CANONICAL or len(canonical_keys) != EXPECTED_CANONICAL:
        raise SystemExit(f'expected {EXPECTED_CANONICAL} canonical viewers, got {len(canonical_keys)}')

    alias_keys = {r['viewer_key'] for r in processing if r['is_canonical_processing_object'] != '1'}
    if canonical_keys & alias_keys:
        raise SystemExit('canonical/alias key overlap')

    proc = {r['viewer_key']: r for r in processing}
    asset_by_key = defaultdict(list)
    for r in assets:
        asset_by_key[r['viewer_key']].append(r)
    missing_asset_viewers = sorted(canonical_keys - set(asset_by_key))
    if missing_asset_viewers:
        raise SystemExit(f'canonical viewers absent from source manifest: {missing_asset_viewers}')

    out = []
    for key in sorted(canonical_keys, key=lambda k: (int(proc[k]['catalog_generation']), int(proc[k]['grade_code']), k)):
        p = proc[key]
        rr = sorted(asset_by_key[key], key=lambda r: int(r['viewer_page']))
        source = [r for r in rr if r['asset_status'] == 'source_jpeg']
        if not source:
            raise SystemExit(f'{key}: canonical object has no source JPEG')
        seen_pages = set()
        for r in source:
            vp = int(r['viewer_page'])
            if vp in seen_pages:
                raise SystemExit(f'{key}: duplicate source viewer_page {vp}')
            seen_pages.add(vp)
            if not r['sha256'] or not r['byte_size'] or not r['source_asset_url']:
                raise SystemExit(f'{key} VP{vp}: missing cryptographic/source fields')
            out.append({
                'manifest_version': VERSION,
                'viewer_key': key,
                'catalog_generation': p['catalog_generation'],
                'grade_code': p['grade_code'],
                'title_core': p['title_core'],
                'processing_mode': p['processing_mode'],
                'viewer_page': r['viewer_page'],
                'source_image_index': r['source_image_index'],
                'source_asset_url': r['source_asset_url'],
                'byte_size': r['byte_size'],
                'sha256': r['sha256'],
                'asset_status': r['asset_status'],
                'page_numbering_policy': 'preserve_original_viewer_page_no_renumbering',
                'source_provenance': 'W3_asset_manifest_source_jpeg',
            })

    # Persist the reconciled missing positions separately rather than manufacturing rows.
    gap_rows = []
    for g in gaps:
        if g['target_state'] != 'internal_unserved_position_observed':
            continue
        key = g['viewer_key']
        if key not in canonical_keys:
            raise SystemExit(f'persistent gap belongs to noncanonical viewer {key}')
        gap_rows.append({
            'manifest_version': VERSION,
            'viewer_key': key,
            'catalog_generation': g['catalog_generation'],
            'grade_code': g['grade_code'],
            'title_core': g['title_core'],
            'viewer_page': g['viewer_page'],
            'source_image_index': g['source_image_index'],
            'source_asset_url': g['target_url'],
            'gap_state': g['target_state'],
            'available_neighbours_sha_verified': g['available_neighbours_sha_verified'],
            'ocr_policy': g['ocr_policy'],
            'page_numbering_policy': 'preserve_gap_no_renumbering',
            'interpretive_limit': g['interpretive_limit'],
        })
    if len(gap_rows) != EXPECTED_PERSISTENT_GAPS:
        raise SystemExit(f'expected {EXPECTED_PERSISTENT_GAPS} persistent gaps, got {len(gap_rows)}')

    if any(r['viewer_key'] in alias_keys for r in out):
        raise SystemExit('alias leaked into canonical page manifest')
    if any(r['asset_status'] != 'source_jpeg' for r in out):
        raise SystemExit('non-source asset leaked into canonical page manifest')
    pairs = [(r['viewer_key'], r['viewer_page']) for r in out]
    if len(pairs) != len(set(pairs)):
        raise SystemExit('duplicate canonical viewer/page rows')

    # Cross-check every canonical book against the source audit state.
    counts = Counter(r['viewer_key'] for r in out)
    for p in canonical_rows:
        key = p['viewer_key']
        expected = int(p['direct_source_jpegs'])
        if counts[key] != expected:
            raise SystemExit(f'{key}: canonical source-page count {counts[key]} != expected {expected}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)
    with GAP_OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(gap_rows[0]))
        w.writeheader(); w.writerows(sorted(gap_rows, key=lambda r: (r['viewer_key'], int(r['viewer_page']))))

    by_gen = defaultdict(lambda: {'viewers': set(), 'pages': 0, 'gaps': 0})
    for r in out:
        g = by_gen[r['catalog_generation']]; g['viewers'].add(r['viewer_key']); g['pages'] += 1
    for r in gap_rows:
        by_gen[r['catalog_generation']]['gaps'] += 1

    lines = [
        '# LTMD-U1 W3 — manifiesto canónico de páginas Español/Lengua', '',
        f'Versión: `{VERSION}`.', '',
        f'- Identidades institucionales cubiertas operacionalmente: **{EXPECTED_IDENTITIES}/{EXPECTED_IDENTITIES}**.',
        f'- Objetos canónicos únicos: **{len(canonical_keys)}**.',
        f'- Páginas fuente canónicas autorizadas para OCR: **{len(out):,}**.',
        f'- Huecos internos persistentes preservados fuera del manifiesto OCR: **{len(gap_rows)}**.',
        f'- Aliases excluidos del cómputo duplicado: **{len(alias_keys)}**.',
        '- Filas no `source_jpeg` en el manifiesto OCR: **0**.',
        '- Renumeración de páginas: **0**.', '',
        '## Por generación', '',
        '| generación | canónicos | páginas OCR | huecos persistentes |',
        '|---:|---:|---:|---:|',
    ]
    for gen in sorted(by_gen, key=int):
        d = by_gen[gen]
        lines.append(f"| {gen} | {len(d['viewers'])} | {d['pages']:,} | {d['gaps']} |")
    lines += ['', '## Contrato downstream',
        'OCR sólo puede consumir `ltmd_u1_w3_spanish_canonical_page_manifest.csv`. Cada fila debe revalidarse en vivo contra `sha256` y `byte_size` antes de reconocimiento. Los 16 aliases heredan productos del canónico mediante provenance; los ocho huecos persistentes quedan explícitos en `ltmd_u1_w3_spanish_canonical_gap_manifest.csv` y nunca se rellenan ni renumeran.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
