#!/usr/bin/env python3
"""Evaluate a 2017-2018 external mirror as a derived recovery candidate.

The candidate site is discovered from its landing page and page links; image
filenames are never guessed. Official H2014P5FCA anchor images are downloaded
only from URLs frozen in the W7 asset manifest and verified by SHA-256/size.
OCR fingerprints are compared around the isolated page-104 gap to infer any
page-number offset. No external image is committed and source admissibility is
not changed.
"""
from __future__ import annotations

import csv
import hashlib
import html.parser
import re
import shutil
import subprocess
import tempfile
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

VERSION = 'LTMD_U1_W7_H2014P5_EXTERNAL_MIRROR_0.1'
TARGET = 'H2014P5FCA'
GAP_PAGE = 104
OFFICIAL_ANCHORS = (4, 103, 105)
CANDIDATE_PAGES = tuple(range(2, 7)) + tuple(range(101, 108))
LANDING = 'https://librosdetexto.online/formacion-civica-etica-quinto-grado-2017-2018/'
ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w7_h2014p5_external_mirror_alignment.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_h2014p5_external_mirror.md')
UA = 'LibroTextoMexicanoDigital/U1-W7 mirror identity diagnostic'


class PageParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self._href = ''
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'a':
            self._href = data.get('href', '')
            self._text = []
        elif tag == 'img':
            self.images.append(data)

    def handle_data(self, data):
        if self._href:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self._href:
            self.links.append((self._href, ' '.join(self._text).strip()))
            self._href = ''
            self._text = []


def fetch(url: str) -> bytes:
    with urlopen(Request(url, headers={'User-Agent': UA}), timeout=45) as response:
        return response.read()


def parse_html(url: str) -> PageParser:
    parser = PageParser()
    parser.feed(fetch(url).decode('utf-8', errors='replace'))
    return parser


def discover_page_urls() -> dict[int, str]:
    parser = parse_html(LANDING)
    urls = {1: LANDING}
    for href, text in parser.links:
        text = text.strip()
        if text.isdigit():
            page = int(text)
            if 1 <= page <= 226:
                urls[page] = urljoin(LANDING, href)
    missing = [p for p in CANDIDATE_PAGES if p not in urls]
    if missing:
        raise SystemExit(f'candidate landing page did not expose page links: {missing}')
    return urls


def discover_image_url(page_url: str, expected_page: int) -> str:
    parser = parse_html(page_url)
    ranked = []
    for img in parser.images:
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or ''
        alt = img.get('alt', '')
        if not src:
            continue
        score = 0
        if re.search(r'Libro\s+Formaci[oó]n\s+C[ií]vica.*Quinto', alt, re.I):
            score += 4
        if re.search(rf'P[aá]gina\s+{expected_page}\b', alt, re.I):
            score += 4
        if 'formacion' in src.lower() and 'quinto' in src.lower():
            score += 2
        ranked.append((score, urljoin(page_url, src), alt))
    if not ranked:
        raise SystemExit(f'no images discovered at candidate page {expected_page}')
    ranked.sort(reverse=True)
    best = ranked[0]
    if best[0] < 4:
        raise SystemExit(
            f'candidate page {expected_page}: no sufficiently identified textbook image; best={best}'
        )
    return best[1]


def official_rows() -> dict[int, dict[str, str]]:
    with ASSETS.open(encoding='utf-8', newline='') as f:
        selected = {
            int(r['viewer_page']): r
            for r in csv.DictReader(f)
            if r['viewer_key'] == TARGET and int(r['viewer_page']) in OFFICIAL_ANCHORS
        }
    if set(selected) != set(OFFICIAL_ANCHORS):
        raise SystemExit(f'official anchors missing: {sorted(set(OFFICIAL_ANCHORS) - set(selected))}')
    return selected


def fetch_verified_official(row: dict[str, str]) -> bytes:
    data = fetch(row['source_asset_url'])
    observed_sha = hashlib.sha256(data).hexdigest()
    if observed_sha != row['sha256'] or len(data) != int(row['byte_size']):
        raise SystemExit(f"official page {row['viewer_page']} failed frozen SHA/size verification")
    return data


def ocr(data: bytes) -> str:
    if not shutil.which('tesseract'):
        raise SystemExit('tesseract is required')
    with tempfile.NamedTemporaryFile(suffix='.jpg') as tmp:
        tmp.write(data); tmp.flush()
        proc = subprocess.run(
            ['tesseract', tmp.name, 'stdout', '-l', 'spa', '--psm', '6'],
            check=True, capture_output=True, text=True,
        )
    return proc.stdout


def norm(text: str) -> str:
    text = unicodedata.normalize('NFKD', text.lower())
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return ' '.join(re.findall(r'[a-z0-9]+', text))


def similarity(a: str, b: str) -> tuple[float, float, float]:
    na, nb = norm(a), norm(b)
    seq = SequenceMatcher(None, na, nb).ratio() if na and nb else 0.0
    ta, tb = set(na.split()), set(nb.split())
    jac = len(ta & tb) / len(ta | tb) if ta and tb else 0.0
    combined = 0.6 * seq + 0.4 * jac
    return seq, jac, combined


def main() -> None:
    page_urls = discover_page_urls()
    candidate_bytes: dict[int, bytes] = {}
    candidate_image_urls: dict[int, str] = {}
    candidate_ocr: dict[int, str] = {}
    for page in CANDIDATE_PAGES:
        image_url = discover_image_url(page_urls[page], page)
        data = fetch(image_url)
        if not data.startswith((b'\xff\xd8\xff', b'\x89PNG')):
            raise SystemExit(f'candidate page {page}: fetched object is not JPEG/PNG')
        candidate_image_urls[page] = image_url
        candidate_bytes[page] = data
        candidate_ocr[page] = ocr(data)
        print('candidate', page, len(data), hashlib.sha256(data).hexdigest(), flush=True)

    official = official_rows()
    rows_out: list[dict[str, str | int | float]] = []
    best_by_anchor = {}
    for anchor in OFFICIAL_ANCHORS:
        official_text = ocr(fetch_verified_official(official[anchor]))
        neighborhood = range(anchor - 2, anchor + 3)
        comparisons = []
        for candidate_page in neighborhood:
            if candidate_page not in candidate_ocr:
                continue
            seq, jac, combined = similarity(official_text, candidate_ocr[candidate_page])
            comparisons.append((combined, candidate_page, seq, jac))
            rows_out.append({
                'analysis_version': VERSION,
                'official_viewer': TARGET,
                'official_page': anchor,
                'official_sha256': official[anchor]['sha256'],
                'candidate_page': candidate_page,
                'candidate_image_url': candidate_image_urls[candidate_page],
                'candidate_sha256': hashlib.sha256(candidate_bytes[candidate_page]).hexdigest(),
                'sequence_similarity': f'{seq:.9f}',
                'token_jaccard': f'{jac:.9f}',
                'combined_similarity': f'{combined:.9f}',
                'page_offset': candidate_page - anchor,
            })
        if not comparisons:
            raise SystemExit(f'anchor {anchor}: no candidate neighborhood')
        comparisons.sort(reverse=True)
        best_by_anchor[anchor] = comparisons[0]

    offsets = [best_by_anchor[p][1] - p for p in OFFICIAL_ANCHORS]
    consistent_offset = offsets[0] if len(set(offsets)) == 1 else None
    min_best_score = min(best_by_anchor[p][0] for p in OFFICIAL_ANCHORS)
    mapping_supported = consistent_offset is not None and min_best_score >= 0.75
    candidate_gap_page = GAP_PAGE + consistent_offset if mapping_supported else None

    gap_sha = ''
    gap_url = ''
    gap_bytes = ''
    if candidate_gap_page is not None and candidate_gap_page in candidate_bytes:
        gap_data = candidate_bytes[candidate_gap_page]
        gap_sha = hashlib.sha256(gap_data).hexdigest()
        gap_url = candidate_image_urls[candidate_gap_page]
        gap_bytes = str(len(gap_data))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows_out[0].keys())
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows_out)

    lines = [
        '# LTMD-U1 W7 — evaluación de espejo externo para H2014P5FCA',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'Espejo candidato: `{LANDING}`.',
        '',
        'Las URLs de página e imagen se descubren desde el HTML del sitio; no se construyen nombres de imagen por heurística. Los anclajes CONALITEG se verifican contra SHA-256 y tamaño antes de OCR. Ninguna imagen externa se guarda en el repositorio.',
        '',
        '## Alineación por anclaje',
        '',
        '| página CONALITEG | mejor página candidato | offset | similitud secuencia | Jaccard tokens | combinada |',
        '|---:|---:|---:|---:|---:|---:|',
    ]
    for anchor in OFFICIAL_ANCHORS:
        combined, candidate_page, seq, jac = best_by_anchor[anchor]
        lines.append(
            f'| {anchor} | {candidate_page} | {candidate_page-anchor:+d} | '
            f'{seq:.6f} | {jac:.6f} | {combined:.6f} |'
        )

    lines += [
        '',
        '## Decisión técnica',
        '',
        f'- Offsets de los tres anclajes: **{offsets}**.',
        f'- Menor similitud combinada entre mejores anclajes: **{min_best_score:.6f}**.',
        f"- Mapeo posicional candidato: **{'soportado' if mapping_supported else 'no soportado'}**.",
    ]
    if mapping_supported:
        lines += [
            f'- Página externa correspondiente al hueco lógico 104: **{candidate_gap_page}**.',
            f'- SHA-256 del objeto externo candidato: `{gap_sha}`.',
            f'- Tamaño del objeto externo candidato: **{gap_bytes} bytes**.',
            f'- URL de imagen candidata descubierta: `{gap_url}`.',
        ]

    lines += [
        '',
        '## Regla epistemológica',
        '',
        'Incluso si el mapeo es soportado, la página candidata es una **reconstrucción derivada desde un espejo externo**. No se etiqueta como `source_jpeg`, no sustituye el 404 institucional y no modifica `ocr_source_admitted`. Su uso analítico posterior requiere registrar explícitamente esta procedencia y mantener separada la capa canónica de fuente.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('offsets', offsets)
    print('mapping_supported', int(mapping_supported))
    print('candidate_gap_page', candidate_gap_page if candidate_gap_page is not None else '')


if __name__ == '__main__':
    main()
