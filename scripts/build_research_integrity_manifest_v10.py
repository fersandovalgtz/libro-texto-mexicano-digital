#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.10 with temporal/bibliographic governance and W7 evidence.

0.10 is additive over the complete 0.9 perimeter. It freezes:

* the separation of catalog cohort from observed bibliographic time;
* reproducible bibliographic observations and their source-verified extractors;
* bounded source-verified bibliographic fingerprints for the W7 admitted cohort;
* reproducible institutional-presence evidence and acceptance criteria for the
  five W7 source-withheld identities;
* the strictly nonsemantic W3-W4-W7 technical comparator;
* the data-model/governance documents that define those semantics.

It does not promote Wayback/Common Crawl infrastructure failures or the
unverified external mirror experiment into the critical scientific perimeter.
"""
from __future__ import annotations

import json
import build_research_integrity_manifest_v09 as v09

base = v09.base
base.VERSION = 'LTMD_INTEGRITY_0.10'

SCOPE = (
    'LTMD v0.10: frozen v0.9 perimeter plus explicit catalog-cohort versus '
    'bibliographic-time semantics, source-verified bibliographic observations '
    'and bounded W7 fingerprints, reproducible presence/acceptance evidence for '
    'the five W7 source-withheld identities, the nonsemantic W3-W4-W7 technical '
    'comparison, and the governing data-model/provenance contracts'
)
SCOPE_ES = (
    'perímetro v0.9 congelado + separación explícita entre cohorte de catálogo '
    'y tiempo bibliográfico, observaciones bibliográficas y huellas W7 '
    'verificadas contra fuente, evidencia reproducible de presencia/criterios '
    'de aceptación para las cinco identidades W7 retenidas, comparación técnica '
    'no semántica W3↔W4↔W7 y contratos de modelo/gobernanza correspondientes'
)
OLD_SCOPE_ES_ASCII = (
    'CN5 piloto + expansión CN4/CN6 cerrada + Ola 2 cerrada + readiness de la '
    'familia estricta Ciencias Naturales + dependencia/contenido único + '
    'infraestructura SEMB 0.3 prehumana + artículo metodológico 0.2.'
)

V10_CRITICAL = [
    # Temporal semantics and bibliographic observation layer.
    'docs/LTMD_CATALOG_GENERATION_SEMANTICS_0_1.md',
    'docs/DATA_MODEL.md',
    'docs/DATA_GOVERNANCE.md',
    'data/catalog/ltmd_bibliographic_observations.csv',
    'data/catalog/ltmd_bibliographic_observations.md',
    'scripts/build_ltmd_bibliographic_observations.py',
    '.github/workflows/build-ltmd-bibliographic-observations.yml',

    # H2014P5FCA source-verified legal-page fingerprint.
    'data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.csv',
    'data/catalog/ltmd_u1_w7_h2014p5_bibliographic_fingerprint.md',
    'scripts/extract_ltmd_u1_w7_h2014p5_bibliographic_fingerprint.py',
    '.github/workflows/extract-ltmd-u1-w7-h2014p5-bibliographic-fingerprint.yml',

    # W7 admitted-cohort bounded bibliographic fingerprints. These paths make
    # 0.10 intentionally non-runnable until the verified build materializes.
    'data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.csv',
    'data/catalog/ltmd_u1_w7_admitted_bibliographic_fingerprints.md',
    'scripts/extract_ltmd_u1_w7_admitted_bibliographic_fingerprints.py',
    '.github/workflows/extract-ltmd-u1-w7-admitted-bibliographic-fingerprints.yml',

    # W7 withheld-source reproducible evidence/governance.
    'data/catalog/ltmd_u1_w7_withheld_viewer_presence.csv',
    'data/catalog/ltmd_u1_w7_withheld_viewer_presence.md',
    'scripts/snapshot_ltmd_u1_w7_withheld_viewer_presence.py',
    '.github/workflows/snapshot-ltmd-u1-w7-withheld-viewer-presence.yml',
    'docs/LTMD_U1_W7_WITHHELD_SOURCE_RESEARCH_0_3.md',
    'docs/LTMD_U1_W7_WITHHELD_SOURCE_ACCEPTANCE_CRITERIA.md',

    # Three-cohort engineering comparison.
    'data/derived/ltmd_u1_w3_w4_w7_technical_comparison.csv',
    'docs/LTMD_U1_W3_W4_W7_TECHNICAL_COMPARISON.md',
    'scripts/compare_ltmd_u1_w3_w4_w7_technical_profiles.py',
    '.github/workflows/analyze-ltmd-u1-w3-w4-w7-technical-comparison.yml',

    # Versioned integrity builder itself.
    'scripts/build_research_integrity_manifest_v10.py',
]

for path in V10_CRITICAL:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)


def main() -> None:
    base.main()

    data = json.loads(base.OUT.read_text(encoding='utf-8'))
    data['scope'] = SCOPE
    base.OUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    report = base.REPORT.read_text(encoding='utf-8')
    old_line = f'Alcance: {OLD_SCOPE_ES_ASCII}'
    new_line = f'Alcance: {SCOPE_ES}.'
    if old_line not in report:
        raise SystemExit(
            'LTMD_INTEGRITY_0.10 scope postprocessor could not locate inherited scope line'
        )
    base.REPORT.write_text(
        report.replace(old_line, new_line, 1),
        encoding='utf-8',
    )


if __name__ == '__main__':
    main()
