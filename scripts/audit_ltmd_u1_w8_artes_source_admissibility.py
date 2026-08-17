#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

VERSION = 'LTMD_U1_W8_ARTES_SOURCE_ADMISSIBILITY_0.1'
WAVE = 'U1-W8-artes'
DOMAIN = 'artes'
EXPECTED = 20

QUEUE = Path('data/catalog/ltmd_u1_wave_queue.csv')
SCOPE = Path('data/catalog/ltmd_u1_w8_scope.csv')
ARCH = Path('data/catalog/ltmd_u1_w8_viewer_architecture.csv')
INVENTORY = Path('data/catalog/ltmd_u1_w8_declared_inventory.csv')
ASSETS = Path('data/catalog/ltmd_u1_w8_artes_asset_summary.csv')
OUT = Path('data/catalog/ltmd_u1_w8_artes_source_admissibility.csv')
REPORT = Path('docs/LTMD_U1_W8_ARTES_SOURCE_ADMISSIBILITY.md')

FIELDS = [
    'admissibility_version', 'book_id', 'viewer_key', 'catalog_generation',
    'grade_code', 'title_core', 'identity_reconciliation_state',
    'source_admissible', 'source_status', 'source_reason',
    'declared_positions', 'source_jpegs', 'terminal_synthetic_candidates',
    'internal_unserved', 'probe_errors', 'direct_asset_ready',
    'semantic_state', 'alias_state', 'source_url',
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def keyed(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row['viewer_key']
        if key in out:
            raise SystemExit(f'W8 admissibility failed: duplicate {label} viewer_key {key}')
        out[key] = row
    return out


def as_int(value: str) -> int:
    return int(value or '0')


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes'}


def main() -> None:
    queue_rows = [
        row for row in read_rows(QUEUE)
        if row['wave_label'] == WAVE and row['operational_domain'] == DOMAIN
    ]
    if len(queue_rows) != EXPECTED:
        raise SystemExit(f'W8 admissibility failed: queue expected {EXPECTED}, got {len(queue_rows)}')

    queue = keyed(queue_rows, 'queue')
    scope = keyed(read_rows(SCOPE), 'scope')
    arch = keyed(read_rows(ARCH), 'architecture')
    inventory = keyed(read_rows(INVENTORY), 'inventory')
    assets = keyed(read_rows(ASSETS), 'asset summary')

    sets = {
        'queue': set(queue),
        'scope': set(scope),
        'architecture': set(arch),
        'inventory': set(inventory),
        'assets': set(assets),
    }
    authority = sets['queue']
    for label, keys in sets.items():
        if keys != authority:
            raise SystemExit(
                'W8 admissibility failed: identity-set drift in '
                f'{label}; missing={sorted(authority - keys)} unexpected={sorted(keys - authority)}'
            )
    if len(authority) != EXPECTED:
        raise SystemExit(f'W8 admissibility failed: expected {EXPECTED} unique identities')

    output: list[dict[str, str | int]] = []
    for key in sorted(authority, key=lambda k: (int(scope[k]['catalog_generation']), int(scope[k]['grade_code']), k)):
        q = queue[key]
        s = scope[key]
        a = arch[key]
        inv = inventory[key]
        asset = assets[key]

        identity_exact = (
            q['viewer_key'] == s['viewer_key'] == a['viewer_key'] == inv['viewer_key'] == asset['viewer_key'] == key
            and inv['ag_clave'] == key
            and asset['ag_clave'] == key
        )
        if not identity_exact:
            raise SystemExit(f'W8 admissibility failed: non-1:1 identity reconciliation for {key}')

        declared = as_int(asset['declared_positions'])
        if declared != as_int(inv['declared_positions']):
            raise SystemExit(f'W8 admissibility failed: declared-position drift for {key}')

        source_jpegs = as_int(asset['source_jpegs'])
        terminal = as_int(asset['terminal_synthetic_candidates'])
        internal = as_int(asset['internal_unserved'])
        probe_errors = as_int(asset['probe_errors'])
        direct_ready = as_bool(asset['direct_asset_ready'])
        standard_arch = as_bool(a['standard_dynamic_architecture']) and as_bool(inv['standard_dynamic_architecture'])

        admissible = (
            identity_exact
            and standard_arch
            and direct_ready
            and source_jpegs > 0
            and internal == 0
            and probe_errors == 0
            and terminal <= 1
        )
        if admissible:
            status = 'SOURCE_ADMISSIBLE'
            reason = 'exact_1_to_1; standard architecture; served source JPEG sequence has no internal gaps or probe errors'
        else:
            status = 'SOURCE_RETAINED'
            reason_parts: list[str] = []
            if not standard_arch:
                reason_parts.append('nonstandard_or_unverified_architecture')
            if source_jpegs == 0:
                reason_parts.append('no_source_jpegs_served')
            if internal:
                reason_parts.append(f'internal_unserved={internal}')
            if probe_errors:
                reason_parts.append(f'probe_errors={probe_errors}')
            if terminal > 1:
                reason_parts.append(f'terminal_synthetic_candidates={terminal}')
            if not direct_ready:
                reason_parts.append('direct_asset_ready=0')
            reason = '; '.join(reason_parts) or 'source gate not satisfied'

        output.append({
            'admissibility_version': VERSION,
            'book_id': key,
            'viewer_key': key,
            'catalog_generation': s['catalog_generation'],
            'grade_code': s['grade_code'],
            'title_core': s['title_core'],
            'identity_reconciliation_state': 'exact_1_to_1',
            'source_admissible': int(admissible),
            'source_status': status,
            'source_reason': reason,
            'declared_positions': declared,
            'source_jpegs': source_jpegs,
            'terminal_synthetic_candidates': terminal,
            'internal_unserved': internal,
            'probe_errors': probe_errors,
            'direct_asset_ready': int(direct_ready),
            'semantic_state': 'WAITING_HUMAN_REFERENCE',
            'alias_state': 'no_alias',
            'source_url': s['source_url'],
        })

    admitted = [row for row in output if row['source_status'] == 'SOURCE_ADMISSIBLE']
    retained = [row for row in output if row['source_status'] == 'SOURCE_RETAINED']
    if len(admitted) != 16 or len(retained) != 4:
        raise SystemExit(
            f'W8 admissibility failed: expected 16 admitted / 4 retained, got {len(admitted)} / {len(retained)}'
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)

    retained_ids = ', '.join(f'`{row["viewer_key"]}`' for row in retained)
    lines = [
        '# LTMD-U1 W8 Artes — compuerta de admisibilidad de fuente',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '## Resultado',
        '',
        f'- Identidades W8 reconciliadas exactamente 1:1: **{len(output)}/{EXPECTED}**.',
        f'- `SOURCE_ADMISSIBLE`: **{len(admitted)}/{EXPECTED}**.',
        f'- `SOURCE_RETAINED`: **{len(retained)}/{EXPECTED}**.',
        '- Alias creados: **0**.',
        '- Estado semántico de las 20 identidades: `WAITING_HUMAN_REFERENCE`.',
        '',
        'Las cinco capas de identidad (cola U1, scope W8, arquitectura, inventario declarado y resumen de activos) deben contener exactamente el mismo conjunto de 20 `viewer_key`; cualquier drift aborta la auditoría.',
        '',
        'Para esta cohorte, `book_id` se materializa como el mismo valor literal de `viewer_key` después de comprobar la reconciliación 1:1. No se infiere ningún alias ni equivalencia histórica.',
        '',
        '## Retenciones de fuente',
        '',
        f'{retained_ids}.',
        '',
        'Los cuatro visores 2018 conservan arquitectura oficial verificable, pero el subtree de activos observado no sirve los JPEG declarados. La retención es de fuente: no se imputa contenido desde 2019 ni desde libros del mismo grado.',
        '',
        '## Regla de admisión',
        '',
        'Una identidad es admisible sólo cuando mantiene reconciliación exacta 1:1, arquitectura dinámica estándar, al menos un JPEG fuente servido, cero huecos internos, cero errores de sondeo, como máximo un candidato terminal sintético y `direct_asset_ready=1`.',
        '',
        'La admisibilidad de fuente es una condición técnica para abrir OCR/FRAGSEG; **no** demuestra independencia semántica, continuidad curricular, equivalencia histórica ni preparación para análisis sustantivo.',
        '',
        'Este gate **no incrementa** por sí mismo la cobertura técnica efectiva global U1. W8 sólo podrá incorporarse a esa cobertura después del procesamiento OCR/FRAGSEG, verificación de integridad, análisis de dependencia por hashes exactos y publicación de la evidencia correspondiente.',
        '',
        'Los activos de terceros se verifican y procesan temporalmente; LTMD no los relicencia ni debe persistir los JPEG fuente en el repositorio.',
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{VERSION}: admitted={len(admitted)} retained={len(retained)}')


if __name__ == '__main__':
    main()
