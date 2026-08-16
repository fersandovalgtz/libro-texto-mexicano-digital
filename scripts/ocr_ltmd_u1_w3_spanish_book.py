#!/usr/bin/env python3
"""SHA-verified adaptive OCR metrics for one canonical LTMD-U1 W3 Español/Lengua viewer.

This technical layer operates only on the reconciled canonical page manifest.
Catalog aliases are not recomputed: their downstream technical products inherit
from canonical_processing_viewer_key through explicit provenance. Source JPEGs
and full OCR text are ephemeral and are never persisted by this script.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import statistics
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

MAN = Path('data/catalog/ltmd_u1_w3_spanish_canonical_page_manifest.csv')
PROC = Path('data/catalog/ltmd_u1_w3_spanish_processing_inventory.csv')
VERSION = 'LTMD_U1_W3_SPANISH_OCR_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W3 Spanish OCR 0.1'
FALLBACK_MIN_WORDS = 5
TIMEOUT = 60
EXPECTED_IDENTITIES = 130
EXPECTED_CANONICAL = 114
EXPECTED_ALIASES = 16
EXPECTED_SOURCE_PAGES = 20765
EXPECTED_PERSISTENT_GAPS = 8
FIELDS = [
    'ocr_version','page_id','viewer_key','catalog_generation','grade','title_core',
    'viewer_page','source_image_index','processing_mode','source_provenance',
    'source_bytes','source_sha256_verified','attempts','selected_psm',
    'recognized_words','ocr_chars','mean_word_confidence','median_word_confidence',
    'low_confidence_word_rate','ocr_class','ocr_status','error'
]


def page_id(row):
    return f"U1-{row['viewer_key']}-P{int(row['viewer_page']):03d}"


def load_topology():
    if not MAN.exists() or not PROC.exists():
        raise SystemExit('W3 canonical manifest/processing inventory not materialized')
    proc = list(csv.DictReader(PROC.open(encoding='utf-8', newline='')))
    if len(proc) != EXPECTED_IDENTITIES:
        raise SystemExit(f'expected {EXPECTED_IDENTITIES} W3 identities, got {len(proc)}')
    keys = [r['viewer_key'] for r in proc]
    if len(keys) != len(set(keys)):
        raise SystemExit('duplicate viewer_key in W3 processing inventory')
    eligible = {r['viewer_key'] for r in proc if r.get('ocr_identity_eligible') == '1'}
    canonical = {r['viewer_key'] for r in proc if r.get('is_canonical_processing_object') == '1'}
    aliases = eligible - canonical
    if len(eligible) != EXPECTED_IDENTITIES:
        raise SystemExit(f'expected all {EXPECTED_IDENTITIES} identities OCR-covered, got {len(eligible)}')
    if len(canonical) != EXPECTED_CANONICAL or len(aliases) != EXPECTED_ALIASES:
        raise SystemExit(f'W3 topology mismatch canonical={len(canonical)} aliases={len(aliases)}')
    canon_map = {r['viewer_key']: r['canonical_processing_viewer_key'] for r in proc}
    if any(not canon_map[k] for k in eligible):
        raise SystemExit('missing canonical_processing_viewer_key')
    if any(canon_map[k] not in canonical for k in eligible):
        raise SystemExit('one or more identities point to a noncanonical processing object')
    if any(canon_map[k] != k for k in canonical):
        raise SystemExit('canonical identity does not self-point')
    gaps = sum(int(r.get('persistent_internal_source_gaps') or 0) for r in proc if r['viewer_key'] in canonical)
    if gaps != EXPECTED_PERSISTENT_GAPS:
        raise SystemExit(f'expected {EXPECTED_PERSISTENT_GAPS} persistent gaps, got {gaps}')

    man = list(csv.DictReader(MAN.open(encoding='utf-8', newline='')))
    if len(man) != EXPECTED_SOURCE_PAGES:
        raise SystemExit(f'expected {EXPECTED_SOURCE_PAGES} canonical source pages, got {len(man)}')
    mkeys = {r['viewer_key'] for r in man}
    if mkeys != canonical:
        raise SystemExit(f'canonical manifest viewer mismatch manifest={len(mkeys)} topology={len(canonical)}')
    if any(r.get('asset_status') != 'source_jpeg' for r in man):
        raise SystemExit('canonical page manifest contains non-source_jpeg rows')
    pids = [page_id(r) for r in man]
    if len(pids) != len(set(pids)):
        raise SystemExit('duplicate page_id in canonical page manifest')
    return canonical


def download_verify(row, target):
    h = hashlib.sha256()
    total = 0
    url = row['source_asset_url']
    expected_sha = row['sha256']
    if not url or not expected_sha:
        raise RuntimeError('missing canonical source evidence')
    with urlopen(Request(url, headers={'User-Agent': UA}), timeout=45) as response, target.open('wb') as f:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            h.update(block)
            total += len(block)
            f.write(block)
    got = h.hexdigest()
    if got != expected_sha:
        raise RuntimeError(f'SHA256 mismatch expected={expected_sha} got={got}')
    if row.get('byte_size') and total != int(row['byte_size']):
        raise RuntimeError(f"byte size mismatch expected={row['byte_size']} got={total}")
    return total


def run_ocr(image, psm):
    env = os.environ.copy()
    env['OMP_THREAD_LIMIT'] = '1'
    proc = subprocess.run(
        ['tesseract', str(image), 'stdout', '-l', 'spa', '--psm', str(psm), 'tsv'],
        capture_output=True, text=True, timeout=TIMEOUT, env=env
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip() or f'tesseract exit {proc.returncode}')
    rows = list(csv.DictReader(proc.stdout.splitlines(), delimiter='\t'))
    words, confs = [], []
    for row in rows:
        text = (row.get('text') or '').strip()
        try:
            conf = float(row.get('conf') or -1)
        except ValueError:
            conf = -1
        if text and conf >= 0:
            words.append(text)
            confs.append(conf)
    low = sum(c < 60 for c in confs) / len(confs) if confs else 1.0
    return {
        'recognized_words': len(words),
        'ocr_chars': sum(len(w) for w in words),
        'mean_word_confidence': f'{statistics.mean(confs):.2f}' if confs else '',
        'median_word_confidence': f'{statistics.median(confs):.2f}' if confs else '',
        'low_confidence_word_rate': f'{low:.4f}',
    }


def score(metrics):
    return (int(metrics['recognized_words']), float(metrics['mean_word_confidence'] or 0))


def process(row, tmp):
    pid = page_id(row)
    image = tmp / f'{pid}.jpg'
    attempts, errors = [], []
    base = {
        'ocr_version': VERSION,
        'page_id': pid,
        'viewer_key': row['viewer_key'],
        'catalog_generation': row['catalog_generation'],
        'grade': row['grade_code'],
        'title_core': row['title_core'],
        'viewer_page': row['viewer_page'],
        'source_image_index': row['source_image_index'],
        'processing_mode': row['processing_mode'],
        'source_provenance': row['source_provenance'],
    }
    empty = {
        'recognized_words': '', 'ocr_chars': '', 'mean_word_confidence': '',
        'median_word_confidence': '', 'low_confidence_word_rate': ''
    }
    try:
        size = download_verify(row, image)
        baseline = None
        try:
            baseline = run_ocr(image, 3)
            attempts.append(f"psm3:ok:{baseline['recognized_words']}")
        except subprocess.TimeoutExpired:
            attempts.append('psm3:timeout')
            errors.append(f'psm3 timeout>{TIMEOUT}s')
        except Exception as exc:
            attempts.append('psm3:error')
            errors.append(f'psm3 {type(exc).__name__}: {exc}')

        if baseline and int(baseline['recognized_words']) > 0:
            return {
                **base, 'source_bytes': size, 'source_sha256_verified': 1,
                'attempts': ';'.join(attempts), 'selected_psm': 3, **baseline,
                'ocr_class': 'text_detected', 'ocr_status': 'ok', 'error': ' | '.join(errors)
            }

        fallback = []
        for psm in (11, 6):
            try:
                metrics = run_ocr(image, psm)
                attempts.append(f"psm{psm}:ok:{metrics['recognized_words']}")
                fallback.append((psm, metrics))
            except subprocess.TimeoutExpired:
                attempts.append(f'psm{psm}:timeout')
                errors.append(f'psm{psm} timeout>{TIMEOUT}s')
            except Exception as exc:
                attempts.append(f'psm{psm}:error')
                errors.append(f'psm{psm} {type(exc).__name__}: {exc}')

        valid = [x for x in fallback if int(x[1]['recognized_words']) >= FALLBACK_MIN_WORDS]
        if valid:
            psm, metrics = max(valid, key=lambda x: score(x[1]))
            return {
                **base, 'source_bytes': size, 'source_sha256_verified': 1,
                'attempts': ';'.join(attempts), 'selected_psm': psm, **metrics,
                'ocr_class': 'text_detected', 'ocr_status': 'ok', 'error': ' | '.join(errors)
            }

        observed = []
        if baseline is not None:
            observed.append((3, baseline))
        observed += fallback
        if observed:
            _, metrics = max(observed, key=lambda x: score(x[1]))
            return {
                **base, 'source_bytes': size, 'source_sha256_verified': 1,
                'attempts': ';'.join(attempts), 'selected_psm': '', **metrics,
                'ocr_class': 'no_text_detected', 'ocr_status': 'ok', 'error': ' | '.join(errors)
            }

        return {
            **base, 'source_bytes': size, 'source_sha256_verified': 1,
            'attempts': ';'.join(attempts), 'selected_psm': '', **empty,
            'ocr_class': 'unresolved', 'ocr_status': 'error', 'error': ' | '.join(errors)
        }
    except Exception as exc:
        return {
            **base, 'source_bytes': '', 'source_sha256_verified': 0,
            'attempts': ';'.join(attempts), 'selected_psm': '', **empty,
            'ocr_class': 'unresolved', 'ocr_status': 'error',
            'error': f'{type(exc).__name__}: {exc}'
        }
    finally:
        image.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewer-key', required=True)
    parser.add_argument('--output-dir', default='data/work/ltmd_u1_w3_spanish_ocr')
    args = parser.parse_args()

    canonical = load_topology()
    if args.viewer_key not in canonical:
        raise SystemExit(f'viewer is not a W3 canonical compute object: {args.viewer_key}')

    allrows = list(csv.DictReader(MAN.open(encoding='utf-8', newline='')))
    source = [r for r in allrows if r['viewer_key'] == args.viewer_key and r['asset_status'] == 'source_jpeg']
    if not source:
        raise SystemExit(f'no W3 canonical source rows for {args.viewer_key}')

    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w3-spanish-ocr-') as td:
        outrows = [process(r, Path(td)) for r in source]
    outrows.sort(key=lambda r: int(r['viewer_page']))

    verified = sum(str(r['source_sha256_verified']) == '1' for r in outrows)
    unresolved = sum(r['ocr_class'] == 'unresolved' or r['ocr_status'] != 'ok' for r in outrows)
    if verified != len(outrows):
        raise SystemExit(f'provenance failure {args.viewer_key}: {verified}/{len(outrows)} SHA verified')

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"ocr_{args.viewer_key.lower()}.csv"
    with out.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(outrows)

    text = sum(r['ocr_class'] == 'text_detected' for r in outrows)
    no_text = sum(r['ocr_class'] == 'no_text_detected' for r in outrows)
    print(f'{args.viewer_key}: pages={len(outrows)} sha={verified} text={text} no_text={no_text} unresolved={unresolved} out={out}')
    if unresolved:
        raise SystemExit(f'{args.viewer_key}: unresolved OCR pages={unresolved}')


if __name__ == '__main__':
    main()
