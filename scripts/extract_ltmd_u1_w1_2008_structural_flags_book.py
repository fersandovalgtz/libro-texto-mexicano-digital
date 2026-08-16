#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from extract_ltmd_u1_w1_1966_structural_flags_book import VOCAB, norm, run_ocr

MET = Path('data/catalog/ltmd_u1_w1_2008_ocr_metrics.csv')
MAN = Path('data/catalog/ltmd_u1_w1_2008_page_manifest.csv')
VERSION = 'LTMD_U1_W1_2008_STRUCTKW_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W1 2008 structural flags'


def download(src, dest):
    h = hashlib.sha256()
    with urlopen(Request(src['effective_source_asset_url'], headers={'User-Agent': UA}), timeout=45) as response, dest.open('wb') as f:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            f.write(chunk)
    if h.hexdigest() != src['sha256']:
        raise RuntimeError(f"SHA mismatch {src['page_id']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--book-id', required=True)
    ap.add_argument('--output-dir', default='data/work/ltmd_u1_w1_2008_structkw')
    args = ap.parse_args()

    metrics = [
        r for r in csv.DictReader(MET.open(encoding='utf-8'))
        if r['book_id'] == args.book_id
    ]
    manifest = {
        r['page_id']: r
        for r in csv.DictReader(MAN.open(encoding='utf-8'))
        if r['book_id'] == args.book_id
        and r['effective_asset_status'].startswith('source_jpeg')
    }
    if not metrics:
        raise SystemExit('no metrics')

    max_page = max(int(r['viewer_page']) for r in metrics)
    candidates = [
        r for r in metrics
        if int(r['viewer_page']) <= 16 or int(r['viewer_page']) > max_page - 16
    ]
    out = []

    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w1-2008-struct-') as td:
        temp = Path(td)
        for r in candidates:
            src = manifest[r['page_id']]
            img = temp / f"{r['page_id']}.jpg"
            verified = 0
            text = ''
            err = ''
            try:
                download(src, img)
                verified = 1
                text = norm(run_ocr(img, r['selected_psm'] or 3))
            except Exception as exc:
                err = f'{type(exc).__name__}: {exc}'

            scores = {
                category: sum(1 for pattern in patterns if re.search(pattern, text))
                for category, patterns in VOCAB.items()
            }
            page = int(r['viewer_page'])
            out.append({
                'scanner_version': VERSION,
                'page_id': r['page_id'],
                'book_id': r['book_id'],
                'catalog_generation': r['catalog_generation'],
                'grade': r['grade'],
                'viewer_page': page,
                'selected_psm': r['selected_psm'],
                'source_sha256_verified': verified,
                'front_zone': int(page <= 16),
                'end_zone': int(page > max_page - 16),
                'front_matter_score': scores['front_matter'],
                'toc_navigation_score': scores['toc_navigation'],
                'bibliography_credits_score': scores['bibliography_credits'],
                'matched_category_count': sum(v > 0 for v in scores.values()),
                'error': err,
            })
            img.unlink(missing_ok=True)

    if any(not int(r['source_sha256_verified']) for r in out):
        raise SystemExit('structural provenance failure')

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"structkw_{args.book_id.lower()}.csv"
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)

    print(f'{args.book_id}: structural candidates={len(out)} all SHA verified')


if __name__ == '__main__':
    main()
