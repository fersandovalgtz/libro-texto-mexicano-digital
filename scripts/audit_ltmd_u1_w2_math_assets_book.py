#!/usr/bin/env python3
"""Audit and hash every declared source position for one W2 Mathematics viewer.

This is diagnostic: internal unserved positions are recorded, not hidden and do
not cause the shard itself to fail. Network/provenance execution failures remain
explicitly distinguishable from HTTP 404 source states. Source bytes are streamed
for SHA-256 only and never persisted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCOPE = Path('data/catalog/ltmd_u1_w2_scope.csv')
DECLARED = Path('data/catalog/ltmd_u1_w2_declared_inventory.csv')
VERSION = 'LTMD_U1_W2_MATH_ASSET_AUDIT_0.1'
BASE = 'https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg'
UA = 'LibroTextoMexicanoDigital/U1-W2 Mathematics asset audit'


def fetch_hash(url: str, attempts: int = 3):
    last = ''
    for attempt in range(1, attempts + 1):
        try:
            h = hashlib.sha256()
            size = 0
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=45) as response:
                status = getattr(response, 'status', None)
                ctype = response.headers.get('Content-Type', '')
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    h.update(chunk)
                    size += len(chunk)
            if status == 200 and 'image' in ctype.lower() and size > 0:
                return {
                    'probe_state': 'served_image', 'http_status': status,
                    'content_type': ctype, 'byte_size': size,
                    'sha256': h.hexdigest(), 'attempts': attempt, 'error': ''
                }
            last = f'unexpected status={status} type={ctype} size={size}'
        except HTTPError as exc:
            if exc.code == 404:
                return {
                    'probe_state': 'http_404', 'http_status': 404,
                    'content_type': exc.headers.get('Content-Type', '') if exc.headers else '',
                    'byte_size': '', 'sha256': '', 'attempts': attempt, 'error': 'HTTP 404'
                }
            last = f'HTTPError {exc.code}'
        except (URLError, TimeoutError, OSError) as exc:
            last = f'{type(exc).__name__}: {exc}'
        if attempt < attempts:
            time.sleep(attempt)
    return {
        'probe_state': 'probe_error', 'http_status': '', 'content_type': '',
        'byte_size': '', 'sha256': '', 'attempts': attempts, 'error': last
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--viewer-key', required=True)
    ap.add_argument('--output-dir', default='data/work/ltmd_u1_w2_math_assets')
    args = ap.parse_args()

    scope = {r['viewer_key']: r for r in csv.DictReader(SCOPE.open(encoding='utf-8'))}
    declared = {r['viewer_key']: r for r in csv.DictReader(DECLARED.open(encoding='utf-8'))}
    if args.viewer_key not in scope or args.viewer_key not in declared:
        raise SystemExit(f'viewer not in frozen W2 scope: {args.viewer_key}')

    meta = scope[args.viewer_key]
    n = int(declared[args.viewer_key]['declared_positions'])
    records = []
    for page in range(1, n + 1):
        idx = 0 if page == 1 else page
        url = BASE.format(key=args.viewer_key, idx=idx)
        probe = fetch_hash(url)
        if probe['probe_state'] == 'served_image':
            asset_status = 'source_jpeg'
        elif probe['probe_state'] == 'http_404' and page == n:
            asset_status = 'terminal_synthetic_candidate'
        elif probe['probe_state'] == 'http_404':
            asset_status = 'internal_unserved'
        else:
            asset_status = 'probe_error'
        records.append({
            'audit_version': VERSION,
            'viewer_key': args.viewer_key,
            'book_id': meta['book_id'],
            'catalog_generation': meta['catalog_generation'],
            'grade_code': meta['grade_code'],
            'title_core': meta['title_core'],
            'viewer_page': page,
            'declared_positions': n,
            'source_image_index': idx,
            'source_asset_url': url,
            'is_final_declared_position': int(page == n),
            'asset_status': asset_status,
            **probe,
        })

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"asset_{args.viewer_key.lower()}.csv"
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    counts = {state: sum(r['asset_status'] == state for r in records) for state in {
        'source_jpeg','terminal_synthetic_candidate','internal_unserved','probe_error'
    }}
    print(
        f"{args.viewer_key}: declared={n} served={counts['source_jpeg']} "
        f"terminal404={counts['terminal_synthetic_candidate']} internal404={counts['internal_unserved']} "
        f"probe_error={counts['probe_error']}"
    )
    if counts['probe_error']:
        raise SystemExit(f"{args.viewer_key}: probe execution errors={counts['probe_error']}")


if __name__ == '__main__':
    main()
