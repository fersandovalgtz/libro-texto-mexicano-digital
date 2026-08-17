#!/usr/bin/env python3
"""Build a 30-identity W7 bibliographic coverage/readiness matrix.

The matrix distinguishes source availability from bibliographic chronology:
* all 30 historical identities remain rows;
* source-admitted vs source-withheld is copied from the frozen gate;
* observation coverage comes from LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4;
* technical instance candidates come from LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.3;
* absent chronology is never filled from catalog_generation.

This is a readiness/coverage product, not an inferential historical analysis.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

VERSION = 'LTMD_U1_W7_BIBLIOGRAPHIC_COVERAGE_0.1'
OBS_VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.4'
CAND_VERSION = 'LTMD_BIBLIOGRAPHIC_INSTANCE_CANDIDATES_0.3'
GATE = Path('data/catalog/ltmd_u1_w7_source_admissibility.csv')
OBS = Path('data/catalog/ltmd_bibliographic_observations.csv')
CAND = Path('data/catalog/ltmd_bibliographic_instance_candidates.csv')
OUT = Path('data/derived/ltmd_u1_w7_bibliographic_coverage.csv')
REPORT = Path('docs/LTMD_U1_W7_BIBLIOGRAPHIC_COVERAGE.md')


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main() -> None:
    gate = read_csv(GATE)
    if len(gate) != 30 or len({r['viewer_key'] for r in gate}) != 30:
        raise SystemExit('W7 source gate is not the expected 30-identity universe')
    observations = read_csv(OBS)
    if {r['observation_version'] for r in observations} != {OBS_VERSION}:
        raise SystemExit('observation version drift')
    candidates = read_csv(CAND)
    if {r['candidate_version'] for r in candidates} != {CAND_VERSION}:
        raise SystemExit('candidate version drift')
    cand_by_viewer = {r['viewer_key']: r for r in candidates}
    if len(cand_by_viewer) != 26:
        raise SystemExit(f'expected 26 candidate-layer objects, found {len(cand_by_viewer)}')

    obs_by_viewer = defaultdict(list)
    for row in observations:
        obs_by_viewer[row['viewer_key']].append(row)

    rows_out = []
    for g in sorted(gate, key=lambda r: (int(r['catalog_generation']), int(r['grade_code']), r['viewer_key'])):
        viewer = g['viewer_key']
        obs = obs_by_viewer.get(viewer, [])
        fields = Counter(r['field'] for r in obs)
        cycles = sorted({
            r['normalized_value'] for r in obs
            if r['field'] in {'school_cycle', 'school_cycle_statement'}
        })
        cand = cand_by_viewer.get(viewer)
        candidate_year = cand['candidate_bibliographic_year'] if cand else ''
        candidate_tier = cand['evidence_tier'] if cand else ''
        candidate_status = cand['candidate_status'] if cand else 'not_in_candidate_layer'

        if g['ocr_source_admitted'] == '0' and viewer.startswith('H2018'):
            readiness = 'source_withheld_subtree_unserved'
        elif g['ocr_source_admitted'] == '0':
            readiness = 'source_withheld_partial_gap'
        elif candidate_year:
            readiness = 'technical_instance_candidate_available'
        elif cycles:
            readiness = 'cycle_observed_no_instance_candidate'
        elif obs:
            readiness = 'bibliographic_observations_no_cycle'
        else:
            readiness = 'source_admitted_no_bibliographic_observation'

        rows_out.append({
            'coverage_version': VERSION,
            'viewer_key': viewer,
            'catalog_generation': g['catalog_generation'],
            'grade_code': g['grade_code'],
            'title_core': g['title_core'],
            'ocr_source_admitted': g['ocr_source_admitted'],
            'source_decision': g['decision'],
            'source_reason_code': g['reason_code'],
            'bibliographic_observation_count': len(obs),
            'edition_history_statement_count': fields['edition_history_statement'],
            'reprint_history_statement_count': fields['reprint_history_statement'],
            'school_cycle_observation_count': len(cycles),
            'school_cycle_values': ';'.join(cycles),
            'isbn_statement_count': fields['isbn_statement'],
            'candidate_status': candidate_status,
            'candidate_bibliographic_year': candidate_year,
            'candidate_evidence_tier': candidate_tier,
            'candidate_year_differs_from_catalog_generation': (
                cand['candidate_year_differs_from_catalog_generation'] if cand else ''
            ),
            'readiness_class': readiness,
            'human_validated': '0' if obs or cand else '',
        })

    if len(rows_out) != 30:
        raise SystemExit('coverage matrix lost historical identities')
    counts = Counter(r['readiness_class'] for r in rows_out)
    expected = {
        'source_withheld_subtree_unserved': 4,
        'source_withheld_partial_gap': 1,
        'technical_instance_candidate_available': 10,  # H2014P5 is held, so 10 admitted + 1 held candidate.
        'cycle_observed_no_instance_candidate': 3,
        'bibliographic_observations_no_cycle': 12,
    }
    # Candidate H2014P5 is held and classified by source first. Therefore 10 of
    # the 11 candidates fall into the admitted-ready class.
    for key, value in expected.items():
        if counts.get(key, 0) != value:
            raise SystemExit(f'readiness count drift for {key}: {counts.get(key,0)} != {value}')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows_out[0])
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows_out)

    by_generation = defaultdict(list)
    for row in rows_out:
        by_generation[row['catalog_generation']].append(row)

    lines = [
        '# LTMD-U1 W7 — cobertura bibliográfica y readiness',
        '',
        f'Versión: `{VERSION}`.',
        '',
        '- Universo histórico preservado: **30/30 identidades**.',
        '- Fuente admitida: **25/30**; retenida: **5/30**.',
        '- Objetos en capa de observaciones: **26**.',
        '- Candidatos técnicos de instancia: **11** en total; **10** sobre fuente admitida y **1** (`H2014P5FCA`) sobre objeto parcialmente retenido.',
        '- `human_validated=0` para toda la capa bibliográfica técnica actual.',
        '',
        'La matriz separa dos ejes de completitud: **fuente** y **cronología bibliográfica**. Un objeto puede tener fuente admitida y carecer de ciclo/fecha candidata; también puede, como `H2014P5FCA`, poseer evidencia bibliográfica fuerte pero permanecer retenido del OCR productivo por un hueco de fuente.',
        '',
        '## Readiness global',
        '',
    ]
    for key, value in sorted(counts.items()):
        lines.append(f'- `{key}`: **{value}**.')

    lines += [
        '',
        '## Cobertura por generación de catálogo',
        '',
        '| generación | identidades | fuente admitida | con ciclo | con candidato | candidatos ≠ cohorte | retenidas |',
        '|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for generation in sorted(by_generation, key=int):
        items = by_generation[generation]
        admitted = sum(r['ocr_source_admitted'] == '1' for r in items)
        cycles = sum(bool(r['school_cycle_values']) for r in items)
        cand = sum(bool(r['candidate_bibliographic_year']) for r in items)
        differs = sum(r['candidate_year_differs_from_catalog_generation'] == '1' for r in items)
        held = len(items) - admitted
        lines.append(
            f'| {generation} | {len(items)} | {admitted} | {cycles} | {cand} | {differs} | {held} |'
        )

    lines += [
        '',
        '## Objeto por objeto',
        '',
        '| objeto | cohorte | grado | fuente | observaciones | ciclo | candidato | tier | readiness |',
        '|---|---:|---:|---|---:|---|---:|---|---|',
    ]
    for r in rows_out:
        lines.append(
            f"| `{r['viewer_key']}` | {r['catalog_generation']} | {r['grade_code']} | "
            f"`{'admitida' if r['ocr_source_admitted']=='1' else 'retenida'}` | "
            f"{r['bibliographic_observation_count']} | `{r['school_cycle_values'] or '—'}` | "
            f"{r['candidate_bibliographic_year'] or '—'} | `{r['candidate_evidence_tier'] or '—'}` | "
            f"`{r['readiness_class']}` |"
        )

    lines += [
        '',
        '## Límite epistemológico',
        '',
        'Readiness no es calidad ni validez histórica. `technical_instance_candidate_available` significa únicamente que el objeto cumple la regla técnica vigente de candidato. No transforma Tier B/C en validación humana ni convierte `catalog_generation` en año editorial. Las cinco retenciones de fuente continúan gobernadas por su gate independiente.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('identities', len(rows_out))
    print('readiness', dict(sorted(counts.items())))


if __name__ == '__main__':
    main()
