#!/usr/bin/env python3
"""Audit LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1 evidence topology.

The resolver intentionally does not use catalog_generation, but its nine strict
matches are not evidentially homogeneous. This audit verifies every resolved
row against normalized observation/evidence tables and distinguishes:

* cross_page_convergence: statement and school-cycle evidence occur on distinct
  source pages / SHA-256 objects;
* same_page_joint_statement: both observations are supported on the same source
  page / SHA-256 object.

Both are reproducible primary-page evidence; the first provides stronger
cross-page corroboration. The audit also counts cases where the resulting
bibliographic year differs from catalog_generation, demonstrating that the
catalog cohort was not merely copied into the result.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_AUDIT_0.1'
RESOLUTION_VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1'
OBS_VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.2'
RESOLUTION = Path('data/catalog/ltmd_bibliographic_instance_resolution.csv')
OBS = Path('data/catalog/ltmd_bibliographic_observations.csv')
EVIDENCE = Path('data/catalog/ltmd_bibliographic_observation_evidence.csv')
OUT = Path('data/catalog/ltmd_bibliographic_instance_resolution_audit.csv')
REPORT = Path('data/catalog/ltmd_bibliographic_instance_resolution_audit.md')


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def parse_statement_year(value: str) -> int:
    m = re.fullmatch(r'[a-z]+_(?:edition|reprint):((?:19|20)\d{2})', value)
    if not m:
        raise SystemExit(f'cannot parse statement year: {value}')
    return int(m.group(1))


def cycle_start(value: str) -> int:
    m = re.fullmatch(r'((?:19|20)\d{2})-((?:19|20)\d{2})', value)
    if not m:
        raise SystemExit(f'invalid school cycle: {value}')
    first, second = map(int, m.groups())
    if second != first + 1:
        raise SystemExit(f'nonconsecutive school cycle: {value}')
    return first


def main() -> None:
    resolution = read_csv(RESOLUTION)
    observations = read_csv(OBS)
    evidence = read_csv(EVIDENCE)

    if {r['resolution_version'] for r in resolution} != {RESOLUTION_VERSION}:
        raise SystemExit('resolution version drift')
    if {r['observation_version'] for r in observations} != {OBS_VERSION}:
        raise SystemExit('observation version drift')
    if {r['observation_version'] for r in evidence} != {OBS_VERSION}:
        raise SystemExit('evidence version drift')

    obs_by_id = {r['observation_id']: r for r in observations}
    if len(obs_by_id) != len(observations):
        raise SystemExit('duplicate observation ids')
    ev_by_id = defaultdict(list)
    for row in evidence:
        ev_by_id[row['observation_id']].append(row)

    resolved = [r for r in resolution if r['resolution_status'] == 'resolved_cycle_start_exact_match']
    if len(resolved) != 9:
        raise SystemExit(f'expected 9 resolved rows, found {len(resolved)}')

    audit_rows = []
    for row in resolved:
        viewer = row['viewer_key']
        ids = row['supporting_observation_ids'].split(';')
        if len(ids) != 2:
            raise SystemExit(f'{viewer}: expected two supporting observation ids, found {ids}')
        support_obs = [obs_by_id.get(obs_id) for obs_id in ids]
        if any(x is None for x in support_obs):
            raise SystemExit(f'{viewer}: missing supporting observation')
        if any(x['viewer_key'] != viewer for x in support_obs):
            raise SystemExit(f'{viewer}: cross-viewer support leakage')

        cycle_obs = [x for x in support_obs if x['field'] in {'school_cycle', 'school_cycle_statement'}]
        statement_obs = [x for x in support_obs if x['field'] in {
            'edition_history_statement', 'reprint_history_statement', 'reprint_year', 'first_edition_year'
        }]
        if len(cycle_obs) != 1 or len(statement_obs) != 1:
            raise SystemExit(f'{viewer}: malformed statement/cycle support pair')
        cycle_obs = cycle_obs[0]
        statement_obs = statement_obs[0]

        effective = int(row['effective_bibliographic_year'])
        start = cycle_start(row['school_cycle'])
        if effective != start or int(row['school_cycle_start_year']) != start:
            raise SystemExit(f'{viewer}: effective year does not equal cycle start')

        if row['resolved_statement_value'].endswith(tuple(str(y) for y in range(1900, 2100))):
            statement_year = parse_statement_year(row['resolved_statement_value'])
        else:
            raise SystemExit(f'{viewer}: unexpected resolved statement value')
        if statement_year != effective:
            raise SystemExit(f'{viewer}: statement year {statement_year} != effective {effective}')

        statement_ev = ev_by_id.get(statement_obs['observation_id'], [])
        cycle_ev = ev_by_id.get(cycle_obs['observation_id'], [])
        if not statement_ev or not cycle_ev:
            raise SystemExit(f'{viewer}: normalized evidence missing')

        statement_pages = sorted({e['evidence_viewer_page'] for e in statement_ev}, key=int)
        cycle_pages = sorted({e['evidence_viewer_page'] for e in cycle_ev}, key=int)
        statement_shas = sorted({e['evidence_sha256'] for e in statement_ev})
        cycle_shas = sorted({e['evidence_sha256'] for e in cycle_ev})

        page_overlap = sorted(set(statement_pages) & set(cycle_pages), key=int)
        sha_overlap = sorted(set(statement_shas) & set(cycle_shas))
        distinct_page_union = sorted(set(statement_pages) | set(cycle_pages), key=int)
        distinct_sha_union = sorted(set(statement_shas) | set(cycle_shas))

        if set(statement_shas).isdisjoint(cycle_shas):
            topology = 'cross_page_convergence'
            evidence_tier = 'A_cross_page'
        elif page_overlap and sha_overlap:
            topology = 'same_page_joint_statement'
            evidence_tier = 'B_same_page'
        else:
            raise SystemExit(f'{viewer}: unsupported evidence topology')

        catalog_generation = int(row['catalog_generation'])
        differs = effective != catalog_generation
        if 'catalog_generation_not_used' not in row['resolution_rule']:
            raise SystemExit(f'{viewer}: resolution rule does not explicitly exclude catalog_generation')

        # Recompute the union and demand exact agreement with the resolver's
        # published summary rather than trusting it.
        published_pages = sorted(row['evidence_viewer_pages'].split(';'), key=int)
        published_shas = sorted(row['evidence_sha256'].split(';'))
        if published_pages != distinct_page_union:
            raise SystemExit(f'{viewer}: published evidence pages drift')
        if published_shas != distinct_sha_union:
            raise SystemExit(f'{viewer}: published evidence SHA drift')

        audit_rows.append({
            'audit_version': VERSION,
            'viewer_key': viewer,
            'catalog_generation': catalog_generation,
            'school_cycle': row['school_cycle'],
            'effective_bibliographic_year': effective,
            'resolved_statement_value': row['resolved_statement_value'],
            'statement_observation_id': statement_obs['observation_id'],
            'cycle_observation_id': cycle_obs['observation_id'],
            'statement_evidence_pages': ';'.join(statement_pages),
            'cycle_evidence_pages': ';'.join(cycle_pages),
            'shared_evidence_pages': ';'.join(page_overlap),
            'distinct_source_pages': len(distinct_page_union),
            'distinct_source_sha256': len(distinct_sha_union),
            'evidence_topology': topology,
            'evidence_tier': evidence_tier,
            'effective_year_differs_from_catalog_generation': int(differs),
            'catalog_generation_excluded_from_rule': 1,
            'audit_pass': 1,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(audit_rows[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(audit_rows)

    topology = Counter(r['evidence_topology'] for r in audit_rows)
    tiers = Counter(r['evidence_tier'] for r in audit_rows)
    differing = sum(int(r['effective_year_differs_from_catalog_generation']) for r in audit_rows)

    lines = [
        '# LTMD — auditoría de resolución de instancia bibliográfica',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Resoluciones 0.1 auditadas: **{len(audit_rows)}/9**.',
        f'- `audit_pass=1`: **{sum(int(r["audit_pass"]) for r in audit_rows)}/9**.',
        f'- Convergencia entre páginas distintas (`A_cross_page`): **{tiers.get("A_cross_page", 0)}**.',
        f'- Declaración conjunta en la misma página (`B_same_page`): **{tiers.get("B_same_page", 0)}**.',
        f'- Años efectivos que difieren de `catalog_generation`: **{differing}/9**.',
        '',
        'La auditoría confirma que las nueve coincidencias cumplen la regla temporal publicada y que `catalog_generation` está excluido de la resolución. También corrige una posible sobrelectura: **sólo los casos Tier A aportan corroboración entre páginas independientes**; Tier B representa dos declaraciones estructuradas en el mismo activo fuente SHA-verificado.',
        '',
        '## Topología de evidencia',
        '',
        '| objeto | cohorte | año efectivo | declaración | páginas declaración | páginas ciclo | tier | difiere de cohorte |',
        '|---|---:|---:|---|---|---|---|---|',
    ]
    for r in audit_rows:
        lines.append(
            f"| `{r['viewer_key']}` | {r['catalog_generation']} | {r['effective_bibliographic_year']} | "
            f"`{r['resolved_statement_value']}` | `{r['statement_evidence_pages']}` | "
            f"`{r['cycle_evidence_pages']}` | `{r['evidence_tier']}` | "
            f"{'sí' if int(r['effective_year_differs_from_catalog_generation']) else 'no'} |"
        )

    lines += [
        '',
        '## Interpretación permitida',
        '',
        '- `A_cross_page`: candidato de año efectivo con convergencia temporal entre páginas fuente distintas.',
        '- `B_same_page`: candidato de año efectivo derivado de una declaración conjunta edición/reimpresión + ciclo en la misma página fuente.',
        '',
        'En ambos casos la fuente es institucional y SHA-verificada, pero `human_validated=0` sigue aplicando. La auditoría recomienda describir estos resultados como **candidatos bibliográficos resueltos por regla técnica**, no como fechas históricas definitivamente validadas por una persona.',
        '',
        '## Interpretación no permitida',
        '',
        'No usar Tier B como si fuera corroboración entre fuentes independientes. No interpretar que un año efectivo igual a la cohorte del catálogo fue derivado de ella; la regla y las observaciones mantienen esa variable fuera del cálculo. Los 17 objetos no resueltos permanecen sin año efectivo y no deben imputarse.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('audit_version', VERSION)
    print('audited', len(audit_rows))
    print('tier_a_cross_page', tiers.get('A_cross_page', 0))
    print('tier_b_same_page', tiers.get('B_same_page', 0))
    print('differs_from_catalog_generation', differing)


if __name__ == '__main__':
    main()
