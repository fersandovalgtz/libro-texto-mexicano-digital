#!/usr/bin/env python3
"""SHA-verified adaptive OCR metrics for one canonical LTMD-U1 W8 Artes viewer."""
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

MAN = Path('data/catalog/ltmd_u1_w8_canonical_page_manifest.csv')
PROC = Path('data/catalog/ltmd_u1_w8_processing_inventory.csv')
VERSION = 'LTMD_U1_W8_ARTES_OCR_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W8 Artes OCR 0.1'
FALLBACK_MIN_WORDS = 5
TIMEOUT = 60
EXPECTED_IDENTITIES = 20
EXPECTED_CANONICAL = 16
EXPECTED_SOURCE_PAGES = 1490
FIELDS = [
    'ocr_version', 'page_id', 'viewer_key', 'catalog_generation', 'grade', 'title_core',
    'viewer_page', 'source_image_index', 'processing_mode', 'source_provenance',
    'source_bytes', 'source_sha256_verified', 'attempts', 'selected_psm',
    'recognized_words', 'ocr_chars', 'mean_word_confidence', 'median_word_confidence',
    'low_confidence_word_rate', 'ocr_class', 'ocr_status', 'error',
]


def load_topology() -> set[str]:
    proc = list(csv.DictReader(PROC.open(encoding='utf-8', newline='')))
    man = list(csv.DictReader(MAN.open(encoding='utf-8', newline='')))
    if len(proc) != EXPECTED_IDENTITIES or len({r['viewer_key'] for r in proc}) != EXPECTED_IDENTITIES:
        raise SystemExit('W8 processing inventory cardinality mismatch')
    canonical = {r['viewer_key'] for r in proc if r['is_canonical_processing_object'] == '1'}
    eligible = {r['viewer_key'] for r in proc if r['ocr_identity_eligible'] == '1'}
    if canonical != eligible or len(canonical) != EXPECTED_CANONICAL:
        raise SystemExit('W8 topology must contain exactly 16 OCR-eligible canonicals')
    if any(r['processing_mode'] != 'direct_canonical' for r in proc if r['viewer_key'] in canonical):
        raise SystemExit('W8 admitted viewer has unexpected processing mode')
    withheld = [r for r in proc if r['viewer_key'] not in canonical]
    if len(withheld) != 4 or any(r['processing_mode'] != 'withheld_source' or r['ocr_identity_eligible'] != '0' for r in withheld):
        raise SystemExit('W8 withheld topology mismatch')
    if len(man) != EXPECTED_SOURCE_PAGES or {r['viewer_key'] for r in man} != canonical:
        raise SystemExit('W8 canonical page manifest cardinality/coverage mismatch')
    if any(r['asset_status'] != 'source_jpeg' for r in man):
        raise SystemExit('W8 canonical page manifest contains non-source row')
    pids = [r['page_id'] for r in man]
    if len(pids) != len(set(pids)):
        raise SystemExit('duplicate W8 canonical page IDs')
    if any(not r['sha256'] or len(r['sha256']) != 64 for r in man):
        raise SystemExit('W8 canonical page manifest contains invalid SHA-256')
    return canonical


def download_verify(row: dict[str, str], target: Path) -> int:
    digest = hashlib.sha256()
    total = 0
    with urlopen(Request(row['source_asset_url'], headers={'User-Agent': UA}), timeout=45) as response, target.open('wb') as handle:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
            total += len(block)
            handle.write(block)
    if digest.hexdigest() != row['sha256']:
        raise RuntimeError('SHA256 mismatch')
    if row.get('byte_size') and total != int(row['byte_size']):
        raise RuntimeError('byte-size mismatch')
    return total


def run_ocr(image: Path, psm: int) -> dict[str, str | int]:
    env = os.environ.copy()
    env['OMP_THREAD_LIMIT'] = '1'
    cp = subprocess.run(
        ['tesseract', str(image), 'stdout', '-l', 'spa', '--psm', str(psm), 'tsv'],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        env=env,
    )
    if cp.returncode:
        raise RuntimeError(cp.stderr.strip() or f'tesseract exit {cp.returncode}')
    words: list[str] = []
    confs: list[float] = []
    for row in csv.DictReader(cp.stdout.splitlines(), delimiter='\t'):
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


def score(metrics: dict[str, str | int]) -> tuple[int, float]:
    return int(metrics['recognized_words']), float(metrics['mean_word_confidence'] or 0)


def process(row: dict[str, str], tmp: Path) -> dict[str, str | int]:
    pid = row['page_id']
    image = tmp / f'{pid}.jpg'
    attempts: list[str] = []
    errors: list[str] = []
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
        'median_word_confidence': '', 'low_confidence_word_rate': '',
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
            return {**base, 'source_bytes': size, 'source_sha256_verified': 1, 'attempts': ';'.join(attempts), 'selected_psm': 3, **baseline, 'ocr_class': 'text_detected', 'ocr_status': 'ok', 'error': ' | '.join(errors)}
        fallback: list[tuple[int, dict[str, str | int]]] = []
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
        valid = [item for item in fallback if int(item[1]['recognized_words']) >= FALLBACK_MIN_WORDS]
        if valid:
            psm, metrics = max(valid, key=lambda item: score(item[1]))
            return {**base, 'source_bytes': size, 'source_sha256_verified': 1, 'attempts': ';'.join(attempts), 'selected_psm': psm, **metrics, 'ocr_class': 'text_detected', 'ocr_status': 'ok', 'error': ' | '.join(errors)}
        observed: list[tuple[int, dict[str, str | int]]] = []
        if baseline is not None:
            observed.append((3, baseline))
        observed += fallback
        if observed:
            _, metrics = max(observed, key=lambda item: score(item[1]))
            return {**base, 'source_bytes': size, 'source_sha256_verified': 1, 'attempts': ';'.join(attempts), 'selected_psm': '', **metrics, 'ocr_class': 'no_text_detected', 'ocr_status': 'ok', 'error': ' | '.join(errors)}
        return {**base, 'source_bytes': size, 'source_sha256_verified': 1, 'attempts': ';'.join(attempts), 'selected_psm': '', **empty, 'ocr_class': 'unresolved', 'ocr_status': 'error', 'error': ' | '.join(errors)}
    except Exception as exc:
        return {**base, 'source_bytes': '', 'source_sha256_verified': 0, 'attempts': ';'.join(attempts), 'selected_psm': '', **empty, 'ocr_class': 'unresolved', 'ocr_status': 'error', 'error': f'{type(exc).__name__}: {exc}'}
    finally:
        image.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewer-key', required=True)
    parser.add_argument('--output-dir', default='data/work/ltmd_u1_w8_artes_ocr')
    args = parser.parse_args()
    canonical = load_topology()
    if args.viewer_key not in canonical:
        raise SystemExit(f'viewer not W8 OCR-eligible canonical: {args.viewer_key}')
    source = [row for row in csv.DictReader(MAN.open(encoding='utf-8', newline='')) if row['viewer_key'] == args.viewer_key]
    with tempfile.TemporaryDirectory(prefix='ltmd-u1-w8-artes-ocr-') as temp_dir:
        rows = [process(row, Path(temp_dir)) for row in source]
    rows.sort(key=lambda row: int(row['viewer_page']))
    verified = sum(str(row['source_sha256_verified']) == '1' for row in rows)
    unresolved = sum(row['ocr_class'] == 'unresolved' or row['ocr_status'] != 'ok' for row in rows)
    if verified != len(rows):
        raise SystemExit(f'provenance failure {args.viewer_key}: {verified}/{len(rows)}')
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"ocr_{args.viewer_key.lower()}.csv"
    with out.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"{args.viewer_key}: pages={len(rows)} sha={verified} "
        f"text={sum(r['ocr_class']=='text_detected' for r in rows)} "
        f"no_text={sum(r['ocr_class']=='no_text_detected' for r in rows)} unresolved={unresolved}"
    )
    if unresolved:
        raise SystemExit(f'{args.viewer_key}: unresolved OCR pages={unresolved}')


if __name__ == '__main__':
    main()
