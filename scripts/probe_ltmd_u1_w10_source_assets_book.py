#!/usr/bin/env python3
"""Probe one W10 source candidate position-by-position without persisting images."""
from __future__ import annotations

import argparse
import csv
import hashlib
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

INV = Path('data/catalog/ltmd_u1_w10_declared_inventory.csv')
ARCH = Path('data/catalog/ltmd_u1_w10_viewer_architecture.csv')
VERSION = 'LTMD_U1_W10_ASSET_PROBE_0.1'
BASE = 'https://historico.conaliteg.gob.mx/c/{key}/{idx:03d}.jpg'
UA = 'LibroTextoMexicanoDigital/U1-W10 exact official asset probe'
EXPECTED = 68


def fetch_hash(url: str, attempts: int = 3) -> dict[str, object]:
    last = ''
    for attempt in range(1, attempts + 1):
        try:
            digest = hashlib.sha256()
            size = 0
            magic = b''
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=45) as response:
                status = int(getattr(response, 'status', 200) or 200)
                content_type = response.headers.get('Content-Type', '')
                first = True
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    if first:
                        magic = block[:2]
                        first = False
                    digest.update(block)
                    size += len(block)
            if status == 200 and 'image' in content_type.lower() and size > 0 and magic == b'\xff\xd8':
                return {
                    'probe_state': 'served_jpeg',
                    'http_status': status,
                    'content_type': content_type,
                    'byte_size': size,
                    'jpeg_magic': 1,
                    'sha256': digest.hexdigest(),
                    'attempts': attempt,
                    'error': '',
                }
            last = f'unexpected status={status} type={content_type!r} size={size} jpeg_magic={magic == b"\\xff\\xd8"}'
        except HTTPError as exc:
            if exc.code == 404:
                return {
                    'probe_state': 'http_404',
                    'http_status': 404,
                    'content_type': exc.headers.get('Content-Type', '') if exc.headers else '',
                    'byte_size': '',
                    'jpeg_magic': 0,
                    'sha256': '',
                    'attempts': attempt,
                    'error': 'HTTP 404',
                }
            last = f'HTTPError {exc.code}'
        except (URLError, TimeoutError, OSError) as exc:
            last = f'{type(exc).__name__}: {exc}'
        if attempt < attempts:
            time.sleep(attempt)
    return {
        'probe_state': 'probe_error',
        'http_status': '',
        'content_type': '',
        'byte_size': '',
        'jpeg_magic': 0,
        'sha256': '',
        'attempts': attempts,
        'error': last,
    }


def read_keyed(path: Path) -> dict[str, dict[str, str]]:
    rows = list(csv.DictReader(path.open(encoding='utf-8', newline='')))
    if len(rows) != EXPECTED or len({r['viewer_key'] for r in rows}) != EXPECTED:
        raise SystemExit(f'W10 asset probe: {path} expected {EXPECTED} unique rows, got {len(rows)}')
    return {r['viewer_key']: r for r in rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--viewer-key', required=True)
    ap.add_argument('--output-dir', default='data/work/ltmd_u1_w10_source_assets')
    args = ap.parse_args()

    inv = read_keyed(INV)
    arch = read_keyed(ARCH)
    if args.viewer_key not in inv:
        raise SystemExit(f'viewer not in W10 processable cohort: {args.viewer_key}')
    m = inv[args.viewer_key]
    a = arch[args.viewer_key]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ready = m['direct_asset_probe_ready'] == '1'
    declared = int(m['declared_positions'] or 0)
    ag_clave = m['ag_clave']
    records: list[dict[str, object]] = []

    if ready:
        if declared <= 0 or not ag_clave:
            raise SystemExit(f'{args.viewer_key}: inconsistent direct_asset_probe_ready metadata')
        for viewer_page in range(1, declared + 1):
            source_index = 0 if viewer_page == 1 else viewer_page
            url = BASE.format(key=ag_clave, idx=source_index)
            probe = fetch_hash(url)
            records.append({
                'probe_version': VERSION,
                'viewer_key': args.viewer_key,
                'catalog_generation': m['catalog_generation'],
                'grade_code': m['grade_code'],
                'title_core': m['title_core'],
                'ag_clave': ag_clave,
                'viewer_page': viewer_page,
                'declared_positions': declared,
                'source_image_index': source_index,
                'source_asset_url': url,
                'is_final_declared_position': int(viewer_page == declared),
                **probe,
            })

        prior_sequence_complete = bool(records[:-1]) and all(r['probe_state'] == 'served_jpeg' for r in records[:-1])
        for row in records:
            if row['probe_state'] == 'served_jpeg':
                status = 'source_jpeg'
            elif row['probe_state'] == 'http_404' and int(row['viewer_page']) == declared and prior_sequence_complete:
                status = 'terminal_synthetic_candidate'
            elif row['probe_state'] == 'http_404':
                status = 'internal_unserved'
            else:
                status = 'probe_error'
            row['asset_status'] = status

        manifest_path = out_dir / f'asset_{args.viewer_key.lower()}.csv'
        with manifest_path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader(); writer.writerows(records)

    counts = {
        status: sum(r.get('asset_status') == status for r in records)
        for status in ('source_jpeg', 'terminal_synthetic_candidate', 'internal_unserved', 'probe_error')
    }
    summary = {
        'probe_version': VERSION,
        'viewer_key': args.viewer_key,
        'catalog_generation': m['catalog_generation'],
        'grade_code': m['grade_code'],
        'title_core': m['title_core'],
        'standard_dynamic_architecture': a['standard_dynamic_architecture'],
        'config_present': m['config_present'],
        'config_ag_clave_exact': m['config_ag_clave_exact'],
        'direct_asset_probe_ready': int(ready),
        'ag_clave': ag_clave,
        'declared_positions': declared,
        'source_jpegs': counts['source_jpeg'],
        'terminal_synthetic_candidates': counts['terminal_synthetic_candidate'],
        'internal_unserved': counts['internal_unserved'],
        'probe_errors': counts['probe_error'],
        'manifest_rows': len(records),
        'source_probe_state': 'asset_probe_completed' if ready else 'not_ready_for_direct_asset_probe',
        'architecture_probe_error': a['probe_error'],
        'source_url': m['source_url'],
    }
    summary_path = out_dir / f'summary_{args.viewer_key.lower()}.csv'
    with summary_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary))
        writer.writeheader(); writer.writerow(summary)

    print(
        f"{args.viewer_key}: ready={int(ready)} declared={declared} served={counts['source_jpeg']} "
        f"terminal={counts['terminal_synthetic_candidate']} internal={counts['internal_unserved']} "
        f"probe_errors={counts['probe_error']}"
    )
    if counts['probe_error']:
        raise SystemExit(f"{args.viewer_key}: operational probe errors={counts['probe_error']}")


if __name__ == '__main__':
    main()
