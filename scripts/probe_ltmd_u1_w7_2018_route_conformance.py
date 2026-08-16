#!/usr/bin/env python3
"""Probe exact W7 viewer-route conformance for the unresolved 2018 cohort.

This is a deliberately small source-side diagnostic. It uses the route contract
extracted from the official viewer code and probes three non-terminal positions
per viewer for the four unresolved 2018 viewers and same-grade 2019 controls.
No aliases are inferred, no image bytes are persisted, and a served response is
read only to record byte size and SHA-256.
"""
from __future__ import annotations

import csv
import hashlib
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

INVENTORY = Path('data/catalog/ltmd_u1_w7_declared_inventory.csv')
ROUTE_CONTRACT = Path('data/catalog/ltmd_u1_w7_image_route_contract.json')
OUT_CSV = Path('data/catalog/ltmd_u1_w7_2018_route_conformance.csv')
OUT_MD = Path('data/catalog/ltmd_u1_w7_2018_route_conformance.md')
VERSION = 'LTMD_U1_W7_2018_ROUTE_CONFORMANCE_0.1'
UA = 'LibroTextoMexicanoDigital/U1-W7 route conformance probe'
BASE = 'https://historico.conaliteg.gob.mx/c'
TARGET_GENERATIONS = {'2018', '2019'}
TARGET_GRADES = {'3', '4', '5', '6'}


def pad(value: int) -> str:
    return str(value).zfill(3)


def source_index(viewer_page: int) -> int:
    return 0 if viewer_page == 1 else viewer_page


def probe(url: str, attempts: int = 2) -> dict[str, object]:
    last_error = ''
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers={'User-Agent': UA, 'Accept': 'image/jpeg,*/*;q=0.1'})
            with urlopen(req, timeout=45) as response:
                body = response.read()
                status = int(getattr(response, 'status', 200))
                content_type = response.headers.get('Content-Type', '')
            return {
                'http_status': status,
                'content_type': content_type,
                'byte_size': len(body),
                'sha256': hashlib.sha256(body).hexdigest(),
                'attempts': attempt,
                'error': '',
            }
        except HTTPError as exc:
            if exc.code == 404:
                return {
                    'http_status': 404,
                    'content_type': exc.headers.get('Content-Type', '') if exc.headers else '',
                    'byte_size': 0,
                    'sha256': '',
                    'attempts': attempt,
                    'error': '',
                }
            last_error = f'HTTPError {exc.code}'
        except (URLError, TimeoutError, OSError) as exc:
            last_error = f'{type(exc).__name__}: {exc}'
        if attempt < attempts:
            time.sleep(attempt)
    return {
        'http_status': '', 'content_type': '', 'byte_size': 0, 'sha256': '',
        'attempts': attempts, 'error': last_error,
    }


def sample_pages(declared: int) -> list[int]:
    # Three non-terminal logical positions: cover, early interior, central interior.
    middle = max(3, declared // 2)
    middle = min(middle, declared - 1)
    pages = [1, 2, middle]
    return list(dict.fromkeys(pages))


def main() -> None:
    contract = json.loads(ROUTE_CONTRACT.read_text(encoding='utf-8'))
    pad_function = contract.get('pad_function') or {}
    pad_snippet = str(pad_function.get('snippet', ''))
    if '.toString()' not in pad_snippet or 'length < 3' not in pad_snippet:
        raise SystemExit('Route contract does not contain the expected three-digit pad() evidence')
    explicit_routes = contract.get('explicit_route_statements') or []
    if not any("'./c/' + ag_clave + '/' + ag_page +'.jpg'" in str(row.get('statement', '')) for row in explicit_routes):
        raise SystemExit('Route contract does not contain the expected ./c/{ag_clave}/{ag_page}.jpg evidence')

    inventory_rows = list(csv.DictReader(INVENTORY.open(encoding='utf-8', newline='')))
    selected = [
        row for row in inventory_rows
        if row['catalog_generation'] in TARGET_GENERATIONS and row['grade_code'] in TARGET_GRADES
        and row['title_core'].lower().startswith('formación cívica')
    ]
    by_generation_grade = {(row['catalog_generation'], row['grade_code']): row for row in selected}
    expected = {(generation, grade) for generation in TARGET_GENERATIONS for grade in TARGET_GRADES}
    missing = expected - set(by_generation_grade)
    if missing:
        raise SystemExit(f'Missing generation/grade controls: {sorted(missing)}')

    rows: list[dict[str, object]] = []
    for generation in ('2018', '2019'):
        for grade in ('3', '4', '5', '6'):
            item = by_generation_grade[(generation, grade)]
            declared = int(item['declared_positions'])
            for viewer_page in sample_pages(declared):
                index = source_index(viewer_page)
                filename = f'{pad(index)}.jpg'
                url = f"{BASE}/{item['ag_clave']}/{filename}"
                result = probe(url)
                rows.append({
                    'probe_version': VERSION,
                    'route_contract_version': contract.get('contract_version', ''),
                    'catalog_generation': generation,
                    'grade_code': grade,
                    'viewer_key': item['viewer_key'],
                    'ag_clave': item['ag_clave'],
                    'declared_positions': declared,
                    'viewer_page': viewer_page,
                    'source_image_index': index,
                    'filename': filename,
                    'source_asset_url': url,
                    **result,
                })

    fieldnames = list(rows[0])
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    grouped: dict[str, Counter] = defaultdict(Counter)
    served_by_generation: Counter = Counter()
    for row in rows:
        generation = str(row['catalog_generation'])
        status = str(row['http_status']) if row['http_status'] != '' else 'error'
        grouped[generation][status] += 1
        if row['http_status'] == 200 and str(row['content_type']).lower().startswith('image/') and int(row['byte_size']) > 0:
            served_by_generation[generation] += 1

    lines = [
        '# LTMD-U1 W7 — conformidad de ruta 2018 frente a control 2019',
        '',
        f'Versión: `{VERSION}`.',
        f'Contrato de ruta aplicado: `{contract.get("contract_version", "")}`.',
        '',
        'Este probe usa exclusivamente la fórmula observada en el código oficial del visor. No prueba aliases, no sustituye claves y no persiste imágenes.',
        '',
        f'- Visores 2018: **4**; posiciones por visor: **3**; solicitudes: **{sum(grouped["2018"].values())}**.',
        f'- Controles 2019: **4**; posiciones por visor: **3**; solicitudes: **{sum(grouped["2019"].values())}**.',
        f'- 2018 HTTP 200 de imagen: **{served_by_generation["2018"]}/{sum(grouped["2018"].values())}**.',
        f'- 2018 HTTP 404: **{grouped["2018"]["404"]}/{sum(grouped["2018"].values())}**.',
        f'- 2019 HTTP 200 de imagen: **{served_by_generation["2019"]}/{sum(grouped["2019"].values())}**.',
        f'- 2019 HTTP 404: **{grouped["2019"]["404"]}/{sum(grouped["2019"].values())}**.',
        '',
        '## Por visor',
        '',
        '| generación | grado | visor | páginas lógicas | estados HTTP |',
        '|---:|---:|---|---|---|',
    ]
    for generation in ('2018', '2019'):
        for grade in ('3', '4', '5', '6'):
            subset = [row for row in rows if row['catalog_generation'] == generation and row['grade_code'] == grade]
            pages = ', '.join(str(row['viewer_page']) for row in subset)
            statuses = ', '.join(str(row['http_status'] or 'error') for row in subset)
            lines.append(f"| {generation} | {grade} | `{subset[0]['viewer_key']}` | {pages} | {statuses} |")

    lines += ['', '## Interpretación', '']
    if served_by_generation['2018'] == 0 and grouped['2018']['404'] == sum(grouped['2018'].values()) and served_by_generation['2019'] == sum(grouped['2019'].values()):
        lines.append('El contraste es consistente con una ruptura o ausencia del subárbol de activos 2018 en la ruta que el propio visor oficial construye, mientras que la misma lógica funciona en los controles 2019. Esto descarta, para este muestreo, un error general de la fórmula de routing implementada por LTMD. No demuestra dónde fueron reubicados los activos 2018 ni autoriza usar 2019 como alias.')
    else:
        lines.append('El patrón no permite todavía clasificar el problema como ausencia específica del subárbol 2018. Deben revisarse los estados individuales antes de ampliar cualquier probe.')
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
