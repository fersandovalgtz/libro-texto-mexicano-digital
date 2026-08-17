#!/usr/bin/env python3
"""Summarize already-audited W7 source gaps without re-probing or aliasing.

This diagnostic consumes the frozen page-level asset audit and source-admissibility
gate. It does not fetch assets, change admissibility, or infer historical identity.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
ADMISSIBILITY = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
OUT = Path('data/catalog/ltmd_u1_w7_withheld_source_gaps.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_withheld_source_gaps.md')
VERSION = 'LTMD_U1_W7_WITHHELD_SOURCE_GAPS_0.1'
CATALOG_LABEL_RULE = (
    'catalog_generation se conserva como etiqueta institucional de cohorte/navegación '
    'del catálogo y no se interpreta como fecha de publicación sin evidencia independiente'
)


def read_csv(path: Path):
    with path.open(encoding='utf-8', newline='') as f:
        yield from csv.DictReader(f)


def compact_ranges(values: list[int]) -> str:
    if not values:
        return ''
    values = sorted(set(values))
    ranges: list[str] = []
    start = prev = values[0]
    for value in values[1:]:
        if value == prev + 1:
            prev = value
            continue
        ranges.append(str(start) if start == prev else f'{start}-{prev}')
        start = prev = value
    ranges.append(str(start) if start == prev else f'{start}-{prev}')
    return ','.join(ranges)


def main() -> None:
    withheld = {
        row['viewer_key']: row
        for row in read_csv(ADMISSIBILITY)
        if row.get('ocr_source_admitted') == '0'
    }
    if len(withheld) != 5:
        raise SystemExit(f'expected 5 withheld W7 viewers, found {len(withheld)}')

    anomalies: list[dict[str, str]] = []
    all_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in read_csv(ASSETS):
        viewer = row['viewer_key']
        if viewer not in withheld:
            continue
        all_counts[viewer][row['asset_status']] += 1
        if row['asset_status'] != 'source_jpeg':
            anomalies.append({
                'diagnostic_version': VERSION,
                'viewer_key': viewer,
                'catalog_generation': row['catalog_generation'],
                'grade_code': row['grade_code'],
                'viewer_page': row['viewer_page'],
                'source_image_index': row['source_image_index'],
                'asset_status': row['asset_status'],
                'http_status': row['http_status'],
                'source_asset_url': row['source_asset_url'],
            })

    expected = {
        'H2014P5FCA': {'source_jpeg': 224, 'internal_unserved': 1, 'terminal_synthetic_candidate': 0, 'probe_error': 0},
        'H2018P3FCA': {'source_jpeg': 0, 'internal_unserved': 113, 'terminal_synthetic_candidate': 1, 'probe_error': 0},
        'H2018P4FCA': {'source_jpeg': 0, 'internal_unserved': 129, 'terminal_synthetic_candidate': 1, 'probe_error': 0},
        'H2018P5FCA': {'source_jpeg': 0, 'internal_unserved': 225, 'terminal_synthetic_candidate': 1, 'probe_error': 0},
        'H2018P6FCA': {'source_jpeg': 0, 'internal_unserved': 209, 'terminal_synthetic_candidate': 1, 'probe_error': 0},
    }
    if set(withheld) != set(expected):
        raise SystemExit(f'withheld viewer set changed: {sorted(withheld)}')
    for viewer, exp in expected.items():
        observed = {key: all_counts[viewer].get(key, 0) for key in exp}
        if observed != exp:
            raise SystemExit(f'{viewer}: audit counts changed: expected={exp} observed={observed}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'diagnostic_version', 'viewer_key', 'catalog_generation', 'grade_code',
        'viewer_page', 'source_image_index', 'asset_status', 'http_status',
        'source_asset_url',
    ]
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(anomalies)

    lines = [
        '# LTMD-U1 W7 — diagnóstico compacto de fuentes retenidas',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Este reporte resume el manifiesto de auditoría ya existente. No vuelve a solicitar activos, no cambia el gate de admisibilidad y no crea aliases.',
        '',
        '## Resumen por visor',
        '',
        '| visor | decisión | JPEG | internos no servidos | rango páginas internas | terminales | página terminal |',
        '|---|---|---:|---:|---|---:|---|',
    ]
    for viewer in sorted(withheld):
        viewer_rows = [r for r in anomalies if r['viewer_key'] == viewer]
        internal_pages = [int(r['viewer_page']) for r in viewer_rows if r['asset_status'] == 'internal_unserved']
        terminal_pages = [int(r['viewer_page']) for r in viewer_rows if r['asset_status'] == 'terminal_synthetic_candidate']
        c = all_counts[viewer]
        decision = withheld[viewer].get('decision', '')
        lines.append(
            f"| `{viewer}` | `{decision}` | {c.get('source_jpeg', 0)} | "
            f"{c.get('internal_unserved', 0)} | `{compact_ranges(internal_pages)}` | "
            f"{c.get('terminal_synthetic_candidate', 0)} | `{compact_ranges(terminal_pages)}` |"
        )

    h2014 = [r for r in anomalies if r['viewer_key'] == 'H2014P5FCA' and r['asset_status'] == 'internal_unserved']
    if len(h2014) != 1:
        raise SystemExit(f'H2014P5FCA expected exactly one internal gap, found {len(h2014)}')
    gap = h2014[0]
    lines += [
        '',
        '## Hueco aislado H2014P5FCA',
        '',
        f"- Página lógica del visor: **{gap['viewer_page']}**.",
        f"- Índice de imagen solicitado: **{gap['source_image_index']}**.",
        f"- Estado observado: `{gap['asset_status']}` / HTTP `{gap['http_status']}`.",
        f"- Ruta oficial auditada: `{gap['source_asset_url']}`.",
        '',
        'Este registro convierte la retención 2014 en un objetivo de recuperación de una sola posición exacta. La recuperación sólo será admisible si preserva la identidad documental de esa posición.',
        '',
        '## Límite epistemológico',
        '',
        f'`{CATALOG_LABEL_RULE}`.',
        'La coincidencia de cohorte, grado, título o cardinalidad no autoriza imputar activos ni equivalencia documental.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('withheld_viewers', len(withheld))
    print('anomaly_rows', len(anomalies))
    print('h2014_gap_page', gap['viewer_page'])
    print('h2014_gap_image_index', gap['source_image_index'])


if __name__ == '__main__':
    main()
