#!/usr/bin/env python3
"""Extract a bounded bibliographic fingerprint from H2014P5FCA legal matter.

Logical pages 1-12 are downloaded and verified against the frozen W7 source
manifest. Page 4, identified by v0.1 as the legal/credits page, receives a
small multi-PSM OCR ensemble to recover edition and ISBN metadata. Full OCR is
not published. This probe does not change source admissibility or reconstruct
page 104.
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

VERSION = 'LTMD_U1_W7_H2014P5_BIBLIOGRAPHIC_FINGERPRINT_0.2'
TARGET = 'H2014P5FCA'
PAGES = range(1, 13)
LEGAL_PAGE = 4
LEGAL_PSMS = (3, 4, 6, 11, 12)
ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.md')
UA = 'LibroTextoMexicanoDigital/U1-W7 bibliographic fingerprint'

MARKER_RE = re.compile(
    r'(isbn|edici[oó]n|reimpresi[oó]n|secretar[ií]a|educaci[oó]n p[uú]blica|'
    r'formaci[oó]n c[ií]vica|derechos reservados|d\.?\s*r\.?|©|2014|2015|'
    r'2016|2017|2018|ciclo escolar)',
    re.I,
)
STRICT_ISBN_RE = re.compile(r'97[89](?:[-\s]?\d){10}')
FUZZY_ISBN_RE = re.compile(r'97[89][0-9OolIiLlSsBb\-\s]{10,28}', re.I)
OCR_DIGIT_MAP = str.maketrans({
    'O': '0', 'o': '0',
    'I': '1', 'i': '1', 'L': '1', 'l': '1',
    'S': '5', 's': '5',
    'B': '8', 'b': '8',
})


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
    with urlopen(Request(row['source_asset_url'], headers={'User-Agent': UA}), timeout=45) as response:
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


def ocr_jpeg(data: bytes, psm: int) -> str:
    if not shutil.which('tesseract'):
        raise SystemExit('tesseract is required')
    with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
        tmp.write(data); tmp.flush()
        proc = subprocess.run(
            ['tesseract', tmp.name, 'stdout', '-l', 'spa', '--psm', str(psm)],
            check=True, capture_output=True, text=True,
        )
    return proc.stdout


def canonical_isbn(value: str, *, fuzzy: bool = False) -> str:
    if fuzzy:
        value = value.translate(OCR_DIGIT_MAP)
    digits = re.sub(r'\D', '', value)
    if len(digits) != 13:
        return ''
    return f'{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:12]}-{digits[12:]}'


def isbn_candidates(text: str) -> tuple[set[str], set[str]]:
    strict = {
        canonical_isbn(match.group(0))
        for match in STRICT_ISBN_RE.finditer(text)
    }
    strict.discard('')
    fuzzy: set[str] = set()
    for line in text.splitlines():
        if 'isbn' not in line.lower():
            continue
        for match in FUZZY_ISBN_RE.finditer(line):
            candidate = canonical_isbn(match.group(0), fuzzy=True)
            if candidate:
                fuzzy.add(candidate)
    return strict, fuzzy


def main() -> None:
    selected = load_rows()
    records = []
    all_strict: set[str] = set()
    all_fuzzy: set[str] = set()
    all_years: set[str] = set()

    for page in PAGES:
        row = selected[page]
        data = download_verified(row)
        psms = LEGAL_PSMS if page == LEGAL_PAGE else (6,)
        texts = [(psm, ocr_jpeg(data, psm)) for psm in psms]
        combined = '\n'.join(text for _, text in texts)
        strict, fuzzy = isbn_candidates(combined)
        years = sorted(set(re.findall(r'\b(?:19|20)\d{2}\b', combined)))
        all_strict.update(strict); all_fuzzy.update(fuzzy); all_years.update(years)

        retained_by_psm = []
        for psm, text in texts:
            retained = [
                ' '.join(line.split())
                for line in text.splitlines()
                if line.strip() and MARKER_RE.search(line)
            ]
            if retained:
                retained_by_psm.append(
                    f"psm{psm}: " + ' || '.join(retained[:40])
                )

        records.append({
            'fingerprint_version': VERSION,
            'viewer_key': TARGET,
            'viewer_page': page,
            'source_image_index': row['source_image_index'],
            'source_sha256': row['sha256'],
            'source_byte_size': row['byte_size'],
            'sha_verified': 1,
            'ocr_psms': ';'.join(map(str, psms)),
            'isbn_strict_candidates': ';'.join(sorted(strict)),
            'isbn_fuzzy_candidates': ';'.join(sorted(fuzzy)),
            'year_candidates': ';'.join(years),
            'bibliographic_lines': ' ### '.join(retained_by_psm),
        })
        print(
            page,
            'psm', ','.join(map(str, psms)),
            'strict', ','.join(sorted(strict)) or '-',
            'fuzzy', ','.join(sorted(fuzzy)) or '-',
            flush=True,
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader(); writer.writerows(records)

    lines = [
        '# LTMD-U1 W7 — huella bibliográfica de H2014P5FCA',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '- Páginas lógicas auditadas: **1–12**.',
        '- JPEG verificados contra SHA-256 y tamaño del manifiesto fuente: **12/12**.',
        f'- Página legal sometida a ensemble OCR: **{LEGAL_PAGE}**, PSM **{", ".join(map(str, LEGAL_PSMS))}**.',
        f"- ISBN estrictos detectados: **{', '.join(sorted(all_strict)) if all_strict else 'ninguno'}**.",
        f"- ISBN reconstruidos desde línea explícita `ISBN` con normalización OCR conservadora: **{', '.join(sorted(all_fuzzy)) if all_fuzzy else 'ninguno'}**.",
        f"- Años detectados: **{', '.join(sorted(all_years)) if all_years else 'ninguno'}**.",
        '',
        'La normalización difusa sólo sustituye confusiones OCR comunes (O→0, I/l→1, S→5, B→8) dentro de una línea que contiene literalmente `ISBN`; no se aplica a texto arbitrario.',
        '',
        'El CSV conserva únicamente líneas OCR con marcadores bibliográficos; no publica el OCR completo. La huella sirve para identificar edición/ISBN contra fuentes externas, pero no rellena la página 104 ni modifica `ocr_source_admitted`.',
        '',
        '## Evidencia por página',
        '',
    ]
    for r in records:
        if r['bibliographic_lines'] or r['isbn_strict_candidates'] or r['isbn_fuzzy_candidates']:
            lines += [f"### Página lógica {r['viewer_page']}", '']
            if r['isbn_strict_candidates']:
                lines.append(f"ISBN estricto: `{r['isbn_strict_candidates']}`.")
            if r['isbn_fuzzy_candidates']:
                lines.append(f"ISBN normalizado: `{r['isbn_fuzzy_candidates']}`.")
            if r['bibliographic_lines']:
                lines.append(f"Marcadores OCR: `{r['bibliographic_lines']}`")
            lines.append('')
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
