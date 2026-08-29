#!/usr/bin/env python3
"""Probe W10 official viewer architecture and declared inventory without OCR.

Only the 68 ledger-authorized required_ftrl_processing identities are probed.
The final exception H2014P1ENA remains outside this pipeline. No textbook image
bytes are persisted in this phase.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCOPE = Path('data/catalog/ltmd_u1_w10_scope.csv')
ARCH_OUT = Path('data/catalog/ltmd_u1_w10_viewer_architecture.csv')
INV_OUT = Path('data/catalog/ltmd_u1_w10_declared_inventory.csv')
REPORT = Path('docs/LTMD_U1_W10_SOURCE_ARCHITECTURE.md')
ARCH_VERSION = 'LTMD_U1_W10_ARCHITECTURE_0.1'
INV_VERSION = 'LTMD_U1_W10_DECLARED_INVENTORY_0.1'
EXPECTED_HISTORICAL = 69
EXPECTED_REQUIRED = 68
FINAL_EXCEPTION = 'H2014P1ENA'
CONFIG_URL = 'https://historico.conaliteg.gob.mx/claves.json'
UA = 'LibroTextoMexicanoDigital/U1-W10 source-first architecture probe'


def get_text(url: str, timeout: int = 35) -> tuple[int, str, str]:
    try:
        with urlopen(Request(url, headers={'User-Agent': UA}), timeout=timeout) as response:
            return int(getattr(response, 'status', 200) or 200), response.read().decode('utf-8', 'replace'), ''
    except HTTPError as exc:
        return exc.code, '', f'HTTPError {exc.code}'
    except (URLError, TimeoutError, OSError) as exc:
        return 0, '', f'{type(exc).__name__}: {exc}'


def main() -> None:
    scope = list(csv.DictReader(SCOPE.open(encoding='utf-8', newline='')))
    if len(scope) != EXPECTED_HISTORICAL or len({r['viewer_key'] for r in scope}) != EXPECTED_HISTORICAL:
        raise SystemExit(f'W10 architecture: expected {EXPECTED_HISTORICAL} unique scope rows, got {len(scope)}')
    exceptions = [r for r in scope if r['documentary_disposition'] == 'final_exception']
    if [r['viewer_key'] for r in exceptions] != [FINAL_EXCEPTION]:
        raise SystemExit(f'W10 architecture: exact final exception mismatch: {[r["viewer_key"] for r in exceptions]}')
    required = [r for r in scope if r['documentary_disposition'] == 'required_ftrl_processing' and r['source_probe_eligible'] == '1']
    if len(required) != EXPECTED_REQUIRED:
        raise SystemExit(f'W10 architecture: expected {EXPECTED_REQUIRED} required rows, got {len(required)}')

    cfg_status, cfg_text, cfg_error = get_text(CONFIG_URL, timeout=50)
    if cfg_status != 200 or not cfg_text:
        raise SystemExit(f'W10 architecture: claves.json unavailable status={cfg_status} error={cfg_error}')
    try:
        cfg = json.loads(cfg_text.lstrip('\ufeff'))
    except json.JSONDecodeError as exc:
        raise SystemExit(f'W10 architecture: invalid claves.json: {exc}') from exc
    if not isinstance(cfg, dict):
        raise SystemExit('W10 architecture: claves.json root is not an object')

    arch_rows: list[dict[str, object]] = []
    inv_rows: list[dict[str, object]] = []
    for s in sorted(required, key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), r['viewer_key'])):
        viewer = s['viewer_key']
        html_status, html, html_error = get_text(s['source_url'])
        base = s['source_url'].rsplit('/', 1)[0] + '/'
        x_discovered = int(bool(re.search(r'(?:src=["\'][^"\']*/)?x\.js(?:[?"\'])', html, re.I)) or 'x.js' in html)
        x_status, xjs, x_error = get_text(base + 'x.js') if x_discovered else (0, '', '')
        ag_pages_signal = int('ag_pages' in xjs)
        standard_arch = int(html_status == 200 and x_discovered == 1 and x_status == 200 and ag_pages_signal == 1)

        raw_cfg = cfg.get(viewer)
        config_present = int(isinstance(raw_cfg, dict))
        ag_clave = str(raw_cfg.get('ag_clave', '')) if isinstance(raw_cfg, dict) else ''
        raw_pages = raw_cfg.get('ag_pages') if isinstance(raw_cfg, dict) else None
        declared_positions = 0
        config_error = ''
        if config_present:
            try:
                declared_positions = int(raw_pages)
                if declared_positions <= 0:
                    config_error = f'nonpositive_ag_pages={raw_pages!r}'
                    declared_positions = 0
            except (TypeError, ValueError):
                config_error = f'invalid_ag_pages={raw_pages!r}'
        else:
            config_error = 'viewer_key_missing_from_claves_json'

        exact_ag_clave = int(config_present == 1 and ag_clave == viewer)
        direct_ready = int(
            standard_arch == 1
            and config_present == 1
            and exact_ag_clave == 1
            and declared_positions > 0
        )
        errors = '; '.join(x for x in (html_error, x_error, config_error) if x)

        arch_rows.append({
            'architecture_version': ARCH_VERSION,
            'viewer_key': viewer,
            'catalog_generation': s['catalog_generation'],
            'grade_code': s['grade_code'],
            'title_core': s['title_core'],
            'html_status': html_status,
            'x_js_discovered': x_discovered,
            'x_js_status': x_status,
            'ag_pages_signal': ag_pages_signal,
            'standard_dynamic_architecture': standard_arch,
            'config_present': config_present,
            'config_ag_clave_exact': exact_ag_clave,
            'declared_positions': declared_positions,
            'direct_asset_probe_ready': direct_ready,
            'probe_error': errors,
            'source_url': s['source_url'],
        })
        inv_rows.append({
            'inventory_version': INV_VERSION,
            'viewer_key': viewer,
            'catalog_generation': s['catalog_generation'],
            'grade_code': s['grade_code'],
            'title_core': s['title_core'],
            'ag_clave': ag_clave,
            'declared_positions': declared_positions,
            'standard_dynamic_architecture': standard_arch,
            'config_present': config_present,
            'config_ag_clave_exact': exact_ag_clave,
            'direct_asset_probe_ready': direct_ready,
            'source_url': s['source_url'],
        })

    ARCH_OUT.parent.mkdir(parents=True, exist_ok=True)
    with ARCH_OUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(arch_rows[0]))
        writer.writeheader(); writer.writerows(arch_rows)
    with INV_OUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inv_rows[0]))
        writer.writeheader(); writer.writerows(inv_rows)

    html_counts = Counter(str(r['html_status']) for r in arch_rows)
    standard = sum(int(r['standard_dynamic_architecture']) for r in arch_rows)
    config_present = sum(int(r['config_present']) for r in arch_rows)
    exact_clave = sum(int(r['config_ag_clave_exact']) for r in arch_rows)
    direct_ready = sum(int(r['direct_asset_probe_ready']) for r in arch_rows)
    declared_total = sum(int(r['declared_positions']) for r in arch_rows)
    by_generation: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for r in arch_rows:
        bucket = by_generation[str(r['catalog_generation'])]
        bucket[0] += 1
        bucket[1] += int(r['direct_asset_probe_ready'])
        bucket[2] += int(r['declared_positions'])

    lines = [
        '# LTMD-U1 W10 — arquitectura e inventario declarado source-first', '',
        f'Arquitectura: `{ARCH_VERSION}`. Inventario: `{INV_VERSION}`.', '',
        f'- Identidades históricas W10: **{EXPECTED_HISTORICAL}**.',
        f'- Identidades procesables sondeadas: **{EXPECTED_REQUIRED}**.',
        f'- Excepción final excluida del probe: **1** (`{FINAL_EXCEPTION}`).',
        f'- HTML 200: **{html_counts.get("200", 0)}/{EXPECTED_REQUIRED}**.',
        f'- Arquitectura dinámica estándar: **{standard}/{EXPECTED_REQUIRED}**.',
        f'- Configuración presente en `claves.json`: **{config_present}/{EXPECTED_REQUIRED}**.',
        f'- `ag_clave` exacta 1:1: **{exact_clave}/{EXPECTED_REQUIRED}**.',
        f'- Listos para auditoría directa de activos: **{direct_ready}/{EXPECTED_REQUIRED}**.',
        f'- Posiciones declaradas para casos configurados: **{declared_total:,}**.', '',
        '## Por generación', '',
        '| generación | procesables | listos para activos | posiciones declaradas |',
        '|---:|---:|---:|---:|',
    ]
    for generation, (count, ready, pages) in sorted(by_generation.items(), key=lambda x: int(x[0])):
        lines.append(f'| {generation} | {count} | {ready} | {pages:,} |')
    lines += [
        '', '## Regla epistemológica', '',
        'Esta capa sólo establece arquitectura observable y configuración declarada en fuentes oficiales. Un HTML 200, una entrada en `claves.json` o una cardinalidad declarada no acreditan por sí mismos una fuente admisible.', '',
        'La siguiente capa prueba los activos oficiales exactos posición por posición, computa únicamente hash SHA-256 y tamaño, no persiste imágenes y conserva cualquier 404, hueco o error como evidencia. OCR permanece cerrado.',
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({
        'required': EXPECTED_REQUIRED,
        'html_200': html_counts.get('200', 0),
        'standard_architecture': standard,
        'config_present': config_present,
        'exact_ag_clave': exact_clave,
        'direct_asset_probe_ready': direct_ready,
        'declared_positions_sum': declared_total,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
