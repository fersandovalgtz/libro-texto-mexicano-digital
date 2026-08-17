#!/usr/bin/env python3
"""Build a publication-safe bibliographic instance candidate layer.

This layer supersedes the *interpretation* (not the audit trail) of
LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1. The resolution algorithm found nine
exact year matches between an edition/reprint statement and the start of a
school cycle, but the evidence-topology audit showed all nine share at least one
source page. Therefore they are preserved as technically resolved *candidates*,
not as definitively validated historical dates.

Evidence tiers:
* A_cross_page_independent: statement and cycle evidence occur on disjoint pages
  (none in the current cohort);
* B_joint_plus_extra_cycle_page: statement/cycle co-occur on one page and the
  cycle is additionally observed on another page;
* C_joint_same_page_only: the match is supported only by joint declarations on
  the same source page.

`catalog_generation` is context only and never enters candidate derivation.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.1'
RESOLUTION_VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1'
AUDIT_VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_AUDIT_0.1'
RESOLUTION = Path('data/catalog/ltmd_bibliographic_instance_resolution.csv')
AUDIT = Path('data/catalog/ltmd_bibliographic_instance_resolution_audit.csv')
OUT = Path('data/catalog/ltmd_bibliographic_instance_candidates.csv')
REPORT = Path('data/catalog/ltmd_bibliographic_instance_candidates.md')


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def split_semicolon(value: str) -> set[str]:
    return {v for v in value.split(';') if v}


def main() -> None:
    resolution = read_csv(RESOLUTION)
    audit = read_csv(AUDIT)
    if {r['resolution_version'] for r in resolution} != {RESOLUTION_VERSION}:
        raise SystemExit('resolution version drift')
    if {r['audit_version'] for r in audit} != {AUDIT_VERSION}:
        raise SystemExit('audit version drift')
    audit_by_viewer = {r['viewer_key']: r for r in audit}
    if len(audit_by_viewer) != 9 or any(r.get('audit_pass') != '1' for r in audit):
        raise SystemExit('instance-resolution audit is incomplete or failing')

    rows_out = []
    for row in resolution:
        viewer = row['viewer_key']
        if row['resolution_status'] == 'resolved_cycle_start_exact_match':
            a = audit_by_viewer.get(viewer)
            if a is None:
                raise SystemExit(f'{viewer}: resolved row lacks audit')
            statement_pages = split_semicolon(a['statement_evidence_pages'])
            cycle_pages = split_semicolon(a['cycle_evidence_pages'])
            shared = statement_pages & cycle_pages
            if not shared:
                tier = 'A_cross_page_independent'
                candidate_status = 'candidate_cross_page_independent_match'
            elif cycle_pages - shared:
                tier = 'B_joint_plus_extra_cycle_page'
                candidate_status = 'candidate_joint_match_with_cycle_corroboration'
            else:
                tier = 'C_joint_same_page_only'
                candidate_status = 'candidate_joint_same_page_match'

            rows_out.append({
                'candidate_version': VERSION,
                'viewer_key': viewer,
                'catalog_generation': row['catalog_generation'],
                'candidate_status': candidate_status,
                'evidence_tier': tier,
                'school_cycle': row['school_cycle'],
                'candidate_bibliographic_year': row['effective_bibliographic_year'],
                'candidate_statement_field': row['resolved_statement_field'],
                'candidate_statement_value': row['resolved_statement_value'],
                'statement_evidence_pages': a['statement_evidence_pages'],
                'cycle_evidence_pages': a['cycle_evidence_pages'],
                'evidence_sha256': row['evidence_sha256'],
                'catalog_generation_excluded_from_rule': '1',
                'candidate_year_differs_from_catalog_generation': a['effective_year_differs_from_catalog_generation'],
                'human_validated': '0',
                'historical_validation_status': 'technical_candidate_not_human_validated',
            })
        else:
            if viewer in audit_by_viewer:
                raise SystemExit(f'{viewer}: unresolved row unexpectedly present in resolved audit')
            rows_out.append({
                'candidate_version': VERSION,
                'viewer_key': viewer,
                'catalog_generation': row['catalog_generation'],
                'candidate_status': row['resolution_status'].replace('unresolved_', 'no_candidate_'),
                'evidence_tier': '',
                'school_cycle': row['school_cycle'],
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

    if len(rows_out) != 26:
        raise SystemExit(f'expected 26 objects, found {len(rows_out)}')
    candidates = [r for r in rows_out if r['candidate_bibliographic_year']]
    if len(candidates) != 9:
        raise SystemExit(f'expected 9 technical candidates, found {len(candidates)}')
    tiers = Counter(r['evidence_tier'] for r in candidates)
    if tiers.get('A_cross_page_independent', 0) != 0:
        raise SystemExit('current audit unexpectedly contains Tier A; review interpretation before publishing')
    if tiers.get('B_joint_plus_extra_cycle_page', 0) != 2:
        raise SystemExit(f'expected 2 Tier B candidates, found {tiers.get("B_joint_plus_extra_cycle_page", 0)}')
    if tiers.get('C_joint_same_page_only', 0) != 7:
        raise SystemExit(f'expected 7 Tier C candidates, found {tiers.get("C_joint_same_page_only", 0)}')

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
        f'- Tier A, evidencia independiente entre páginas: **{tiers.get("A_cross_page_independent", 0)}**.',
        f'- Tier B, declaración conjunta + corroboración adicional de ciclo: **{tiers.get("B_joint_plus_extra_cycle_page", 0)}**.',
        f'- Tier C, declaración conjunta en una sola página: **{tiers.get("C_joint_same_page_only", 0)}**.',
        f'- Candidatos cuyo año difiere de `catalog_generation`: **{differs}/9**.',
        '',
        'Esta capa corrige deliberadamente la terminología de `LTMD_BIBLIOGRAPHIC_INSTANCE_RESOLUTION_0.1`. Las nueve coincidencias son **candidatos bibliográficos técnicamente resueltos**, no fechas históricas definitivamente validadas. Ninguna tiene actualmente Tier A de corroboración independiente entre páginas.',
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
        '## Uso permitido',
        '',
        'Los nueve años pueden usarse como **candidatos de cronología de ejemplar** en controles de calidad, planificación de verificación y análisis de sensibilidad. Tier B conserva una corroboración adicional del ciclo en otra página; Tier C no.',
        '',
        '## Uso no permitido',
        '',
        'No presentar estos años como fechas bibliográficas humanas validadas ni como prueba de circulación nacional. No usar `catalog_generation` para completar los 17 objetos sin candidato. No seleccionar el año u ordinal mayor entre las declaraciones históricas observadas.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    print('objects', len(rows_out))
    print('candidates', len(candidates))
    print('tier_a', tiers.get('A_cross_page_independent', 0))
    print('tier_b', tiers.get('B_joint_plus_extra_cycle_page', 0))
    print('tier_c', tiers.get('C_joint_same_page_only', 0))
    print('differs_from_catalog_generation', differs)


if __name__ == '__main__':
    main()
