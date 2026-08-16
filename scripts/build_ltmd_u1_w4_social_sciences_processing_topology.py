#!/usr/bin/env python3
"""Build reconciled W4 Social Sciences processing inventory and canonical page manifest.

W4 may proceed only when all 14 frozen identities are full direct sources, no
internal gaps/probe errors exist, and no complete served-asset sequence is
byte-identical to another W4 identity. Under those evidence conditions every
identity remains its own canonical processing object.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

READINESS = Path('data/catalog/ltmd_u1_w4_social_sciences_source_readiness.csv')
REL = Path('data/catalog/ltmd_u1_w4_social_sciences_exact_asset_relationships.csv')
ASSETS = Path('data/catalog/ltmd_u1_w4_social_sciences_asset_manifest.csv')
PROCESSING = Path('data/catalog/ltmd_u1_w4_social_sciences_processing_inventory.csv')
PAGES = Path('data/catalog/ltmd_u1_w4_social_sciences_canonical_page_manifest.csv')
REPORT = Path('data/catalog/ltmd_u1_w4_social_sciences_processing_topology.md')
VERSION = 'LTMD_U1_W4_SOCIAL_SCIENCES_PROCESSING_0.1'
PAGE_VERSION = 'LTMD_U1_W4_SOCIAL_SCIENCES_CANONICAL_PAGE_MANIFEST_0.1'
EXPECTED_IDENTITIES = 14
EXPECTED_SOURCE_PAGES = 2414
EXPECTED_TERMINAL = 14


def main():
    readiness = list(csv.DictReader(READINESS.open(encoding='utf-8', newline='')))
    relationships = list(csv.DictReader(REL.open(encoding='utf-8', newline='')))
    assets = list(csv.DictReader(ASSETS.open(encoding='utf-8', newline='')))

    if len(readiness) != EXPECTED_IDENTITIES or len({r['viewer_key'] for r in readiness}) != EXPECTED_IDENTITIES:
        raise SystemExit(f'W4 readiness cardinality drift: {len(readiness)}')
    if any(r['source_state'] != 'full_direct_source' for r in readiness):
        raise SystemExit('W4 processing topology blocked: one or more identities are not full_direct_source')
    if any(int(r['internal_unserved']) != 0 for r in readiness):
        raise SystemExit('W4 processing topology blocked: internal source gap present')
    if relationships:
        raise SystemExit(f'W4 processing topology requires explicit alias decision; exact relationships={len(relationships)}')

    keys = {r['viewer_key'] for r in readiness}
    by_key = defaultdict(list)
    for row in assets:
        by_key[row['viewer_key']].append(row)
    if set(by_key) != keys:
        raise SystemExit('W4 source manifest/readiness viewer mismatch')
    if any(r['asset_status'] == 'probe_error' for r in assets):
        raise SystemExit('W4 source manifest still contains probe errors')

    processing = []
    for r in sorted(readiness, key=lambda x: (int(x['catalog_generation']), int(x['grade_code']), x['viewer_key'])):
        processing.append({
            'processing_version': VERSION,
            'viewer_key': r['viewer_key'],
            'catalog_generation': r['catalog_generation'],
            'grade_code': r['grade_code'],
            'title_core': r['title_core'],
            'original_source_state': r['source_state'],
            'processing_mode': 'direct_canonical',
            'canonical_processing_viewer_key': r['viewer_key'],
            'ocr_identity_eligible': 1,
            'is_canonical_processing_object': 1,
            'declared_positions': r['declared_positions'],
            'direct_source_jpegs': r['source_jpegs'],
            'terminal_synthetic_candidates': r['terminal_synthetic_candidates'],
            'persistent_internal_source_gaps': 0,
            'evidence_basis': 'full_direct_asset_audit_no_internal_gaps_no_complete_byte_exact_alias',
            'block_reason': '',
            'interpretive_limit': 'Operational processing topology only; canonical processing status does not establish edition year or curricular equivalence.',
        })

    with PROCESSING.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(processing[0]))
        writer.writeheader(); writer.writerows(processing)

    proc = {r['viewer_key']: r for r in processing}
    pages = []
    terminal = 0
    for key in sorted(keys, key=lambda k: (int(proc[k]['catalog_generation']), int(proc[k]['grade_code']), k)):
        rr = sorted(by_key[key], key=lambda r: int(r['viewer_page']))
        declared = int(proc[key]['declared_positions'])
        if len(rr) != declared:
            raise SystemExit(f'{key}: source audit cardinality {len(rr)} != declared {declared}')
        served = [r for r in rr if r['asset_status'] == 'source_jpeg']
        terminal_rows = [r for r in rr if r['asset_status'] == 'terminal_synthetic_candidate']
        internal = [r for r in rr if r['asset_status'] == 'internal_unserved']
        if internal:
            raise SystemExit(f'{key}: internal source gap leaked into reconciled topology')
        if len(served) != int(proc[key]['direct_source_jpegs']):
            raise SystemExit(f'{key}: source-page count mismatch')
        terminal += len(terminal_rows)
        for r in served:
            if not r['sha256'] or not r['byte_size'] or not r['source_asset_url']:
                raise SystemExit(f"{key} VP{r['viewer_page']}: missing source evidence")
            pages.append({
                'manifest_version': PAGE_VERSION,
                'viewer_key': key,
                'catalog_generation': proc[key]['catalog_generation'],
                'grade_code': proc[key]['grade_code'],
                'title_core': proc[key]['title_core'],
                'processing_mode': 'direct_canonical',
                'viewer_page': r['viewer_page'],
                'source_image_index': r['source_image_index'],
                'source_asset_url': r['source_asset_url'],
                'byte_size': r['byte_size'],
                'sha256': r['sha256'],
                'asset_status': 'source_jpeg',
                'page_numbering_policy': 'preserve_original_viewer_page_no_renumbering',
                'source_provenance': 'W4_social_sciences_asset_manifest_source_jpeg',
            })

    if len(pages) != EXPECTED_SOURCE_PAGES:
        raise SystemExit(f'W4 canonical page count drift: {len(pages)} != {EXPECTED_SOURCE_PAGES}')
    if terminal != EXPECTED_TERMINAL:
        raise SystemExit(f'W4 terminal-candidate count drift: {terminal} != {EXPECTED_TERMINAL}')
    pairs = [(r['viewer_key'], int(r['viewer_page'])) for r in pages]
    if len(pairs) != len(set(pairs)):
        raise SystemExit('duplicate W4 canonical viewer/page rows')

    with PAGES.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(pages[0]))
        writer.writeheader(); writer.writerows(pages)

    by_gen = defaultdict(lambda: {'viewers': set(), 'pages': 0, 'terminal': 0})
    for r in pages:
        g = by_gen[r['catalog_generation']]
        g['viewers'].add(r['viewer_key']); g['pages'] += 1
    for r in processing:
        by_gen[r['catalog_generation']]['terminal'] += int(r['terminal_synthetic_candidates'])

    lines = [
        '# LTMD-U1 W4 — topología reconciliada de procesamiento Ciencias Sociales',
        '',
        f'Versión de procesamiento: `{VERSION}`.',
        f'Versión del manifiesto de páginas: `{PAGE_VERSION}`.',
        '',
        f'- Identidades W4: **{len(processing)}/{EXPECTED_IDENTITIES}**.',
        f'- Identidades OCR-eligible: **{sum(int(r["ocr_identity_eligible"]) for r in processing)}/{EXPECTED_IDENTITIES}**.',
        f'- Objetos canónicos independientes a nivel de activos: **{sum(int(r["is_canonical_processing_object"]) for r in processing)}**.',
        '- Aliases de libro completo byte-exacto: **0**.',
        '- Huecos internos persistentes: **0**.',
        f'- Páginas fuente canónicas autorizadas para OCR: **{len(pages):,}**.',
        f'- Terminales sintéticos excluidos del OCR: **{terminal}**.',
        '- Renumeración de páginas: **0**.',
        '',
        '## Por generación',
        '',
        '| generación | canónicos | páginas OCR | terminales sintéticos |',
        '|---:|---:|---:|---:|',
    ]
    for gen in sorted(by_gen, key=int):
        d = by_gen[gen]
        lines.append(f"| {gen} | {len(d['viewers'])} | {d['pages']:,} | {d['terminal']} |")
    lines += [
        '',
        '## Contrato downstream',
        '',
        'OCR W4 sólo puede consumir `ltmd_u1_w4_social_sciences_canonical_page_manifest.csv`. Cada JPEG debe revalidarse en vivo contra SHA-256 y tamaño. Los 14 terminales sintéticos no se procesan ni se convierten en páginas. La inexistencia de aliases de libro completo no impide que existan páginas o fragmentos reutilizados parcialmente entre documentos; esas dependencias se medirán por separado.',
        '',
        'Este contrato autoriza procesamiento técnico OCR/PAGESTRUCT/FRAGSEG. No autoriza inferencias semánticas históricas ni convierte la etiqueta operacional `ciencias_sociales` en una categoría curricular validada.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
