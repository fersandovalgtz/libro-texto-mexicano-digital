#!/usr/bin/env python3
"""Validate the LTMD-U1 W7 Civics/Ethics asset provenance layer.

The validator is intentionally offline: it checks internal reproducibility and
provenance invariants without contacting the source server.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

INVENTORY = Path('data/catalog/ltmd_u1_w7_declared_inventory.csv')
MANIFEST = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
SUMMARY = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_summary.csv')
DEFAULT_REPORT = Path('data/validation/ltmd_u1_w7_provenance_validation.md')
VERSION = 'LTMD_U1_W7_CIVICS_ETHICS_ASSET_AUDIT_0.1'
EXPECTED_VIEWERS = 30
EXPECTED_ROWS = 4191
SHA256_RE = re.compile(r'^[0-9a-f]{64}$')

REQUIRED_MANIFEST_FIELDS = {
    'audit_version', 'viewer_key', 'catalog_generation', 'grade_code',
    'title_core', 'viewer_ui', 'ag_clave', 'viewer_page',
    'declared_positions', 'source_image_index', 'source_asset_url',
    'is_final_declared_position', 'asset_status', 'probe_state',
    'http_status', 'content_type', 'byte_size', 'sha256', 'attempts', 'error',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise SystemExit(f'W7 provenance validation failed: {message}')


def as_int(value: str, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        fail(f'{label} is not an integer: {value!r}')


def validate(report_path: Path) -> None:
    inventory_rows = read_csv(INVENTORY)
    manifest_rows = read_csv(MANIFEST)
    summary_rows = read_csv(SUMMARY)

    if len(inventory_rows) != EXPECTED_VIEWERS:
        fail(f'inventory viewer count {len(inventory_rows)} != {EXPECTED_VIEWERS}')
    if len(summary_rows) != EXPECTED_VIEWERS:
        fail(f'summary viewer count {len(summary_rows)} != {EXPECTED_VIEWERS}')
    if len(manifest_rows) != EXPECTED_ROWS:
        fail(f'manifest row count {len(manifest_rows)} != {EXPECTED_ROWS}')
    if not manifest_rows:
        fail('manifest is empty')

    missing_fields = REQUIRED_MANIFEST_FIELDS - set(manifest_rows[0])
    if missing_fields:
        fail(f'manifest missing fields: {sorted(missing_fields)}')

    inventory = {row['viewer_key']: row for row in inventory_rows}
    if len(inventory) != EXPECTED_VIEWERS:
        fail('inventory contains duplicate viewer_key values')
    summaries = {row['viewer_key']: row for row in summary_rows}
    if len(summaries) != EXPECTED_VIEWERS:
        fail('summary contains duplicate viewer_key values')
    if set(inventory) != set(summaries):
        fail('inventory/summary viewer coverage mismatch')

    manifest_viewers = {row['viewer_key'] for row in manifest_rows}
    if manifest_viewers != set(inventory):
        fail('manifest/inventory viewer coverage mismatch')

    seen_pairs: set[tuple[str, int]] = set()
    by_viewer: dict[str, list[dict[str, str]]] = {key: [] for key in inventory}
    status_counts = Counter()

    for row in manifest_rows:
        key = row['viewer_key']
        inv = inventory[key]
        page = as_int(row['viewer_page'], f'{key}.viewer_page')
        declared = as_int(row['declared_positions'], f'{key}.declared_positions')
        expected_declared = as_int(inv['declared_positions'], f'{key}.inventory.declared_positions')
        if declared != expected_declared:
            fail(f'{key} declared_positions drift: {declared} != {expected_declared}')
        if not 1 <= page <= declared:
            fail(f'{key} viewer_page out of range: {page}/{declared}')
        pair = (key, page)
        if pair in seen_pairs:
            fail(f'duplicate manifest key: {pair}')
        seen_pairs.add(pair)

        if row['audit_version'] != VERSION:
            fail(f'{key} audit_version drift: {row["audit_version"]!r}')
        for field in ('catalog_generation', 'grade_code', 'title_core', 'ag_clave'):
            if row[field] != inv[field]:
                fail(f'{key} {field} drift: {row[field]!r} != {inv[field]!r}')

        expected_index = 0 if page == 1 else page
        index = as_int(row['source_image_index'], f'{key}.source_image_index')
        if index != expected_index:
            fail(f'{key} page {page} source_image_index {index} != {expected_index}')
        expected_url = f'https://historico.conaliteg.gob.mx/c/{inv["ag_clave"]}/{expected_index:03d}.jpg'
        if row['source_asset_url'] != expected_url:
            fail(f'{key} page {page} source_asset_url drift')

        is_final = as_int(row['is_final_declared_position'], f'{key}.is_final_declared_position')
        if is_final not in (0, 1) or is_final != int(page == declared):
            fail(f'{key} page {page} invalid final-position flag')

        attempts = as_int(row['attempts'], f'{key}.attempts')
        if attempts < 1:
            fail(f'{key} page {page} attempts < 1')

        status = row['asset_status']
        probe = row['probe_state']
        status_counts[status] += 1
        if status == 'source_jpeg':
            if probe != 'served_image' or row['http_status'] != '200':
                fail(f'{key} page {page} served image has inconsistent probe/status')
            if 'image' not in row['content_type'].lower():
                fail(f'{key} page {page} served image lacks image content type')
            if as_int(row['byte_size'], f'{key}.byte_size') <= 0:
                fail(f'{key} page {page} served image has non-positive byte size')
            if not SHA256_RE.fullmatch(row['sha256']):
                fail(f'{key} page {page} invalid SHA-256')
        elif status in {'terminal_synthetic_candidate', 'internal_unserved'}:
            if probe != 'http_404' or row['http_status'] != '404':
                fail(f'{key} page {page} 404 state has inconsistent probe/status')
            if row['sha256'] or row['byte_size']:
                fail(f'{key} page {page} 404 state unexpectedly has byte/hash evidence')
            if status == 'terminal_synthetic_candidate' and not is_final:
                fail(f'{key} page {page} terminal candidate is not final')
            if status == 'internal_unserved' and is_final:
                fail(f'{key} page {page} internal gap is final')
        elif status == 'probe_error':
            fail(f'{key} page {page} persisted probe_error')
        else:
            fail(f'{key} page {page} unknown asset_status: {status!r}')

        by_viewer[key].append(row)

    if len(seen_pairs) != EXPECTED_ROWS:
        fail('manifest unique-key cardinality mismatch')

    ready_count = 0
    for key, rows in by_viewer.items():
        rows.sort(key=lambda row: int(row['viewer_page']))
        expected_declared = int(inventory[key]['declared_positions'])
        if [int(row['viewer_page']) for row in rows] != list(range(1, expected_declared + 1)):
            fail(f'{key} page sequence is not contiguous')

        counts = Counter(row['asset_status'] for row in rows)
        served = [row for row in rows if row['asset_status'] == 'source_jpeg']
        source_bytes = sum(int(row['byte_size']) for row in served)
        unique_hashes = len({row['sha256'] for row in served})
        ready = int(counts['internal_unserved'] == 0 and counts['probe_error'] == 0 and bool(served))
        ready_count += ready
        summary = summaries[key]
        expected_summary = {
            'audit_version': VERSION,
            'catalog_generation': inventory[key]['catalog_generation'],
            'grade_code': inventory[key]['grade_code'],
            'title_core': inventory[key]['title_core'],
            'ag_clave': inventory[key]['ag_clave'],
            'declared_positions': str(len(rows)),
            'source_jpegs': str(len(served)),
            'terminal_synthetic_candidates': str(counts['terminal_synthetic_candidate']),
            'internal_unserved': str(counts['internal_unserved']),
            'probe_errors': str(counts['probe_error']),
            'source_bytes': str(source_bytes),
            'unique_source_hashes': str(unique_hashes),
            'direct_asset_ready': str(ready),
        }
        for field, expected in expected_summary.items():
            if summary[field] != expected:
                fail(f'{key} summary {field} drift: {summary[field]!r} != {expected!r}')

    total_inventory_positions = sum(int(row['declared_positions']) for row in inventory_rows)
    if total_inventory_positions != EXPECTED_ROWS:
        fail(f'inventory declared total {total_inventory_positions} != {EXPECTED_ROWS}')

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = [
        '# LTMD-U1 W7 — validación del contrato de procedencia',
        '',
        f'Versión validada: `{VERSION}`.',
        '',
        '- Estado: **PASS**.',
        f'- Visores: **{EXPECTED_VIEWERS}**.',
        f'- Filas del manifiesto: **{EXPECTED_ROWS:,}**.',
        f'- Claves `(viewer_key, viewer_page)` únicas: **{len(seen_pairs):,}**.',
        f'- Visores `direct_asset_ready`: **{ready_count}/{EXPECTED_VIEWERS}**.',
        f'- JPEG con tamaño y SHA-256 válidos: **{status_counts["source_jpeg"]:,}**.',
        f'- Candidatos terminales 404: **{status_counts["terminal_synthetic_candidate"]:,}**.',
        f'- Huecos internos 404: **{status_counts["internal_unserved"]:,}**.',
        '- Errores de sondeo persistidos: **0**.',
        '',
        '## Invariantes verificadas',
        '',
        'La validación exige cobertura exacta del inventario W7, secuencias de página contiguas, URL de sondeo determinista, coherencia entre estado HTTP y estado técnico, tamaño y SHA-256 para cada JPEG servido, semántica estricta para 404 terminales e internos, ausencia de `probe_error` persistidos y recomputación exacta del resumen por visor.',
        '',
        'Este PASS valida la integridad interna y la reproducibilidad del registro de procedencia. No demuestra identidad histórica entre ediciones, equivalencia curricular, autoría, completitud semántica ni autorización para OCR.',
    ]
    report_path.write_text('\n'.join(report) + '\n', encoding='utf-8')
    print('\n'.join(report))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    validate(args.report)


if __name__ == '__main__':
    main()
