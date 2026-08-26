#!/usr/bin/env python3
"""Search a bounded Common Crawl phase for exact W7 withheld-source URIs.

This is a fallback archive probe after Wayback availability errors. Phase 0.3
queries two Common Crawl indexes per year for 2017-2020, centered on the served
H2014P5FCA reprint (cycle 2017-2018) and the unresolved 2018 viewers. Every
established institutional path is queried under both exact HTTP and HTTPS URIs,
because archive indexes treat schemes as distinct URLs. It does not use title
search, nearby-key search, or aliases.
"""
from __future__ import annotations

import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

VERSION = 'LTMD_U1_W7_COMMONCRAWL_SOURCE_DISCOVERY_0.3'
COLLINFO = 'https://index.commoncrawl.org/collinfo.json'
UA = 'LibroTextoMexicanoDigital/U1-W7 exact-uri Common Crawl discovery'
TIMEOUT = 15
WORKERS = 10
PHASE_YEARS = (2017, 2018, 2019, 2020)
COLLECTIONS_PER_YEAR = 2
URI_SCHEMES = ('http', 'https')
OUT = Path('data/catalog/ltmd_u1_w7_commoncrawl_source_discovery.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_commoncrawl_source_discovery.md')

TARGETS = [
    {
        'target_id': 'H2014P5FCA_page104',
        'target_kind': 'exact_missing_asset',
        'viewer_key': 'H2014P5FCA',
        'path': 'historico.conaliteg.gob.mx/c/H2014P5FCA/104.jpg',
    },
    *[
        {
            'target_id': f'{key}_viewer',
            'target_kind': 'exact_viewer',
            'viewer_key': key,
            'path': f'historico.conaliteg.gob.mx/{key}.htm',
        }
        for key in ('H2018P3FCA', 'H2018P4FCA', 'H2018P5FCA', 'H2018P6FCA')
    ],
]


def get_json(url: str):
    with urlopen(Request(url, headers={'User-Agent': UA}), timeout=TIMEOUT) as response:
        return json.loads(response.read().decode('utf-8', errors='replace'))


def collection_year(collection_id: str) -> int | None:
    try:
        return int(collection_id.split('-')[2])
    except (IndexError, ValueError):
        return None


def select_phase_collections(collections: list[dict]) -> list[dict]:
    selected: list[dict] = []
    for year in PHASE_YEARS:
        year_items = sorted(
            [c for c in collections if collection_year(c.get('id', '')) == year],
            key=lambda c: c['id'],
        )
        if not year_items:
            continue
        picks = [year_items[0]]
        if len(year_items) > 1:
            picks.append(year_items[-1])
        selected.extend(picks[:COLLECTIONS_PER_YEAR])
    dedup = {c['id']: c for c in selected}
    return [dedup[key] for key in sorted(dedup)]


def exact_uri(target: dict, scheme: str) -> str:
    if scheme not in URI_SCHEMES:
        raise ValueError(f'unsupported scheme: {scheme}')
    return f"{scheme}://{target['path']}"


def query_one(collection: dict, target: dict, scheme: str) -> dict:
    endpoint = collection.get('cdx-api') or f"https://index.commoncrawl.org/{collection['id']}-index"
    source_url = exact_uri(target, scheme)
    query_url = endpoint + '?' + urlencode({
        'url': source_url,
        'output': 'json',
        'filter': 'status:200',
    })
    try:
        with urlopen(Request(query_url, headers={'User-Agent': UA}), timeout=TIMEOUT) as response:
            raw = response.read().decode('utf-8', errors='replace')
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return {
            'target': target,
            'scheme': scheme,
            'source_url': source_url,
            'collection_id': collection['id'],
            'query_url': query_url,
            'probe_state': 'index_ok',
            'rows': rows,
            'error': '',
        }
    except HTTPError as exc:
        return {
            'target': target,
            'scheme': scheme,
            'source_url': source_url,
            'collection_id': collection['id'],
            'query_url': query_url,
            'probe_state': f'index_http_{exc.code}',
            'rows': [],
            'error': f'HTTP {exc.code}',
        }
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            'target': target,
            'scheme': scheme,
            'source_url': source_url,
            'collection_id': collection['id'],
            'query_url': query_url,
            'probe_state': 'index_network_error',
            'rows': [],
            'error': f'{type(exc).__name__}: {exc}',
        }


def main() -> None:
    observed_utc = datetime.now(timezone.utc).isoformat()
    collections = select_phase_collections(get_json(COLLINFO))
    if not collections:
        raise SystemExit('no Common Crawl phase collections selected for 2017-2020')
    print('selected_collections', ','.join(c['id'] for c in collections), flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [
            pool.submit(query_one, collection, target, scheme)
            for collection in collections
            for target in TARGETS
            for scheme in URI_SCHEMES
        ]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(
                result['target']['target_id'], result['scheme'], result['collection_id'],
                result['probe_state'], 'captures', len(result['rows']), flush=True,
            )

    records: list[dict[str, str]] = []
    summaries = []
    for target in TARGETS:
        target_results = [r for r in results if r['target']['target_id'] == target['target_id']]
        captures = []
        for result in target_results:
            for row in result['rows']:
                record = {
                    'discovery_version': VERSION,
                    'observed_utc': observed_utc,
                    'target_id': target['target_id'],
                    'target_kind': target['target_kind'],
                    'viewer_key': target['viewer_key'],
                    'query_scheme': result['scheme'],
                    'source_url': result['source_url'],
                    'collection_id': result['collection_id'],
                    'probe_state': result['probe_state'],
                    'query_url': result['query_url'],
                    'timestamp': str(row.get('timestamp', '')),
                    'url': str(row.get('url', '')),
                    'status': str(row.get('status', '')),
                    'mime': str(row.get('mime', '')),
                    'mime_detected': str(row.get('mime-detected', '')),
                    'digest': str(row.get('digest', '')),
                    'length': str(row.get('length', '')),
                    'offset': str(row.get('offset', '')),
                    'filename': str(row.get('filename', '')),
                }
                captures.append(record)
                records.append(record)
        timestamps = sorted(r['timestamp'] for r in captures if r['timestamp'])
        states: dict[str, int] = {}
        for result in target_results:
            states[result['probe_state']] = states.get(result['probe_state'], 0) + 1
        schemes_with_captures = sorted({r['query_scheme'] for r in captures})
        summaries.append({
            **target,
            'collections_queried': len(collections),
            'uri_queries': len(target_results),
            'index_ok': states.get('index_ok', 0),
            'index_errors': len(target_results) - states.get('index_ok', 0),
            'capture_count': len(captures),
            'schemes_with_captures': ','.join(schemes_with_captures),
            'first_capture': timestamps[0] if timestamps else '',
            'last_capture': timestamps[-1] if timestamps else '',
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        'discovery_version', 'observed_utc', 'target_id', 'target_kind',
        'viewer_key', 'query_scheme', 'source_url', 'collection_id', 'probe_state',
        'query_url', 'timestamp', 'url', 'status', 'mime', 'mime_detected',
        'digest', 'length', 'offset', 'filename',
    ]
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    selected_ids = ', '.join(c['id'] for c in collections)
    lines = [
        '# LTMD-U1 W7 — descubrimiento Common Crawl de fuentes retenidas',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'Observado UTC: `{observed_utc}`.',
        '',
        f'Fase temporal: **2017–2020**, hasta **{COLLECTIONS_PER_YEAR}** índices por año.',
        f'Índices seleccionados: `{selected_ids}`.',
        f'Esquemas exactos consultados por ruta: `{", ".join(URI_SCHEMES)}`.',
        '',
        'La consulta usa únicamente URIs institucionales exactos. HTTP y HTTPS se consultan por separado porque los índices archivísticos los tratan como URLs distintas. Esta ampliación no introduce búsquedas por similitud. Cero capturas no equivale a ausencia global en Common Crawl ni en la web histórica.',
        '',
        '## Resumen',
        '',
        '| objetivo | colecciones | consultas URI | índice OK | errores | capturas | esquemas con captura | primera | última |',
        '|---|---:|---:|---:|---:|---:|---|---|---|',
    ]
    for item in summaries:
        lines.append(
            f"| `{item['target_id']}` | {item['collections_queried']} | {item['uri_queries']} | "
            f"{item['index_ok']} | {item['index_errors']} | {item['capture_count']} | "
            f"`{item['schemes_with_captures']}` | `{item['first_capture']}` | `{item['last_capture']}` |"
        )

    h2014 = next(item for item in summaries if item['target_id'] == 'H2014P5FCA_page104')
    lines += [
        '',
        '## Página 104 de H2014P5FCA',
        '',
        f"Las variantes HTTP/HTTPS del URI exacto produjeron **{h2014['capture_count']}** captura(s) en esta fase, con **{h2014['index_ok']}/{h2014['uri_queries']}** consultas de índice válidas.",
        '',
        'Si existen capturas, `filename`, `offset`, `length` y `digest` permiten una recuperación WARC dirigida. No se incorpora ningún byte al corpus en esta etapa.',
        '',
        '## Límite epistemológico',
        '',
        'No se consultan títulos, ediciones parecidas ni claves 2019 como sustitutos. Ningún cero de esta fase se interpreta como inexistencia del recurso; la fuente productiva permanece retenida hasta reconstrucción con procedencia suficiente.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
