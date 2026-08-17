#!/usr/bin/env python3
"""Discover archived source evidence for LTMD-U1 W7 withheld viewers.

The probe is deliberately conservative: it queries Wayback CDX only for exact
institutional viewer URIs, the one exact missing H2014 asset, and the four exact
H2018 asset-subtree prefixes already established by the viewer route contract.
It does not search by title similarity and does not create aliases.
"""
from __future__ import annotations

import csv
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

VERSION = 'LTMD_U1_W7_WAYBACK_SOURCE_DISCOVERY_0.2'
CDX = 'https://web.archive.org/cdx/search/cdx'
UA = 'LibroTextoMexicanoDigital/U1-W7 exact-uri archive discovery'
OUT = Path('data/catalog/ltmd_u1_w7_wayback_source_discovery.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_wayback_source_discovery.md')
MAX_WORKERS = 5
TIMEOUT_SECONDS = 20
ATTEMPTS = 2

VIEWERS = [
    'H2014P5FCA',
    'H2018P3FCA',
    'H2018P4FCA',
    'H2018P5FCA',
    'H2018P6FCA',
]

TARGETS = [
    {
        'target_id': 'H2014P5FCA_viewer',
        'target_kind': 'exact_viewer',
        'viewer_key': 'H2014P5FCA',
        'cdx_url': 'historico.conaliteg.gob.mx/H2014P5FCA.htm',
        'expected_original_prefix': 'http',
    },
    {
        'target_id': 'H2014P5FCA_page104',
        'target_kind': 'exact_missing_asset',
        'viewer_key': 'H2014P5FCA',
        'cdx_url': 'historico.conaliteg.gob.mx/c/H2014P5FCA/104.jpg',
        'expected_original_prefix': 'http',
    },
] + [
    {
        'target_id': f'{key}_viewer',
        'target_kind': 'exact_viewer',
        'viewer_key': key,
        'cdx_url': f'historico.conaliteg.gob.mx/{key}.htm',
        'expected_original_prefix': 'http',
    }
    for key in VIEWERS[1:]
] + [
    {
        'target_id': f'{key}_asset_subtree',
        'target_kind': 'exact_asset_subtree',
        'viewer_key': key,
        'cdx_url': f'historico.conaliteg.gob.mx/c/{key}/*',
        'expected_original_prefix': 'http',
    }
    for key in VIEWERS[1:]
]

FIELDS = ['timestamp', 'original', 'statuscode', 'mimetype', 'digest', 'length']


def fetch_cdx(target: dict[str, str]) -> tuple[str, str, list[dict[str, str]]]:
    params = {
        'url': target['cdx_url'],
        'output': 'json',
        'fl': ','.join(FIELDS),
        'filter': 'statuscode:200',
        'collapse': 'urlkey',
        'limit': '5000',
    }
    url = CDX + '?' + urlencode(params)
    last_error = ''
    for attempt in range(1, ATTEMPTS + 1):
        try:
            with urlopen(Request(url, headers={'User-Agent': UA}), timeout=TIMEOUT_SECONDS) as response:
                raw = response.read().decode('utf-8', errors='replace')
            data = json.loads(raw)
            if not data:
                return url, 'cdx_ok', []
            header = data[0]
            if header != FIELDS:
                return url, 'cdx_schema_error', []
            rows = [dict(zip(header, row)) for row in data[1:]]
            return url, 'cdx_ok', rows
        except HTTPError as exc:
            last_error = f'HTTP {exc.code}'
            if exc.code in {400, 404}:
                return url, f'cdx_http_{exc.code}', []
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = f'{type(exc).__name__}: {exc}'
        if attempt < ATTEMPTS:
            time.sleep(2)
    return url, 'cdx_network_error:' + last_error, []


def main() -> None:
    observed_utc = datetime.now(timezone.utc).isoformat()
    fetched: dict[str, tuple[dict[str, str], str, str, list[dict[str, str]]]] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_cdx, target): target for target in TARGETS}
        for future in as_completed(futures):
            target = futures[future]
            query_url, probe_state, rows = future.result()
            fetched[target['target_id']] = (target, query_url, probe_state, rows)
            print(target['target_id'], probe_state, len(rows), flush=True)

    records: list[dict[str, str]] = []
    summaries: list[dict[str, object]] = []
    for target_id in sorted(fetched):
        target, query_url, probe_state, rows = fetched[target_id]
        valid_rows = []
        for row in rows:
            original = row.get('original', '')
            if original and not original.startswith(target['expected_original_prefix']):
                continue
            valid_rows.append(row)
            records.append({
                'discovery_version': VERSION,
                'observed_utc': observed_utc,
                'target_id': target['target_id'],
                'target_kind': target['target_kind'],
                'viewer_key': target['viewer_key'],
                'cdx_query_url': query_url,
                'probe_state': probe_state,
                **{field: row.get(field, '') for field in FIELDS},
            })
        timestamps = sorted(r['timestamp'] for r in valid_rows if r.get('timestamp'))
        summaries.append({
            **target,
            'probe_state': probe_state,
            'capture_count': len(valid_rows),
            'first_capture': timestamps[0] if timestamps else '',
            'last_capture': timestamps[-1] if timestamps else '',
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'discovery_version', 'observed_utc', 'target_id', 'target_kind',
        'viewer_key', 'cdx_query_url', 'probe_state', *FIELDS,
    ]
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    lines = [
        '# LTMD-U1 W7 — descubrimiento archivístico de fuentes retenidas',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'Observado UTC: `{observed_utc}`.',
        '',
        f'Contrato operativo: {MAX_WORKERS} consultas concurrentes; timeout {TIMEOUT_SECONDS}s; {ATTEMPTS} intentos por objetivo.',
        '',
        'Se consulta Wayback CDX exclusivamente con URIs institucionales exactos o prefijos exactos ya demostrados por el contrato de routing. Una captura archivada es evidencia de disponibilidad histórica del URI, no prueba automática de identidad bibliográfica; una consulta sin capturas tampoco prueba inexistencia del recurso.',
        '',
        '## Resumen',
        '',
        '| objetivo | clase | estado CDX | capturas/URLs archivadas | primera | última |',
        '|---|---|---|---:|---|---|',
    ]
    for item in summaries:
        lines.append(
            f"| `{item['target_id']}` | `{item['target_kind']}` | `{item['probe_state']}` | "
            f"{item['capture_count']} | `{item['first_capture']}` | `{item['last_capture']}` |"
        )

    h2014 = next(item for item in summaries if item['target_id'] == 'H2014P5FCA_page104')
    lines += [
        '',
        '## Objetivo prioritario H2014P5FCA',
        '',
        f"La página faltante exacta `c/H2014P5FCA/104.jpg` produjo **{h2014['capture_count']}** registro(s) CDX con estado `{h2014['probe_state']}` en este corte.",
        '',
        'Si existen capturas, el siguiente paso es recuperar sus bytes archivados y comprobar tipo, tamaño, SHA-256 y correspondencia posicional antes de cualquier admisión. Si no existen capturas, la retención permanece sin imputación.',
        '',
        '## Límite epistemológico',
        '',
        'Este proceso no busca candidatos 2019 por similitud. Los cuatro `H2018...` sólo se investigan por su visor institucional exacto y por el prefijo de activos que el código oficial del visor ya demostró. Ningún resultado de CDX modifica por sí solo `ocr_source_admitted`.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
