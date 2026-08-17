#!/usr/bin/env python3
"""Snapshot institutional presence of the five source-withheld W7 identities.

This probe requests only metadata/configuration and viewer HTML. It does not
request textbook page assets. It verifies that each source-withheld identity is
still represented in the official `claves.json`, that its declared page count
matches LTMD's frozen source-admissibility row, and that its viewer HTML remains
HTTP-accessible. Raw remote files are not persisted; hashes and bounded title
metadata are recorded for reproducibility.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

VERSION = 'LTMD_U1_W7_WITHHELD_VIEWER_PRESENCE_0.1'
BASE = 'https://historico.conaliteg.gob.mx/'
CLAVES_URL = BASE + 'claves.json'
ADMISSIBILITY = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
OUT = Path('data/catalog/ltmd_u1_w7_withheld_viewer_presence.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_withheld_viewer_presence.md')
UA = 'LibroTextoMexicanoDigital/U1-W7 withheld-viewer presence snapshot 0.1'
EXPECTED_WITHHELD = {
    'H2014P5FCA',
    'H2018P3FCA', 'H2018P4FCA', 'H2018P5FCA', 'H2018P6FCA',
}


def fetch(url: str) -> tuple[bytes, str, int]:
    req = Request(url, headers={'User-Agent': UA})
    with urlopen(req, timeout=45) as response:
        return response.read(), response.headers.get('Content-Type', ''), response.status


def clean_title(html: str) -> str:
    m = re.search(r'<title[^>]*>(.*?)</title>', html, flags=re.I | re.S)
    if not m:
        return ''
    value = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).strip()
    return unescape(value)


def main() -> None:
    with ADMISSIBILITY.open(encoding='utf-8', newline='') as f:
        held = {
            r['viewer_key']: r for r in csv.DictReader(f)
            if r.get('ocr_source_admitted') == '0'
        }
    if set(held) != EXPECTED_WITHHELD:
        raise SystemExit(f'withheld identity drift: {sorted(held)}')

    claves_bytes, claves_type, claves_status = fetch(CLAVES_URL)
    if claves_status != 200:
        raise SystemExit(f'claves.json HTTP {claves_status}')
    claves_sha = hashlib.sha256(claves_bytes).hexdigest()
    claves = json.loads(claves_bytes.decode('utf-8'))

    observed = datetime.now(timezone.utc).isoformat()
    records = []
    for key in sorted(held):
        gate = held[key]
        if key not in claves:
            raise SystemExit(f'{key}: absent from live claves.json')
        entry = claves[key]
        if entry.get('ag_clave') != key:
            raise SystemExit(f'{key}: ag_clave mismatch: {entry}')
        if int(entry.get('ag_pages')) != int(gate['declared_positions']):
            raise SystemExit(
                f"{key}: ag_pages drift {entry.get('ag_pages')} != {gate['declared_positions']}"
            )

        viewer_url = BASE + key + '.htm'
        body, content_type, status = fetch(viewer_url)
        if status != 200:
            raise SystemExit(f'{key}: viewer HTTP {status}')
        html = body.decode('utf-8', errors='replace')
        title = clean_title(html)
        title_normalized = ' '.join(title.split())
        # The key itself may be supplied by JS rather than title text; the
        # snapshot therefore records title evidence instead of requiring a
        # fragile exact title template.
        if not title_normalized:
            raise SystemExit(f'{key}: viewer has no HTML title')

        records.append({
            'snapshot_version': VERSION,
            'observed_utc': observed,
            'viewer_key': key,
            'catalog_generation': gate['catalog_generation'],
            'grade_code': gate['grade_code'],
            'title_core': gate['title_core'],
            'source_decision': gate['decision'],
            'reason_code': gate['reason_code'],
            'declared_positions_gate': gate['declared_positions'],
            'ag_pages_live': str(entry['ag_pages']),
            'claves_json_sha256': claves_sha,
            'claves_json_content_type': claves_type,
            'viewer_url': viewer_url,
            'viewer_http_status': status,
            'viewer_content_type': content_type,
            'viewer_byte_size': len(body),
            'viewer_sha256': hashlib.sha256(body).hexdigest(),
            'viewer_html_title': title_normalized,
            'viewer_present': 1,
            'configuration_present': 1,
        })
        print(key, status, len(body), hashlib.sha256(body).hexdigest(), flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(records)

    lines = [
        '# LTMD-U1 W7 — snapshot de presencia de visores retenidos',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'Observado UTC: `{observed}`.',
        '',
        f'- Identidades retenidas verificadas: **{len(records)}/5**.',
        f'- `claves.json` HTTP 200, SHA-256: `{claves_sha}`.',
        '- El probe **no solicita activos JPEG de páginas**.',
        '',
        '## Resultado',
        '',
        '| visor | decisión fuente | posiciones gate/live | visor HTTP | bytes HTML | título HTML |',
        '|---|---|---:|---:|---:|---|',
    ]
    for r in records:
        lines.append(
            f"| `{r['viewer_key']}` | `{r['source_decision']}` | "
            f"{r['declared_positions_gate']}/{r['ag_pages_live']} | {r['viewer_http_status']} | "
            f"{r['viewer_byte_size']} | `{r['viewer_html_title']}` |"
        )
    lines += [
        '',
        '## Interpretación',
        '',
        'Las cinco identidades siguen presentes como objetos de configuración y como visores HTML institucionales en este corte. Este resultado **no levanta ninguna retención de fuente**: la admisibilidad OCR depende de los activos de página, y este snapshot deliberadamente no los solicita. Para los cuatro H2018, presencia del visor y ausencia de servicio del subárbol JPEG son hechos compatibles y deben mantenerse separados.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
