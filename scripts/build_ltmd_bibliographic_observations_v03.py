#!/usr/bin/env python3
"""Build LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.3.

0.3 is additive over 0.2. It incorporates only reprint statements recovered by
LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.1, whose normalization is limited
to the documented `reimpresión` i→l/I/1 OCR confusion, supported by >=2 PSM
modes and a year equal to an already observed school-cycle start.

No other fuzzy OCR correction is admitted by this version.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import build_ltmd_bibliographic_observations_v02 as v02

VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.3'
RECOVERY_VERSION = 'LTMD_U1_W7_REPRINT_OCR_CONFUSION_RECOVERY_0.1'
RECOVERY = Path('data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.csv')
OUT = Path('data/catalog/ltmd_bibliographic_observations.csv')
EVIDENCE_OUT = Path('data/catalog/ltmd_bibliographic_observation_evidence.csv')
REPORT = Path('data/catalog/ltmd_bibliographic_observations.md')


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main() -> None:
    # Rebuild 0.2 deterministically, then promote the materialized rows to 0.3.
    v02.main()
    observations = read_csv(v02.OUT)
    evidence = read_csv(v02.EVIDENCE_OUT)
    if len(observations) != 93 or len(evidence) != 95:
        raise SystemExit(
            f'0.2 baseline drift: observations={len(observations)} evidence={len(evidence)}'
        )
    if {r['observation_version'] for r in observations} != {v02.VERSION}:
        raise SystemExit('0.2 observation version drift')
    if {r['observation_version'] for r in evidence} != {v02.VERSION}:
        raise SystemExit('0.2 evidence version drift')

    for row in observations:
        row['observation_version'] = VERSION
    for row in evidence:
        row['observation_version'] = VERSION

    recovery = read_csv(RECOVERY)
    if {r['recovery_version'] for r in recovery} != {RECOVERY_VERSION}:
        raise SystemExit('reprint recovery version drift')
    if len(recovery) != 2:
        raise SystemExit(f'expected exactly two narrow recovered statements, found {len(recovery)}')
    if any(r['year_matches_school_cycle_start'] != '1' for r in recovery):
        raise SystemExit('recovery contains a year that does not match school-cycle start')
    if any(int(r['psm_support_count']) < 2 for r in recovery):
        raise SystemExit('recovery contains insufficient PSM support')

    existing_ids = {r['observation_id'] for r in observations}
    recovered_ids = []
    for r in sorted(recovery, key=lambda x: x['viewer_key']):
        value = r['recovered_statement_value']
        obs_id = f"{r['viewer_key']}:reprint_history_statement:{value}"
        if obs_id in existing_ids:
            raise SystemExit(f'recovered statement already exists in 0.2: {obs_id}')
        existing_ids.add(obs_id)
        recovered_ids.append(obs_id)

        observations.append({
            'observation_version': VERSION,
            'observation_id': obs_id,
            'viewer_key': r['viewer_key'],
            'catalog_generation': r['catalog_generation'],
            'field': 'reprint_history_statement',
            'normalized_value': value,
            'display_value': v02.display_value('reprint', value),
            'evidence_class': 'primary_source_page_ocr_multipsm_narrow_confusion_normalized',
            'evidence_viewer_page': r['evidence_viewer_page'],
            'evidence_image_index': r['evidence_image_index'],
            'evidence_sha256': r['evidence_sha256'],
            'evidence_byte_size': r['evidence_byte_size'],
            'extraction_source_version': RECOVERY_VERSION,
            'human_validated': '0',
            'admissibility_note': (
                'institutional SHA-verified source page; reimpresion token normalized only under '
                'documented i->l/I/1 OCR confusion; >=2 PSM support; year already matches observed '
                'school-cycle start; catalog_generation not used'
            ),
            'support_class': 'strong_multipsm_narrow_reprint_confusion',
            'support_evidence_count': '1',
        })
        evidence.append({
            'observation_version': VERSION,
            'observation_id': obs_id,
            'viewer_key': r['viewer_key'],
            'field': 'reprint_history_statement',
            'normalized_value': value,
            'evidence_viewer_page': r['evidence_viewer_page'],
            'evidence_image_index': r['evidence_image_index'],
            'evidence_sha256': r['evidence_sha256'],
            'evidence_byte_size': r['evidence_byte_size'],
            'support_class': 'strong_multipsm_narrow_reprint_confusion',
            'psm_support_count': r['psm_support_count'],
            'psm_modes': r['psm_modes'],
            'isbn13_checksum_valid': '',
            'extraction_source_version': RECOVERY_VERSION,
        })

    ids = [r['observation_id'] for r in observations]
    if len(ids) != len(set(ids)):
        raise SystemExit('duplicate observation ids after 0.3 promotion')
    if len(observations) != 95 or len(evidence) != 97:
        raise SystemExit(
            f'0.3 cardinality drift: observations={len(observations)} evidence={len(evidence)}'
        )

    obs_fields = list(observations[0].keys())
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=obs_fields)
        writer.writeheader(); writer.writerows(observations)
    evidence_fields = list(evidence[0].keys())
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
        '- Observaciones añadidas por recuperación OCR estrecha: **2**.',
        '',
        '0.3 conserva las 93 observaciones de 0.2 y añade únicamente dos `reprint_history_statement` cuya palabra `reimpresión` fue afectada por la confusión OCR documentada `i→l/I/1`. Cada recuperación tiene ≥2 PSM, página institucional SHA-verificada y año igual al inicio de un ciclo escolar ya observado. **No se habilita fuzzy matching general.**',
        '',
        'Recuperaciones incorporadas:',
        '',
    ]
    for obs_id in recovered_ids:
        row = next(r for r in observations if r['observation_id'] == obs_id)
        lines.append(
            f"- `{row['viewer_key']}`: `{row['normalized_value']}` en página "
            f"{row['evidence_viewer_page']}, SHA `{row['evidence_sha256'][:16]}…`."
        )
    lines += [
        '',
        '## Conteo por campo',
        '',
    ]
    for field in sorted(by_field):
        lines.append(f'- `{field}`: **{by_field[field]}**.')
    lines += [
        '',
        '## Contrato',
        '',
        '- Las declaraciones de edición/reimpresión siguen siendo historia bibliográfica observada, no selección automática de la edición efectiva.',
        '- Las dos recuperaciones 0.3 preservan token OCR bruto, PSM y regla de normalización en el artefacto de recovery.',
        '- `catalog_generation` permanece fuera de la inferencia.',
        '- `human_validated=0` permanece explícito.',
        '- Cualquier otra corrección OCR futura requiere una regla separada, acotada y versionada.',
        '',
        'Véanse `data/catalog/ltmd_u1_w7_reprint_ocr_confusion_recovery.md`, `docs/DATA_MODEL.md` y `docs/HISTORICAL_ANALYSIS_PLAN_0_3.md`.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    print('observations', len(observations))
    print('evidence_rows', len(evidence))
    print('recovered_additions', len(recovered_ids))


if __name__ == '__main__':
    main()
