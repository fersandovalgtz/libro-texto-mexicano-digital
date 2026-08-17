#!/usr/bin/env python3
"""Extract a bounded bibliographic fingerprint from H2014P5FCA legal matter.

Only logical pages 1-12 are downloaded. Every JPEG must match the SHA-256 and
byte size already frozen in the W7 asset audit before OCR. Full OCR text is not
published; only lines matching bibliographic markers are retained. This probe
does not change source admissibility and does not reconstruct page 104.
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

VERSION = 'LTMD_U1_W7_H2014P5_BIBLIOGRAPHIC_FINGERPRINT_0.1'
TARGET = 'H2014P5FCA'
PAGES = range(1, 13)
ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.md')
UA = 'LibroTextoMexicanoDigital/U1-W7 bibliographic fingerprint'

MARKER_RE = re.compile(
    r'(isbn|edici[oó]n|reimpresi[oó]n|secretar[ií]a|educaci[oó]n p[uú]blica|'
    r'formaci[oó]n c[ií]vica|derechos reservados|d\.?\s*r\.?|©|2014|2015)',
    re.I,
)
ISBN_RE = re.compile(r'97[89](?:[-\s]?\d){10}')
YEAR_RE = re.compile(r'\b(?:19|20)\d{2}\b')


def load_rows() -> dict[int, dict[str, str]]:
    with ASSETS.open(encoding='utf-8', newline='') as f:
        rows = [r for r in csv.DictReader(f) if r['viewer_key'] == TARGET]
    selected = {int(r['viewer_page']): r for r in rows if int(r['viewer_page']) in PAGES}
    missing = sorted(set(PAGES) - set(selected))
    if missing:
        raise SystemExit(f'missing manifest rows for pages {missing}')
    for page, row in selected.items():
        if row['asset_status'] != 'source_jpeg' or not row.get('sha256'):
            raise SystemExit(f'page {page}: not a hashable source_jpeg')
    return selected


def download_verified(row: dict[str, str]) -> bytes:
    req = Request(row['source_asset_url'], headers={'User-Agent': UA})
    with urlopen(req, timeout=45) as response:
        data = response.read()
    observed_sha = hashlib.sha256(data).hexdigest()
    if observed_sha != row['sha256']:
        raise SystemExit(
            f"{row['viewer_key']} page {row['viewer_page']}: SHA mismatch "
            f"expected={row['sha256']} observed={observed_sha}"
        )
    if len(data) != int(row['byte_size']):
        raise SystemExit(
            f"{row['viewer_key']} page {row['viewer_page']}: size mismatch "
            f"expected={row['byte_size']} observed={len(data)}"
        )
    return data


def ocr_jpeg(data: bytes) -> str:
    if not shutil.which('tesseract'):
        raise SystemExit('tesseract is required')
    with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
        tmp.write(data); tmp.flush()
        proc = subprocess.run(
            ['tesseract', tmp.name, 'stdout', '-l', 'spa', '--psm', '6'],
            check=True,
            capture_output=True,
            text=True,
        )
    return proc.stdout


def canonical_isbn(value: str) -> str:
    digits = re.sub(r'\D', '', value)
    if len(digits) != 13:
        return digits
    return f'{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:12]}-{digits[12:]}'


def main() -> None:
    selected = load_rows()
    records = []
    all_isbns: set[str] = set()
    all_years: set[str] = set()
    for page in PAGES:
        row = selected[page]
        data = download_verified(row)
        text = ocr_jpeg(data)
        lines = [' '.join(line.split()) for line in text.splitlines() if line.strip()]
        retained = [line for line in lines if MARKER_RE.search(line)]
        isbns = sorted({canonical_isbn(m.group(0)) for m in ISBN_RE.finditer(text)})
        years = sorted(set(YEAR_RE.findall(text)))
        # YEAR_RE contains a noncapturing century, so findall returns full match.
        years = sorted(set(re.findall(r'\b(?:19|20)\d{2}\b', text)))
        all_isbns.update(isbns); all_years.update(years)
        records.append({
            'fingerprint_version': VERSION,
            'viewer_key': TARGET,
            'viewer_page': page,
            'source_image_index': row['source_image_index'],
            'source_sha256': row['sha256'],
            'source_byte_size': row['byte_size'],
            'sha_verified': 1,
            'isbn_candidates': ';'.join(isbns),
            'year_candidates': ';'.join(years),
            'bibliographic_lines': ' || '.join(retained[:40]),
        })
        print(page, 'isbn', ','.join(isbns) or '-', 'markers', len(retained), flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0].keys())
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)

    lines = [
        '# LTMD-U1 W7 — huella bibliográfica de H2014P5FCA',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '- Páginas lógicas auditadas: **1–12**.',
        '- JPEG verificados contra SHA-256 y tamaño del manifiesto fuente: **12/12**.',
        f"- ISBN detectados por OCR: **{', '.join(sorted(all_isbns)) if all_isbns else 'ninguno'}**.",
        f"- Años detectados por OCR: **{', '.join(sorted(all_years)) if all_years else 'ninguno'}**.",
        '',
        'El CSV conserva únicamente líneas OCR con marcadores bibliográficos; no publica el OCR completo de las páginas. La huella sirve para identificar edición/ISBN contra fuentes externas, pero no rellena la página 104 ni modifica `ocr_source_admitted`.',
        '',
        '## Evidencia por página',
        '',
    ]
    for r in records:
        if r['bibliographic_lines'] or r['isbn_candidates']:
            lines.append(f"### Página lógica {r['viewer_page']}")
            lines.append('')
            if r['isbn_candidates']:
                lines.append(f"ISBN candidato: `{r['isbn_candidates']}`.")
            if r['bibliographic_lines']:
                lines.append(f"Marcadores OCR: `{r['bibliographic_lines']}`")
            lines.append('')
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
