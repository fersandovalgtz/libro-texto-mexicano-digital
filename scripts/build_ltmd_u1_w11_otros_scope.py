#!/usr/bin/env python3
"""Freeze the authoritative LTMD-U1 W11 residual cohort from the master queue."""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path

QUEUE = Path('data/catalog/ltmd_u1_wave_queue.csv')
OUT = Path('data/catalog/ltmd_u1_w11_scope.csv')
REPORT = Path('docs/LTMD_U1_W11_FREEZE.md')
VERSION = 'LTMD_U1_W11_OTROS_SCOPE_0.1'
DOMAIN = 'otros_no_clasificados'
WAVE = 'U1-W11-otros_no_clasificados'
EXPECTED = 111
FIELDS = ['scope_version','viewer_key','catalog_generation','grade_code','title_core','source_url','operational_domain']

def fail(message: str) -> None:
    raise SystemExit(f'W11 scope failed: {message}')

def main() -> None:
    queue = list(csv.DictReader(QUEUE.open(encoding='utf-8', newline='')))
    rows = [r for r in queue if r['wave_label'] == WAVE and r['operational_domain'] == DOMAIN]
    keys = [r['viewer_key'] for r in rows]
    if len(rows) != EXPECTED:
        fail(f'expected {EXPECTED} rows, got {len(rows)}')
    if len(set(keys)) != EXPECTED:
        fail('duplicate viewer keys')
    if any(not r['source_url'] for r in rows):
        fail('missing source URL in master queue')
    out = [
        {
            'scope_version': VERSION,
            'viewer_key': r['viewer_key'],
            'catalog_generation': r['catalog_generation'],
            'grade_code': r['grade_code'],
            'title_core': r['title_core'],
            'source_url': r['source_url'],
            'operational_domain': DOMAIN,
        }
        for r in rows
    ]
    out.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), r['viewer_key']))
    canonical = '\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(',', ':')) for r in out) + '\n'
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(out)
    generations = Counter(r['catalog_generation'] for r in out)
    grades = Counter(r['grade_code'] for r in out)
    lines = [
        '# LTMD-U1 W11 — alcance congelado Otros/No clasificados', '',
        f'Versión: `{VERSION}`.', '',
        f'- Identidades congeladas: **{EXPECTED}/{EXPECTED}**.',
        f'- SHA-256 del snapshot normalizado: `{digest}`.',
        '- Autoridad de origen: `data/catalog/ltmd_u1_wave_queue.csv`.',
        '- Dominio operacional: `otros_no_clasificados`.',
        '- Estado semántico: `WAITING_HUMAN_REFERENCE`.', '',
        '## Distribución por generación de catálogo'
    ]
    for g, n in sorted(generations.items(), key=lambda x: int(x[0])):
        lines.append(f'- {g}: **{n}** identidades.')
    lines += ['', '## Distribución por grado']
    for g, n in sorted(grades.items(), key=lambda x: int(x[0])):
        lines.append(f'- grado {g}: **{n}** identidades.')
    lines += ['', '## Identidades congeladas']
    for r in out:
        lines.append(f"- `{r['viewer_key']}` — catálogo {r['catalog_generation']}, grado {r['grade_code']} — {r['title_core']}.")
    lines += [
        '', '## Reglas de apertura', '',
        '1. La pertenencia a W11 procede exclusivamente de la cola maestra; no se reconstruye a partir de prefijos, títulos ni materias aparentes.',
        '2. `otros_no_clasificados` es una categoría operacional residual, no una categoría histórica, curricular ni semántica.',
        '3. Antes de construir un pipeline común se auditarán heterogeneidad documental, arquitectura del visor y configuración de fuente.',
        '4. Ninguna coincidencia de título, grado, generación, cardinalidad, OCR o apariencia visual autoriza un alias.',
        '5. No se autoriza OCR, PAGESTRUCT ni FRAGSEG hasta superar una compuerta de fuente explícita.',
        '6. Las ausencias, huecos, arquitecturas no estándar y rutas no servidas se conservan como resultados; no se imputan.',
        '7. W11 no modifica la cobertura técnica efectiva de U1 por el solo congelamiento del alcance.', '',
        'Este documento fija G0. La siguiente decisión debe basarse en evidencia de heterogeneidad y arquitectura, no en conveniencia de procesamiento.'
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))

if __name__ == '__main__':
    main()
