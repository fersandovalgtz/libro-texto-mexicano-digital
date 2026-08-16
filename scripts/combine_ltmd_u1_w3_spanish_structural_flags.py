#!/usr/bin/env python3
"""Combine LTMD-U1 W3 Español/Lengua structural-flag shards."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

METRICS = Path('data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv')
OUT = Path('data/catalog/ltmd_u1_w3_spanish_structural_keyword_flags.csv')
VERSION = 'LTMD_U1_W3_SPANISH_STRUCTKW_0.1'
EXPECTED_CANONICAL = 114


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', default='data/work/ltmd_u1_w3_spanish_structkw')
    args = parser.parse_args()

    metrics = list(csv.DictReader(METRICS.open(encoding='utf-8', newline='')))
    by = {}
    for row in metrics:
        by.setdefault(row['viewer_key'], []).append(row)
    if len(by) != EXPECTED_CANONICAL:
        raise SystemExit(f'expected {EXPECTED_CANONICAL} canonical OCR viewers, found {len(by)}')

    expected = set()
    for key, rows in by.items():
        max_page = max(int(r['viewer_page']) for r in rows)
        expected |= {
            (key, r['page_id']) for r in rows
            if int(r['viewer_page']) <= 16 or int(r['viewer_page']) > max_page - 16
        }

    files = sorted(Path(args.input_dir).rglob('structkw_*.csv'))
    if len(files) != EXPECTED_CANONICAL:
        raise SystemExit(f'expected {EXPECTED_CANONICAL} structkw shards, got {len(files)}')

    rows = []
    seen = []
    for path in files:
        shard = list(csv.DictReader(path.open(encoding='utf-8', newline='')))
        if not shard:
            raise SystemExit(f'empty structural shard {path}')
        keys = {r['viewer_key'] for r in shard}
        versions = {r['scanner_version'] for r in shard}
        if len(keys) != 1 or versions != {VERSION}:
            raise SystemExit(f'invalid structural shard {path}')
        seen.extend(keys)
        rows.extend(shard)

    if set(seen) != set(by) or len(seen) != EXPECTED_CANONICAL:
        raise SystemExit('structural canonical viewer coverage mismatch')
    keys = {(r['viewer_key'], r['page_id']) for r in rows}
    if len(keys) != len(rows):
        raise SystemExit('duplicate structural page keys')
    if keys != expected:
        raise SystemExit(f'structural coverage mismatch missing={len(expected-keys)} extra={len(keys-expected)}')
    if any(r['source_sha256_verified'] != '1' for r in rows):
        raise SystemExit('structural SHA failure')

    rows.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade']), r['viewer_key'], int(r['viewer_page'])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f'wrote {len(rows)} W3 Español/Lengua structural rows for {EXPECTED_CANONICAL} canonical viewers; all SHA verified')


if __name__ == '__main__':
    main()
