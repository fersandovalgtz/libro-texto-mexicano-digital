#!/usr/bin/env python3
"""Audit W3 Spanish/Language 2018 routing anomalies against paired 2019 routes.

The 2018 viewer identities remain catalog records in their own right. This script
only tests whether each anomalous 2018 entry can be resolved operationally through
the corresponding 2019 content route. It requires matched metadata/cardinality and
re-fetches every paired 2019 source JPEG, comparing live SHA-256 and byte size with
the persisted W3 2019 reference manifest. Source bytes are streamed and discarded.
"""
from __future__ import annotations

import csv
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

STATES = Path('data/catalog/ltmd_u1_w3_spanish_asset_states.csv')
MANIFEST = Path('data/catalog/ltmd_u1_w3_spanish_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_2018_2019_route_identity.csv')
REL = Path('data/catalog/ltmd_u1_w3_spanish_2018_2019_route_relationships.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_2018_2019_route_identity.md')
VERSION = 'LTMD_U1_W3_SPANISH_2018_2019_ROUTE_IDENTITY_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W3 Spanish 2018-2019 route identity'
EXPECTED_ANOMALOUS_VIEWERS = 8


def fetch_hash(url: str, max_attempts: int = 3):
    last = ''
    for attempt in range(1, max_attempts + 1):
        try:
            h = hashlib.sha256()
            size = 0
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=45) as r:
                status = getattr(r, 'status', None)
                ctype = r.headers.get('Content-Type', '')
                while True:
                    block = r.read(1024 * 1024)
                    if not block:
                        break
                    h.update(block)
                    size += len(block)
            if status == 200 and 'image' in ctype.lower() and size:
                return h.hexdigest(), size, status, ctype, attempt, ''
            last = f'unexpected status={status} type={ctype} size={size}'
        except Exception as exc:
            last = f'{type(exc).__name__}: {exc}'
        if attempt < max_attempts:
            time.sleep(attempt)
    return '', 0, '', '', max_attempts, last


def norm_title(value: str) -> str:
    return ' '.join(value.casefold().split())


def main():
    states = list(csv.DictReader(STATES.open(encoding='utf-8')))
    manifest = list(csv.DictReader(MANIFEST.open(encoding='utf-8')))
    state_by_key = {r['viewer_key']: r for r in states}
    man_by_key = {}
    for row in manifest:
        man_by_key.setdefault(row['viewer_key'], []).append(row)

    anomalies = [
        r for r in states
        if r['catalog_generation'] == '2018'
        and r['asset_state'] == 'routing_anomaly_all_or_near_all'
    ]
    if len(anomalies) != EXPECTED_ANOMALOUS_VIEWERS:
        raise SystemExit(
            f'expected {EXPECTED_ANOMALOUS_VIEWERS} W3 2018 routing anomalies, got {len(anomalies)}'
        )

    pairs = []
    for a in sorted(anomalies, key=lambda r: r['viewer_key']):
        key18 = a['viewer_key']
        key19 = key18.replace('H2018', 'H2019', 1)
        if key19 == key18 or key19 not in state_by_key:
            raise SystemExit(f'paired 2019 viewer not found for {key18}: {key19}')
        b = state_by_key[key19]
        checks = {
            'paired_generation_2019': b['catalog_generation'] == '2019',
            'paired_full_direct': b['asset_state'] == 'full_direct',
            'same_grade': a['grade_code'] == b['grade_code'],
            'same_title_core': norm_title(a['title_core']) == norm_title(b['title_core']),
            'same_declared_positions': a['declared_positions'] == b['declared_positions'],
        }
        if not all(checks.values()):
            raise SystemExit(f'pair metadata/cardinality mismatch {key18}->{key19}: {checks}')
        refs = {
            int(r['viewer_page']): r
            for r in man_by_key[key19]
            if r['asset_status'] == 'source_jpeg'
        }
        expected_source = int(b['source_jpegs'])
        if len(refs) != expected_source:
            raise SystemExit(f'{key19}: expected {expected_source} reference JPEG rows, got {len(refs)}')
        rows18 = man_by_key[key18]
        internal_pages = sorted(
            int(r['viewer_page']) for r in rows18 if r['asset_status'] == 'internal_unserved'
        )
        if internal_pages != sorted(refs):
            raise SystemExit(
                f'{key18}->{key19}: 2018 unresolved pages do not exactly match 2019 source-page set '
                f'({len(internal_pages)} vs {len(refs)})'
            )
        pairs.append((a, b, refs))

    rows = []
    futures = {}
    with ThreadPoolExecutor(max_workers=16) as pool:
        for a, b, refs in pairs:
            for page, ref in sorted(refs.items()):
                row = {
                    'audit_version': VERSION,
                    'viewer_key_2018': a['viewer_key'],
                    'viewer_key_2019': b['viewer_key'],
                    'grade_code': a['grade_code'],
                    'title_core': a['title_core'],
                    'viewer_page': page,
                    'declared_positions': a['declared_positions'],
                    'alternate_route_url': ref['source_asset_url'],
                    'reference_sha256_2019': ref['sha256'],
                    'reference_byte_size_2019': ref['byte_size'],
                }
                rows.append(row)
                futures[pool.submit(fetch_hash, ref['source_asset_url'])] = row
        for future in as_completed(futures):
            sha, size, status, ctype, attempts, error = future.result()
            row = futures[future]
            row.update({
                'observed_sha256': sha,
                'observed_byte_size': size,
                'http_status': status,
                'content_type': ctype,
                'fetch_attempts': attempts,
                'error': error,
                'sha256_matches_2019_reference': int(bool(sha) and sha == row['reference_sha256_2019']),
                'byte_size_matches_2019_reference': int(str(size) == str(row['reference_byte_size_2019'])),
            })

    rows.sort(key=lambda r: (r['viewer_key_2018'], int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    relationships = []
    for a, b, refs in pairs:
        rr = [r for r in rows if r['viewer_key_2018'] == a['viewer_key']]
        sha_ok = sum(int(r['sha256_matches_2019_reference']) for r in rr)
        size_ok = sum(int(r['byte_size_matches_2019_reference']) for r in rr)
        complete = sha_ok == len(rr) == len(refs) and size_ok == len(rr)
        relationships.append({
            'relationship_version': VERSION,
            'viewer_key_2018': a['viewer_key'],
            'viewer_key_2019': b['viewer_key'],
            'grade_code': a['grade_code'],
            'title_core': a['title_core'],
            'declared_positions': a['declared_positions'],
            'compared_source_assets': len(rr),
            'sha256_matches': sha_ok,
            'byte_size_matches': size_ok,
            'complete_route_resolution': int(complete),
            'relationship_type': (
                'catalog_entry_resolves_through_paired_2019_asset_route'
                if complete else 'paired_route_identity_not_proven'
            ),
            'canonical_processing_viewer_key': b['viewer_key'] if complete else '',
            'interpretive_limit': (
                'Operational route resolution only. Catalog identities remain distinct; '
                'this does not assign a bibliographic edition year to the 2018 entry.'
            ),
        })

    with REL.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(relationships[0]))
        writer.writeheader()
        writer.writerows(relationships)

    total = len(rows)
    sha_ok = sum(int(r['sha256_matches_2019_reference']) for r in rows)
    size_ok = sum(int(r['byte_size_matches_2019_reference']) for r in rows)
    complete_viewers = sum(int(r['complete_route_resolution']) for r in relationships)
    lines = [
        '# LTMD-U1 W3 — resolución de rutas Español/Lengua 2018 ↔ 2019',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Visores 2018 con anomalía de routing auditados: **{len(relationships)}**.',
        f'- Activos emparejados y rehasheados: **{total}**.',
        f'- SHA-256 coincidente con referencia 2019: **{sha_ok}/{total}**.',
        f'- Tamaño coincidente con referencia 2019: **{size_ok}/{total}**.',
        f'- Visores con resolución completa por ruta 2019: **{complete_viewers}/{len(relationships)}**.',
        '',
        '## Por visor',
    ]
    for rel in relationships:
        lines.append(
            f"- `{rel['viewer_key_2018']}` → `{rel['viewer_key_2019']}`: "
            f"{rel['sha256_matches']}/{rel['compared_source_assets']} SHA idénticos; "
            f"estado=`{rel['relationship_type']}`."
        )
    lines += [
        '',
        '## Interpretación',
        'La resolución completa permite reutilizar operacionalmente el contenido canónico ya servido bajo la clave 2019, sin duplicar OCR. Las dos entradas de catálogo se conservan como identidades institucionales separadas. La evidencia es de enrutamiento y bytes digitales; no demuestra por sí sola identidad bibliográfica ni fecha de edición.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

    if complete_viewers != len(relationships) or sha_ok != total or size_ok != total:
        raise SystemExit('one or more W3 Spanish 2018/2019 route pairs remain unresolved')


if __name__ == '__main__':
    main()
