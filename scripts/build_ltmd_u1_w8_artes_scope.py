#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

QUEUE = Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT = Path('data/catalog/ltmd_u1_w8_scope.csv')
REPORT = Path('data/catalog/ltmd_u1_w8_scope.md')
VERSION = 'LTMD_U1_W8_SCOPE_0.1'
DOMAIN = 'artes'
WAVE = 'U1-W8-artes'
EXPECTED = 20
FIELDS = ['scope_version','viewer_key','catalog_generation','grade_code','title_core','source_url','operational_domain']

EXPECTED_KEYS = {
    'H2008P2ED259','H2008P5ED279','H2011P1ED295','H2011P2ED302',
    'H2011P3ED309','H2011P4ED317','H2011P5ED327','H2011P6CI337',
    'H2014P3EAA','H2014P4EAA','H2014P5EAA','H2014P6EAA',
    'H2018P3EAA','H2018P4EAA','H2018P5EAA','H2018P6EAA',
    'H2019P3EAA','H2019P4EAA','H2019P5EAA','H2019P6EAA',
}

def fail(message: str) -> None:
    raise SystemExit(f'W8 scope failed: {message}')

def main() -> None:
    rows = [
        r for r in csv.DictReader(QUEUE.open(encoding='utf-8', newline=''))
        if r['wave_label'] == WAVE and r['queue_status'] == 'queued' and r['operational_domain'] == DOMAIN
    ]
    keys = {r['viewer_key'] for r in rows}
    if len(rows) != EXPECTED:
        fail(f'expected {EXPECTED} rows, got {len(rows)}')
    if len(keys) != EXPECTED:
        fail('duplicate viewer keys')
    if keys != EXPECTED_KEYS:
        fail(f'cohort drift: missing={sorted(EXPECTED_KEYS-keys)} unexpected={sorted(keys-EXPECTED_KEYS)}')

    out = [{
        'scope_version': VERSION,
        'viewer_key': r['viewer_key'],
        'catalog_generation': r['catalog_generation'],
        'grade_code': r['grade_code'],
        'title_core': r['title_core'],
        'source_url': r['source_url'],
        'operational_domain': DOMAIN,
    } for r in rows]
    out.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), r['viewer_key']))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(out)

    generations: dict[int, int] = {}
    for row in out:
        generation = int(row['catalog_generation'])
        generations[generation] = generations.get(generation, 0) + 1

    lines = [
        '# LTMD-U1 W8 — alcance congelado Artes', '', f'Versión: `{VERSION}`.', '',
        f'- Visores: **{EXPECTED}**.',
        '- Autoridad: `data/catalog/ltmd_u1_wave_queue.csv`.',
        '- Cohorte protegida además por un conjunto explícito de 20 `viewer_key` para detectar drift.',
        '', '## Por generación', '', '| generación | visores |', '|---:|---:|',
    ]
    for generation, count in sorted(generations.items()):
        lines.append(f'| {generation} | {count} |')
    lines += [
        '',
        '`H2011P6CI337` se conserva literalmente: la cola maestra lo titula `EDUCACIÓN ARTÍSTICA` y lo clasifica en `artes`; el identificador no se reinterpreta por apariencia.',
        '',
        'La etiqueta `artes` es operacional. No constituye por sí misma una ontología curricular ni prueba continuidad semántica entre generaciones.',
        '',
        'Las identidades de catálogo permanecen independientes. Ningún alias se infiere por título, grado, generación, cardinalidad, OCR o similitud visual.',
        '',
        'W8 se abre primero en capas de fuente/arquitectura. OCR productivo permanece cerrado hasta reconciliar inventario declarado, activos, routing y huecos internos.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__ == '__main__':
    main()
