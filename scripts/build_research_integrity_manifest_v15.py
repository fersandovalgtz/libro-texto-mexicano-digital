#!/usr/bin/env python3
"""Build LTMD_INTEGRITY_0.15 after W9/W10 technical closure.

0.15 is strictly additive over 0.14.  It freezes the complete W9 technical
closure and the W10 source-first evidence chain through technical completion,
including the global coverage/dashboard and landing-page synchronization code.

The builder is intentionally gated: it refuses to run until the W10 completion
report exists.  This prevents a partially processed W10 cohort from being
promoted into the repository's current research-integrity perimeter.
"""
from __future__ import annotations

import json
from pathlib import Path
import build_research_integrity_manifest_v14 as v14

base = v14.base
base.VERSION = 'LTMD_INTEGRITY_0.15'

SCOPE = (
    'LTMD v0.15: frozen v0.14 perimeter plus complete LTMD-U1 W9 technical '
    'closure and the W10 Integrados/Multiarea source-first chain from frozen '
    'scope, viewer/source audit and source admissibility through byte-exact '
    'processing topology, SHA-verified OCR, conservative PAGESTRUCT, frozen-engine '
    'FRAGSEG, exact-text reuse/dependence and evidence-gated technical completion, '
    'including explicit source retentions, global U1 coverage reconstruction and '
    'Spanish/English landing-page synchronization'
)
SCOPE_ES = (
    'perímetro v0.14 congelado + cierre técnico completo LTMD-U1 W9 y cadena '
    'source-first W10 Integrados/Multiarea desde alcance congelado, auditoría de '
    'visor/fuente y admisibilidad hasta topología byte-exacta, OCR verificado por '
    'SHA, PAGESTRUCT conservador, FRAGSEG con motor congelado, '
    'reutilización/dependencia textual exacta y cierre técnico condicionado a '
    'evidencia, incluidas retenciones explícitas, reconstrucción global de '
    'cobertura U1 y sincronización de las portadas en español/inglés'
)

ROOT = Path('.')
REQUIRED_CLOSURE = [
    'docs/LTMD_U1_W9_COMPLETION.md',
    'docs/LTMD_U1_W10_SOURCE_ADMISSIBILITY.md',
    'docs/LTMD_U1_W10_PROCESSING_TOPOLOGY.md',
    'docs/LTMD_U1_W10_OCR.md',
    'docs/LTMD_U1_W10_PAGESTRUCT.md',
    'docs/LTMD_U1_W10_FRAGSEG.md',
    'docs/LTMD_U1_W10_EXACT_REUSE.md',
    'docs/LTMD_U1_W10_COMPLETION.md',
    'data/catalog/ltmd_u1_coverage.md',
    'data/catalog/ltmd_u1_coverage_summary.csv',
    'README.md',
    'README.en.md',
]

STATIC_CRITICAL = [
    'scripts/build_research_integrity_manifest_v15.py',
    'scripts/build_ltmd_u1_coverage_dashboard.py',
    'scripts/sync_readme_coverage.py',
    '.github/workflows/build-ltmd-u1-coverage-dashboard.yml',
    '.github/workflows/sync-readme-coverage.yml',
    '.github/workflows/research-integrity-manifest-v15.yml',
    'docs/LTMD_U1_W10_SOURCE_ANOMALIES.md',
    'docs/LTMD_U1_W10_TOPOLOGY_DIAGNOSTIC.md',
]


def add(path: str) -> None:
    if path not in base.CRITICAL:
        base.CRITICAL.append(path)


def discover_wave_perimeter() -> None:
    """Add W9/W10 evidence and executable provenance deterministically."""
    for rel in REQUIRED_CLOSURE:
        if not (ROOT / rel).is_file():
            raise SystemExit(f'LTMD_INTEGRITY_0.15 gate closed: missing {rel}')
        add(rel)

    for rel in STATIC_CRITICAL:
        if not (ROOT / rel).is_file():
            raise SystemExit(f'LTMD_INTEGRITY_0.15 critical file missing: {rel}')
        add(rel)

    catalog = ROOT / 'data/catalog'
    for p in sorted(catalog.iterdir()):
        if p.is_file() and p.name.startswith(('ltmd_u1_w9_', 'ltmd_u1_w10_')):
            add(p.as_posix())

    docs = ROOT / 'docs'
    for p in sorted(docs.iterdir()):
        if p.is_file() and p.name.startswith(('LTMD_U1_W9_', 'LTMD_U1_W10_')):
            add(p.as_posix())

    scripts = ROOT / 'scripts'
    for p in sorted(scripts.iterdir()):
        name = p.name
        if p.is_file() and p.suffix == '.py' and ('_w9_' in name or '_w10_' in name):
            add(p.as_posix())

    workflows = ROOT / '.github/workflows'
    for p in sorted(workflows.iterdir()):
        name = p.name
        if p.is_file() and p.suffix in {'.yml', '.yaml'} and ('w9' in name or 'w10' in name):
            add(p.as_posix())


def main() -> None:
    discover_wave_perimeter()
    v14.main()

    data = json.loads(base.OUT.read_text(encoding='utf-8'))
    data['scope'] = SCOPE
    data['semantic_validation_status'] = 'WAITING_HUMAN_REFERENCE'
    base.OUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    report = base.REPORT.read_text(encoding='utf-8')
    inherited_line = f'Alcance: {v14.SCOPE_ES}.'
    new_line = f'Alcance: {SCOPE_ES}.'
    if inherited_line not in report:
        raise SystemExit(
            'LTMD_INTEGRITY_0.15 scope postprocessor could not locate v0.14 scope line'
        )
    report = report.replace(inherited_line, new_line, 1)
    epistemic = (
        '\n\n## Límite epistemológico\n\n'
        '`LTMD_INTEGRITY_0.15` certifica existencia, bytes, procedencia y perímetro '
        'computacional crítico; no convierte OCR, PAGESTRUCT, FRAGSEG, hashes ni '
        'reutilización exacta en validación semántica o interpretación histórica. '
        '`WAITING_HUMAN_REFERENCE` permanece vigente. Los originales de fuente y '
        'el OCR íntegro permanecen fuera del perímetro público.\n'
    )
    if '## Límite epistemológico' not in report:
        report = report.rstrip() + epistemic
    base.REPORT.write_text(report, encoding='utf-8')


if __name__ == '__main__':
    main()
