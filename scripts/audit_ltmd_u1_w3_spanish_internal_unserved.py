#!/usr/bin/env python3
"""Re-audit W3 Spanish/Language viewers with a small number of internal 404s.

Targets are derived from the persisted W3 asset states rather than hard-coded.
Each target URL is retried; available immediate neighbours are re-fetched and must
reproduce the persisted SHA-256/byte size. A persistent target 404 with verified
neighbours is preserved as an explicit digital-source gap. No page shifting or
renumbering is allowed. Source bytes are streamed only for hashes and discarded.
"""
from __future__ import annotations

import csv
import hashlib
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

STATES = Path('data/catalog/ltmd_u1_w3_spanish_asset_states.csv')
MANIFEST = Path('data/catalog/ltmd_u1_w3_spanish_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_internal_unserved_audit.csv')
REPORT = Path('data/catalog/ltmd_u1_w3_spanish_internal_unserved_audit.md')
VERSION = 'LTMD_U1_W3_SPANISH_INTERNAL_UNSERVED_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W3 Spanish internal-unserved audit'
EXPECTED_PARTIAL_VIEWERS = 7
EXPECTED_TARGETS = 8


def fetch_hash(url: str, max_attempts: int = 5):
    log = []
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
            log.append(f'{attempt}:{status}:{ctype}:{size}')
            if status == 200 and 'image' in ctype.lower() and size:
                return {
                    'reachable': 1,
                    'status': status,
                    'content_type': ctype,
                    'byte_size': size,
                    'sha256': h.hexdigest(),
                    'attempts': attempt,
                    'attempt_log': '|'.join(log),
                    'error': '',
                }
            last = f'unexpected status={status} type={ctype} size={size}'
        except HTTPError as exc:
            log.append(f'{attempt}:HTTP{exc.code}')
            last = f'HTTPError {exc.code}'
        except (URLError, TimeoutError, OSError) as exc:
            log.append(f'{attempt}:{type(exc).__name__}:{exc}')
            last = f'{type(exc).__name__}: {exc}'
        if attempt < max_attempts:
            time.sleep(0.7 * attempt)
    return {
        'reachable': 0,
        'status': '',
        'content_type': '',
        'byte_size': '',
        'sha256': '',
        'attempts': max_attempts,
        'attempt_log': '|'.join(log),
        'error': last or 'target remained unavailable',
    }


def main():
    states = list(csv.DictReader(STATES.open(encoding='utf-8')))
    manifest = list(csv.DictReader(MANIFEST.open(encoding='utf-8')))
    partial_keys = {
        r['viewer_key'] for r in states if r['asset_state'] == 'partial_internal_unserved'
    }
    if len(partial_keys) != EXPECTED_PARTIAL_VIEWERS:
        raise SystemExit(
            f'expected {EXPECTED_PARTIAL_VIEWERS} partial W3 viewers, got {len(partial_keys)}'
        )

    by_key_page = {(r['viewer_key'], int(r['viewer_page'])): r for r in manifest}
    targets = [
        r for r in manifest
        if r['viewer_key'] in partial_keys and r['asset_status'] == 'internal_unserved'
    ]
    if len(targets) != EXPECTED_TARGETS:
        raise SystemExit(f'expected {EXPECTED_TARGETS} internal target rows, got {len(targets)}')

    out = []
    for target in sorted(targets, key=lambda r: (r['viewer_key'], int(r['viewer_page']))):
        key = target['viewer_key']
        page = int(target['viewer_page'])
        observed = fetch_hash(target['source_asset_url'], 5)
        neighbour_records = []
        for neighbour_page in (page - 1, page + 1):
            neighbour = by_key_page.get((key, neighbour_page))
            if not neighbour or neighbour['asset_status'] != 'source_jpeg':
                continue
            got = fetch_hash(neighbour['source_asset_url'], 3)
            ok = int(
                got['reachable']
                and got['sha256'] == neighbour['sha256']
                and str(got['byte_size']) == str(neighbour['byte_size'])
            )
            neighbour_records.append((neighbour_page, neighbour, got, ok))
        if not neighbour_records:
            raise SystemExit(f'{key} VP{page}: no source-JPEG neighbour available for control')
        neighbours_ok = all(record[3] for record in neighbour_records)
        if observed['reachable']:
            state = 'unexpectedly_recovered'
        elif neighbours_ok:
            state = 'internal_unserved_position_observed'
        else:
            state = 'audit_inconclusive'

        prev = next((x for x in neighbour_records if x[0] == page - 1), None)
        nxt = next((x for x in neighbour_records if x[0] == page + 1), None)
        out.append({
            'audit_version': VERSION,
            'viewer_key': key,
            'catalog_generation': target['catalog_generation'],
            'grade_code': target['grade_code'],
            'title_core': target['title_core'],
            'viewer_page': page,
            'source_image_index': target['source_image_index'],
            'target_url': target['source_asset_url'],
            'target_state': state,
            'target_reachable': observed['reachable'],
            'target_http_status': observed['status'],
            'target_content_type': observed['content_type'],
            'target_byte_size': observed['byte_size'],
            'target_sha256': observed['sha256'],
            'target_attempts': observed['attempts'],
            'target_attempt_log': observed['attempt_log'],
            'prev_page': prev[0] if prev else '',
            'prev_url': prev[1]['source_asset_url'] if prev else '',
            'prev_sha256_match': prev[3] if prev else '',
            'next_page': nxt[0] if nxt else '',
            'next_url': nxt[1]['source_asset_url'] if nxt else '',
            'next_sha256_match': nxt[3] if nxt else '',
            'available_neighbours_sha_verified': int(neighbours_ok),
            'ocr_policy': (
                'include_recovered_source_page'
                if state == 'unexpectedly_recovered'
                else 'omit_only_this_unserved_position_without_renumbering'
                if state == 'internal_unserved_position_observed'
                else 'block_viewer_pending_resolution'
            ),
            'interpretive_limit': (
                'Observed behavior of the public digital asset route; it does not by itself prove '
                'that a bibliographic page is absent from the physical or printed edition.'
            ),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)

    persistent = sum(r['target_state'] == 'internal_unserved_position_observed' for r in out)
    recovered = sum(r['target_state'] == 'unexpectedly_recovered' for r in out)
    inconclusive = sum(r['target_state'] == 'audit_inconclusive' for r in out)
    by_viewer = {}
    for row in out:
        by_viewer.setdefault(row['viewer_key'], []).append(row)

    lines = [
        '# LTMD-U1 W3 — auditoría focal de posiciones internas no servidas Español/Lengua',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Visores parciales auditados: **{len(by_viewer)}**.',
        f'- Posiciones internas re-auditadas: **{len(out)}**.',
        f'- Persisten como `internal_unserved_position_observed`: **{persistent}**.',
        f'- Recuperadas inesperadamente: **{recovered}**.',
        f'- Inconclusas: **{inconclusive}**.',
        '',
        '## Casos',
    ]
    for key, rows in sorted(by_viewer.items()):
        details = ', '.join(f"VP{r['viewer_page']}={r['target_state']}" for r in rows)
        neighbour_ok = all(int(r['available_neighbours_sha_verified']) for r in rows)
        lines.append(f"- `{key}`: {details}; controles vecinos SHA={'OK' if neighbour_ok else 'FAIL'}.")
    lines += [
        '',
        '## Política de corpus',
        'Un hueco digital persistente y local, rodeado por vecinos que reproducen sus SHA persistidos, no invalida todo el libro. El visor puede entrar al OCR con esa posición explícitamente ausente, sin renumerar páginas ni fabricar continuidad. Si una posición reaparece, su hash recuperado se incorpora como suplemento de reconciliación. Un caso inconcluso bloquea únicamente ese visor hasta resolverlo.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

    if inconclusive:
        raise SystemExit('one or more W3 internal-unserved audits are inconclusive')


if __name__ == '__main__':
    main()
