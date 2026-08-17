#!/usr/bin/env python3
"""Evaluate a 2017-2018 external mirror as a derived recovery candidate.

The mirror is used only as a candidate reconstruction source. Page routes must
self-identify in returned HTML, candidate image URLs are extracted from that
HTML rather than guessed, and all official CONALITEG anchors are verified
against frozen SHA-256/size before OCR comparison. No external image is stored
in the repository and source admissibility is never changed here.
"""
from __future__ import annotations

import csv
import hashlib
import html
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

VERSION = 'LTMD_U1_W7_H2014P5_EXTERNAL_MIRROR_0.3'
TARGET = 'H2014P5FCA'
GAP_PAGE = 104
OFFICIAL_ANCHORS = (4, 103, 105)
CANDIDATE_PAGES = tuple(range(2, 7)) + tuple(range(101, 108))
LANDING = 'https://librosdetexto.online/formacion-civica-etica-quinto-grado-2017-2018/'
ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w7_h2014p5_external_mirror_alignment.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_h2014p5_external_mirror.md')
UA = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0 Safari/537.36 '
    'LTMD-source-audit/0.3'
)
HEADERS = {
    'User-Agent': UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-MX,es;q=0.9,en;q=0.5',
}


class PageParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.text: list[str] = []
        self._href = ''
        self._anchor_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'a':
            self._href = data.get('href', '')
            self._anchor_text = []
        elif tag == 'img':
            self.images.append(data)

    def handle_data(self, data):
        if data.strip():
            self.text.append(data)
        if self._href:
            self._anchor_text.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self._href:
            self.links.append((self._href, ' '.join(self._anchor_text).strip()))
            self._href = ''
            self._anchor_text = []


def fetch(url: str) -> bytes:
    with urlopen(Request(url, headers=HEADERS), timeout=45) as response:
        return response.read()


def parse_html_bytes(raw: bytes) -> PageParser:
    parser = PageParser()
    parser.feed(raw.decode('utf-8', errors='replace'))
    return parser


def page_self_identifies(parser: PageParser, expected_page: int) -> bool:
    plain = html.unescape(' '.join(parser.text))
    if re.search(rf'P[aá]gina\s*:?[ ]*{expected_page}\s*/\s*226\b', plain, re.I):
        return True
    for img in parser.images:
        alt = img.get('alt', '')
        if (
            re.search(r'Libro\s+Formaci[oó]n\s+C[ií]vica.*Quinto', alt, re.I)
            and re.search(rf'P[aá]gina\s+{expected_page}\b', alt, re.I)
        ):
            return True
    return False


def image_url_from_validated_page(raw: bytes, page_url: str, expected_page: int) -> str:
    parser = parse_html_bytes(raw)
    if not page_self_identifies(parser, expected_page):
        raise SystemExit(f'candidate route did not self-identify as page {expected_page}: {page_url}')

    ranked: dict[str, tuple[int, str]] = {}
    for img in parser.images:
        alt = img.get('alt', '')
        candidates = [
            img.get('data-lazy-src', ''), img.get('data-src', ''), img.get('src', '')
        ]
        for src in candidates:
            if not src:
                continue
            absolute = urljoin(page_url, src)
            score = 0
            if re.search(r'Libro\s+Formaci[oó]n\s+C[ií]vica.*Quinto', alt, re.I):
                score += 4
            if re.search(rf'P[aá]gina\s+{expected_page}\b', alt, re.I):
                score += 4
            if 'formacion_civica' in absolute.lower() or 'formacion-civica' in absolute.lower():
                score += 3
            if 'quinto' in absolute.lower():
                score += 1
            prior = ranked.get(absolute)
            if prior is None or score > prior[0]:
                ranked[absolute] = (score, alt)

    if not ranked:
        raise SystemExit(f'validated page {expected_page} exposed no image candidates')
    ordered = sorted(
        ((score, url, alt) for url, (score, alt) in ranked.items()), reverse=True
    )
    best = ordered[0]
    if best[0] < 4:
        raise SystemExit(
            f'validated page {expected_page}: no image sufficiently identified as target book; best={best}'
        )
    if len(ordered) > 1 and ordered[1][0] == best[0] and ordered[1][1] != best[1]:
        raise SystemExit(
            f'validated page {expected_page}: ambiguous image candidates at score {best[0]}'
        )
    return best[1]


def discover_candidate_pages() -> tuple[dict[int, str], dict[int, str], dict[int, bytes]]:
    landing_raw = fetch(LANDING)
    landing_parser = parse_html_bytes(landing_raw)
    linked: dict[int, str] = {}
    for href, text in landing_parser.links:
        text = text.strip()
        if text.isdigit():
            linked[int(text)] = urljoin(LANDING, href)

    page_urls: dict[int, str] = {}
    methods: dict[int, str] = {}
    raws: dict[int, bytes] = {}
    for page in CANDIDATE_PAGES:
        candidates = []
        if page in linked:
            candidates.append(('landing_link', linked[page]))
        # Public site navigation has been observed using /{page}/ WordPress routes.
        route = urljoin(LANDING, f'{page}/')
        if all(url != route for _, url in candidates):
            candidates.append(('validated_page_route', route))

        accepted = None
        errors = []
        for method, url in candidates:
            try:
                raw = fetch(url)
                parser = parse_html_bytes(raw)
                if page_self_identifies(parser, page):
                    accepted = (method, url, raw)
                    break
                errors.append(f'{method}:not_self_identified')
            except Exception as exc:  # diagnostic fallback across candidate routes
                errors.append(f'{method}:{type(exc).__name__}:{exc}')
        if accepted is None:
            raise SystemExit(f'candidate page {page}: no validated route; {errors}')
        methods[page], page_urls[page], raws[page] = accepted
    return page_urls, methods, raws


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
    suffix = '.png' if data.startswith(b'\x89PNG') else '.jpg'
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
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
    return seq, jac, 0.6 * seq + 0.4 * jac


def main() -> None:
    page_urls, route_methods, page_raws = discover_candidate_pages()
    candidate_bytes: dict[int, bytes] = {}
    candidate_image_urls: dict[int, str] = {}
    candidate_ocr: dict[int, str] = {}
    for page in CANDIDATE_PAGES:
        image_url = image_url_from_validated_page(page_raws[page], page_urls[page], page)
        data = fetch(image_url)
        if not data.startswith((b'\xff\xd8\xff', b'\x89PNG')):
            raise SystemExit(f'candidate page {page}: fetched object is not JPEG/PNG')
        candidate_image_urls[page] = image_url
        candidate_bytes[page] = data
        candidate_ocr[page] = ocr(data)
        print(
            'candidate', page, route_methods[page], len(data),
            hashlib.sha256(data).hexdigest(), flush=True,
        )

    official = official_rows()
    rows_out: list[dict[str, str | int | float]] = []
    best_by_anchor = {}
    for anchor in OFFICIAL_ANCHORS:
        official_text = ocr(fetch_verified_official(official[anchor]))
        comparisons = []
        for candidate_page in range(anchor - 2, anchor + 3):
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
                'candidate_page_route': page_urls[candidate_page],
                'route_discovery_method': route_methods[candidate_page],
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

    gap_sha = gap_url = gap_bytes = ''
    if candidate_gap_page is not None and candidate_gap_page in candidate_bytes:
        gap_data = candidate_bytes[candidate_gap_page]
        gap_sha = hashlib.sha256(gap_data).hexdigest()
        gap_url = candidate_image_urls[candidate_gap_page]
        gap_bytes = str(len(gap_data))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        writer.writeheader(); writer.writerows(rows_out)

    validated_routes = sum(
        1 for p in CANDIDATE_PAGES if route_methods[p] == 'validated_page_route'
    )
    lines = [
        '# LTMD-U1 W7 — evaluación de espejo externo para H2014P5FCA',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'Espejo candidato: `{LANDING}`.',
        '',
        f'Rutas aceptadas mediante autoverificación de página: **{validated_routes}/{len(CANDIDATE_PAGES)}** usaron la ruta candidata `/{page}/`; las demás provinieron de enlaces expuestos por el landing.',
        '',
        'Cada ruta se acepta sólo cuando el HTML devuelto identifica el número de página mediante su texto `Página N / 226` o metadatos equivalentes. La URL de imagen se extrae después de ese mismo HTML y nunca se construye por nombre de archivo. Los anclajes CONALITEG se verifican contra SHA-256 y tamaño antes de OCR. Ninguna imagen externa se guarda en el repositorio.',
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
        'Incluso con mapeo soportado, la página candidata es una **reconstrucción derivada desde un espejo externo**. No se etiqueta como `source_jpeg`, no sustituye el 404 institucional y no modifica `ocr_source_admitted`. Su uso analítico posterior requiere procedencia explícita y una capa separada de la fuente canónica.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('offsets', offsets)
    print('mapping_supported', int(mapping_supported))
    print('candidate_gap_page', candidate_gap_page if candidate_gap_page is not None else '')


if __name__ == '__main__':
    main()
