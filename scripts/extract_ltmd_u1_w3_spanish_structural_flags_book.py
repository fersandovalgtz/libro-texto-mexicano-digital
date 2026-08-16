#!/usr/bin/env python3
"""Extract conservative structural keyword flags for one canonical W3 Español/Lengua viewer."""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from urllib.request import Request, urlopen

METRICS = Path('data/catalog/ltmd_u1_w3_spanish_ocr_metrics.csv')
MAN = Path('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv')
VERSION = 'LTMD_U1_W3_SPANISH_STRUCTKW_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W3 Spanish structural flags 0.1'
EXPECTED_CANONICAL = 114
VOCAB = {
    'front_matter': [
        r'\bpresentacion\b', r'\bprologo\b', r'\bintroduccion\b', r'\bconoce tu libro\b',
        r'\bal alumno\b', r'\bal maestro\b', r'\bmensaje\b', r'\bcomo usar este libro\b'
    ],
    'toc_navigation': [
        r'\bindice\b', r'\bcontenido(?:s)?\b', r'\bpagina(?:s)?\b', r'\bbloque(?:s)?\b',
        r'\btema(?:s)?\b', r'\bleccion(?:es)?\b', r'\bunid(?:ad|ades)\b'
    ],
    'bibliography_credits': [
        r'\bbibliografia\b', r'\breferencias\b', r'\bfuentes consultadas\b', r'\bpara saber mas\b',
        r'\bisbn\b', r'\bderechos reservados\b', r'\bprimera edicion\b', r'\bsegunda edicion\b',
        r'\btercera edicion\b', r'\bcoordinacion\b', r'\bsecretaria de educacion publica\b',
        r'\bimpreso en mexico\b', r'\bcreditos iconograficos\b', r'\bcreditos fotograficos\b',
        r'\bcreditos de imagenes\b', r'\bfuentes de (?:las )?imagenes\b', r'\bfuentes de imagen\b',
        r'\bimagen de portada\b', r'\bfotografia de portada\b', r'\bilustracion de portada\b',
        r'\bagradecimientos\b', r'\bcolofon\b'
    ]
}


def norm(text):
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', text.casefold())


def download_verify(row, target):
    h = hashlib.sha256()
    total = 0
    with urlopen(Request(row['source_asset_url'], headers={'User-Agent': UA}), timeout=45) as response, target.open('wb') as f:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            h.update(block)
            total += len(block)
            f.write(block)
    if h.hexdigest() != row['sha256']:
        raise RuntimeError(f"SHA mismatch {row['viewer_key']} page {row['viewer_page']}")
    if row.get('byte_size') and total != int(row['byte_size']):
        raise RuntimeError(f"byte-size mismatch {row['viewer_key']} page {row['viewer_page']}")


def run_ocr(image, psm):
    env = os.environ.copy()
    env['OMP_THREAD_LIMIT'] = '1'
    cp = subprocess.run(
        ['tesseract', str(image), 'stdout', '-l', 'spa', '--psm', str(psm or 3)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=90,
        check=False, env=env
    )
    return cp.stdout if cp.returncode == 0 else ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewer-key', required=True)
    parser.add_argument('--output-dir', default='data/work/ltmd_u1_w3_spanish_structkw')
    args = parser.parse_args()

    metrics_all = list(csv.DictReader(METRICS.open(encoding='utf-8', newline='')))
    if len({r['viewer_key'] for r in metrics_all}) != EXPECTED_CANONICAL:
        raise SystemExit(f'W3 structural flags require {EXPECTED_CANONICAL} canonical OCR viewers')
    metrics = [r for r in metrics_all if r['viewer_key'] == args.viewer_key]
    if not metrics:
        raise SystemExit(f'no W3 OCR rows for {args.viewer_key}')

    manifest = {
        (r['viewer_key'], int(r['viewer_page'])): r
        for r in csv.DictReader(MAN.open(encoding='utf-8', newline=''))
        if r['asset_status'] == 'source_jpeg'
    }
    max_page = max(int(r['viewer_page']) for r in metrics)
    candidates = [r for r in metrics if int(r['viewer_page']) <= 16 or int(r['viewer_page']) > max_page - 16]
    out = []

    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w3-spanish-struct-') as td:
        td = Path(td)
        for row in candidates:
            src = manifest[(args.viewer_key, int(row['viewer_page']))]
            image = td / f"{row['page_id']}.jpg"
            text = ''
            verified = 0
            error = ''
            try:
                download_verify(src, image)
                verified = 1
                text = norm(run_ocr(image, row['selected_psm'] or 3))
            except Exception as exc:
                error = f'{type(exc).__name__}: {exc}'
            scores = {cat: sum(1 for pattern in patterns if re.search(pattern, text)) for cat, patterns in VOCAB.items()}
            page = int(row['viewer_page'])
            out.append({
                'scanner_version': VERSION,
                'page_id': row['page_id'],
                'viewer_key': row['viewer_key'],
                'catalog_generation': row['catalog_generation'],
                'grade': row['grade'],
                'title_core': row['title_core'],
                'viewer_page': page,
                'selected_psm': row['selected_psm'],
                'source_sha256_verified': verified,
                'front_zone': int(page <= 16),
                'end_zone': int(page > max_page - 16),
                'front_matter_score': scores['front_matter'],
                'toc_navigation_score': scores['toc_navigation'],
                'bibliography_credits_score': scores['bibliography_credits'],
                'matched_category_count': sum(v > 0 for v in scores.values()),
                'error': error,
            })
            image.unlink(missing_ok=True)

    if any(not int(r['source_sha256_verified']) for r in out):
        raise SystemExit(f'{args.viewer_key}: structural source verification failure')
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f'structkw_{args.viewer_key.lower()}.csv'
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)
    print(f'{args.viewer_key}: structural candidates={len(out)} all SHA verified; out={path}')


if __name__ == '__main__':
    main()
