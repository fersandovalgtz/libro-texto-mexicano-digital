#!/usr/bin/env python3
"""Build the LTMD-U1 W7 source-admissibility gate for productive OCR.

The gate is offline and conservative. A viewer is OCR-admitted only when the
published asset audit marks it `direct_asset_ready=1`. The five excluded viewers
are retained with evidence-backed causes: one isolated 2014 internal gap and
four 2018 viewers whose exact official route was independently reconfirmed as
404 while same-grade 2019 controls returned 200.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

SUMMARY = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_summary.csv')
CONFORMANCE = Path('data/catalog/ltmd_u1_w7_2018_route_conformance.csv')
OUT_CSV = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
OUT_MD = Path('data/catalog/ltmd_u1_w7_source_admissibility.md')
VERSION = 'LTMD_U1_W7_SOURCE_ADMISSIBILITY_0.1'
EXPECTED_VIEWERS = 30
EXPECTED_ADMITTED = 25
EXPECTED_WITHHELD = 5


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def fail(message: str) -> None:
    raise SystemExit(f'W7 source admissibility failed: {message}')


def main() -> None:
    summary = read_csv(SUMMARY)
    conformance = read_csv(CONFORMANCE)
    if len(summary) != EXPECTED_VIEWERS:
        fail(f'asset summary has {len(summary)} viewers, expected {EXPECTED_VIEWERS}')

    conf_by_viewer: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in conformance:
        conf_by_viewer[row['viewer_key']].append(row)

    # Conformance must cover exactly the four 2018 problem viewers and four 2019 controls,
    # three positions each.
    if len(conformance) != 24:
        fail(f'route conformance has {len(conformance)} rows, expected 24')
    target_2018 = {row['viewer_key'] for row in conformance if row['catalog_generation'] == '2018'}
    if target_2018 != {'H2018P3FCA', 'H2018P4FCA', 'H2018P5FCA', 'H2018P6FCA'}:
        fail(f'unexpected 2018 conformance viewer set: {sorted(target_2018)}')
    for key in target_2018:
        rows = conf_by_viewer[key]
        if len(rows) != 3 or any(row['http_status'] != '404' for row in rows):
            fail(f'{key} does not have the expected 3/3 exact-route 404 evidence')
    controls = [row for row in conformance if row['catalog_generation'] == '2019']
    if len(controls) != 12 or any(row['http_status'] != '200' for row in controls):
        fail('2019 route controls are not 12/12 HTTP 200')

    output: list[dict[str, str]] = []
    for row in summary:
        ready = row['direct_asset_ready'] == '1'
        key = row['viewer_key']
        generation = row['catalog_generation']
        internal = int(row['internal_unserved'])
        served = int(row['source_jpegs'])
        declared = int(row['declared_positions'])

        if ready:
            decision = 'ocr_source_admitted'
            admitted = '1'
            reason_code = 'direct_asset_ready'
            evidence = (
                f'asset_audit: source_jpegs={served}; internal_unserved={internal}; '
                f'direct_asset_ready=1'
            )
        elif key == 'H2014P5FCA':
            if generation != '2014' or internal != 1 or served != 224 or declared != 225:
                fail(f'{key} isolated-gap invariants drifted')
            decision = 'withheld_source_gap'
            admitted = '0'
            reason_code = 'isolated_internal_unserved'
            evidence = 'asset_audit: source_jpegs=224/225; internal_unserved=1; exact missing position unresolved'
        elif key in target_2018:
            if generation != '2018' or served != 0 or internal <= 0:
                fail(f'{key} 2018 source-unavailable invariants drifted')
            decision = 'withheld_source_subtree_unserved'
            admitted = '0'
            reason_code = 'official_route_sample_3of3_404'
            evidence = (
                f'asset_audit: source_jpegs=0/{declared}; internal_unserved={internal}; '
                'route_conformance: 3/3 sampled official routes HTTP 404; matched-grade 2019 controls 12/12 HTTP 200'
            )
        else:
            fail(f'unclassified non-ready viewer {key}')

        output.append({
            'gate_version': VERSION,
            'viewer_key': key,
            'catalog_generation': generation,
            'grade_code': row['grade_code'],
            'title_core': row['title_core'],
            'declared_positions': row['declared_positions'],
            'source_jpegs': row['source_jpegs'],
            'internal_unserved': row['internal_unserved'],
            'direct_asset_ready': row['direct_asset_ready'],
            'ocr_source_admitted': admitted,
            'decision': decision,
            'reason_code': reason_code,
            'evidence': evidence,
        })

    decisions = Counter(row['decision'] for row in output)
    admitted_rows = [row for row in output if row['ocr_source_admitted'] == '1']
    withheld_rows = [row for row in output if row['ocr_source_admitted'] == '0']
    if len(admitted_rows) != EXPECTED_ADMITTED:
        fail(f'admitted viewers {len(admitted_rows)} != {EXPECTED_ADMITTED}')
    if len(withheld_rows) != EXPECTED_WITHHELD:
        fail(f'withheld viewers {len(withheld_rows)} != {EXPECTED_WITHHELD}')

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)

    by_generation: dict[str, Counter] = defaultdict(Counter)
    for row in output:
        by_generation[row['catalog_generation']]['total'] += 1
        by_generation[row['catalog_generation']]['admitted'] += int(row['ocr_source_admitted'])
        by_generation[row['catalog_generation']]['withheld'] += int(row['ocr_source_admitted'] == '0')

    lines = [
        '# LTMD-U1 W7 — gate de admisibilidad de fuente para OCR',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Este gate separa la integridad del alcance histórico de la disponibilidad técnica de fuente. No elimina visores del corpus W7: decide únicamente cuáles pueden entrar al OCR productivo sin sustitución heurística.',
        '',
        f'- Visores W7: **{len(output)}**.',
        f'- Admitidos para OCR de fuente: **{len(admitted_rows)}/{len(output)}**.',
        f'- Retenidos por evidencia de fuente incompleta/no servida: **{len(withheld_rows)}/{len(output)}**.',
        f'- Retenido por hueco interno aislado 2014: **{decisions["withheld_source_gap"]}**.',
        f'- Retenidos por subárbol oficial 2018 no servido: **{decisions["withheld_source_subtree_unserved"]}**.',
        '',
        '## Por generación',
        '',
        '| generación | visores | admitidos | retenidos |',
        '|---:|---:|---:|---:|',
    ]
    for generation in sorted(by_generation, key=int):
        counts = by_generation[generation]
        lines.append(f"| {generation} | {counts['total']} | {counts['admitted']} | {counts['withheld']} |")

    lines += [
        '',
        '## Visores retenidos',
        '',
        '| visor | generación | grado | decisión | causa |',
        '|---|---:|---:|---|---|',
    ]
    for row in withheld_rows:
        lines.append(
            f"| `{row['viewer_key']}` | {row['catalog_generation']} | {row['grade_code']} | "
            f"`{row['decision']}` | `{row['reason_code']}` |"
        )

    lines += [
        '',
        '## Regla de operación',
        '',
        'El OCR productivo W7 puede ejecutarse únicamente sobre filas con `ocr_source_admitted=1`. Los cinco visores retenidos conservan su identidad de catálogo y permanecen dentro del alcance científico W7, pero no pueden ser sustituidos por ediciones 2019 ni por otras claves sin evidencia documental/criptográfica independiente.',
        '',
        'Este gate autoriza una cohorte técnica parcial; no declara W7 históricamente completo ni convierte ausencia de fuente en ausencia de obra.',
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_MD.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
