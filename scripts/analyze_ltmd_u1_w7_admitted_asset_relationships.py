#!/usr/bin/env python3
"""Analyze exact served-asset relationships inside the OCR-admitted W7 cohort.

Only viewers already admitted by LTMD_U1_W7_SOURCE_ADMISSIBILITY_0.1 participate
in canonicalization analysis. Catalog identities are never merged here. Equality
means exact equality of the complete served-page sequence encoded as
(viewer_page, source_image_index, byte_size, SHA-256).
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
GATE = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
FINGERPRINTS = Path('data/catalog/ltmd_u1_w7_admitted_asset_fingerprints.csv')
REL = Path('data/catalog/ltmd_u1_w7_exact_asset_relationships.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_admitted_asset_relationships.md')
VERSION = 'LTMD_U1_W7_ADMITTED_ASSET_REL_0.1'
EXPECTED_TOTAL = 30
EXPECTED_ADMITTED = 25
EXPECTED_SOURCE_PAGES = 3261


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise SystemExit(f'W7 admitted asset relationships failed: {message}')


def sequence_payload(rows: list[dict[str, str]]) -> list[list[object]]:
    served = [row for row in rows if row['asset_status'] == 'source_jpeg']
    return [
        [int(row['viewer_page']), int(row['source_image_index']), int(row['byte_size']), row['sha256']]
        for row in sorted(served, key=lambda item: int(item['viewer_page']))
    ]


def fingerprint(payload: list[list[object]]) -> str:
    raw = json.dumps(payload, ensure_ascii=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    gate = read_csv(GATE)
    assets = read_csv(ASSETS)
    if len(gate) != EXPECTED_TOTAL or len({row['viewer_key'] for row in gate}) != EXPECTED_TOTAL:
        fail(f'gate viewer cardinality drift: {len(gate)}')
    admitted = [row for row in gate if row['ocr_source_admitted'] == '1']
    if len(admitted) != EXPECTED_ADMITTED:
        fail(f'admitted viewer cardinality drift: {len(admitted)}')
    admitted_keys = {row['viewer_key'] for row in admitted}
    if any(row['direct_asset_ready'] != '1' for row in admitted):
        fail('admitted cohort contains a viewer not marked direct_asset_ready')

    by_viewer: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assets:
        by_viewer[row['viewer_key']].append(row)
    if not admitted_keys.issubset(by_viewer):
        fail('asset manifest does not cover every admitted viewer')

    meta = {row['viewer_key']: row for row in admitted}
    fp_rows: list[dict[str, object]] = []
    payloads: dict[str, list[list[object]]] = {}
    fps: dict[str, str] = {}
    total_source_pages = 0

    for key in sorted(admitted_keys, key=lambda k: (int(meta[k]['catalog_generation']), int(meta[k]['grade_code']), k)):
        rows = by_viewer[key]
        declared = int(meta[key]['declared_positions'])
        if len(rows) != declared:
            fail(f'{key}: manifest rows {len(rows)} != declared {declared}')
        statuses = Counter(row['asset_status'] for row in rows)
        if statuses['internal_unserved'] or statuses['probe_error']:
            fail(f'{key}: non-admissible source state leaked into admitted cohort')
        if statuses['source_jpeg'] != int(meta[key]['source_jpegs']):
            fail(f'{key}: served page count drift')
        for row in rows:
            if row['asset_status'] == 'source_jpeg':
                if not row['sha256'] or not row['byte_size'] or not row['source_asset_url']:
                    fail(f"{key} VP{row['viewer_page']}: missing provenance evidence")
        payload = sequence_payload(rows)
        digest = fingerprint(payload)
        payloads[key] = payload
        fps[key] = digest
        total_source_pages += len(payload)
        fp_rows.append({
            'analysis_version': VERSION,
            'viewer_key': key,
            'catalog_generation': meta[key]['catalog_generation'],
            'grade_code': meta[key]['grade_code'],
            'title_core': meta[key]['title_core'],
            'served_page_count': len(payload),
            'served_sequence_sha256': digest,
        })

    if total_source_pages != EXPECTED_SOURCE_PAGES:
        fail(f'admitted source page total {total_source_pages} != {EXPECTED_SOURCE_PAGES}')

    exact: list[dict[str, object]] = []
    keys = [row['viewer_key'] for row in fp_rows]
    for a, b in combinations(keys, 2):
        if fps[a] != fps[b]:
            continue
        if payloads[a] != payloads[b]:
            fail('SHA-256 sequence fingerprint collision/inconsistency')
        exact.append({
            'analysis_version': VERSION,
            'viewer_a': a,
            'viewer_b': b,
            'generation_a': meta[a]['catalog_generation'],
            'generation_b': meta[b]['catalog_generation'],
            'grade_a': meta[a]['grade_code'],
            'grade_b': meta[b]['grade_code'],
            'same_grade': int(meta[a]['grade_code'] == meta[b]['grade_code']),
            'served_page_count': len(payloads[a]),
            'served_sequence_sha256': fps[a],
            'relationship': 'full_served_asset_sequence_byte_exact',
        })

    with FINGERPRINTS.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fp_rows[0]))
        writer.writeheader(); writer.writerows(fp_rows)
    rel_fields = ['analysis_version','viewer_a','viewer_b','generation_a','generation_b','grade_a','grade_b','same_grade','served_page_count','served_sequence_sha256','relationship']
    with REL.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=rel_fields)
        writer.writeheader(); writer.writerows(exact)

    cross = [row for row in exact if row['generation_a'] != row['generation_b']]
    same_grade_cross = [row for row in cross if row['same_grade'] == 1]
    lines = [
        '# LTMD-U1 W7 — relaciones exactas de activos en la cohorte admitida',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Visores W7 totales preservados: **{EXPECTED_TOTAL}**.',
        f'- Visores fuente admitidos analizados: **{len(admitted)}/{EXPECTED_ADMITTED}**.',
        f'- Páginas JPEG servidas y hasheadas en la cohorte: **{total_source_pages:,}**.',
        f'- Pares con secuencia completa byte-idéntica: **{len(exact)}**.',
        f'- Pares byte-idénticos entre generaciones: **{len(cross)}**.',
        f'- Pares byte-idénticos entre generaciones y mismo grado: **{len(same_grade_cross)}**.',
        '',
        '## Relaciones exactas',
        '',
    ]
    if exact:
        for row in exact:
            lines.append(
                f"- `{row['viewer_a']}` ↔ `{row['viewer_b']}`: {row['served_page_count']} JPEG en secuencia completa byte-idéntica; "
                f"generaciones {row['generation_a']}↔{row['generation_b']}; mismo grado={row['same_grade']}."
            )
    else:
        lines.append('- No se detectaron pares con secuencia completa byte-idéntica entre los 25 visores admitidos.')

    lines += [
        '',
        '## Límite de interpretación',
        '',
        'Una relación `full_served_asset_sequence_byte_exact` demuestra igualdad de los bytes servidos en toda la secuencia de páginas, pero no fusiona identidades bibliográficas ni prueba equivalencia curricular o histórica. Si existen pares exactos, la topología OCR posterior puede deduplicar computación conservando todas las identidades y provenance.',
        '',
        'Los cinco visores retenidos por el gate de fuente no participan en esta comparación y no pueden convertirse en aliases por ausencia de activos.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
