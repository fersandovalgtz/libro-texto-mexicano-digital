#!/usr/bin/env python3
"""Compare H2014P5FCA against same-grade W7 sources by exact page hashes.

This analysis uses only hashes already recorded by the W7 source audit. It does
not fetch images, fill the missing page, or alter source admissibility. Its goal
is to test whether a same-grade source is an exact positional near-neighbor of
the 224 observable H2014P5FCA pages.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ASSETS = Path('data/catalog/ltmd_u1_w7_civics_ethics_asset_manifest.csv')
OUT = Path('data/catalog/ltmd_u1_w7_h2014p5_exact_neighbors.csv')
MISMATCHES = Path('data/catalog/ltmd_u1_w7_h2014p5_exact_neighbor_mismatches.csv')
REPORT = Path('data/catalog/ltmd_u1_w7_h2014p5_exact_neighbors.md')
VERSION = 'LTMD_U1_W7_H2014P5_EXACT_NEIGHBORS_0.1'
TARGET = 'H2014P5FCA'
GRADE = '5'
TARGET_GAP_PAGE = 104


def rows(path: Path):
    with path.open(encoding='utf-8', newline='') as f:
        yield from csv.DictReader(f)


def main() -> None:
    by_viewer: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    meta: dict[str, dict[str, str]] = {}
    for row in rows(ASSETS):
        if row['grade_code'] != GRADE:
            continue
        meta.setdefault(row['viewer_key'], row)
        if row['asset_status'] == 'source_jpeg' and row.get('sha256'):
            by_viewer[row['viewer_key']][int(row['viewer_page'])] = row

    target = by_viewer.get(TARGET, {})
    if len(target) != 224:
        raise SystemExit(f'{TARGET}: expected 224 served pages, found {len(target)}')
    if TARGET_GAP_PAGE in target:
        raise SystemExit(f'{TARGET}: expected page {TARGET_GAP_PAGE} to be absent')

    candidate_keys = sorted(k for k in by_viewer if k != TARGET and by_viewer[k])
    if not candidate_keys:
        raise SystemExit('no same-grade W7 source candidates with served pages')

    summaries: list[dict[str, str | int | float]] = []
    mismatch_rows: list[dict[str, str | int]] = []

    for candidate_key in candidate_keys:
        candidate = by_viewer[candidate_key]
        overlap = sorted(set(target) & set(candidate))
        exact = []
        mismatch = []
        for page in overlap:
            if target[page]['sha256'] == candidate[page]['sha256']:
                exact.append(page)
            else:
                mismatch.append(page)
                mismatch_rows.append({
                    'analysis_version': VERSION,
                    'target_viewer': TARGET,
                    'candidate_viewer': candidate_key,
                    'viewer_page': page,
                    'target_sha256': target[page]['sha256'],
                    'candidate_sha256': candidate[page]['sha256'],
                    'target_byte_size': target[page]['byte_size'],
                    'candidate_byte_size': candidate[page]['byte_size'],
                })
        candidate_gap = candidate.get(TARGET_GAP_PAGE)
        summaries.append({
            'analysis_version': VERSION,
            'target_viewer': TARGET,
            'target_generation': meta[TARGET]['catalog_generation'],
            'candidate_viewer': candidate_key,
            'candidate_generation': meta[candidate_key]['catalog_generation'],
            'grade_code': GRADE,
            'target_served_pages': len(target),
            'candidate_served_pages': len(candidate),
            'positional_overlap_pages': len(overlap),
            'exact_positional_matches': len(exact),
            'positional_mismatches': len(mismatch),
            'exact_positional_rate': f'{(len(exact) / len(overlap)) if overlap else 0:.9f}',
            'candidate_has_target_gap_page': int(candidate_gap is not None),
            'candidate_gap_page_sha256': candidate_gap['sha256'] if candidate_gap else '',
            'candidate_gap_page_byte_size': candidate_gap['byte_size'] if candidate_gap else '',
            'candidate_gap_page_source_url': candidate_gap['source_asset_url'] if candidate_gap else '',
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    summary_fields = list(summaries[0].keys())
    with OUT.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=summary_fields)
        w.writeheader(); w.writerows(summaries)

    mismatch_fields = [
        'analysis_version', 'target_viewer', 'candidate_viewer', 'viewer_page',
        'target_sha256', 'candidate_sha256', 'target_byte_size', 'candidate_byte_size',
    ]
    with MISMATCHES.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=mismatch_fields)
        w.writeheader(); w.writerows(mismatch_rows)

    ranked = sorted(
        summaries,
        key=lambda r: (float(r['exact_positional_rate']), int(r['exact_positional_matches'])),
        reverse=True,
    )
    best = ranked[0]

    lines = [
        '# LTMD-U1 W7 — vecinos exactos de H2014P5FCA',
        '',
        f'Versión: `{VERSION}`.',
        '',
        'Este análisis compara SHA-256 de páginas ya auditadas en la misma posición lógica. No descarga activos, no imputa la página 104 y no cambia el gate de admisibilidad.',
        '',
        '## Comparación',
        '',
        '| candidato | generación catálogo | páginas candidato | solapamiento posicional | exactas | distintas | tasa exacta | tiene pág. 104 |',
        '|---|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for r in ranked:
        lines.append(
            f"| `{r['candidate_viewer']}` | {r['candidate_generation']} | {r['candidate_served_pages']} | "
            f"{r['positional_overlap_pages']} | {r['exact_positional_matches']} | {r['positional_mismatches']} | "
            f"{float(r['exact_positional_rate']):.6f} | {r['candidate_has_target_gap_page']} |"
        )

    lines += [
        '',
        '## Mejor vecino observado',
        '',
        f"- Candidato: `{best['candidate_viewer']}`.",
        f"- Coincidencias SHA-256 en posiciones comparables: **{best['exact_positional_matches']}/{best['positional_overlap_pages']}**.",
        f"- Tasa exacta posicional: **{float(best['exact_positional_rate']):.6f}**.",
        f"- El candidato {'sí' if int(best['candidate_has_target_gap_page']) else 'no'} contiene una fuente servida en la página lógica **{TARGET_GAP_PAGE}**.",
    ]
    if int(best['candidate_has_target_gap_page']):
        lines += [
            f"- SHA-256 de la página 104 candidata: `{best['candidate_gap_page_sha256']}`.",
            f"- Tamaño: **{best['candidate_gap_page_byte_size']} bytes**.",
            f"- URI fuente institucional del candidato: `{best['candidate_gap_page_source_url']}`.",
        ]

    lines += [
        '',
        '## Regla de interpretación',
        '',
        'Una tasa 1.0 sobre las páginas observables sería evidencia criptográfica de equivalencia posicional para esas páginas, pero no observa directamente la página faltante y por sí sola no convierte el libro completo en byte-idéntico. Cualquier uso de la página 104 de otro visor debe registrarse como reconstrucción derivada con procedencia explícita, salvo que evidencia archivística o documental independiente cierre la identidad del objeto.',
    ]
    REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print('target_served_pages', len(target))
    print('candidate_count', len(ranked))
    print('best_candidate', best['candidate_viewer'])
    print('best_exact_matches', best['exact_positional_matches'])
    print('best_overlap', best['positional_overlap_pages'])
    print('best_rate', best['exact_positional_rate'])


if __name__ == '__main__':
    main()
