#!/usr/bin/env python3
"""Freeze authoritative LTMD-U1 W10 scope with documentary dispositions."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

QUEUE = Path('data/catalog/ltmd_u1_wave_queue.csv')
LEDGER = Path('data/research/ltmd_u1_ftrl_completion_ledger.csv')
OUT = Path('data/catalog/ltmd_u1_w10_scope.csv')
REPORT = Path('docs/LTMD_U1_W10_FREEZE.md')
VERSION = 'LTMD_U1_W10_INTEGRADOS_SCOPE_0.2'
DOMAIN = 'integrados_multiarea'
WAVE = 'U1-W10-integrados_multiarea'
LEDGER_WAVE = 'W10'
EXPECTED_HISTORICAL = 69
EXPECTED_PROCESSABLE = 68
FINAL_EXCEPTION = 'H2014P1ENA'
FIELDS = [
    'scope_version', 'viewer_key', 'catalog_generation', 'grade_code',
    'title_core', 'source_url', 'operational_domain',
    'documentary_disposition', 'retention_class', 'tracking_issue',
    'source_probe_eligible',
]


def fail(message: str) -> None:
    raise SystemExit(f'W10 scope failed: {message}')


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    queue = [
        r for r in read_rows(QUEUE)
        if r['wave_label'] == WAVE and r['operational_domain'] == DOMAIN
    ]
    ledger = [
        r for r in read_rows(LEDGER)
        if r['wave'] == LEDGER_WAVE and r['operational_domain'] == DOMAIN
    ]
    if len(queue) != EXPECTED_HISTORICAL:
        fail(f'expected {EXPECTED_HISTORICAL} queue rows, got {len(queue)}')
    if len(ledger) != EXPECTED_HISTORICAL:
        fail(f'expected {EXPECTED_HISTORICAL} ledger rows, got {len(ledger)}')

    qkeys = [r['viewer_key'] for r in queue]
    lkeys = [r['viewer_key'] for r in ledger]
    if len(set(qkeys)) != EXPECTED_HISTORICAL or len(set(lkeys)) != EXPECTED_HISTORICAL:
        fail('duplicate viewer keys')
    if set(qkeys) != set(lkeys):
        fail(f'queue/ledger identity drift: queue_only={sorted(set(qkeys)-set(lkeys))} ledger_only={sorted(set(lkeys)-set(qkeys))}')
    if any(not r['source_url'] for r in queue):
        fail('missing source URL in master queue')

    ledger_by = {r['viewer_key']: r for r in ledger}
    dispositions = Counter(r['documentary_disposition'] for r in ledger)
    expected_dispositions = Counter({'required_ftrl_processing': EXPECTED_PROCESSABLE, 'final_exception': 1})
    if dispositions != expected_dispositions:
        fail(f'unexpected documentary dispositions: {dict(dispositions)}')
    exceptions = [r['viewer_key'] for r in ledger if r['documentary_disposition'] == 'final_exception']
    if exceptions != [FINAL_EXCEPTION]:
        fail(f'final exception must be exactly {FINAL_EXCEPTION}, got {exceptions}')
    if any(r['documentary_disposition'] == 'active_retention' for r in ledger):
        fail('W10 must not contain active_retention at G0')

    out = []
    for r in queue:
        lr = ledger_by[r['viewer_key']]
        out.append({
            'scope_version': VERSION,
            'viewer_key': r['viewer_key'],
            'catalog_generation': r['catalog_generation'],
            'grade_code': r['grade_code'],
            'title_core': r['title_core'],
            'source_url': r['source_url'],
            'operational_domain': DOMAIN,
            'documentary_disposition': lr['documentary_disposition'],
            'retention_class': lr.get('retention_class', ''),
            'tracking_issue': lr.get('tracking_issue', ''),
            'source_probe_eligible': int(lr['documentary_disposition'] == 'required_ftrl_processing'),
        })
    out.sort(key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), r['viewer_key']))

    canonical = '\n'.join(
        json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        for r in out
    ) + '\n'
    digest = hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(out)

    historical_generations = Counter(r['catalog_generation'] for r in out)
    processable = [r for r in out if r['source_probe_eligible'] == 1]
    processable_generations = Counter(r['catalog_generation'] for r in processable)
    grades = Counter(r['grade_code'] for r in out)
    exception = next(r for r in out if r['viewer_key'] == FINAL_EXCEPTION)

    lines = [
        '# LTMD-U1 W10 — alcance congelado Integrados/Multiarea', '',
        f'Versión: `{VERSION}`.', '',
        f'- Identidades históricas: **{EXPECTED_HISTORICAL}**.',
        f'- Elegibles para procesamiento/source probe: **{EXPECTED_PROCESSABLE}**.',
        '- Retenciones activas: **0**.',
        f'- Excepciones finales: **1** (`{FINAL_EXCEPTION}`).',
        f'- SHA-256 del snapshot normalizado: `{digest}`.',
        '- Autoridad de pertenencia: `data/catalog/ltmd_u1_wave_queue.csv`.',
        '- Autoridad de disposición documental: `data/research/ltmd_u1_ftrl_completion_ledger.csv`.',
        '- Dominio operacional: `integrados_multiarea`.',
        '- Estado semántico: `WAITING_HUMAN_REFERENCE`.', '',
        '## Excepción final', '',
        f"`{FINAL_EXCEPTION}` conserva `documentary_disposition=final_exception`, `retention_class={exception['retention_class']}` y seguimiento en issue `{exception['tracking_issue']}`. No entra al probe productivo W10 ni se sustituye por una edición, clave, título o secuencia parecida.", '',
        '## Distribución histórica por generación de catálogo',
    ]
    for generation, count in sorted(historical_generations.items(), key=lambda x: int(x[0])):
        lines.append(f'- {generation}: **{count}** identidades.')
    lines += ['', '## Distribución procesable por generación de catálogo']
    for generation, count in sorted(processable_generations.items(), key=lambda x: int(x[0])):
        lines.append(f'- {generation}: **{count}** identidades.')
    lines += ['', '## Distribución histórica por grado']
    for grade, count in sorted(grades.items(), key=lambda x: int(x[0])):
        lines.append(f'- grado {grade}: **{count}** identidades.')
    lines += ['', '## Identidades congeladas']
    for r in out:
        marker = ' — **EXCEPCIÓN FINAL**' if r['viewer_key'] == FINAL_EXCEPTION else ''
        lines.append(
            f"- `{r['viewer_key']}` — catálogo {r['catalog_generation']}, grado {r['grade_code']} — {r['title_core']} — `{r['documentary_disposition']}`{marker}."
        )
    lines += [
        '', '## Reglas de apertura', '',
        '1. La pertenencia a W10 procede exclusivamente de la cola maestra; no se reconstruye a partir del prefijo del identificador ni del título.',
        '2. La elegibilidad de procesamiento procede exclusivamente del ledger canónico y no reabre excepciones finales ya cerradas documentalmente.',
        '3. Ninguna coincidencia de título, grado, generación, cardinalidad, OCR o apariencia visual autoriza un alias.',
        '4. La siguiente fase es estrictamente `source-first`: arquitectura/configuración → inventario declarado → auditoría de activos → admisibilidad → topología canónica.',
        '5. No se autoriza OCR, PAGESTRUCT ni FRAGSEG para una identidad hasta que su fuente haya superado la compuerta de admisibilidad correspondiente.',
        '6. Las ausencias, huecos o rutas no servidas se conservan como resultados; no se imputan.',
        '7. W10 no modifica la cobertura técnica efectiva de U1 por el solo hecho de congelar el alcance.', '',
        'Este documento fija G0. Cualquier cambio posterior del universo W10 o de sus disposiciones requiere una nueva versión explícita y evidencia documental.',
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({
        'historical_identities': EXPECTED_HISTORICAL,
        'source_probe_eligible': EXPECTED_PROCESSABLE,
        'final_exception': FINAL_EXCEPTION,
        'snapshot_sha256': digest,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
