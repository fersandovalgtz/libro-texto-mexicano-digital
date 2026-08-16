#!/usr/bin/env python3
"""Extract the W7 image-route contract from the viewer's dynamic helper code.

Only the already-identified same-origin JavaScript helper (`magazine.js`) is
retrieved. No book image is requested. The output freezes the exact statements
that map a logical viewer page to the `ag_page` filename and image URL.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

DYNAMIC = Path('data/catalog/ltmd_u1_w7_dynamic_dependencies.json')
OUT_JSON = Path('data/catalog/ltmd_u1_w7_image_route_contract.json')
OUT_MD = Path('data/catalog/ltmd_u1_w7_image_route_contract.md')
VERSION = 'LTMD_U1_W7_IMAGE_ROUTE_CONTRACT_0.2'
UA = 'LibroTextoMexicanoDigital/U1-W7 image route contract extractor'


def fetch(url: str) -> tuple[bytes, str, int]:
    req = Request(url, headers={'User-Agent': UA, 'Accept': 'application/javascript,text/javascript,*/*;q=0.1'})
    with urlopen(req, timeout=45) as response:
        body = response.read()
        content_type = response.headers.get('Content-Type', '')
        status = int(getattr(response, 'status', 200))
    return body, content_type, status


def compact(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def extract_function(lines: list[str], name: str) -> dict[str, object] | None:
    start = None
    pattern = re.compile(rf'function\s+{re.escape(name)}\s*\(')
    for idx, line in enumerate(lines):
        if pattern.search(line):
            start = idx
            break
    if start is None:
        return None

    block: list[str] = []
    depth = 0
    opened = False
    end = start
    for idx in range(start, len(lines)):
        line = lines[idx]
        block.append(line)
        depth += line.count('{')
        if line.count('{'):
            opened = True
        depth -= line.count('}')
        end = idx
        if opened and depth <= 0:
            break
    snippet = compact('\n'.join(block))
    return {
        'name': name,
        'start_line': start + 1,
        'end_line': end + 1,
        'snippet': snippet,
        'snippet_sha256': hashlib.sha256(snippet.encode('utf-8')).hexdigest(),
    }


def main() -> None:
    dynamic = json.loads(DYNAMIC.read_text(encoding='utf-8'))
    candidates = [
        row['url'] for row in dynamic.get('sources', [])
        if str(row.get('url', '')).endswith('/magazine.js') and row.get('status') == 200
    ]
    if len(candidates) != 1:
        raise SystemExit(f'Expected one HTTP-200 magazine.js dependency, found {len(candidates)}')
    url = candidates[0]
    body, content_type, status = fetch(url)
    text = body.decode('utf-8', errors='replace')
    lines = text.splitlines()

    relevant: list[dict[str, object]] = []
    for number, line in enumerate(lines, start=1):
        lower = line.lower()
        if any(token in lower for token in ('ag_page', 'addpage', 'loadpage', '.jpg', 'ag_clave', 'function pad')):
            lo = max(0, number - 3)
            hi = min(len(lines), number + 2)
            snippet = compact('\n'.join(lines[lo:hi]))
            relevant.append({
                'line': number,
                'snippet': snippet,
                'snippet_sha256': hashlib.sha256(snippet.encode('utf-8')).hexdigest(),
            })

    ag_page_statements = [
        {'line': number, 'statement': compact(line), 'sha256': hashlib.sha256(compact(line).encode('utf-8')).hexdigest()}
        for number, line in enumerate(lines, start=1)
        if 'ag_page' in line
    ]
    route_statements = [
        {'line': number, 'statement': compact(line), 'sha256': hashlib.sha256(compact(line).encode('utf-8')).hexdigest()}
        for number, line in enumerate(lines, start=1)
        if '.jpg' in line.lower() or ("attr('src'" in line.lower() and 'ag_clave' in line)
    ]
    explicit_route = [row for row in route_statements if 'ag_clave' in row['statement'] and 'ag_page' in row['statement']]
    pad_function = extract_function(lines, 'pad')
    addpage_function = extract_function(lines, 'addPage')
    loadpage_function = extract_function(lines, 'loadPage')

    payload = {
        'contract_version': VERSION,
        'policy': 'JavaScript source extraction only; no book-image asset requests.',
        'dynamic_dependency_version': dynamic.get('inspection_version'),
        'source': {
            'url': url,
            'status': status,
            'content_type': content_type,
            'byte_size': len(body),
            'sha256': hashlib.sha256(body).hexdigest(),
        },
        'ag_page_statement_count': len(ag_page_statements),
        'route_statement_count': len(route_statements),
        'explicit_route_statement_count': len(explicit_route),
        'pad_function': pad_function,
        'addpage_function': addpage_function,
        'loadpage_function': loadpage_function,
        'ag_page_statements': ag_page_statements,
        'route_statements': route_statements,
        'explicit_route_statements': explicit_route,
        'context_evidence': relevant,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    md = [
        '# LTMD-U1 W7 — contrato de ruta de imagen',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Política: extracción exclusiva de JavaScript; no se solicitan activos de página.',
        '',
        f'- Fuente: `{url}`.',
        f'- HTTP: **{status}**.',
        f'- SHA-256 de la fuente: `{payload["source"]["sha256"]}`.',
        f'- Sentencias con `ag_page`: **{len(ag_page_statements)}**.',
        f'- Sentencias de ruta/imagen: **{len(route_statements)}**.',
        f'- Sentencias explícitas que combinan `ag_clave` + `ag_page`: **{len(explicit_route)}**.',
        '',
        '## Función `pad()` observada',
        '',
    ]
    if pad_function:
        md.append(f"- líneas {pad_function['start_line']}–{pad_function['end_line']}: `{pad_function['snippet']}`")
        md.append(f"- SHA-256 del fragmento: `{pad_function['snippet_sha256']}`.")
    else:
        md.append('No se localizó una definición de `pad()` en la fuente observada.')
    md += ['', '## Transformación observada de página', '']
    for row in ag_page_statements:
        md.append(f"- línea {row['line']}: `{row['statement']}`")
    md += ['', '## Construcción observada de URL', '']
    for row in explicit_route:
        md.append(f"- línea {row['line']}: `{row['statement']}`")
    md += [
        '',
        'Este contrato documenta únicamente el algoritmo observado en el código del visor. No demuestra que los archivos resultantes existan para todas las generaciones; esa disponibilidad debe comprobarse por separado y de forma mínima.',
    ]
    OUT_MD.write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
