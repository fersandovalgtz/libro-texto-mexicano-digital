#!/usr/bin/env python3
"""Resolve a strict subset of LTMD bibliographic instance chronology.

This layer answers a narrower question than the observation layer: when can the
specific served object be assigned an effective bibliographic year/statement
without using `catalog_generation`?

Rule 0.1 is intentionally conservative:
* a school-cycle observation `YYYY-YYYY+1` must exist;
* an edition/reprint observation on the same viewer must carry year `YYYY`;
* exactly one statement may match that cycle-start year;
* H2014P5FCA's custom v0.1 observations are normalized into the same logic;
* catalog_generation is copied only as context and never used in resolution.

If there is no matching statement, or more than one, the object remains
unresolved/ambiguous. This script does not select the maximum edition/year.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1'
OBS_VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.2'
OBS = Path('data/catalog/ltmd_bibliographic_observations.csv')
EVIDENCE = Path('data/catalog/ltmd_bibliographic_observation_evidence.csv')
OUT = Path('data/catalog/ltmd_bibliographic_instance_resolution.csv')
REPORT = Path('data/catalog/ltmd_bibliographic_instance_resolution.md')


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def year_from_history(value: str) -> int | None:
    m = re.fullmatch(r'[a-z]+_(?:edition|reprint):((?:19|20)\d{2})', value)
    return int(m.group(1)) if m else None


def cycle_start(value: str) -> int | None:
    m = re.fullmatch(r'((?:19|20)\d{2})-((?:19|20)\d{2})', value)
    if not m:
        return None
    first, second = map(int, m.groups())
    if second != first + 1:
        return None
    return first


def main() -> None:
    observations = read_csv(OBS)
    if not observations:
        raise SystemExit('bibliographic observation layer is empty')
    if {r['observation_version'] for r in observations} != {OBS_VERSION}:
        raise SystemExit('bibliographic observation version drift')
    evidence = read_csv(EVIDENCE)
    evidence_by_obs = defaultdict(list)
    for row in evidence:
        evidence_by_obs[row['observation_id']].append(row)

    by_viewer = defaultdict(list)
    for row in observations:
        by_viewer[row['viewer_key']].append(row)

    rows_out = []
    for viewer in sorted(by_viewer):
        rows = by_viewer[viewer]
        generations = {r['catalog_generation'] for r in rows}
        if len(generations) != 1:
            raise SystemExit(f'{viewer}: catalog_generation drift inside observations')
        generation = next(iter(generations))

        cycles: list[tuple[str, str, int]] = []
        statements: list[tuple[str, str, str, int]] = []

        for r in rows:
            field = r['field']
            value = r['normalized_value']
            if field in {'school_cycle', 'school_cycle_statement'}:
                start = cycle_start(value)
                if start is not None:
                    cycles.append((r['observation_id'], value, start))
            elif field in {'edition_history_statement', 'reprint_history_statement'}:
                year = year_from_history(value)
                if year is not None:
                    statements.append((r['observation_id'], field, value, year))
            elif viewer == 'H2014P5FCA' and field == 'first_edition_year':
                statements.append((r['observation_id'], 'first_edition_year', f'first_edition:{value}', int(value)))
            elif viewer == 'H2014P5FCA' and field == 'reprint_year':
                # Pair the custom reprint-year observation with its explicit
                # reprint_statement from the same source page.
                statement = next(
                    (x for x in rows if x['field'] == 'reprint_statement'),
                    None,
                )
                if statement is None:
                    raise SystemExit('H2014P5FCA reprint_year lacks reprint_statement')
                statements.append((r['observation_id'], 'reprint_history_statement', f"{statement['normalized_value']}:{value}", int(value)))

        # De-duplicate the same cycle value/statement semantics while retaining
        # one source observation id for traceability.
        cycle_map = {}
        for obs_id, value, start in cycles:
            cycle_map.setdefault((value, start), obs_id)
        statement_map = {}
        for obs_id, field, value, year in statements:
            statement_map.setdefault((field, value, year), obs_id)

        cycle_values = sorted(cycle_map)
        if not cycle_values:
            status = 'unresolved_no_school_cycle'
            cycle_value = ''
            start_year = ''
            matches = []
        elif len(cycle_values) > 1:
            status = 'ambiguous_multiple_school_cycles'
            cycle_value = ';'.join(v for v, _ in cycle_values)
            start_year = ';'.join(str(y) for _, y in cycle_values)
            matches = []
        else:
            cycle_value, start = cycle_values[0]
            start_year = str(start)
            matches = [
                (field, value, year, obs_id)
                for (field, value, year), obs_id in statement_map.items()
                if year == start
            ]
            if len(matches) == 1:
                status = 'resolved_cycle_start_exact_match'
            elif not matches:
                status = 'unresolved_no_statement_matches_cycle_start'
            else:
                status = 'ambiguous_multiple_statements_match_cycle_start'

        if status == 'resolved_cycle_start_exact_match':
            field, statement_value, effective_year, statement_obs_id = matches[0]
            cycle_obs_id = cycle_map[(cycle_value, int(start_year))]
            statement_evidence = evidence_by_obs.get(statement_obs_id, [])
            cycle_evidence = evidence_by_obs.get(cycle_obs_id, [])
            # Custom H2014P5 observations are guaranteed to have evidence rows
            # in 0.2; fail if normalization ever loses them.
            if not statement_evidence or not cycle_evidence:
                raise SystemExit(f'{viewer}: resolved observation lacks normalized evidence')
            source_pages = sorted({r['evidence_viewer_page'] for r in statement_evidence + cycle_evidence}, key=int)
            source_shas = sorted({r['evidence_sha256'] for r in statement_evidence + cycle_evidence})
            resolution_field = field
            resolution_value = statement_value
            effective_year_str = str(effective_year)
            supporting_observation_ids = f'{statement_obs_id};{cycle_obs_id}'
            evidence_pages = ';'.join(source_pages)
            evidence_shas = ';'.join(source_shas)
        else:
            resolution_field = ''
            resolution_value = ''
            effective_year_str = ''
            supporting_observation_ids = ''
            evidence_pages = ''
            evidence_shas = ''

        rows_out.append({
            'resolution_version': VERSION,
            'viewer_key': viewer,
            'catalog_generation': generation,
            'resolution_status': status,
            'school_cycle': cycle_value,
            'school_cycle_start_year': start_year,
            'resolved_statement_field': resolution_field,
            'resolved_statement_value': resolution_value,
            'effective_bibliographic_year': effective_year_str,
            'resolution_rule': (
                'exact_statement_year_equals_school_cycle_start;catalog_generation_not_used'
                if status == 'resolved_cycle_start_exact_match' else ''
            ),
            'supporting_observation_ids': supporting_observation_ids,
            'evidence_viewer_pages': evidence_pages,
            'evidence_sha256': evidence_shas,
            'human_validated': '0',
        })

    if len(rows_out) != 26:
        raise SystemExit(f'expected 26 observed objects, found {len(rows_out)}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows_out[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows_out)

    resolved = [r for r in rows_out if r['resolution_status'] == 'resolved_cycle_start_exact_match']
    statuses = defaultdict(int)
    for row in rows_out:
        statuses[row['resolution_status']] += 1

    lines = [
        '# LTMD — resolución estricta de instancia bibliográfica',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Objetos evaluados: **{len(rows_out)}**.',
        f'- Objetos resueltos por coincidencia exacta declaración↔inicio de ciclo: **{len(resolved)}**.',
        f'- Objetos no resueltos/ambiguos: **{len(rows_out)-len(resolved)}**.',
        '',
        'Regla 0.1: una declaración explícita de edición/reimpresión y un `school_cycle` del mismo objeto deben coincidir exactamente en el año inicial del ciclo. `catalog_generation` no participa. La regla no selecciona el año máximo ni el ordinal máximo.',
        '',
        '## Estados',
        '',
    ]
    for status, count in sorted(statuses.items()):
        lines.append(f'- `{status}`: **{count}**.')

    lines += [
        '',
        '## Objetos resueltos',
        '',
        '| objeto | cohorte catálogo | ciclo | declaración resuelta | año efectivo | evidencia |',
        '|---|---:|---|---|---:|---|',
    ]
    for row in resolved:
        lines.append(
            f"| `{row['viewer_key']}` | {row['catalog_generation']} | `{row['school_cycle']}` | "
            f"`{row['resolved_statement_value']}` | {row['effective_bibliographic_year']} | "
            f"pág. `{row['evidence_viewer_pages']}` |"
        )

    lines += [
        '',
        '## No resueltos',
        '',
        '| objeto | cohorte | estado | ciclo observado |',
        '|---|---:|---|---|',
    ]
    for row in rows_out:
        if row in resolved:
            continue
        lines.append(
            f"| `{row['viewer_key']}` | {row['catalog_generation']} | "
            f"`{row['resolution_status']}` | `{row['school_cycle'] or '—'}` |"
        )

    lines += [
        '',
        '## Límite epistemológico',
        '',
        'Una resolución 0.1 significa que dos declaraciones bibliográficas independientes dentro de la capa observacional convergen temporalmente. No demuestra por sí sola circulación nacional en ese ciclo ni reemplaza validación humana de la transcripción OCR. Los objetos no resueltos permanecen explícitamente sin año efectivo; no se imputan desde la cohorte de catálogo.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    print('objects', len(rows_out))
    print('resolved', len(resolved))
    for row in resolved:
        print(row['viewer_key'], row['effective_bibliographic_year'], row['resolved_statement_value'])


if __name__ == '__main__':
    main()
