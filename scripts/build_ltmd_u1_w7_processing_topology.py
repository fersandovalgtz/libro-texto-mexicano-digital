#!/usr/bin/env python3
"""Build reconciled W7 processing inventory and canonical page manifest.

All 30 catalog identities remain represented. Exactly the 25 viewers admitted by
the W7 source-admissibility gate become independent direct canonical OCR
objects, because the admitted-asset relationship analysis found zero complete
byte-exact aliases. Five identities remain explicitly withheld.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

GATE = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
REL = Path('data/catalog/ltmd_u1_w7_exact_asset_relationships.csv')
ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
PROCESSING = Path('data/catalog/ltmd_u1_w7_processing_inventory.csv')
PAGES = Path('data/catalog/ltmd_u1_w7_canonical_page_manifest.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_processing_topology.md')
VERSION = 'LTMD_U1_W7_PROCESSING_0.1'
PAGE_VERSION = 'LTMD_U1_W7_CANONICAL_PAGE_MANIFEST_0.1'
EXPECTED_IDENTITIES = 30
EXPECTED_CANONICAL = 25
EXPECTED_SOURCE_PAGES = 3261
EXPECTED_TERMINAL = 25
EXPECTED_WITHHELD = 5


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise SystemExit(f'W7 processing topology failed: {message}')


def main() -> None:
    gate = read_csv(GATE)
    relationships = read_csv(REL)
    assets = read_csv(ASSETS)
    if len(gate) != EXPECTED_IDENTITIES or len({r['viewer_key'] for r in gate}) != EXPECTED_IDENTITIES:
        fail(f'gate identity cardinality drift: {len(gate)}')
    if relationships:
        fail(f'exact full-sequence relationships require canonical alias decisions: {len(relationships)}')

    admitted = {r['viewer_key'] for r in gate if r['ocr_source_admitted'] == '1'}
    withheld = {r['viewer_key'] for r in gate if r['ocr_source_admitted'] == '0'}
    if len(admitted) != EXPECTED_CANONICAL or len(withheld) != EXPECTED_WITHHELD:
        fail(f'gate split drift: admitted={len(admitted)} withheld={len(withheld)}')

    gate_by_key = {r['viewer_key']: r for r in gate}
    by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assets:
        by_key[row['viewer_key']].append(row)
    if set(by_key) != set(gate_by_key):
        fail('asset manifest/gate viewer coverage mismatch')

    processing: list[dict[str, object]] = []
    for key in sorted(gate_by_key, key=lambda k: (int(gate_by_key[k]['catalog_generation']), int(gate_by_key[k]['grade_code']), k)):
        g = gate_by_key[key]
        is_admitted = key in admitted
        processing.append({
            'processing_version': VERSION,
            'viewer_key': key,
            'catalog_generation': g['catalog_generation'],
            'grade_code': g['grade_code'],
            'title_core': g['title_core'],
            'source_gate_decision': g['decision'],
            'processing_mode': 'direct_canonical' if is_admitted else 'withheld_source',
            'canonical_processing_viewer_key': key if is_admitted else '',
            'ocr_identity_eligible': int(is_admitted),
            'is_canonical_processing_object': int(is_admitted),
            'declared_positions': g['declared_positions'],
            'direct_source_jpegs': g['source_jpegs'],
            'persistent_internal_source_gaps': g['internal_unserved'],
            'evidence_basis': (
                'source_admitted_no_complete_byte_exact_alias' if is_admitted
                else g['reason_code']
            ),
            'block_reason': '' if is_admitted else g['reason_code'],
            'interpretive_limit': 'Operational OCR topology only; catalog identity and curricular interpretation remain independent of processing status.',
        })

    with PROCESSING.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(processing[0]))
        writer.writeheader(); writer.writerows(processing)

    proc = {str(r['viewer_key']): r for r in processing}
    pages: list[dict[str, object]] = []
    terminal = 0
    for key in sorted(admitted, key=lambda k: (int(gate_by_key[k]['catalog_generation']), int(gate_by_key[k]['grade_code']), k)):
        rr = sorted(by_key[key], key=lambda r: int(r['viewer_page']))
        declared = int(gate_by_key[key]['declared_positions'])
        if len(rr) != declared:
            fail(f'{key}: source audit cardinality {len(rr)} != declared {declared}')
        counts = Counter(r['asset_status'] for r in rr)
        if counts['internal_unserved'] or counts['probe_error']:
            fail(f'{key}: non-admissible source row leaked into canonical cohort')
        served = [r for r in rr if r['asset_status'] == 'source_jpeg']
        terminals = [r for r in rr if r['asset_status'] == 'terminal_synthetic_candidate']
        if len(served) != int(gate_by_key[key]['source_jpegs']):
            fail(f'{key}: served count drift')
        terminal += len(terminals)
        for r in served:
            if not r['sha256'] or not r['byte_size'] or not r['source_asset_url']:
                fail(f"{key} VP{r['viewer_page']}: missing source evidence")
            pages.append({
                'manifest_version': PAGE_VERSION,
                'viewer_key': key,
                'catalog_generation': gate_by_key[key]['catalog_generation'],
                'grade_code': gate_by_key[key]['grade_code'],
                'title_core': gate_by_key[key]['title_core'],
                'processing_mode': 'direct_canonical',
                'viewer_page': r['viewer_page'],
                'source_image_index': r['source_image_index'],
                'source_asset_url': r['source_asset_url'],
                'byte_size': r['byte_size'],
                'sha256': r['sha256'],
                'asset_status': 'source_jpeg',
                'page_numbering_policy': 'preserve_original_viewer_page_no_renumbering',
                'source_provenance': 'W7_civics_ethics_asset_manifest_source_jpeg',
            })

    if len(pages) != EXPECTED_SOURCE_PAGES:
        fail(f'canonical page count {len(pages)} != {EXPECTED_SOURCE_PAGES}')
    if terminal != EXPECTED_TERMINAL:
        fail(f'terminal candidate count {terminal} != {EXPECTED_TERMINAL}')
    pairs = [(r['viewer_key'], int(r['viewer_page'])) for r in pages]
    if len(pairs) != len(set(pairs)):
        fail('duplicate canonical viewer/page rows')
    if {r['viewer_key'] for r in pages} != admitted:
        fail('canonical page manifest viewer coverage mismatch')

    with PAGES.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pages[0]))
        writer.writeheader(); writer.writerows(pages)

    by_generation: dict[str, dict[str, object]] = defaultdict(lambda: {'total': 0, 'canonical': 0, 'withheld': 0, 'pages': 0})
    for row in processing:
        bucket = by_generation[str(row['catalog_generation'])]
        bucket['total'] = int(bucket['total']) + 1
        bucket['canonical'] = int(bucket['canonical']) + int(row['is_canonical_processing_object'])
        bucket['withheld'] = int(bucket['withheld']) + int(not int(row['ocr_identity_eligible']))
    for row in pages:
        bucket = by_generation[str(row['catalog_generation'])]
        bucket['pages'] = int(bucket['pages']) + 1

    lines = [
        '# LTMD-U1 W7 — topología reconciliada de procesamiento Cívica/Ética',
        '',
        f'Versión de procesamiento: `{VERSION}`.',
        f'Versión del manifiesto de páginas: `{PAGE_VERSION}`.',
        '',
        f'- Identidades históricas W7 preservadas: **{len(processing)}/{EXPECTED_IDENTITIES}**.',
        f'- Identidades OCR elegibles: **{len(admitted)}/{EXPECTED_IDENTITIES}**.',
        f'- Objetos canónicos independientes a nivel de activos: **{len(admitted)}**.',
        '- Aliases de libro completo byte-exacto entre admitidos: **0**.',
        f'- Identidades retenidas por fuente: **{len(withheld)}**.',
        f'- Páginas fuente canónicas autorizadas para OCR: **{len(pages):,}**.',
        f'- Terminales sintéticos excluidos del OCR: **{terminal}**.',
        '- Renumeración de páginas: **0**.',
        '',
        '## Por generación',
        '',
        '| generación | identidades | canónicos OCR | retenidos | páginas OCR |',
        '|---:|---:|---:|---:|---:|',
    ]
    for generation in sorted(by_generation, key=int):
        b = by_generation[generation]
        lines.append(f"| {generation} | {b['total']} | {b['canonical']} | {b['withheld']} | {b['pages']:,} |")

    lines += [
        '',
        '## Contrato downstream',
        '',
        'El OCR W7 sólo puede consumir `ltmd_u1_w7_canonical_page_manifest.csv` y únicamente visores marcados `ocr_identity_eligible=1` en `ltmd_u1_w7_processing_inventory.csv`. Cada JPEG debe descargarse temporalmente y revalidarse contra tamaño y SHA-256 antes del OCR; no se persisten imágenes fuente.',
        '',
        'Los cinco visores retenidos siguen siendo identidades históricas del alcance W7. Su ausencia del manifiesto OCR expresa una restricción de fuente, no una inferencia de inexistencia documental ni equivalencia con otra edición.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
