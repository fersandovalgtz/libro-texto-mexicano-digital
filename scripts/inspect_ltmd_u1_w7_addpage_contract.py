#!/usr/bin/env python3
"""Locate the observed addPage implementation used by unresolved LTMD-U1 W7 viewers.

The inspection is source-only: it reads the already-published routing diagnostic
to obtain same-origin JavaScript URLs, retrieves only those JavaScript resources,
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
VERSION = 'LTMD_U1_W7_ADDPAGE_CONTRACT_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W7 addPage contract inspector'
TOKENS = ('addPage', 'loadPage', '.jpg', '/c/', 'ag_clave')


def fetch(url: str, attempts: int = 3) -> dict[str, object]:
    error = ''
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={'User-Agent': UA, 'Accept': 'application/javascript,text/javascript,*/*;q=0.1'})
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


def compact(value: str, limit: int = 900) -> str:
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


def main() -> None:
    routing = json.loads(ROUTING.read_text(encoding='utf-8'))
    script_urls: list[str] = []
    for viewer in routing.get('viewers', []):
        for item in viewer.get('scripts', []):
            url = item.get('url', '')
            if url and url not in script_urls:
                script_urls.append(url)

    if not script_urls:
        raise SystemExit('No JavaScript URLs available in W7 routing diagnostics')

    sources: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []
    for url in script_urls:
        record = fetch(url)
        text = str(record.pop('text', ''))
        sources.append(record)
        lines = text.splitlines() or [text]
        for idx, line in enumerate(lines):
            if not any(token.lower() in line.lower() for token in TOKENS):
                continue
            lo = max(0, idx - 2)
            hi = min(len(lines), idx + 3)
            snippet = compact('\n'.join(lines[lo:hi]))
            hits.append({
                'source_url': url,
                'line': idx + 1,
                'classification': classify(snippet),
                'tokens': [token for token in TOKENS if token.lower() in snippet.lower()],
                'snippet_sha256': hashlib.sha256(snippet.encode('utf-8')).hexdigest(),
                'snippet': snippet,
            })

    definitions = [hit for hit in hits if 'definition' in str(hit['classification'])]
    addpage_uses = [hit for hit in hits if 'addPage' in hit['tokens']]
    payload = {
        'contract_version': VERSION,
        'policy': 'Same-origin JavaScript only; no book-image asset requests.',
        'routing_diagnostic_version': routing.get('diagnostic_version'),
        'script_source_count': len(sources),
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
        'Política: sólo JavaScript del mismo origen ya declarado por los visores; no se solicitan activos de página.',
        '',
        f'- Fuentes JavaScript inspeccionadas: **{len(sources)}**.',
        f'- Evidencias de ruta: **{len(hits)}**.',
        f'- Usos de `addPage`: **{len(addpage_uses)}**.',
        f'- Definiciones observadas de `addPage`: **{len(definitions)}**.',
        '',
        '## Resultado',
        '',
    ]
    if definitions:
        for hit in definitions:
            lines.append(f"- `{hit['classification']}` en `{hit['source_url']}`, línea {hit['line']}; snippet SHA-256 `{hit['snippet_sha256']}`.")
    else:
        lines.append('No se observó una definición de `addPage` en los JavaScript declarados por los cinco visores. La cadena de routing permanece no resuelta y no autoriza inferir una ruta de imagen alternativa.')
    lines += [
        '',
        'El JSON conserva los hashes de las fuentes y fragmentos mínimos suficientes para auditar la conclusión. La ausencia de una definición en este perímetro no demuestra que no exista código cargado dinámicamente; sólo delimita lo observado en las fuentes declaradas por el visor.',
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
