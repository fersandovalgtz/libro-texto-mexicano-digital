#!/usr/bin/env python3
"""Inspect dynamic JavaScript dependencies for unresolved LTMD-U1 W7 viewers.

The inspection is source-only. It retrieves the five unresolved viewer HTML
pages plus same-origin JavaScript referenced directly or discovered from those
sources. It never requests page-image assets. The purpose is to resolve the
observed `addPage` call chain without inventing aliases or image routes.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from collections import deque
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROUTING = Path('data/catalog/ltmd_u1_w7_routing_diagnostics.json')
OUT_JSON = Path('data/catalog/ltmd_u1_w7_dynamic_dependencies.json')
OUT_MD = Path('data/catalog/ltmd_u1_w7_dynamic_dependencies.md')
VERSION = 'LTMD_U1_W7_DYNAMIC_DEPENDENCIES_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W7 dynamic dependency inspector'
MAX_DISCOVERED = 40
MAX_DEPTH = 2

JS_LITERAL_RE = re.compile(r"(?P<q>['\"])(?P<value>[^'\"<>\n]+?\.js(?:\?[^'\"<>\n]*)?)(?P=q)", re.I)
DEFINITION_PATTERNS = {
    'addPage_named_function_definition': re.compile(r'function\s+addPage\s*\(', re.I),
    'addPage_function_assignment_definition': re.compile(r'addPage\s*=\s*function\s*\(', re.I),
    'addPage_arrow_assignment_definition': re.compile(r'(?:const|let|var)\s+addPage\s*=\s*\([^)]*\)\s*=>', re.I),
}
LOADPAGE_PATTERNS = {
    'loadPage_named_function_definition': re.compile(r'function\s+loadPage\s*\(', re.I),
    'loadPage_function_assignment_definition': re.compile(r'loadPage\s*=\s*function\s*\(', re.I),
}
LOADER_TOKENS = (
    'Modernizr.load', 'getScript', "createElement('script", 'createElement("script',
    '.src', 'appendChild', 'document.write', 'import(', 'require(', 'dataType',
)
ROUTE_TOKENS = ('addPage', 'loadPage', '.jpg', '.jpeg', '/c/', 'ag_clave', 'ag_pages')


def fetch_text(url: str, attempts: int = 3) -> dict[str, object]:
    last_error = ''
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/javascript,text/javascript,*/*;q=0.1'})
            with urlopen(req, timeout=45) as response:
                body = response.read()
                status = int(getattr(response, 'status', 200))
                content_type = response.headers.get('Content-Type', '')
                charset = response.headers.get_content_charset()
            text = body.decode(charset or 'utf-8', errors='replace')
            return {
                'url': url,
                'status': status,
                'content_type': content_type,
                'byte_size': len(body),
                'sha256': hashlib.sha256(body).hexdigest(),
                'attempts': attempt,
                'error': '',
                'text': text,
            }
        except HTTPError as exc:
            last_error = f'HTTPError {exc.code}'
        except (URLError, TimeoutError, OSError) as exc:
            last_error = f'{type(exc).__name__}: {exc}'
        if attempt < attempts:
            time.sleep(attempt)
    return {
        'url': url, 'status': None, 'content_type': '', 'byte_size': 0,
        'sha256': '', 'attempts': attempts, 'error': last_error, 'text': '',
    }


def compact(value: str, limit: int = 1100) -> str:
    return re.sub(r'\s+', ' ', value).strip()[:limit]


def context_hits(source_url: str, text: str) -> list[dict[str, object]]:
    lines = text.splitlines() or [text]
    hits: list[dict[str, object]] = []
    seen: set[str] = set()
    for idx, line in enumerate(lines):
        if not any(token.lower() in line.lower() for token in (*LOADER_TOKENS, *ROUTE_TOKENS)):
            continue
        snippet = compact('\n'.join(lines[max(0, idx - 2): min(len(lines), idx + 3)]))
        digest = hashlib.sha256(snippet.encode('utf-8')).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        classes: list[str] = []
        for name, pattern in {**DEFINITION_PATTERNS, **LOADPAGE_PATTERNS}.items():
            if pattern.search(snippet):
                classes.append(name)
        if any(token.lower() in snippet.lower() for token in LOADER_TOKENS):
            classes.append('dynamic_loader_evidence')
        if 'addpage' in snippet.lower() and not any(name.startswith('addPage_') for name in classes):
            classes.append('addPage_use')
        if 'loadpage' in snippet.lower() and not any(name.startswith('loadPage_') for name in classes):
            classes.append('loadPage_use')
        if '.jpg' in snippet.lower() or '.jpeg' in snippet.lower() or '/c/' in snippet.lower():
            classes.append('image_route_evidence')
        hits.append({
            'source_url': source_url,
            'line': idx + 1,
            'classifications': sorted(set(classes)) or ['route_related'],
            'snippet_sha256': digest,
            'snippet': snippet,
        })
        if len(hits) >= 150:
            break
    return hits


def js_candidates(source_url: str, text: str, origin: str) -> list[str]:
    found: list[str] = []
    for match in JS_LITERAL_RE.finditer(text):
        value = match.group('value').strip()
        resolved = urljoin(source_url, value)
        parsed = urlparse(resolved)
        if parsed.scheme not in {'http', 'https'} or parsed.netloc.lower() != origin:
            continue
        if not parsed.path.lower().endswith('.js'):
            continue
        if resolved not in found:
            found.append(resolved)
        if len(found) >= MAX_DISCOVERED:
            break
    return found


def serializable(record: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in record.items() if key != 'text'}


def main() -> None:
    routing = json.loads(ROUTING.read_text(encoding='utf-8'))
    viewers = routing.get('viewers', [])
    if not viewers:
        raise SystemExit('W7 routing diagnostics contain no unresolved viewers')

    origin = urlparse(str(viewers[0]['source_url'])).netloc.lower()
    initial_urls: list[str] = []
    for viewer in viewers:
        html_url = str(viewer.get('source_url', ''))
        if html_url and html_url not in initial_urls:
            initial_urls.append(html_url)
        for script in viewer.get('scripts', []):
            url = str(script.get('url', ''))
            if url and url not in initial_urls:
                initial_urls.append(url)

    queue: deque[tuple[str, int, str]] = deque((url, 0, 'declared_by_viewer') for url in initial_urls)
    visited: set[str] = set()
    records: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []
    discovered_edges: list[dict[str, object]] = []

    while queue and len(visited) < len(initial_urls) + MAX_DISCOVERED:
        url, depth, discovered_from = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        record = fetch_text(url)
        text = str(record.get('text', ''))
        row = serializable(record)
        row['depth'] = depth
        row['discovered_from'] = discovered_from
        records.append(row)
        hits.extend(context_hits(url, text))

        if depth >= MAX_DEPTH or not text:
            continue
        for candidate in js_candidates(url, text, origin):
            if candidate == url:
                continue
            edge = {'from': url, 'to': candidate, 'depth': depth + 1}
            if edge not in discovered_edges:
                discovered_edges.append(edge)
            if candidate not in visited:
                queue.append((candidate, depth + 1, url))

    definition_hits = [
        hit for hit in hits
        if any(classification.startswith('addPage_') and classification.endswith('_definition')
               for classification in hit['classifications'])
    ]
    loadpage_definition_hits = [
        hit for hit in hits
        if any(classification.startswith('loadPage_') and classification.endswith('_definition')
               for classification in hit['classifications'])
    ]
    dynamic_loader_hits = [hit for hit in hits if 'dynamic_loader_evidence' in hit['classifications']]
    image_route_hits = [hit for hit in hits if 'image_route_evidence' in hit['classifications']]
    newly_discovered = [record for record in records if int(record['depth']) > 0]
    successful_new = [record for record in newly_discovered if record.get('status') == 200]

    payload = {
        'inspection_version': VERSION,
        'policy': 'HTML/JavaScript source inspection only; no page-image asset requests.',
        'routing_diagnostic_version': routing.get('diagnostic_version'),
        'origin': origin,
        'initial_source_count': len(initial_urls),
        'source_count_total': len(records),
        'new_dependency_count': len(newly_discovered),
        'new_dependency_http_200_count': len(successful_new),
        'dynamic_loader_evidence_count': len(dynamic_loader_hits),
        'addpage_definition_count': len(definition_hits),
        'loadpage_definition_count': len(loadpage_definition_hits),
        'image_route_evidence_count': len(image_route_hits),
        'sources': records,
        'dependency_edges': discovered_edges,
        'addpage_definitions': definition_hits,
        'loadpage_definitions': loadpage_definition_hits,
        'dynamic_loader_evidence': dynamic_loader_hits,
        'image_route_evidence': image_route_hits,
        'all_route_hits': hits,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# LTMD-U1 W7 — dependencias dinámicas del visor',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Política: inspección exclusiva de HTML/JavaScript del mismo origen; no se solicitan activos de página.',
        '',
        f'- Fuentes iniciales: **{len(initial_urls)}**.',
        f'- Fuentes inspeccionadas en total: **{len(records)}**.',
        f'- Dependencias JavaScript nuevas descubiertas: **{len(newly_discovered)}**.',
        f'- Dependencias nuevas con HTTP 200: **{len(successful_new)}**.',
        f'- Evidencias de carga dinámica: **{len(dynamic_loader_hits)}**.',
        f'- Definiciones observadas de `addPage`: **{len(definition_hits)}**.',
        f'- Definiciones observadas de `loadPage`: **{len(loadpage_definition_hits)}**.',
        f'- Evidencias explícitas de ruta de imagen: **{len(image_route_hits)}**.',
        '',
        '## Dependencias nuevas',
        '',
    ]
    if newly_discovered:
        for item in newly_discovered:
            lines.append(f"- `{item['url']}` — HTTP {item['status']} — {item['byte_size']} bytes — SHA-256 `{item['sha256'] or 'n/a'}` — descubierta desde `{item['discovered_from']}`.")
    else:
        lines.append('No se descubrieron dependencias JavaScript adicionales dentro del perímetro observado.')
    lines += ['', '## Resultado', '']
    if definition_hits:
        lines.append('Se localizó al menos una definición observable de `addPage`; el JSON conserva la fuente y el snippet hasheado para el siguiente paso de reconstrucción de ruta.')
    elif loadpage_definition_hits or image_route_hits:
        lines.append('No apareció una definición de `addPage`, pero sí evidencia auxiliar de `loadPage` o de rutas de imagen. Esa evidencia delimita el siguiente probe sin autorizar aliases por heurística.')
    else:
        lines.append('La cadena sigue incompleta dentro del perímetro observado. No se autoriza inferir ni sondear rutas de imagen alternativas sin nueva evidencia de código o fuente.')
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
