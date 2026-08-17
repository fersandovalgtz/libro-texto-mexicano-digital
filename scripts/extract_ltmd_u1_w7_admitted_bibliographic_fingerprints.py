#!/usr/bin/env python3
"""Extract bounded bibliographic fingerprints for the 25 source-admitted W7 viewers.

Scientific contract
-------------------
* The admitted cohort comes only from the frozen W7 source-admissibility gate.
* Only logical pages 1..12 are inspected for each admitted viewer.
* Every downloaded source object must match SHA-256 and byte size in the frozen
  W7 asset manifest before OCR.
* OCR is technical evidence extraction, not human transcription. PSM 6 is run
  on every bounded page; extra PSM modes are used only when bibliographic
  markers are already detected on that page.
* The script retains marker-bearing lines and conservative structured
  candidates. It never infers publication dates from catalog_generation.
* No source image and no full-page OCR text is persisted.
"""
from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

VERSION = 'LTMD_U1_W7_ADMITTED_BIBLIOGRAPHIC_FINGERPRINTS_0.1'
ADMISSIBILITY = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.md')
PAGES = tuple(range(1, 13))
ENSEMBLE_PSMS = (3, 4, 11, 12)
UA = 'LibroTextoMexicanoDigital/U1-W7 admitted bibliographic fingerprint 0.1'

MARKER_RE = re.compile(
    r'(isbn|edici[oó]n|reimpresi[oó]n|impresi[oó]n|ciclo\s+escolar|'
    r'derechos\s+reservados|d\.?\s*r\.?|secretar[ií]a\s+de\s+educaci[oó]n\s+p[uú]blica|'
    r'subsecretar[ií]a\s+de\s+educaci[oó]n\s+b[aá]sica|©)',
    re.I,
)
ISBN_RE = re.compile(r'97[89](?:[-\s]?\d){10}')
YEAR_RE = re.compile(r'\b(?:19|20)\d{2}\b')
CYCLE_RE = re.compile(r'ciclo\s+escolar\D{0,12}((?:19|20)\d{2})\s*[-–/]\s*((?:19|20)\d{2})', re.I)
EDITION_RE = re.compile(
    r'\b(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima)\s+'
    r'edici[oó]n\D{0,18}((?:19|20)\d{2})', re.I,
)
REPRINT_RE = re.compile(
    r'\b(primera|segunda|tercera|cuarta|quinta|sexta|s[eé]ptima|octava|novena|d[eé]cima)\s+'
    r'reimpresi[oó]n\D{0,18}((?:19|20)\d{2})', re.I,
)

ORDINAL = {
    'primera': 'first', 'segunda': 'second', 'tercera': 'third', 'cuarta': 'fourth',
    'quinta': 'fifth', 'sexta': 'sixth', 'septima': 'seventh', 'séptima': 'seventh',
    'octava': 'eighth', 'novena': 'ninth', 'decima': 'tenth', 'décima': 'tenth',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def admitted_viewers() -> dict[str, dict[str, str]]:
    rows = read_csv(ADMISSIBILITY)
    admitted = {r['viewer_key']: r for r in rows if r.get('ocr_source_admitted') == '1'}
    if len(admitted) != 25:
        raise SystemExit(f'expected 25 W7 source-admitted viewers, found {len(admitted)}')
    if any(r.get('decision') != 'ocr_source_admitted' for r in admitted.values()):
        raise SystemExit('admitted cohort contains a non-admitted decision')
    return admitted


def asset_rows_for(admitted: dict[str, dict[str, str]]) -> dict[tuple[str, int], dict[str, str]]:
    selected: dict[tuple[str, int], dict[str, str]] = {}
    for row in read_csv(ASSETS):
        key = row.get('viewer_key', '')
        if key not in admitted:
            continue
        try:
            page = int(row.get('viewer_page', ''))
        except ValueError:
            continue
        if page not in PAGES:
            continue
        if row.get('asset_status') != 'source_jpeg' or not row.get('sha256'):
            raise SystemExit(f'{key} page {page}: bounded legal/front-matter page is not a hashable source_jpeg')
        selected[(key, page)] = row
    expected = {(key, page) for key in admitted for page in PAGES}
    missing = sorted(expected - set(selected))
    if missing:
        raise SystemExit(f'missing {len(missing)} bounded asset-manifest rows; first={missing[:10]}')
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


def ocr(data: bytes, psm: int) -> str:
    if not shutil.which('tesseract'):
        raise SystemExit('tesseract is required')
    with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
        tmp.write(data)
        tmp.flush()
        proc = subprocess.run(
            ['tesseract', tmp.name, 'stdout', '-l', 'spa', '--psm', str(psm)],
            check=True, capture_output=True, text=True,
        )
    return proc.stdout


def canonical_isbn(value: str) -> str:
    digits = re.sub(r'\D', '', value)
    return digits if len(digits) != 13 else f'{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:12]}-{digits[12:]}'


def normalize_ordinal(value: str) -> str:
    low = value.lower()
    low = ''.join(ch for ch in unicodedata.normalize('NFKD', low) if not unicodedata.combining(ch))
    return ORDINAL.get(low, low)


def marker_lines(text: str, psm: int) -> list[str]:
    lines = [' '.join(line.split()) for line in text.splitlines() if line.strip()]
    return [f'psm{psm}: {line}' for line in lines if MARKER_RE.search(line)]


def structured_candidates(text: str) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    isbns = sorted({canonical_isbn(m.group(0)) for m in ISBN_RE.finditer(text)})
    years = sorted(set(YEAR_RE.findall(text)))
    cycles = sorted({f'{m.group(1)}-{m.group(2)}' for m in CYCLE_RE.finditer(text)})
    editions = sorted({f'{normalize_ordinal(m.group(1))}_edition:{m.group(2)}' for m in EDITION_RE.finditer(text)})
    reprints = sorted({f'{normalize_ordinal(m.group(1))}_reprint:{m.group(2)}' for m in REPRINT_RE.finditer(text)})
    return isbns, years, cycles, editions, reprints


def main() -> None:
    admitted = admitted_viewers()
    assets = asset_rows_for(admitted)
    records: list[dict[str, str | int]] = []
    viewer_evidence_pages: dict[str, set[int]] = defaultdict(set)
    viewer_candidates: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for viewer_key in sorted(admitted):
        gate = admitted[viewer_key]
        for page in PAGES:
            row = assets[(viewer_key, page)]
            data = download_verified(row)
            texts: list[tuple[int, str]] = [(6, ocr(data, 6))]
            if MARKER_RE.search(texts[0][1]):
                for psm in ENSEMBLE_PSMS:
                    texts.append((psm, ocr(data, psm)))

            combined_text = '\n'.join(text for _, text in texts)
            retained: list[str] = []
            for psm, text in texts:
                retained.extend(marker_lines(text, psm))
            # Stable de-duplication without destroying OCR-mode provenance.
            retained = list(dict.fromkeys(retained))
            isbns, years, cycles, editions, reprints = structured_candidates(combined_text)
            has_evidence = bool(retained or isbns or cycles or editions or reprints)
            if has_evidence:
                viewer_evidence_pages[viewer_key].add(page)
                for value in isbns: viewer_candidates[viewer_key]['isbn'].add(value)
                for value in cycles: viewer_candidates[viewer_key]['school_cycle'].add(value)
                for value in editions: viewer_candidates[viewer_key]['edition'].add(value)
                for value in reprints: viewer_candidates[viewer_key]['reprint'].add(value)

            records.append({
                'fingerprint_version': VERSION,
                'viewer_key': viewer_key,
                'catalog_generation': gate['catalog_generation'],
                'grade_code': gate['grade_code'],
                'title_core': gate['title_core'],
                'viewer_page': page,
                'source_image_index': row['source_image_index'],
                'source_sha256': row['sha256'],
                'source_byte_size': row['byte_size'],
                'sha_verified': 1,
                'ocr_psm_modes': ';'.join(str(psm) for psm, _ in texts),
                'bibliographic_evidence_detected': int(has_evidence),
                'isbn_candidates': ';'.join(isbns),
                'year_candidates': ';'.join(years),
                'school_cycle_candidates': ';'.join(cycles),
                'edition_candidates': ';'.join(editions),
                'reprint_candidates': ';'.join(reprints),
                'bibliographic_lines': ' || '.join(retained[:80]),
            })
        print(viewer_key, 'evidence_pages', sorted(viewer_evidence_pages[viewer_key]), flush=True)

    if len(records) != 25 * len(PAGES):
        raise SystemExit(f'expected 300 fingerprint rows, found {len(records)}')
    if sum(int(r['sha_verified']) for r in records) != len(records):
        raise SystemExit('not all bounded pages are SHA verified')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0].keys())
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)

    generation_counts = Counter(r['catalog_generation'] for r in admitted.values())
    lines = [
        '# LTMD-U1 W7 — huellas bibliográficas de la cohorte admitida',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '- Visores fuente admitidos: **25/25**.',
        '- Ventana auditada: páginas lógicas **1–12** de cada visor.',
        '- Páginas fuente descargadas, SHA-256+tamaño verificadas y sometidas a OCR técnico: **300/300**.',
        '- Las imágenes y el OCR de página completa no se persisten.',
        '- `catalog_generation` se conserva como cohorte de catálogo y **no** se usa para completar fechas bibliográficas.',
        '',
        'Cohorte por generación de catálogo: ' + ', '.join(f'**{k}: {generation_counts[k]}**' for k in sorted(generation_counts)) + '.',
        '',
        '## Resumen por objeto',
        '',
        '| objeto | cohorte | grado | páginas con evidencia | edición candidata | reimpresión candidata | ciclo candidato | ISBN candidato |',
        '|---|---:|---:|---|---|---|---|---|',
    ]
    for key in sorted(admitted):
        c = viewer_candidates[key]
        fmt = lambda name: ', '.join(sorted(c.get(name, set()))) or '—'
        pages = ','.join(map(str, sorted(viewer_evidence_pages[key]))) or '—'
        lines.append(
            f"| `{key}` | {admitted[key]['catalog_generation']} | {admitted[key]['grade_code']} | `{pages}` | "
            f"`{fmt('edition')}` | `{fmt('reprint')}` | `{fmt('school_cycle')}` | `{fmt('isbn')}` |"
        )
    lines += [
        '',
        '## Límite epistemológico',
        '',
        'Los candidatos son lecturas OCR de páginas institucionales cuya identidad binaria fue verificada contra el manifiesto fuente. No son todavía metadatos bibliográficos canónicos: cada promoción a `ltmd_bibliographic_observations.csv` requiere una regla explícita y reproducible sobre una página concreta. OCR dudoso, fechas aisladas y coincidencia con `catalog_generation` no se promueven por defecto.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    print('viewers', len(admitted))
    print('rows', len(records))
    print('sha_verified', sum(int(r['sha_verified']) for r in records))
    print('viewers_with_evidence', sum(bool(viewer_evidence_pages[k]) for k in admitted))


if __name__ == '__main__':
    main()
