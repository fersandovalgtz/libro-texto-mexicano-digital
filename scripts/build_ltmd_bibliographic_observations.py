#!/usr/bin/env python3
"""Build LTMD bibliographic observations from verified source-page evidence.

The first implementation is intentionally narrow: it promotes only temporal
statements redundantly observed in the SHA-verified H2014P5FCA legal-page OCR
fingerprint. It does not infer missing fields from catalog_generation and does
not import secondary-source ISBNs.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

VERSION = 'LTMD_BIBLIOGRAPHIC_OBSERVATIONS_0.1'
FINGERPRINT = Path('data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.csv')
SOURCE_MANIFEST = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_bibliographic_observations.csv')
REPORT = Path('data/catalog/ltmd_bibliographic_observations.md')
TARGET = 'H2014P5FCA'
LEGAL_PAGE = 4


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def require_pattern(text: str, pattern: str, label: str) -> re.Match[str]:
    match = re.search(pattern, text, flags=re.I)
    if not match:
        raise SystemExit(f'missing required bibliographic pattern for {label}: {pattern}')
    return match


def main() -> None:
    fp_rows = read_csv(FINGERPRINT)
    legal = [
        row for row in fp_rows
        if row.get('viewer_key') == TARGET and row.get('viewer_page') == str(LEGAL_PAGE)
    ]
    if len(legal) != 1:
        raise SystemExit(f'expected one {TARGET} legal-page fingerprint row, found {len(legal)}')
    legal = legal[0]
    if legal.get('sha_verified') != '1':
        raise SystemExit('legal-page fingerprint is not SHA-verified')
    if legal.get('fingerprint_version') != 'LTMD_U1_W7_H2014P5_BIBLIOGRAPHIC_FINGERPRINT_0.2':
        raise SystemExit(f"unexpected fingerprint version: {legal.get('fingerprint_version')}")

    source_rows = [
        row for row in read_csv(SOURCE_MANIFEST)
        if row.get('viewer_key') == TARGET and row.get('viewer_page') == str(LEGAL_PAGE)
    ]
    if len(source_rows) != 1:
        raise SystemExit(f'expected one source-manifest row for legal page, found {len(source_rows)}')
    source = source_rows[0]
    if source.get('asset_status') != 'source_jpeg':
        raise SystemExit('legal page is not source_jpeg in frozen manifest')
    if source.get('sha256') != legal.get('source_sha256'):
        raise SystemExit('fingerprint/source manifest SHA disagreement')
    if source.get('byte_size') != legal.get('source_byte_size'):
        raise SystemExit('fingerprint/source manifest size disagreement')

    evidence = legal.get('bibliographic_lines', '')
    require_pattern(evidence, r'Primera\s+edici[oó]n[,\s]+2014', 'first_edition_year')
    require_pattern(evidence, r'Tercera\s+reimpresi[oó]n[,\s]+2017', 'reprint_year')
    require_pattern(evidence, r'ciclo\s+escolar\s+2017\s*[-–]\s*2018', 'school_cycle')

    common = {
        'observation_version': VERSION,
        'viewer_key': TARGET,
        'catalog_generation': source['catalog_generation'],
        'evidence_class': 'primary_source_page_ocr_ensemble',
        'evidence_viewer_page': str(LEGAL_PAGE),
        'evidence_image_index': source['source_image_index'],
        'evidence_sha256': source['sha256'],
        'evidence_byte_size': source['byte_size'],
        'extraction_source_version': legal['fingerprint_version'],
        'human_validated': '0',
        'admissibility_note': (
            'primary institutional page; OCR statement redundantly observed; '
            'catalog_generation not used to infer bibliographic value'
        ),
    }

    observations = [
        {
            **common,
            'observation_id': f'{TARGET}:first_edition_year:2014',
            'field': 'first_edition_year',
            'normalized_value': '2014',
            'display_value': 'Primera edición, 2014',
        },
        {
            **common,
            'observation_id': f'{TARGET}:reprint_statement:third',
            'field': 'reprint_statement',
            'normalized_value': 'third_reprint',
            'display_value': 'Tercera reimpresión',
        },
        {
            **common,
            'observation_id': f'{TARGET}:reprint_year:2017',
            'field': 'reprint_year',
            'normalized_value': '2017',
            'display_value': 'Tercera reimpresión, 2017',
        },
        {
            **common,
            'observation_id': f'{TARGET}:school_cycle:2017-2018',
            'field': 'school_cycle',
            'normalized_value': '2017-2018',
            'display_value': 'ciclo escolar 2017-2018',
        },
    ]

    ids = [row['observation_id'] for row in observations]
    if len(ids) != len(set(ids)):
        raise SystemExit('duplicate bibliographic observation IDs')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'observation_version', 'observation_id', 'viewer_key', 'catalog_generation',
        'field', 'normalized_value', 'display_value', 'evidence_class',
        'evidence_viewer_page', 'evidence_image_index', 'evidence_sha256',
        'evidence_byte_size', 'extraction_source_version', 'human_validated',
        'admissibility_note',
    ]
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(observations)

    lines = [
        '# LTMD — observaciones bibliográficas reproducibles',
        '',
        f'Versión: `{VERSION}`.',
        '',
        f'Observaciones materializadas: **{len(observations)}**.',
        f'Objetos con observaciones: **1** (`{TARGET}`).',
        '',
        'Esta capa separa las fechas bibliográficas observadas de `catalog_generation`. No completa años ausentes por cohorte de catálogo y no importa ISBN desde fuentes secundarias.',
        '',
        '## Observaciones',
        '',
        '| objeto | generación catálogo | campo | valor | evidencia |',
        '|---|---:|---|---|---|',
    ]
    for row in observations:
        lines.append(
            f"| `{row['viewer_key']}` | {row['catalog_generation']} | `{row['field']}` | "
            f"`{row['normalized_value']}` | pág. {row['evidence_viewer_page']}, "
            f"SHA `{row['evidence_sha256'][:16]}…` |"
        )
    lines += [
        '',
        '## Contrato',
        '',
        '- Cada valor debe tener una página fuente identificada y una huella criptográfica concordante con el manifiesto canónico.',
        '- `catalog_generation` es contexto de navegación/cohorte, no fuente del valor bibliográfico.',
        '- `human_validated=0` indica que la extracción procede de OCR técnico; no invalida la procedencia de la página, pero conserva separada la futura validación humana de la transcripción.',
        '- La expansión a otros objetos debe añadir reglas reproducibles específicas y nunca rellenar valores desconocidos por cercanía temporal.',
        '',
        'Véase `docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md`.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('version', VERSION)
    print('observations', len(observations))
    print('viewer_keys', 1)
    print('catalog_generation', source['catalog_generation'])
    print('evidence_sha256', source['sha256'])


if __name__ == '__main__':
    main()
