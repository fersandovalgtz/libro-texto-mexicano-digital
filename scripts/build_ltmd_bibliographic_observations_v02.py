#!/usr/bin/env python3
"""Build LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.2.

Version 0.2 preserves the narrow H2014P5FCA observations from 0.1 and extends
the layer with only `strong_multipsm` candidates from the source-verified W7
admitted-cohort audit. It deliberately models edition/reprint candidates as
*history statements*, not as a resolved current edition for the viewer.

Two normalized outputs are produced:
* `ltmd_bibliographic_observations.csv`: one semantic observation per object,
  field and normalized value;
* `ltmd_bibliographic_observation_evidence.csv`: one or more page/SHA evidence
  rows supporting each observation.

No value is inferred from catalog_generation. ISBN observations require the
candidate-support audit's valid ISBN-13 checksum gate.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

import build_ltmd_bibliographic_observations as v01

VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.2'
SUPPORT_VERSION = 'LTMD_U1_W7_BIBLIOGRAPHIC_CANDIDATE_SUPPORT_0.1'
FINGERPRINT_VERSION = 'LTMD_U1_W7_ADMITTED_BIBLIOGRAPHIC_FINGERPRINTS_0.1'
SUPPORT = Path('data/catalog/ltmd_u1_w7_bibliographic_candidate_support.csv')
FINGERPRINT = Path('data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.csv')
OUT = Path('data/catalog/ltmd_bibliographic_observations.csv')
EVIDENCE_OUT = Path('data/catalog/ltmd_bibliographic_observation_evidence.csv')
REPORT = Path('data/catalog/ltmd_bibliographic_observations.md')

FIELD_MAP = {
    'edition': 'edition_history_statement',
    'reprint': 'reprint_history_statement',
    'school_cycle': 'school_cycle_statement',
    'isbn': 'isbn_statement',
}
ORDINAL_DISPLAY = {
    'first': 'Primera', 'second': 'Segunda', 'third': 'Tercera', 'fourth': 'Cuarta',
    'fifth': 'Quinta', 'sixth': 'Sexta', 'seventh': 'Séptima', 'eighth': 'Octava',
    'ninth': 'Novena', 'tenth': 'Décima',
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def display_value(kind: str, value: str) -> str:
    if kind == 'school_cycle':
        return f'ciclo escolar {value}'
    if kind == 'isbn':
        return f'ISBN {value}'
    m = re.fullmatch(r'([a-z]+)_(edition|reprint):((?:19|20)\d{2})', value)
    if not m:
        return value
    ordinal, statement, year = m.groups()
    label = ORDINAL_DISPLAY.get(ordinal, ordinal.title())
    noun = 'edición' if statement == 'edition' else 'reimpresión'
    return f'{label} {noun}, {year}'


def main() -> None:
    # Rebuild the v0.1 baseline from its primary evidence, rather than trusting
    # whatever output version happens to be committed at invocation time.
    v01.main()
    baseline = read_csv(v01.OUT)
    if len(baseline) != 4:
        raise SystemExit(f'expected four v0.1 baseline observations, found {len(baseline)}')

    support_rows = read_csv(SUPPORT)
    if not support_rows:
        raise SystemExit('candidate-support audit is empty')
    if {r['audit_version'] for r in support_rows} != {SUPPORT_VERSION}:
        raise SystemExit('candidate-support version drift')

    fingerprint_rows = read_csv(FINGERPRINT)
    if len(fingerprint_rows) != 300:
        raise SystemExit(f'expected 300 fingerprint rows, found {len(fingerprint_rows)}')
    if {r['fingerprint_version'] for r in fingerprint_rows} != {FINGERPRINT_VERSION}:
        raise SystemExit('admitted fingerprint version drift')
    fp_by_page = {(r['viewer_key'], r['viewer_page']): r for r in fingerprint_rows}
    if len(fp_by_page) != 300:
        raise SystemExit('duplicate viewer/page rows in admitted fingerprint')

    observations: list[dict[str, str]] = []
    evidence: list[dict[str, str]] = []

    # Preserve v0.1 semantics but version the materialized layer as 0.2.
    for row in baseline:
        obs = dict(row)
        obs['observation_version'] = VERSION
        obs['support_class'] = 'strong_custom_ensemble_rule'
        obs['support_evidence_count'] = '1'
        observations.append(obs)
        evidence.append({
            'observation_version': VERSION,
            'observation_id': obs['observation_id'],
            'viewer_key': obs['viewer_key'],
            'field': obs['field'],
            'normalized_value': obs['normalized_value'],
            'evidence_viewer_page': obs['evidence_viewer_page'],
            'evidence_image_index': obs['evidence_image_index'],
            'evidence_sha256': obs['evidence_sha256'],
            'evidence_byte_size': obs['evidence_byte_size'],
            'support_class': 'strong_custom_ensemble_rule',
            'psm_support_count': '5',
            'psm_modes': '3;4;6;11;12',
            'isbn13_checksum_valid': '',
            'extraction_source_version': obs['extraction_source_version'],
        })

    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in support_rows:
        if row.get('promotable_under_0_1_rule') != '1':
            continue
        if row.get('support_class') != 'strong_multipsm':
            raise SystemExit('promotable support row is not strong_multipsm')
        kind = row['candidate_kind']
        if kind not in FIELD_MAP:
            raise SystemExit(f'unknown promotable candidate kind: {kind}')
        if kind == 'isbn' and row.get('isbn13_checksum_valid') != '1':
            raise SystemExit('promotable ISBN lacks valid ISBN-13 checksum')
        groups[(row['viewer_key'], kind, row['candidate_value'])].append(row)

    for (viewer_key, kind, value), rows in sorted(groups.items()):
        rows = sorted(rows, key=lambda r: (-int(r['psm_support_count']), int(r['viewer_page'])))
        primary = rows[0]
        fp = fp_by_page.get((viewer_key, primary['viewer_page']))
        if fp is None:
            raise SystemExit(f'missing fingerprint evidence for {viewer_key} p{primary["viewer_page"]}')
        if fp['source_sha256'] != primary['source_sha256'] or fp['sha_verified'] != '1':
            raise SystemExit(f'support/fingerprint SHA mismatch for {viewer_key} p{primary["viewer_page"]}')

        field = FIELD_MAP[kind]
        obs_id = f'{viewer_key}:{field}:{value}'
        observations.append({
            'observation_version': VERSION,
            'observation_id': obs_id,
            'viewer_key': viewer_key,
            'catalog_generation': primary['catalog_generation'],
            'field': field,
            'normalized_value': value,
            'display_value': display_value(kind, value),
            'evidence_class': 'primary_source_page_ocr_multipsm',
            'evidence_viewer_page': primary['viewer_page'],
            'evidence_image_index': fp['source_image_index'],
            'evidence_sha256': fp['source_sha256'],
            'evidence_byte_size': fp['source_byte_size'],
            'extraction_source_version': SUPPORT_VERSION,
            'human_validated': '0',
            'admissibility_note': (
                'institutional source page; same structured statement observed by >=2 OCR PSM modes; '
                'history statement only, not resolved current-edition semantics; catalog_generation not used to infer value'
            ),
            'support_class': 'strong_multipsm',
            'support_evidence_count': str(len(rows)),
        })

        for evidence_row in rows:
            efp = fp_by_page.get((viewer_key, evidence_row['viewer_page']))
            if efp is None or efp['source_sha256'] != evidence_row['source_sha256']:
                raise SystemExit(f'evidence fingerprint mismatch for {viewer_key} p{evidence_row["viewer_page"]}')
            evidence.append({
                'observation_version': VERSION,
                'observation_id': obs_id,
                'viewer_key': viewer_key,
                'field': field,
                'normalized_value': value,
                'evidence_viewer_page': evidence_row['viewer_page'],
                'evidence_image_index': efp['source_image_index'],
                'evidence_sha256': efp['source_sha256'],
                'evidence_byte_size': efp['source_byte_size'],
                'support_class': evidence_row['support_class'],
                'psm_support_count': evidence_row['psm_support_count'],
                'psm_modes': evidence_row['psm_modes'],
                'isbn13_checksum_valid': evidence_row['isbn13_checksum_valid'],
                'extraction_source_version': SUPPORT_VERSION,
            })

    ids = [r['observation_id'] for r in observations]
    if len(ids) != len(set(ids)):
        dupes = sorted({x for x in ids if ids.count(x) > 1})
        raise SystemExit(f'duplicate observation ids: {dupes[:10]}')

    # Structural invariants: all 25 admitted W7 viewers receive at least one
    # promoted observation; the held H2014P5 baseline remains represented too.
    admitted_observation_viewers = {
        r['viewer_key'] for r in observations
        if r['viewer_key'] != v01.TARGET
    }
    if len(admitted_observation_viewers) != 25:
        raise SystemExit(
            f'expected observations for 25 admitted W7 viewers, found {len(admitted_observation_viewers)}'
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    obs_fields = [
        'observation_version', 'observation_id', 'viewer_key', 'catalog_generation',
        'field', 'normalized_value', 'display_value', 'evidence_class',
        'evidence_viewer_page', 'evidence_image_index', 'evidence_sha256',
        'evidence_byte_size', 'extraction_source_version', 'human_validated',
        'admissibility_note', 'support_class', 'support_evidence_count',
    ]
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=obs_fields)
        writer.writeheader(); writer.writerows(observations)

    evidence_fields = [
        'observation_version', 'observation_id', 'viewer_key', 'field',
        'normalized_value', 'evidence_viewer_page', 'evidence_image_index',
        'evidence_sha256', 'evidence_byte_size', 'support_class',
        'psm_support_count', 'psm_modes', 'isbn13_checksum_valid',
        'extraction_source_version',
    ]
    with EVIDENCE_OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=evidence_fields)
        writer.writeheader(); writer.writerows(evidence)

    by_field = defaultdict(int)
    for row in observations:
        by_field[row['field']] += 1
    viewers = sorted({r['viewer_key'] for r in observations})

    lines = [
        '# LTMD — observaciones bibliográficas reproducibles',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'- Observaciones semánticas materializadas: **{len(observations)}**.',
        f'- Objetos con ≥1 observación: **{len(viewers)}**.',
        f'- Filas de evidencia página/SHA: **{len(evidence)}**.',
        f'- W7 admitidos cubiertos por observaciones fuertes: **{len(admitted_observation_viewers)}/25**.',
        '- `H2014P5FCA` se conserva mediante la regla primaria específica de 0.1 pese a estar retenido del OCR productivo por su hueco de fuente.',
        '',
        '## Semántica',
        '',
        '`edition_history_statement` y `reprint_history_statement` significan **declaraciones bibliográficas observadas en el objeto**, no una selección automática de la edición/reimpresión que deba usarse como fecha canónica del visor. `school_cycle_statement` e `isbn_statement` conservan la misma lógica de observación. La resolución a campos de libro como `edition_year` requiere una regla posterior explícita.',
        '',
        '## Conteo por campo',
        '',
    ]
    for field in sorted(by_field):
        lines.append(f'- `{field}`: **{by_field[field]}**.')

    lines += [
        '',
        '## Observaciones',
        '',
        '| objeto | cohorte | campo | valor | página primaria | soporte | evidencias |',
        '|---|---:|---|---|---:|---|---:|',
    ]
    for row in observations:
        lines.append(
            f"| `{row['viewer_key']}` | {row['catalog_generation']} | `{row['field']}` | "
            f"`{row['normalized_value']}` | {row['evidence_viewer_page']} | "
            f"`{row['support_class']}` | {row['support_evidence_count']} |"
        )

    lines += [
        '',
        '## Contrato',
        '',
        '- Cada observación mantiene una página primaria y SHA; la tabla de evidencia conserva todas las páginas fuertes que la corroboran.',
        '- Ningún ISBN con checksum ISBN-13 inválido entra a la capa de observaciones.',
        '- `catalog_generation` se copia sólo como contexto de cohorte y nunca genera el valor observado.',
        '- `human_validated=0` mantiene explícita la ausencia de validación humana de la transcripción OCR.',
        '- Esta capa no resuelve por sí sola cuál declaración histórica corresponde a la edición vigente o al año de circulación del ejemplar.',
        '',
        'Véanse `docs/DATA_MODEL.md`, `docs/DATA_GOVERNANCE.md` y `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    print('observations', len(observations))
    print('evidence_rows', len(evidence))
    print('viewer_keys', len(viewers))
    print('admitted_w7_viewers', len(admitted_observation_viewers))


if __name__ == '__main__':
    main()
