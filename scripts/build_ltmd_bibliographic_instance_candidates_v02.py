#!/usr/bin/env python3
"""Build LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.2 directly from observations 0.3.

This supersedes the interpretive role of the earlier resolution/candidate 0.1
chain. It derives candidates only from LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.3 and
its normalized evidence table.

Candidate rule:
* exactly one valid school-cycle value for the viewer;
* exactly one edition/reprint statement whose year equals cycle start;
* catalog_generation is never used in derivation;
* evidence topology is recorded explicitly:
  A = disjoint statement/cycle source pages;
  B = joint source page plus additional corroborating page(s);
  C = joint same-page evidence only.

All candidates remain technical and human_validated=0.
"""
from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.2'
OBS_VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.3'
OBS = Path('data/catalog/ltmd_bibliographic_observations.csv')
EVIDENCE = Path('data/catalog/ltmd_bibliographic_observation_evidence.csv')
OUT = Path('data/catalog/ltmd_bibliographic_instance_candidates.csv')
REPORT = Path('data/catalog/ltmd_bibliographic_instance_candidates.md')


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def cycle_start(value: str) -> int | None:
    m = re.fullmatch(r'((?:19|20)\d{2})-((?:19|20)\d{2})', value)
    if not m:
        return None
    first, second = map(int, m.groups())
    return first if second == first + 1 else None


def history_year(value: str) -> int | None:
    m = re.fullmatch(r'[a-z]+_(?:edition|reprint):((?:19|20)\d{2})', value)
    return int(m.group(1)) if m else None


def main() -> None:
    observations = read_csv(OBS)
    evidence = read_csv(EVIDENCE)
    if {r['observation_version'] for r in observations} != {OBS_VERSION}:
        raise SystemExit('observation version drift')
    if {r['observation_version'] for r in evidence} != {OBS_VERSION}:
        raise SystemExit('evidence version drift')
    if len(observations) != 95 or len(evidence) != 97:
        raise SystemExit(
            f'observation/evidence cardinality drift: {len(observations)}/{len(evidence)}'
        )

    ev_by_obs = defaultdict(list)
    for row in evidence:
        ev_by_obs[row['observation_id']].append(row)
    by_viewer = defaultdict(list)
    for row in observations:
        by_viewer[row['viewer_key']].append(row)
    if len(by_viewer) != 26:
        raise SystemExit(f'expected 26 observed objects, found {len(by_viewer)}')

    rows_out = []
    for viewer in sorted(by_viewer):
        rows = by_viewer[viewer]
        generations = {r['catalog_generation'] for r in rows}
        if len(generations) != 1:
            raise SystemExit(f'{viewer}: catalog_generation drift')
        generation = next(iter(generations))

        cycles: dict[str, str] = {}
        statements: dict[tuple[str, str, int], str] = {}
        custom_reprint_statement = next(
            (r['normalized_value'] for r in rows if r['field'] == 'reprint_statement'),
            None,
        )

        for r in rows:
            field = r['field']
            value = r['normalized_value']
            if field in {'school_cycle', 'school_cycle_statement'}:
                start = cycle_start(value)
                if start is not None:
                    cycles.setdefault(value, r['observation_id'])
            elif field in {'edition_history_statement', 'reprint_history_statement'}:
                year = history_year(value)
                if year is not None:
                    statements.setdefault((field, value, year), r['observation_id'])
            elif field == 'first_edition_year':
                year = int(value)
                normalized = f'first_edition:{year}'
                statements.setdefault(('edition_history_statement', normalized, year), r['observation_id'])
            elif field == 'reprint_year' and custom_reprint_statement:
                year = int(value)
                normalized = f'{custom_reprint_statement}:{year}'
                statements.setdefault(('reprint_history_statement', normalized, year), r['observation_id'])

        if not cycles:
            status = 'no_candidate_no_school_cycle'
            cycle_value = ''
            candidate = None
        elif len(cycles) > 1:
            status = 'no_candidate_ambiguous_multiple_school_cycles'
            cycle_value = ';'.join(sorted(cycles))
            candidate = None
        else:
            cycle_value = next(iter(cycles))
            start = cycle_start(cycle_value)
            assert start is not None
            matches = [
                (field, value, year, obs_id)
                for (field, value, year), obs_id in statements.items()
                if year == start
            ]
            if not matches:
                status = 'no_candidate_no_statement_matches_cycle_start'
                candidate = None
            elif len(matches) > 1:
                status = 'no_candidate_ambiguous_multiple_statements_match_cycle_start'
                candidate = None
            else:
                status = 'technical_candidate_exact_cycle_start_match'
                candidate = matches[0]

        if candidate is None:
            rows_out.append({
                'candidate_version': VERSION,
                'viewer_key': viewer,
                'catalog_generation': generation,
                'candidate_status': status,
                'evidence_tier': '',
                'school_cycle': cycle_value,
                'candidate_bibliographic_year': '',
                'candidate_statement_field': '',
                'candidate_statement_value': '',
                'statement_evidence_pages': '',
                'cycle_evidence_pages': '',
                'evidence_sha256': '',
                'catalog_generation_excluded_from_rule': '1',
                'candidate_year_differs_from_catalog_generation': '',
                'human_validated': '0',
                'historical_validation_status': 'no_strict_candidate',
            })
            continue

        field, value, year, statement_obs_id = candidate
        cycle_obs_id = cycles[cycle_value]
        statement_ev = ev_by_obs.get(statement_obs_id, [])
        cycle_ev = ev_by_obs.get(cycle_obs_id, [])
        if not statement_ev or not cycle_ev:
            raise SystemExit(f'{viewer}: candidate lacks normalized evidence')
        statement_pages = {e['evidence_viewer_page'] for e in statement_ev}
        cycle_pages = {e['evidence_viewer_page'] for e in cycle_ev}
        statement_shas = {e['evidence_sha256'] for e in statement_ev}
        cycle_shas = {e['evidence_sha256'] for e in cycle_ev}
        shared_pages = statement_pages & cycle_pages
        all_pages = statement_pages | cycle_pages
        all_shas = statement_shas | cycle_shas
        if not shared_pages:
            tier = 'A_cross_page_independent'
            candidate_status = 'candidate_cross_page_independent_match'
        elif all_pages - shared_pages:
            tier = 'B_joint_plus_extra_page_corroboration'
            candidate_status = 'candidate_joint_match_with_extra_page_corroboration'
        else:
            tier = 'C_joint_same_page_only'
            candidate_status = 'candidate_joint_same_page_match'

        rows_out.append({
            'candidate_version': VERSION,
            'viewer_key': viewer,
            'catalog_generation': generation,
            'candidate_status': candidate_status,
            'evidence_tier': tier,
            'school_cycle': cycle_value,
            'candidate_bibliographic_year': str(year),
            'candidate_statement_field': field,
            'candidate_statement_value': value,
            'statement_evidence_pages': ';'.join(sorted(statement_pages, key=int)),
            'cycle_evidence_pages': ';'.join(sorted(cycle_pages, key=int)),
            'evidence_sha256': ';'.join(sorted(all_shas)),
            'catalog_generation_excluded_from_rule': '1',
            'candidate_year_differs_from_catalog_generation': str(int(year != int(generation))),
            'human_validated': '0',
            'historical_validation_status': 'technical_candidate_not_human_validated',
        })

    if len(rows_out) != 26:
        raise SystemExit(f'expected 26 candidate rows, found {len(rows_out)}')
    candidates = [r for r in rows_out if r['candidate_bibliographic_year']]
    tiers = Counter(r['evidence_tier'] for r in candidates)
    statuses = Counter(r['candidate_status'] for r in rows_out)

    # Frozen expected outcome after the narrow 0.3 recovery. These invariants
    # protect against silent future broadening of OCR normalization.
    if len(candidates) != 11:
        raise SystemExit(f'expected 11 technical candidates, found {len(candidates)}')
    if tiers.get('A_cross_page_independent', 0) != 0:
        raise SystemExit('unexpected Tier A evidence; review before publication')
    if tiers.get('B_joint_plus_extra_page_corroboration', 0) != 2:
        raise SystemExit(f'expected 2 Tier B candidates, found {tiers}')
    if tiers.get('C_joint_same_page_only', 0) != 9:
        raise SystemExit(f'expected 9 Tier C candidates, found {tiers}')
    if statuses.get('no_candidate_no_statement_matches_cycle_start', 0) != 3:
        raise SystemExit(f'expected 3 cycle-known unmatched objects, found {statuses}')
    if statuses.get('no_candidate_no_school_cycle', 0) != 12:
        raise SystemExit(f'expected 12 objects without school cycle, found {statuses}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows_out[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows_out)

    differs = sum(int(r['candidate_year_differs_from_catalog_generation']) for r in candidates)
    lines = [
        '# LTMD — candidatos de instancia bibliográfica',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Objetos evaluados: **{len(rows_out)}**.',
        f'- Candidatos técnicos con año: **{len(candidates)}**.',
        f'- Sin candidato estricto: **{len(rows_out)-len(candidates)}**.',
        f'- Tier A, páginas independientes: **{tiers.get("A_cross_page_independent", 0)}**.',
        f'- Tier B, declaración conjunta + página corroborante adicional: **{tiers.get("B_joint_plus_extra_page_corroboration", 0)}**.',
        f'- Tier C, declaración conjunta en una sola página: **{tiers.get("C_joint_same_page_only", 0)}**.',
        f'- Candidatos cuyo año difiere de `catalog_generation`: **{differs}/{len(candidates)}**.',
        '',
        '0.2 se reconstruye directamente desde `LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.3`; ya no depende de la tabla de “resolution” 0.1. Las dos recuperaciones OCR estrechas incorporadas en Observaciones 0.3 elevan la cobertura de **9 a 11** candidatos sin cambiar la regla temporal.',
        '',
        '## Candidatos',
        '',
        '| objeto | cohorte | ciclo | declaración | año candidato | tier | difiere de cohorte |',
        '|---|---:|---|---|---:|---|---|',
    ]
    for r in candidates:
        lines.append(
            f"| `{r['viewer_key']}` | {r['catalog_generation']} | `{r['school_cycle']}` | "
            f"`{r['candidate_statement_value']}` | {r['candidate_bibliographic_year']} | "
            f"`{r['evidence_tier']}` | "
            f"{'sí' if r['candidate_year_differs_from_catalog_generation'] == '1' else 'no'} |"
        )
    lines += [
        '',
        '## Sin candidato estricto',
        '',
        '| objeto | cohorte | estado | ciclo observado |',
        '|---|---:|---|---|',
    ]
    for r in rows_out:
        if r['candidate_bibliographic_year']:
            continue
        lines.append(
            f"| `{r['viewer_key']}` | {r['catalog_generation']} | `{r['candidate_status']}` | "
            f"`{r['school_cycle'] or '—'}` |"
        )
    lines += [
        '',
        '## Interpretación',
        '',
        'Estos años son **candidatos técnicos de cronología de ejemplar**, no fechas humanas validadas. Tier B incluye una página adicional que corrobora parte de la declaración temporal; Tier C no. Actualmente no existe ningún Tier A con declaración editorial y ciclo respaldados por páginas completamente independientes.',
        '',
        'Los 15 objetos sin candidato permanecen sin año efectivo. En particular, tres tienen ciclo escolar pero ninguna declaración editorial/reimpresión compatible aun después de la recuperación OCR estrecha; doce carecen de ciclo escolar fuerte en la ventana bibliográfica auditada.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    print('objects', len(rows_out))
    print('candidates', len(candidates))
    print('tier_a', tiers.get('A_cross_page_independent', 0))
    print('tier_b', tiers.get('B_joint_plus_extra_page_corroboration', 0))
    print('tier_c', tiers.get('C_joint_same_page_only', 0))
    print('differs_from_catalog_generation', differs)


if __name__ == '__main__':
    main()
