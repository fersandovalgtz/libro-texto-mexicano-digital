#!/usr/bin/env python3
"""Extract a minimal, auditable route contract from the live CONALITEG viewer.

This stage retrieves only claves.json and x.js. It does not request book-image
assets. It records hashes plus minimal route-relevant evidence for the five W7
viewers that remain unresolved after the direct-asset audit.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

BASE = 'https://historico.conaliteg.gob.mx/'
KEYS_URL = BASE + 'claves.json'
JS_URL = BASE + 'x.js'
INVENTORY = Path('data/catalog/ltmd_u1_w7_declared_inventory.csv')
SUMMARY = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_summary.csv')
OUT_JSON = Path('data/catalog/ltmd_u1_w7_viewer_route_contract.json')
OUT_MD = Path('data/catalog/ltmd_u1_w7_viewer_route_contract.md')
VERSION = 'LTMD_U1_W7_VIEWER_ROUTE_CONTRACT_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W7 route-contract extractor'


def fetch(url: str) -> tuple[bytes, str]:
    req = Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urlopen(req, timeout=60) as response:
        body = response.read()
        content_type = response.headers.get('Content-Type', '')
        if int(getattr(response, 'status', 200)) != 200:
            raise SystemExit(f'non-200 response for {url}')
    return body, content_type


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def js_evidence(text: str) -> list[dict[str, object]]:
    # Keep the evidence minimal. These are not a vendored copy of x.js; each
    # snippet is a bounded line fragment selected only for route semantics.
    patterns = (
        'ag_clave', 'ag_pages', 'addPage', 'new Image', '.jpg', '.jpeg',
        "'/c/", '"/c/', "'c/", '"c/', '.attr(\'src\'', '.attr("src"',
        'src=', 'src =', 'image', 'imagen',
    )
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for line_no, raw in enumerate(text.splitlines(), start=1):
        low = raw.lower()
        hits = [token for token in patterns if token.lower() in low]
        if not hits:
            continue
        compact = re.sub(r'\s+', ' ', raw).strip()
        if not compact:
            continue
        # Restrict each excerpt to a short technical fragment.
        snippet = compact[:360]
        key = hashlib.sha256(snippet.encode('utf-8')).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        records.append({
            'line': line_no,
            'tokens': hits,
            'snippet_sha256': key,
            'snippet': snippet,
        })
    return records


def main() -> None:
    inventory_rows = list(csv.DictReader(INVENTORY.open(encoding='utf-8', newline='')))
    summary_rows = list(csv.DictReader(SUMMARY.open(encoding='utf-8', newline='')))
    inventory = {row['viewer_key']: row for row in inventory_rows}
    unresolved = [row['viewer_key'] for row in summary_rows if row['direct_asset_ready'] != '1']
    if len(unresolved) != 5:
        raise SystemExit(f'expected 5 unresolved W7 viewers, found {len(unresolved)}')

    keys_body, keys_type = fetch(KEYS_URL)
    js_body, js_type = fetch(JS_URL)
    keys_data = json.loads(keys_body.decode('utf-8-sig'))
    js_text = js_body.decode('utf-8', errors='replace')

    entries = {}
    missing = []
    for key in unresolved:
        if key not in keys_data:
            missing.append(key)
            continue
        entries[key] = keys_data[key]
    if missing:
        raise SystemExit(f'unresolved viewer keys absent from claves.json: {missing}')

    evidence = js_evidence(js_text)
    if not evidence:
        raise SystemExit('no route-relevant evidence extracted from x.js')

    # Derive field-name inventory only; do not infer semantics beyond values
    # explicitly present in claves.json.
    entry_fields: dict[str, list[str]] = {}
    for key, entry in entries.items():
        if isinstance(entry, dict):
            entry_fields[key] = sorted(entry)
        else:
            entry_fields[key] = []

    payload = {
        'contract_version': VERSION,
        'policy': 'Evidence extraction only; no book-image asset requests.',
        'sources': {
            'claves_json': {
                'url': KEYS_URL,
                'content_type': keys_type,
                'byte_size': len(keys_body),
                'sha256': digest(keys_body),
            },
            'viewer_javascript': {
                'url': JS_URL,
                'content_type': js_type,
                'byte_size': len(js_body),
                'sha256': digest(js_body),
            },
        },
        'unresolved_viewer_count': len(unresolved),
        'viewer_entries': entries,
        'viewer_entry_fields': entry_fields,
        'javascript_route_evidence': evidence,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# LTMD-U1 W7 — contrato observado del routing del visor',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Esta capa observa `claves.json` y `x.js` del visor histórico de CONALITEG. No solicita ni conserva imágenes de los libros.',
        '',
        f'- Visores W7 no resueltos: **{len(unresolved)}**.',
        f'- SHA-256 de `claves.json`: `{digest(keys_body)}`.',
        f'- SHA-256 de `x.js`: `{digest(js_body)}`.',
        f'- Fragmentos técnicos de routing retenidos: **{len(evidence)}**.',
        '',
        '## Entradas observadas en `claves.json`',
        '',
        '| visor | generación | grado | campos observados | entrada |',
        '|---|---:|---:|---|---|',
    ]
    for key in unresolved:
        inv = inventory[key]
        rendered = json.dumps(entries[key], ensure_ascii=False, sort_keys=True)
        lines.append(f"| `{key}` | {inv['catalog_generation']} | {inv['grade_code']} | `{', '.join(entry_fields[key])}` | `{rendered}` |")
    lines += [
        '',
        '## Regla epistemológica',
        '',
        'Una ruta alternativa para activos sólo puede incorporarse al pipeline si puede reconstruirse de manera determinista a partir de estas fuentes observadas. Coincidencias por año, grado, título o número de páginas no constituyen evidencia suficiente.',
        '',
        'El JSON asociado conserva los fragmentos mínimos de JavaScript relevantes para auditar esa reconstrucción.',
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
