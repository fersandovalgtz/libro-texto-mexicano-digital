#!/usr/bin/env python3
"""Detect exact byte-identical W2 Mathematics viewer objects after the asset audit.

Aliases are asserted only when two direct-ready viewers have the same number of
served source JPEGs and the same SHA-256 at every served viewer_page position.
No fuzzy similarity or title/year inference is used.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

MAN = Path('data/catalog/ltmd_u1_w2_math_asset_manifest.csv')
SUMMARY = Path('data/catalog/ltmd_u1_w2_math_asset_summary.csv')
OUT = Path('data/catalog/ltmd_u1_w2_math_exact_aliases.csv')
REPORT = Path('data/catalog/ltmd_u1_w2_math_exact_aliases.md')
VERSION = 'LTMD_U1_W2_MATH_EXACT_ALIASES_0.1'


def rows(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main():
    manifest = rows(MAN)
    summary = rows(SUMMARY)
    ready = {r['viewer_key']: r for r in summary if int(r['direct_asset_ready']) == 1}
    by_viewer = defaultdict(list)
    for r in manifest:
        if r['viewer_key'] in ready and r['asset_status'] == 'source_jpeg':
            by_viewer[r['viewer_key']].append(r)

    signatures = defaultdict(list)
    for viewer, rr in by_viewer.items():
        rr.sort(key=lambda r: int(r['viewer_page']))
        # Include page positions as well as hashes: exact alignment is required.
        signature = tuple((int(r['viewer_page']), r['sha256'], int(r['byte_size'])) for r in rr)
        expected = int(ready[viewer]['source_jpegs'])
        if len(signature) != expected or any(not sha for _, sha, _ in signature):
            raise SystemExit(f'incomplete direct-ready signature for {viewer}')
        signatures[signature].append(viewer)

    aliases = []
    group_no = 0
    for sig, viewers in sorted(signatures.items(), key=lambda item: item[1]):
        if len(viewers) < 2:
            continue
        group_no += 1
        viewers = sorted(viewers)
        canonical = viewers[0]  # operational canonical only; no historical priority implied.
        for viewer in viewers:
            if viewer == canonical:
                continue
            aliases.append({
                'alias_version': VERSION,
                'alias_group': f'MATH-ALIAS-{group_no:03d}',
                'viewer_key': viewer,
                'canonical_viewer_key': canonical,
                'source_jpeg_count': len(sig),
                'all_pages_byte_identical_aligned': 1,
                'interpretive_limit': 'Operational byte alias only; viewer identities and bibliographic records remain distinct.',
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ['alias_version','alias_group','viewer_key','canonical_viewer_key','source_jpeg_count','all_pages_byte_identical_aligned','interpretive_limit']
    with OUT.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(aliases)

    groups = len({r['alias_group'] for r in aliases})
    lines = [
        '# LTMD-U1 W2 — aliases exactos de Matemáticas', '',
        f'Versión: `{VERSION}`.', '',
        f'- Visores `direct_asset_ready`: **{len(ready)}**.',
        f'- Grupos con ≥2 objetos byte-idénticos alineados: **{groups}**.',
        f'- Visores alias que pueden heredar procesamiento técnico del canónico: **{len(aliases)}**.', '',
        '## Criterio', '',
        'Un alias sólo se registra si los dos objetos tienen la misma secuencia completa de páginas fuente servidas, con el mismo `viewer_page`, tamaño y SHA-256 en cada posición. No se usa similitud, OCR, título, año ni resultados semánticos.', '',
        'El canónico es una decisión operacional reproducible para evitar cómputo duplicado; no implica prioridad bibliográfica ni que los registros de catálogo sean la misma entidad histórica.'
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(REPORT.read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
