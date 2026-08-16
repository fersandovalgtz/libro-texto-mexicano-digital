#!/usr/bin/env python3
"""Locate the observed addPage implementation used by unresolved LTMD-U1 W7 viewers.

The inspection is source-only. It reads the published routing diagnostic,
retrieves the unresolved viewer HTML plus its declared same-origin JavaScript,
and records hashes plus minimal call/definition snippets. No page-image assets
are requested or persisted.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROUTING = Path('data/catalog/ltmd_u1_w7_routing_diagnostics.json')
OUT_JSON = Path('data/catalog/ltmd_u1_w7_addpage_contract.json')
OUT_MD = Path('data/catalog/ltmd_u1_w7_addpage_contract.md')
VERSION = 'LTMD_U1_W7_ADDPAGE_CONTRACT_0.2'
UA = 'LibroTextoMexicanoDigital/U1-W7 addPage contract inspector'
TOKENS = ('addPage', 'loadPage', '.jpg', '/c/', 'ag_clave')


def fetch(url: str, attempts: int = 3) -> dict[str, object]:
    error = ''
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/javascript,text/javascript,*/*;q=0.1'})
            with urlopen(req, timeout=45) as response:
                body = response.read()
                status = int(getattr(response, 'status', 200))
                content_type = response.headers.get('Content-Type', '')
            text = body.decode('utf-8', errors='replace')
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
            error = f'HTTPError {exc.code}'
        except (URLError, TimeoutError, OSError) as exc:
            error = f'{type(exc).__name__}: {exc}'
        if attempt < attempts:
            time.sleep(attempt)
    return {'url': url, 'status': None, 'content_type': '', 'byte_size': 0, 'sha256': '', 'attempts': attempts, 'error': error, 'text': ''}


def compact(value: str, limit: int = 1200) -> str:
    return re.sub(r'\s+', ' ', value).strip()[:limit]


def classify(snippet: str) -> str:
    if re.search(r'function\s+addPage\s*\(', snippet):
        return 'named_function_definition'
    if re.search(r'addPage\s*=\s*function\s*\(', snippet):
        return 'function_assignment_definition'
    if re.search(r'(?:const|let|var)\s+addPage\s*=\s*', snippet):
        return 'variable_definition'
    if 'addPage(' in snippet:
        return 'call_or_other_use'
    return 'route_related'


def scan(source_url: str, source_kind: str, text: str) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    lines = text.splitlines() or [text]
    for idx, line in enumerate(lines):
        if not any(token.lower() in line.lower() for token in TOKENS):
            continue
        lo = max(0, idx - 3)
        hi = min(len(lines), idx + 4)
        snippet = compact('\n'.join(lines[lo:hi]))
        hits.append({
            'source_url': source_url,
            'source_kind': source_kind,
            'line': idx + 1,
            'classification': classify(snippet),
            'tokens': [token for token in TOKENS if token.lower() in snippet.lower()],
            'snippet_sha256': hashlib.sha256(snippet.encode('utf-8')).hexdigest(),
            'snippet': snippet,
        })
    return hits


def main() -> None:
    routing = json.loads(ROUTING.read_text(encoding='utf-8'))
    html_urls: list[str] = []
    script_urls: list[str] = []
    for viewer in routing.get('viewers', []):
        source_url = viewer.get('source_url', '')
        if source_url and source_url not in html_urls:
            html_urls.append(source_url)
        for item in viewer.get('scripts', []):
            url = item.get('url', '')
            if url and url not in script_urls:
                script_urls.append(url)

    if not html_urls or not script_urls:
        raise SystemExit('W7 routing diagnostics lack viewer HTML or JavaScript URLs')

    sources: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []
    for source_kind, urls in (('viewer_html', html_urls), ('declared_javascript', script_urls)):
        for url in urls:
            record = fetch(url)
            text = str(record.pop('text', ''))
            record['source_kind'] = source_kind
            sources.append(record)
            hits.extend(scan(url, source_kind, text))

    definitions = [hit for hit in hits if 'definition' in str(hit['classification'])]
    addpage_uses = [hit for hit in hits if 'addPage' in hit['tokens']]
    payload = {
        'contract_version': VERSION,
        'policy': 'Unresolved viewer HTML plus declared same-origin JavaScript only; no book-image asset requests.',
        'routing_diagnostic_version': routing.get('diagnostic_version'),
        'viewer_html_source_count': len(html_urls),
        'javascript_source_count': len(script_urls),
        'source_count': len(sources),
        'sources': sources,
        'route_hit_count': len(hits),
        'addpage_use_count': len(addpage_uses),
        'addpage_definition_count': len(definitions),
        'addpage_definitions': definitions,
        'route_hits': hits,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# LTMD-U1 W7 — contrato observado de `addPage`',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Política: HTML de los visores no resueltos y JavaScript declarado del mismo origen; no se solicitan activos de página.',
        '',
        f'- HTML de visores inspeccionados: **{len(html_urls)}**.',
        f'- Fuentes JavaScript inspeccionadas: **{len(script_urls)}**.',
        f'- Evidencias de ruta: **{len(hits)}**.',
        f'- Usos de `addPage`: **{len(addpage_uses)}**.',
        f'- Definiciones observadas de `addPage`: **{len(definitions)}**.',
        '',
        '## Resultado',
        '',
    ]
    if definitions:
        for hit in definitions:
            lines.append(f"- `{hit['classification']}` en `{hit['source_url']}`, línea {hit['line']}; fuente `{hit['source_kind']}`; snippet SHA-256 `{hit['snippet_sha256']}`.")
    else:
        lines.append('No se observó una definición de `addPage` ni en el HTML de los cinco visores ni en sus JavaScript declarados. La cadena de routing permanece no resuelta y no autoriza inferir una ruta de imagen alternativa.')
    lines += [
        '',
        'El JSON conserva hashes de las fuentes y fragmentos mínimos suficientes para auditar la conclusión. Si no aparece una definición, el siguiente perímetro legítimo es detectar referencias/cargas dinámicas adicionales; no probar rutas de imagen por heurística.',
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
